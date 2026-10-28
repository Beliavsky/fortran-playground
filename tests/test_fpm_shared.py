"""Compatibility, artifact ownership and tamper checks for shared dependencies."""
import copy
import json
import os
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from fpm_shared import (dependency_contract, digest, build_context, export_dependency,
                        validate_export, rewrite_shared_sources, enable_shared_consumer)


class SharedTests(unittest.TestCase):
    def test_catalog_sharing_requires_explicit_current_recipe_and_valid_repositories(self):
        from fpm_catalog_build import validate_build, adapter_digest, NAME_ADAPTER_SHA256
        options = {'adapter_sha256': adapter_digest(), 'shared_dependencies': {
            'adapter_sha256': 'a'*64, 'repositories': ['fortran-lang/stdlib']}}
        validate_build({'id': 'sample', 'catalog_build': options})
        bad = []
        legacy = copy.deepcopy(options); legacy['adapter_sha256'] = NAME_ADAPTER_SHA256; bad.append(legacy)
        for value in ([], ['fortran-lang/stdlib']*2, ['../../stdlib'], ['https://example.com/library']):
            option = copy.deepcopy(options); option['shared_dependencies']['repositories'] = value; bad.append(option)
        option = copy.deepcopy(options); option['shared_dependencies']['adapter_sha256'] = 'stale'; bad.append(option)
        for option in bad:
            with self.subTest(option=option), self.assertRaises(ValueError):
                validate_build({'id': 'sample', 'catalog_build': option})

    def test_patched_or_repackaged_shared_sources_cannot_reuse_an_unpatched_export(self):
        from xprecompile_fpm import build_package
        package = {'repository': 'example/dependency', 'catalog_build': {
            'shared_dependencies': {'repositories': ['example/dependency']}}}
        patched = {**package, 'catalog_patches': {'edits': ['source edit']}}
        repackaged = copy.deepcopy(package)
        repackaged['catalog_build']['source_packages'] = {'example/dependency': {'sources': ['subset.f90']}}
        for candidate in (patched, repackaged):
            with self.subTest(candidate=candidate), self.assertRaisesRegex(ValueError, 'unpatched'):
                build_package(None, None, candidate, 'recipe')

    def fixture(self, directory):
        root = Path(directory)/('library-'+'a'*40)
        root.mkdir()
        (root/'fpm.toml').write_text('name="dependency"\nversion="VERSION"\n[preprocess.cpp]\nmacros=["RANK=7"]\n')
        (root/'source.f90').write_text('module sample\nend module\n')
        pin = {'repository':'example/dependency','revision':'a'*40,'sha256':'b'*64}
        context = build_context({})
        contract = dependency_contract(pin,root,{'dependency':root},context,'recipe','adapter')
        return root,pin,contract

    def test_identity_tracks_build_inputs_but_not_version_rendering_or_source_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root,pin,contract = self.fixture(temporary)
            original = digest(contract)
            (root/'fpm.toml').write_text((root/'fpm.toml').read_text().replace('VERSION','0.8.1'))
            self.assertEqual(original,digest(dependency_contract(pin,root,{},build_context({}),'recipe','adapter')))
            for field in ('revision','sha256'):
                changed={**pin,field:'c'*len(pin[field])}
                self.assertNotEqual(original,digest(dependency_contract(changed,root,{},build_context({}),'recipe','adapter')))
            for context in ({'environment':{'FPM_FFLAGS':'-fdefault-integer-8'},'apt_packages':[]},
                            {'environment':{'FPM_LDFLAGS':'-lblas'},'apt_packages':[]},
                            {'environment':{},'apt_packages':['libblas-dev=1']}):
                self.assertNotEqual(original,digest(dependency_contract(pin,root,{},context,'recipe','adapter')))
            self.assertNotEqual(original,digest(dependency_contract(pin,root,{},build_context({}),'new compiler recipe','adapter')))
            self.assertNotEqual(original,digest(dependency_contract(pin,root,{},build_context({}),'recipe','new adapter')))
            (root/'fpm.toml').write_text((root/'fpm.toml').read_text().replace('RANK=7','RANK=4'))
            self.assertNotEqual(original,digest(dependency_contract(pin,root,{},build_context({}),'recipe','adapter')))

    def test_edge_preprocessing_and_nonleaf_dependencies_are_not_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root,pin,contract=self.fixture(temporary)
            parent=Path(temporary)/'parent';parent.mkdir()
            (parent/'fpm.toml').write_text('name="parent"\n[dependencies.dep]\npath="../'+root.name+'"\npreprocess.cpp.macros=["RANK=4"]\n')
            self.assertNotEqual(digest(contract),digest(dependency_contract(pin,root,{'parent':parent},build_context({}),'recipe','adapter')))
            (root/'fpm.toml').write_text('name="dep"\n[dependencies]\nother="*"\n')
            with self.assertRaisesRegex(ValueError,'leaf'):
                dependency_contract(pin,root,{},build_context({}),'recipe','adapter')

    def test_export_uses_only_dependency_objects_and_modules_then_checks_all_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);root,pin,contract=self.fixture(temporary)
            project=base/'consumer';build=project/'build';mods=build/'mod';mods.mkdir(parents=True)
            (build/'cache.toml').write_text('[dependency]\nproj-dir="../'+root.name+'"\n')
            (mods/'sample.mod').write_bytes(b'correct module')
            (mods/'unrelated.mod').write_bytes(b'not this dependency')
            obj=build/'sample.o';obj.write_bytes(b'object')
            c_source=root/'system.c';c_source.write_text('void utility(void) {}\n')
            c_object=build/'system.o';c_object.write_bytes(b'C object')
            other=build/'other.o';other.write_bytes(b'unrelated')
            commands=[{'directory':str(project),'file':str(root/'source.f90'),
                       'arguments':['gfortran','-c',str(root/'source.f90'),'-J',str(mods),'-o',str(obj)]},
                      {'directory':str(project),'file':str(c_source),
                       'arguments':['gcc','-c',str(c_source),'-o',str(c_object)]},
                      {'directory':str(project),'file':str(base/'other.f90'),
                       'arguments':['gfortran','-c','other.f90','-o',str(other)]}]
            (build/'compile_commands.json').write_text(json.dumps(commands))
            metadata=base/'precompiled.json';metadata.write_text(json.dumps({'recipe':'recipe',
                'compiler_version':'16.2.0','records':[pin]}))
            invocations=[]
            def archive(command,**kwargs):
                invocations.append(command)
                self.assertEqual(command[3:],[str(obj),str(c_object)])
                Path(command[2]).write_bytes(b'archive')
            with patch.dict(os.environ,{'FPM_FFLAGS':'','FPM_LDFLAGS':''}),patch('fpm_shared.subprocess.run',side_effect=archive):
                manifest=export_dependency(contract,base/'cache',project)
                self.assertEqual(manifest['compiled_objects'],0)
                self.assertEqual(manifest['exported_objects'],2)
                self.assertEqual(len(invocations),1)
                self.assertNotIn('include/unrelated.mod',manifest['files'])
                directory=base/'cache'/manifest['key']
                validate_export(directory,manifest['key'],contract)
                export_dependency(contract,base/'cache',project)
                self.assertEqual(len(invocations),1,'Existing valid export must not run ar/compiler again')
                (directory/'include/sample.mod').write_bytes(b'bad')
                with self.assertRaisesRegex(ValueError,'checksum'):
                    validate_export(directory,manifest['key'])

    def test_source_shim_keeps_original_sources_and_runtime_hook_declares_external_modules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root,_,_=self.fixture(temporary)
            before=(root/'source.f90').read_bytes()
            key='a'*24
            plan={'repository':'example/dependency','key':key,'modules':['sample'],
                  'library':'fpm_shared_'+key}
            rewrite_shared_sources({'example/dependency':root},[plan])
            self.assertEqual((root/'source.f90').read_bytes(),before)
            m=tomllib.loads((root/'fpm.toml').read_text())
            self.assertEqual(m['library']['source-dir'],'playground-shared')
            self.assertEqual(m['build']['external-modules'],['sample'])
            project=Path(temporary)/'consumer';project.mkdir()
            def consumer(package,source):
                (project/'fpm.toml').write_text('name="main"\n[build]\nauto-tests=false\n')
                return project
            config=Path(temporary)/'plan.json';config.write_text(json.dumps([plan]))
            import fpm_cache
            with patch('fpm_shared.PLAN',config),patch.object(fpm_cache,'consumer_project',consumer),patch.dict(
                    os.environ,{'FPM_FFLAGS':'-fcoarray=single','FPM_LDFLAGS':''}):
                enable_shared_consumer()
                fpm_cache.consumer_project(root,'program main\nend program\n')
                m=tomllib.loads((project/'fpm.toml').read_text())
                self.assertEqual(m['build']['link'],['fpm_shared_'+key])
                self.assertIn('sample',m['build']['external-modules'])
                self.assertIn('-fcoarray=single',os.environ['FPM_FFLAGS'])
                self.assertIn('/opt/fpm/shared/'+key+'/include',os.environ['FPM_FFLAGS'])

    def test_old_cache_recipe_and_worker_are_not_globally_invalidated(self):
        from fpm_cache import BUILD_FILES, WORKER_FILES
        from fpm_shared import SHARED_FILES
        self.assertFalse(set(SHARED_FILES)&set(BUILD_FILES))
        self.assertFalse(set(SHARED_FILES)&set(WORKER_FILES))

    def test_enable_preserves_catalog_metadata_and_is_idempotent(self):
        import xshared_fpm
        package={'id':'sample','repository':'example/sample','revision':'a'*40,'archive_sha256':'b'*64,
                 'dependencies':[{'repository':'fortran-lang/stdlib','revision':'c'*40,'sha256':'d'*64}]}
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path=root/'fpm_catalog.json'
            path.write_text(json.dumps({'schema':1,'survey_date':'2026-10-26','packages':[package]}))
            with patch.object(xshared_fpm,'ROOT',root),patch.object(xshared_fpm,'catalog',return_value=[package]),patch.object(
                    xshared_fpm,'implementation_digest',return_value='e'*64),patch('sys.argv',['xshared_fpm','--enable','sample']):
                xshared_fpm.main()
                first=path.read_text()
                xshared_fpm.main()
                self.assertEqual(path.read_text(),first)
            self.assertEqual(json.loads(first)['survey_date'],'2026-10-26')
            self.assertEqual(json.loads(first)['schema'],1)

    def test_worker_layer_inputs_survive_return_for_later_child_image_builds(self):
        from unittest.mock import Mock
        import xprecompile_fpm
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            names=('fpm_cache.py','fpm_build.py','fpm_sources.py','fpm_compilers.py',
                   'xfpm_worker.py','fpm_targets.py','fortran_plot.py','fortran_image.py')
            for name in names:(root/name).write_text('# source\n')
            vendor=root/'vendor/pyplot-fortran';vendor.mkdir(parents=True)
            (vendor/'LICENSE').write_text('license')
            image=Mock();image.add_local_dir.return_value=image;image.env.return_value=image;image.build.return_value=image
            with patch.object(xprecompile_fpm,'ROOT',root),patch('fpm_cache.worker_identity',return_value='test-worker'):
                xprecompile_fpm.refresh_worker('app',image)
            directory=image.add_local_dir.call_args.args[0]
            self.assertTrue(directory.is_dir())
            self.assertTrue((directory/'vendor/pyplot-fortran/LICENSE').is_file())
            self.assertTrue(all((directory/name).is_file() for name in names))

    def test_storage_counts_shared_archive_once_and_rejects_conflicting_measurements(self):
        from xprecompile_fpm import artifact_totals
        dep={'repository':'example/dep','key':'a'*24,'artifact_bytes':100,'manifest_sha256':'b'*64}
        entries={'one':{'artifact_bytes':10,'shared_dependencies':[dep]},
                 'two':{'artifact_bytes':20,'shared_dependencies':[dep]}}
        totals=artifact_totals(entries)
        self.assertEqual(totals['total_artifact_bytes'],130)
        self.assertEqual(totals['shared_artifact_bytes'],100)
        self.assertEqual(totals['shared_dependencies'][0]['users'],['one','two'])
        entries['two']['shared_dependencies']=[{**dep,'manifest_sha256':'c'*64}]
        with self.assertRaisesRegex(ValueError,'Conflicting'):
            artifact_totals(entries)
