"""Catalog adapters must stay explicit, locked and isolated from public requests."""
import hashlib
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import Mock, patch

from fpm_cache import cache_identity
from fpm_catalog_build import CatalogPreparer, adapter_digest, validate_build, build_image
from fpm_sources import Preparer, validate_request
from test_fpm_service import archive, PAYLOAD


class CatalogBuildTests(unittest.TestCase):
    def options(self, **values):
        return {'adapter_sha256': adapter_digest(), **values}

    def test_cpp_flags_are_pinned_and_scoped_to_unshared_source_recipes(self):
        from fpm_catalog_build import SOURCE_ALLOWANCE_ADAPTER_SHA256
        source = {'manifest': 'name="cpp"\n[library]\nsource-dir="playground-library"\n',
                  'sources': ['src/binding.cpp']}
        package = {'id': 'cpp', 'repository': 'example/cpp',
                   'revision': 'a'*40, 'archive_sha256': 'b'*64, 'catalog_build': self.options(
            source_packages={'example/cpp': source},
            environment={'FPM_CXXFLAGS': '-std=c++20 -I/usr/include/torch/csrc/api/include'})}
        validate_build(package)
        changed = json.loads(json.dumps(package))
        changed['catalog_build']['environment']['FPM_CXXFLAGS'] = '-std=c++17'
        self.assertNotEqual(cache_identity(package, 'recipe'),cache_identity(changed,'recipe'))
        for changes in ({'adapter_sha256': SOURCE_ALLOWANCE_ADAPTER_SHA256},
                        {'source_packages': {}},
                        {'shared_dependencies': {'adapter_sha256':'a'*64,'repositories':['example/cpp']}}):
            changed = json.loads(json.dumps(package));changed['catalog_build'].update(changes)
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError,r'C\+\+ flags'):
                validate_build(changed)
        with self.assertRaisesRegex(ValueError,'Invalid FPM request'):
            validate_request({**PAYLOAD,'environment':{'FPM_CXXFLAGS':'-std=c++20'}})

    def test_reviewed_source_limit_and_legacy_cache_policy(self):
        from fpm_catalog_build import UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': []}
        for count in (0, 500, 501, 809, 1000, 1001):
            spec['sources'] = [f'src/item_{i}.f90' for i in range(count)]
            for digest, maximum in ((adapter_digest(), 1000),
                                    (SOURCE_LIMIT_ADAPTER_SHA256, 1000),
                                    (UPPERCASE_FYPP_ADAPTER_SHA256, 500)):
                package = {'id': 'limit', 'catalog_build': self.options(
                    adapter_sha256=digest, source_packages={'example/library': spec})}
                with self.subTest(count=count, maximum=maximum):
                    if 1 <= count <= maximum:
                        validate_build(package)
                    else:
                        with self.assertRaisesRegex(ValueError, 'source package'):
                            validate_build(package)

    def test_short_source_root_preserves_contents_and_rejects_public_or_old_options(self):
        from fpm_catalog_build import SOURCE_LIMIT_ADAPTER_SHA256
        data = archive({'src/solver.f90': 'module solver\nend module\n',
                        'README': 'original source tree\n'})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['src/solver.f90'], 'short_root': True}
        options = self.options(source_packages={'example/library': spec})
        with tempfile.TemporaryDirectory() as temporary:
            relative, records = CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
            root = Path(temporary)/relative
            self.assertEqual(root.name, 'p')
            self.assertEqual((root/'README').read_text(),
                             'original source tree\n')
            self.assertEqual((root/'src/solver.f90').read_bytes(),
                             (root/'playground-library/solver.f90').read_bytes())
            self.assertEqual(records, [pin])
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            original = Path(outside)/'README'
            original.write_text('outside staging area')
            with patch('fpm_catalog_build.extract_archive', return_value=Path(outside)):
                with self.assertRaisesRegex(ValueError, 'staging area'):
                    CatalogPreparer(temporary, options=options, pins=[pin],
                        downloader=lambda *a, **k: data).prepare(PAYLOAD)
            self.assertEqual(original.read_text(), 'outside staging area')
        with self.assertRaises(ValueError):
            validate_build({'id': 'old', 'catalog_build': {**options,
                'adapter_sha256': SOURCE_LIMIT_ADAPTER_SHA256}})
        for value in ('../other', 1, None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Short catalog'):
                validate_build({'id': 'bad', 'catalog_build': self.options(
                    source_packages={'example/library': {**spec, 'short_root': value}})})
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'no fpm.toml'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)

    def test_cpp_wrappers_and_generated_headers_preserve_previous_recipes(self):
        from fpm_catalog_build import GENERATED_SOURCE_ADAPTER_SHA256
        data = archive({'bridge.f90': 'module bridge\nend module\n',
                        'bridge.cxx': 'extern "C" int answer() { return 42; }\n'})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['bridge.f90', 'bridge.cxx', 'generated/version.cpp']}
        asset = {'schema': 1, 'repository': pin['repository'], 'revision': pin['revision'],
                 'inputs': {}, 'files': {'generated/config.h': '#define VERSION 1\n',
                                        'generated/version.cpp': 'const int version = 1;\n'}}
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as assets:
            folder = Path(assets)/'fpm_catalog/generated'
            folder.mkdir(parents=True)
            encoded = json.dumps(asset).encode()
            (folder/'cpp.json').write_bytes(encoded)
            spec['generated'] = {'asset': 'cpp.json', 'sha256': hashlib.sha256(encoded).hexdigest()}
            options = self.options(source_packages={'example/library': spec})
            validate_build({'id': 'cpp', 'catalog_build': options})
            with patch('fpm_catalog_build.ROOT', Path(assets)):
                relative, records = CatalogPreparer(temporary, options=options, pins=[pin],
                    downloader=lambda *a, **k: data).prepare(PAYLOAD)
            root = Path(temporary)/relative
            self.assertEqual((root/'generated/config.h').read_text(), '#define VERSION 1\n')
            self.assertEqual((root/'playground-library/bridge.cpp').read_bytes(), (root/'bridge.cxx').read_bytes())
            self.assertTrue((root/'playground-library/version.cpp').is_file())
            self.assertEqual(records, [pin])
            with self.assertRaises(ValueError):
                validate_build({'id': 'cpp', 'catalog_build': {**options,
                    'adapter_sha256': GENERATED_SOURCE_ADAPTER_SHA256}})
            with self.assertRaises(ValueError):
                validate_build({'id': 'cpp', 'catalog_build': self.options(source_packages={
                    'example/library': {**spec, 'sources': ['bridge.cxx', 'bridge.cpp']}})})
        # Generated Fortran recipes from the previous adapter remain valid,
        # with exactly their original cache keys and asset contracts.
        old = {'id': 'old', 'repository': 'example/library', 'revision': 'a'*40,
               'archive_sha256': pin['sha256'], 'catalog_build': {
                   'adapter_sha256': GENERATED_SOURCE_ADAPTER_SHA256,
                   'source_packages': {'example/library': {**spec, 'sources': ['bridge.f90']}}}}
        key = cache_identity(old, 'recipe')
        validate_build(old)
        self.assertEqual(cache_identity(old, 'recipe'), key)

    def test_generated_assets_check_inputs_pin_paths_and_export_originals(self):
        from fpm_catalog_build import FYPP_ADAPTER_SHA256
        template = b'original template\n'
        data = archive({'source.m4': template.decode(), 'src/lib.f90': 'module lib\nend module\n'})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        asset = {'schema': 1, 'repository': pin['repository'], 'revision': pin['revision'],
                 'inputs': {'source.m4': hashlib.sha256(template).hexdigest()},
                 'files': {'include/value.inc': 'integer, parameter :: n=4\n'}}
        with tempfile.TemporaryDirectory() as assets:
            folder = Path(assets)/'fpm_catalog/generated'
            folder.mkdir(parents=True)
            def options(value=asset):
                encoded = json.dumps(value).encode()
                (folder/'test.json').write_bytes(encoded)
                return self.options(source_packages={'example/library': {
                    'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                    'sources': ['src/lib.f90'], 'generated': {'asset': 'test.json',
                        'sha256': hashlib.sha256(encoded).hexdigest()}}})
            def prepare(opts):
                with tempfile.TemporaryDirectory() as temporary, patch('fpm_catalog_build.ROOT', Path(assets)):
                    relative, records = CatalogPreparer(temporary, options=opts, pins=[pin],
                        downloader=lambda *a, **k: data).prepare(PAYLOAD)
                    root = Path(temporary)/relative
                    self.assertEqual((root/'source.m4').read_bytes(), template)
                    self.assertEqual((root/'include/value.inc').read_text(), asset['files']['include/value.inc'])
                    self.assertEqual(records, [pin])
            opts = options()
            validate_build({'id': 'x', 'catalog_build': opts})
            prepare(opts)
            (folder/'test.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'asset checksum'):
                prepare(opts)
            for value, message in (({**asset, 'revision': 'b'*40}, 'source lock'),
                                   ({**asset, 'inputs': {'source.m4': '0'*64}}, 'input checksum'),
                                   ({**asset, 'files': {'../escape.inc': 'bad'}}, 'leaves'),
                                   ({**asset, 'files': {'src/lib.f90': 'changed'}}, 'overwrite')):
                with self.assertRaisesRegex(ValueError, message):
                    prepare(options(value))
            with self.assertRaises(ValueError):
                validate_build({'id': 'old', 'catalog_build': {**options(), 'adapter_sha256': FYPP_ADAPTER_SHA256}})
            old_fypp = {'id': 'old', 'catalog_build': {'adapter_sha256': FYPP_ADAPTER_SHA256,
                'source_packages': {'example/library': {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                    'sources': ['x.fpp'], 'fypp': {'version': '3.2', 'outputs': {'x.fpp': 'a'*64}}}}}}
            validate_build(old_fypp)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'no fpm.toml'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)

    def test_fypp_generation_is_locked_reproducible_and_catalog_only(self):
        from fpm_catalog_build import MPI_ADAPTER_SHA256
        template = '#:include "kinds.fypp"\nmodule solver\ninteger, parameter :: n = ${count}$\nend module\n'
        expected = b'module solver\ninteger, parameter :: n = 3\nend module\n'
        data = archive({'lib/solver.fpp': template, 'lib/kinds.fypp': '#:set count = 3\n'})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['lib/solver.fpp'], 'fypp': {'version': '3.2', 'outputs': {
                    'lib/solver.fpp': hashlib.sha256(expected).hexdigest()}}}
        options = self.options(source_packages={'example/library': spec})
        validate_build({'id': 'library', 'catalog_build': options})
        with tempfile.TemporaryDirectory() as temporary:
            relative, records = CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
            root = Path(temporary)/relative
            self.assertEqual((root/'playground-library/solver.f90').read_bytes(), expected)
            self.assertEqual((root/'lib/solver.fpp').read_text(), template)
            self.assertEqual(records, [pin])
        bad = {**spec, 'fypp': {'version': '3.2', 'outputs': {'lib/solver.fpp': '0'*64}}}
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'generated source checksum'):
            CatalogPreparer(temporary, options=self.options(source_packages={'example/library': bad}),
                pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)
        with tempfile.TemporaryDirectory() as temporary, patch('importlib.metadata.version', return_value='3.1'), self.assertRaisesRegex(ValueError, 'fypp==3.2'):
            CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
        for invalid in ({**spec, 'fypp': {'version': '3.1', 'outputs': spec['fypp']['outputs']}},
                        {**spec, 'fypp': {'version': '3.2', 'outputs': {}}},
                        {**spec, 'sources': ['lib/solver.fpp', 'other/solver.f90']}):
            with self.assertRaises(ValueError):
                validate_build({'id': 'x', 'catalog_build': self.options(source_packages={'example/library': invalid})})
        with self.assertRaises(ValueError):
            validate_build({'id': 'old', 'catalog_build': {**options, 'adapter_sha256': MPI_ADAPTER_SHA256}})
        old = {'id': 'mpi', 'repository': 'example/library', 'revision': 'a'*40,
               'archive_sha256': pin['sha256'], 'catalog_build': {
                   'adapter_sha256': MPI_ADAPTER_SHA256, 'environment': {'UCX_TLS': 'self,sm'}}}
        key = cache_identity(old, 'recipe')
        validate_build(old)
        self.assertEqual(cache_identity(old, 'recipe'), key)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'no fpm.toml'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)

    def test_locked_uppercase_fypp_templates_are_rendered_as_free_form(self):
        from fpm_catalog_build import CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256
        template = '#:set n = 4\nmodule templated\nUSE other, ONLY: &\n  ${", ".join(set(["zeta", "alpha", "beta"]))}$\ninteger, parameter :: count = ${n}$\nend module\n'
        expected = b'module templated\nUSE other, ONLY: alpha, beta, zeta\ninteger, parameter :: count = 4\nend module\n'
        data = archive({'src/templated.F': template})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['src/templated.F'], 'fypp': {'version': '3.2', 'outputs': {
                    'src/templated.F': hashlib.sha256(expected).hexdigest()}}}
        options = self.options(source_packages={'example/library': spec})
        validate_build({'id': 'library', 'catalog_build': options})
        with tempfile.TemporaryDirectory() as temporary:
            relative, _ = CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
            root = Path(temporary)/relative
            self.assertEqual((root/'src/templated.F').read_text(), template)
            self.assertEqual((root/'playground-library/templated.f90').read_bytes(), expected)
        with self.assertRaises(ValueError):
            validate_build({'id': 'old', 'catalog_build': {**options,
                'adapter_sha256': CPP_SOURCE_ADAPTER_SHA256}})
        validate_build({'id': 'prior-uppercase', 'catalog_build': {**options,
            'adapter_sha256': UPPERCASE_FYPP_ADAPTER_SHA256}})
        bad = {**spec, 'sources': ['src/templated.F', 'other/templated.f90']}
        with self.assertRaises(ValueError):
            validate_build({'id': 'collision', 'catalog_build': self.options(
                source_packages={'example/library': bad})})

    def test_catalog_name_override_preserves_public_validation_and_old_recipes(self):
        from fpm_catalog_build import SOURCE_ADAPTER_SHA256
        data = archive({'fpm.toml': 'name="library.2"\n'})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        options = self.options(manifest_names={'example/library': 'library'})
        validate_build({'id': 'library', 'catalog_build': options})
        with tempfile.TemporaryDirectory() as temporary:
            root, records = CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
            self.assertEqual(tomllib.loads((Path(temporary)/root/'fpm.toml').read_text())['name'], 'library')
            self.assertEqual(records, [pin])
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'package name'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)
        validate_build({'id': 'old', 'catalog_build': {'adapter_sha256': SOURCE_ADAPTER_SHA256}})
        for invalid in ({**options, 'adapter_sha256': SOURCE_ADAPTER_SHA256},
                        self.options(manifest_names={'example/library': 'bad.name'})):
            with self.assertRaises(ValueError):
                validate_build({'id': 'library', 'catalog_build': invalid})

    def test_locked_non_fpm_sources_export_as_an_ordinary_library(self):
        data = archive({'solver.f90': 'module solver\nend module\n',
                        'examples/main.f90': 'program upstream\nend program\n'})
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['solver.f90']}
        options = self.options(source_packages={'example/library': spec})
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        validate_build({'id': 'library', 'catalog_build': options})
        with tempfile.TemporaryDirectory() as temporary:
            preparer = CatalogPreparer(temporary, options=options, pins=[pin], downloader=lambda *a, **k: data)
            path, records = preparer.prepare(PAYLOAD)
            root = Path(temporary) / path
            self.assertEqual([p.name for p in (root/'playground-library').iterdir()], ['solver.f90'])
            self.assertEqual((root/'solver.f90').read_bytes(), (root/'playground-library/solver.f90').read_bytes())
            self.assertTrue((root/'examples/main.f90').exists())
            self.assertEqual(records, [pin])
            self.assertEqual(preparer.prepare(PAYLOAD)[0], path)
        for pins in (None, [{**pin, 'sha256': '0'*64}]):
            with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'lock|checksum'):
                CatalogPreparer(temporary, options=options, pins=pins,
                                downloader=lambda *a, **k: data).prepare(PAYLOAD)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'no fpm.toml'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)
        for sources in (['../solver.f90'], ['/solver.f90'], ['a/solver.f90','b/solver.f90']):
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                validate_build({'id': 'x', 'catalog_build': self.options(
                    source_packages={'example/library': {**spec, 'sources': sources}})})

    def test_legacy_adapter_identity_keeps_existing_package_keys(self):
        from fpm_catalog_build import LEGACY_ADAPTER_SHA256
        options = {'adapter_sha256': LEGACY_ADAPTER_SHA256, 'manifest_versions': {'example/library':'0.0.0'}}
        validate_build({'id': 'library', 'catalog_build': options})
        with self.assertRaises(ValueError):
            validate_build({'id': 'library', 'catalog_build': {**options, 'source_packages': {'example/library': {}}}})

    def test_mixed_sources_are_locked_and_old_recipes_keep_their_file_policy(self):
        from fpm_catalog_build import FORTRAN_SOURCE_ADAPTER_SHA256
        data = archive({'src/bridge.f90': 'module bridge\nend module\n',
                        'native/helper.c': 'int helper(void) { return 42; }\n',
                        'native/main.c': 'int main(void) { return 1; }\n'})
        spec = {'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                'sources': ['src/bridge.f90', 'native/helper.c']}
        options = self.options(source_packages={'example/library': spec})
        package = {'id': 'library', 'catalog_build': options}
        validate_build(package)
        pin = {'repository': 'example/library', 'revision': 'a'*40,
               'sha256': hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as temporary:
            path, records = CatalogPreparer(temporary, options=options, pins=[pin],
                downloader=lambda *a, **k: data).prepare(PAYLOAD)
            root = Path(temporary)/path
            self.assertEqual({p.name for p in (root/'playground-library').iterdir()},
                             {'bridge.f90', 'helper.c'})
            self.assertEqual((root/'native/helper.c').read_bytes(),
                             (root/'playground-library/helper.c').read_bytes())
            self.assertEqual(records, [pin])
        with self.assertRaisesRegex(ValueError, 'supported C'):
            validate_build({**package, 'catalog_build': {
                **options, 'adapter_sha256': FORTRAN_SOURCE_ADAPTER_SHA256}})
        old = {**options, 'adapter_sha256': FORTRAN_SOURCE_ADAPTER_SHA256,
               'source_packages': {'example/library': {**spec, 'sources': ['src/bridge.f90']}}}
        validate_build({**package, 'catalog_build': old})
        original = {'id': 'library', 'repository': 'example/library', 'revision': 'a'*40,
                    'archive_sha256': pin['sha256'], 'catalog_build': old}
        key = cache_identity(original, 'recipe')
        validate_build(original)
        self.assertEqual(cache_identity(original, 'recipe'), key)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'no fpm.toml'):
            Preparer(temporary, pins=[pin], downloader=lambda *a, **k: data).prepare(PAYLOAD)

    def test_environment_and_adapter_only_invalidate_opted_in_package(self):
        package = {'id': 'x', 'repository': 'owner/x', 'revision': 'a'*40, 'archive_sha256': 'b'*64}
        old = cache_identity(package, 'recipe')
        self.assertEqual(old, cache_identity({**package, 'catalog_build': {}}, 'recipe'))
        selected = {**package, 'catalog_build': self.options(apt_packages=['libblas-dev=3.12.1-6'])}
        self.assertNotEqual(old, cache_identity(selected, 'recipe'))
        selected['catalog_build']['apt_packages'] = ['libblas-dev=3.12.1-7']
        self.assertNotEqual(cache_identity(selected, 'recipe'), cache_identity(
            {**package, 'catalog_build': self.options(apt_packages=['libblas-dev=3.12.1-6'])}, 'recipe'))

    def test_local_mpi_transport_is_operator_only_and_keeps_mixed_source_recipes(self):
        from fpm_catalog_build import C_SOURCE_ADAPTER_SHA256
        options = self.options(environment={'UCX_TLS': 'self,sm'})
        validate_build({'id': 'mpi-library', 'catalog_build': options})
        image = Mock()
        build_image('app', image, options)
        image.env.assert_called_once_with({'UCX_TLS': 'self,sm'})
        for value in ('all', 'tcp', 'self,sm\x00', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_build({'id': 'x', 'catalog_build': self.options(environment={'UCX_TLS': value})})
        with self.assertRaises(ValueError):
            validate_build({'id': 'x', 'catalog_build': {**options, 'adapter_sha256': C_SOURCE_ADAPTER_SHA256}})
        old = {'id': 'mixed', 'repository': 'example/library', 'revision': 'a'*40,
               'archive_sha256': 'b'*64, 'catalog_build': {
                   'adapter_sha256': C_SOURCE_ADAPTER_SHA256,
                   'source_packages': {'example/library': {
                       'manifest': 'name="library"\n[library]\nsource-dir="playground-library"\n',
                       'sources': ['bridge.f90', 'helper.c']}}}}
        key = cache_identity(old, 'recipe')
        validate_build(old)
        self.assertEqual(cache_identity(old, 'recipe'), key)
        with self.assertRaises(ValueError):
            validate_request({**PAYLOAD, 'environment': {'UCX_TLS': 'self,sm'}})

    def test_system_dependencies_are_exact_and_environment_is_restricted(self):
        for options in (self.options(apt_packages=['libblas-dev']),
                        self.options(environment={'PATH': '/attacker'}),
                        self.options(metapackages=['openmp']),
                        {'adapter_sha256': 'outdated'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                validate_build({'id': 'x', 'catalog_build': options})
        options = self.options(apt_packages=['libblas-dev=3.12.1-6'],
                               metapackages=['openmp'], environment={'FPM_FFLAGS': '-fopenmp'})
        validate_build({'id': 'x', 'catalog_build': options})
        image = Mock()
        image.apt_install.return_value = image
        image.env.return_value = image
        build_image('app', image, options)
        image.apt_install.assert_called_once_with('libblas-dev=3.12.1-6')
        image.env.assert_called_once_with({'FPM_FFLAGS': '-fopenmp'})

    def test_registry_mapping_and_openmp_are_resolved_before_offline_build(self):
        root = archive({'fpm.toml': 'name="library"\n[dependencies]\nhelper="*"\nopenmp="*"\n'})
        helper = archive({'fpm.toml': 'name="helper"'})
        pins = [{'repository': 'example/library', 'revision': 'a'*40, 'sha256': hashlib.sha256(root).hexdigest()},
                {'repository': 'example/helper', 'revision': 'b'*40, 'sha256': hashlib.sha256(helper).hexdigest()}]
        options = self.options(registry={'helper': {'git': 'https://github.com/example/helper', 'rev': 'b'*40}},
                               metapackages=['openmp'], environment={'FPM_FFLAGS': '-fopenmp'})
        urls = []
        def download(url, **kwargs):
            urls.append(url)
            return helper if '/example/helper/' in url else root
        with tempfile.TemporaryDirectory() as temporary:
            path, records = CatalogPreparer(temporary, pins=pins, options=options, downloader=download).prepare(PAYLOAD)
            manifest = tomllib.loads((Path(temporary)/path/'fpm.toml').read_text())
            self.assertNotIn('openmp', manifest['dependencies'])
            self.assertEqual(manifest['build']['link'], ['gomp'])
            self.assertEqual(set(manifest['dependencies']['helper']), {'path'})
            self.assertEqual([p['revision'] for p in records], ['a'*40, 'b'*40])
            self.assertFalse(any('/commits/' in url for url in urls))
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'registry'):
            Preparer(temporary, downloader=download).prepare({**PAYLOAD, 'revision': 'a'*40})
        with self.assertRaisesRegex(ValueError, 'Invalid FPM request'):
            validate_request({**PAYLOAD, 'catalog_build': options})

    def test_gitlab_mirror_is_explicit_and_pinned(self):
        root = archive({'fpm.toml': 'name="library"\n[dependencies]\nhelper={git="https://gitlab.com/example/helper.git",tag="v1"}'})
        helper = archive({'fpm.toml': 'name="helper"\nversion="VERSION"'})
        pins = [{'repository': 'example/library', 'revision': 'a'*40, 'sha256': hashlib.sha256(root).hexdigest()},
                {'repository': 'example/helper', 'revision': 'b'*40, 'sha256': hashlib.sha256(helper).hexdigest()}]
        options = self.options(git_aliases={'https://gitlab.com/example/helper':'https://github.com/example/helper'},
                               manifest_versions={'example/helper':'0.0.0'})
        def download(url, **kwargs):
            self.assertNotIn('gitlab.com', url)
            return helper if '/example/helper/' in url else root
        with tempfile.TemporaryDirectory() as temporary:
            _, records = CatalogPreparer(temporary, options=options, pins=pins, downloader=download).prepare(PAYLOAD)
            self.assertEqual(records[-1]['repository'], 'example/helper')
            manifests = [tomllib.loads(p.read_text()) for p in Path(temporary).rglob('fpm.toml')]
            self.assertEqual(next(m for m in manifests if m['name'] == 'helper')['version'], '0.0.0')
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
            CatalogPreparer(temporary, options={}, pins=pins, downloader=download).prepare(PAYLOAD)


class CatalogPatchTests(unittest.TestCase):
    def package(self, data=b'old source\n', before='old', after='new', path='src/code.f90'):
        from fpm_catalog_patches import patch_digest
        return {'id': 'patched', 'catalog_patches': {'adapter_sha256': patch_digest(),
            'edits': [{'path': path, 'sha256': hashlib.sha256(data).hexdigest(),
                       'before': before, 'after': after}]}}

    def test_checksum_guarded_patch_and_cache_isolation(self):
        from fpm_catalog_patches import apply_patches
        package = self.package()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)/'src/code.f90'
            source.parent.mkdir()
            source.write_bytes(b'old source\n')
            apply_patches(package, temporary)
            self.assertEqual(source.read_bytes(), b'new source\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                apply_patches(package, temporary)
        base = {'id': 'x', 'repository': 'owner/x', 'revision': 'a'*40, 'archive_sha256': 'b'*64}
        self.assertEqual(cache_identity(base, 'recipe'), cache_identity({**base, 'catalog_patches': {}}, 'recipe'))
        self.assertNotEqual(cache_identity(base, 'recipe'), cache_identity({**base, **package}, 'recipe'))
        changed = self.package(after='different')
        self.assertNotEqual(cache_identity({**base, **package}, 'recipe'), cache_identity({**base, **changed}, 'recipe'))

    def test_manifest_patch_survives_platform_line_endings_but_rejects_content_changes(self):
        from fpm_catalog_patches import apply_patches
        original = b'name = "demo"\n[build]\nlink = "flann"\n'
        package = self.package(data=original, before='link = "flann"',
                               after='link = ":libflann.so.1.9"', path='fpm.toml')
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / 'fpm.toml'
            for data in (original, original.replace(b'\n', b'\r\n')):
                manifest.write_bytes(data)
                apply_patches(package, temporary)
                self.assertEqual(manifest.read_bytes(), original.replace(b'"flann"', b'":libflann.so.1.9"'))
            changed = original.replace(b'"demo"', b'"different"')
            manifest.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                apply_patches(package, temporary)
            self.assertEqual(manifest.read_bytes(), changed)

    def test_legacy_patch_keeps_strict_byte_semantics(self):
        from fpm_catalog_patches import apply_patches, LEGACY_ADAPTER_SHA256, validate_patches
        package = self.package()
        package['catalog_patches']['adapter_sha256'] = LEGACY_ADAPTER_SHA256
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'src/code.f90'
            source.parent.mkdir()
            source.write_bytes(b'old source\r\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                apply_patches(package, temporary)
            source.write_bytes(b'old source\n')
            apply_patches(package, temporary)
            self.assertEqual(source.read_bytes(), b'new source\n')
        package['catalog_patches']['adapter_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validate_patches(package)

    def test_patch_rejects_escape_and_ambiguous_matches(self):
        from fpm_catalog_patches import apply_patches, validate_patches
        for path in ('../code.f90', '/code.f90', 'C:/code.f90', 'src\\code.f90'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_patches(self.package(path=path))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)/'src/code.f90'
            source.parent.mkdir()
            for data, before in ((b'old old', 'old'), (b'something else', 'old')):
                source.write_bytes(data)
                with self.assertRaisesRegex(ValueError, 'exactly once'):
                    apply_patches(self.package(data=data, before=before), temporary)
