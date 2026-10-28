"""Dependency graph identities, link order, source isolation and archive integrity."""
import copy
import json
import os
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from fpm_shared import dependency_contract, digest, build_context
from fpm_shared_graph import (dependency_graph, export_graph_dependency, validate_graph_export,
                              rewrite_graph_sources, graph_digest)


class GraphTests(unittest.TestCase):
    def fixture(self, directory):
        roots = {}; records = []
        for i, name in enumerate(('base', 'middle', 'top')):
            revision = str(i+1)*40
            root = Path(directory)/(name+'-'+revision); root.mkdir()
            (root/'src').mkdir()
            (root/'src'/f'{name}.f90').write_text(f'module {name}\nend module\n')
            (root/'fpm.toml').write_text(f'name="{name}"\n[library]\nsource-dir="src"\n')
            roots['example/'+name] = root
            records.append({'repository':'example/'+name,'revision':revision,'sha256':str(i+4)*64})
        for name, children in [('middle',['base']),('top',['base','middle'])]:
            root=roots['example/'+name]
            with (root/'fpm.toml').open('a') as stream:
                for child in children:
                    stream.write(f'[dependencies.{child}]\npath="../{roots["example/"+child].name}"\n')
        return records,roots

    def graph(self, records, roots):
        return dependency_graph(records,roots,build_context({}),'recipe','leaf','graph')

    def test_topological_order_diamond_deduplication_and_leaf_key_compatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            records,roots=self.fixture(directory); graph=self.graph(records,roots)
            self.assertEqual(list(graph),['example/base','example/middle','example/top'])
            self.assertEqual(graph['example/base'],dependency_contract(records[0],roots['example/base'],
                roots,build_context({}),'recipe','leaf'))
            self.assertEqual(len(graph),3)
            self.assertEqual([p['repository'] for p in graph['example/top']['dependencies']],
                             ['example/base','example/middle'])

    def test_source_and_dependency_updates_invalidate_dependents_not_unrelated_leaves(self):
        with tempfile.TemporaryDirectory() as directory:
            records,roots=self.fixture(directory); before=self.graph(records,roots)
            changed=copy.deepcopy(records); changed[0]['revision']='9'*40
            after=self.graph(changed,roots)
            self.assertTrue(all(digest(before[name])!=digest(after[name]) for name in before))
            (roots['example/middle']/'src/middle.f90').write_text('module middle\ninteger::updated\nend module\n')
            after=self.graph(records,roots)
            self.assertEqual(before['example/base'],after['example/base'])
            self.assertNotEqual(before['example/middle'],after['example/middle'])
            self.assertNotEqual(before['example/top'],after['example/top'])

    def test_cycles_unresolved_paths_and_unpinned_repositories_are_rejected(self):
        for mode in ('cycle','outside','unresolved','unpinned'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                records,roots=self.fixture(directory)
                if mode=='unpinned':records.pop()
                else:
                    root=roots['example/base']
                    spec={'cycle':f'path="../{roots["example/top"].name}"',
                          'outside':'path="../outside"','unresolved':'git="https://github.com/example/other"'}[mode]
                    with (root/'fpm.toml').open('a') as stream:stream.write('[dependencies.other]\n'+spec+'\n')
                with self.assertRaises(ValueError):self.graph(records,roots)

    def test_hosted_shims_keep_original_sources_and_flatten_dependencies_in_link_order(self):
        with tempfile.TemporaryDirectory() as directory:
            records,roots=self.fixture(directory); graph=self.graph(records,roots)
            plans=[{'repository':name,'key':digest(contract)[:24],
                    'modules':[name.split('/')[1]],'library':'fpm_shared_'+digest(contract)[:24]}
                   for name,contract in reversed(list(graph.items()))]
            rewrite_graph_sources(roots,plans)
            for name,root in roots.items():
                manifest=tomllib.loads((root/'fpm.toml').read_text())
                self.assertNotIn('dependencies',manifest)
                self.assertEqual(manifest['build']['link'],[p['library'] for p in plans])
                self.assertTrue((root/'src'/(name.split('/')[1]+'.f90')).exists())
            self.assertEqual(plans[0]['repository'],'example/top')
            self.assertEqual(plans[-1]['repository'],'example/base')

    def test_flattening_retains_native_links_from_transitive_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            records,roots=self.fixture(directory)
            with (roots['example/base']/'fpm.toml').open('a') as stream:
                stream.write('[build]\nlink=["blas","lapack"]\n')
            graph=self.graph(records,roots)
            plans=[{'repository':name,'key':digest(contract)[:24], 'modules':[],
                    'library':'fpm_shared_'+digest(contract)[:24]}
                   for name,contract in reversed(list(graph.items()))]
            rewrite_graph_sources(roots,plans)
            top=tomllib.loads((roots['example/top']/'fpm.toml').read_text())
            self.assertEqual(top['build']['link'],[p['library'] for p in plans]+['blas','lapack'])

    def test_export_nonleaf_contains_only_own_objects_and_detects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            records,roots=self.fixture(directory); contract=self.graph(records,roots)['example/middle']
            project=Path(directory)/'consumer'; build=project/'build'; build.mkdir(parents=True)
            (build/'cache.toml').write_text(''.join(f'[{i}]\nproj-dir="{root.as_posix()}"\n' for i,root in enumerate(roots.values())))
            (Path(directory)/'precompiled.json').write_text(json.dumps({'recipe':'recipe','compiler_version':'16.2.0','records':records}))
            commands=[]
            for name,root in roots.items():
                short=name.split('/')[1]; obj=build/(short+'.o');obj.write_bytes(b'object')
                (build/(short+'.mod')).write_bytes(b'module')
                commands.append({'directory':str(project),'file':str(root/'src'/(short+'.f90')),
                    'arguments':['gfortran','-J'+str(build),'-o',str(obj)]})
            (build/'compile_commands.json').write_text(json.dumps(commands))
            invocations=[]
            def archive(args,**kwargs):
                invocations.append(args)
                self.assertEqual(args[3:],[str(build/'middle.o')])
                Path(args[2]).write_bytes(b'archive')
            message={'contract':contract,'leaf_adapter':'leaf','graph_adapter':'graph'}
            with patch.dict(os.environ,{'FPM_FFLAGS':'','FPM_LDFLAGS':''}),patch('fpm_shared_graph.subprocess.run',side_effect=archive):
                manifest=export_graph_dependency(message,Path(directory)/'cache',project)
                path=Path(directory)/'cache'/manifest['key']
                self.assertEqual(manifest['modules'],['middle'])
                self.assertEqual(manifest['compiled_objects'],0)
                self.assertEqual(len(invocations),1)
                export_graph_dependency(message,Path(directory)/'cache',project)
                self.assertEqual(len(invocations),1)
                validate_graph_export(path,manifest['key'],contract)
                (path/'include/middle.mod').write_bytes(b'corrupted')
                with self.assertRaises(ValueError):validate_graph_export(path,manifest['key'])

    def test_procedural_libraries_without_modules_are_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);contract={'source':'procedure'};key=digest(contract)[:24]
            (root/'lib').mkdir();library='fpm_shared_'+key
            archive=root/'lib'/('lib'+library+'.a');archive.write_bytes(b'archive')
            from fpm_shared import file_hash
            manifest={'key':key,'contract':contract,'modules':[],'library':library,
                      'files':{archive.relative_to(root).as_posix():{'bytes':archive.stat().st_size,'sha256':file_hash(archive)}}}
            (root/'manifest.json').write_text(json.dumps(manifest))
            validate_graph_export(root,key,contract)
            archive.write_bytes(b'changed')
            with self.assertRaises(ValueError):validate_graph_export(root,key)

    def test_enabling_graph_is_idempotent_preserves_metadata_and_rejects_patched_sources(self):
        from xshared_graph import enable_packages
        root=Path(__file__).resolve().parents[1]
        document={'schema':1,'survey_date':'original','packages':[{'id':'top','repository':'example/top',
            'dependencies':[{'repository':'example/base'}]}]}
        result=enable_packages(document,{'top'},root)
        self.assertEqual(result['survey_date'],'original')
        self.assertEqual(result,enable_packages(result,{'top'},root))
        self.assertNotIn('catalog_build',document['packages'][0])
        setting=result['packages'][0]['catalog_build']['shared_dependencies']
        self.assertEqual(setting['repositories'],['example/top','example/base'])
        self.assertEqual(setting['adapter_sha256'],graph_digest(root))
        document['packages'][0]['catalog_patches']={'edits':['change']}
        with self.assertRaisesRegex(ValueError,'unpatched'):enable_packages(document,{'top'},root)

    def test_batch_opt_in_preserves_existing_patched_recipes_and_unselected_packages(self):
        import xprecompile_fpm
        document={'schema':1,'survey_date':'original','packages':[
            {'id':'eligible','repository':'example/eligible'},
            {'id':'patched','repository':'example/patched','catalog_patches':{'edits':['edit']}},
            {'id':'repackaged','repository':'example/repackaged','catalog_build':{'source_packages':{'library':{}}}},
            {'id':'unselected','repository':'example/unselected'}]}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'fpm_catalog.json'
            path.write_text(json.dumps(document))
            with patch.object(xprecompile_fpm,'ROOT',root),patch('xshared_graph.graph_digest',return_value='a'*64):
                enabled=xprecompile_fpm.enable_shared_catalog({'eligible','patched','repackaged'})
                self.assertEqual(enabled,{'eligible'})
                updated=json.loads(path.read_text())
                self.assertEqual(updated['packages'][1:],document['packages'][1:])
                self.assertEqual(updated['survey_date'],'original')
                first=path.read_text()
                xprecompile_fpm.enable_shared_catalog({'eligible','patched','repackaged'})
                self.assertEqual(path.read_text(),first)
