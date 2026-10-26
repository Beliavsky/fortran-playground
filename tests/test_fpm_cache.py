"""Cache routing and invalidation must not depend on user-controlled paths."""
import json
from pathlib import Path
import re
import tempfile
import shutil
import types
from unittest.mock import Mock, patch
import unittest

from fpm_cache import (catalog, cache_identity, match_package, cached_request_matches, library_inventory,
                       recipe_identity, BUILD_FILES)


class CacheTests(unittest.TestCase):
    def test_catalog_has_pins_checksums_sources_and_descriptions(self):
        root = Path(__file__).resolve().parents[1]
        packages = catalog()
        self.assertIn('fortran-lapack', [p['id'] for p in packages])
        self.assertEqual(len({p['id'] for p in packages}), len(packages))
        generated = json.loads((root / 'site/fpm/packages.json').read_text())
        for package in packages:
            self.assertRegex(package['revision'], r'^[0-9a-f]{40}$')
            self.assertRegex(package['archive_sha256'], r'^[0-9a-f]{64}$')
            self.assertNotIn('\n', package['description'])
            demo = root / 'fpm_catalog/demos' / (package['id'] + '.f90')
            source = demo.read_text()
            self.assertIn('PASS ' + package['id'], source)
            self.assertEqual(next(p for p in generated if p['id'] == package['id'])['source'], source)

    def test_only_exact_pinned_gnu16_consumers_match(self):
        package = catalog()[0]
        payload = {'url': 'https://github.com/' + package['repository'], 'revision': package['revision']}
        self.assertEqual(match_package(payload), package)
        self.assertEqual(match_package({**payload, 'url': payload['url'] + '.git'}), package)
        for changes in ({'revision': ''}, {'revision': 'HEAD'}, {'revision': 'a'*40},
                        {'compiler': 'gfortran17'}, {'compiler': 'ifx'}, {'workflow': 'package'},
                        {'url': payload['url'] + '/evil'}):
            self.assertIsNone(match_package({**payload, **changes}))
        self.assertNotEqual(cache_identity(package, 'old-base'), cache_identity(package, 'new-base'))
        self.assertNotEqual(cache_identity(package, 'base'), cache_identity({**package, 'revision': 'a'*40}, 'base'))

    def test_package_identity_ignores_catalog_metadata_and_pins_every_dependency(self):
        package = catalog()[0]
        key = cache_identity(package, 'recipe')
        self.assertEqual(key, cache_identity({**package, 'description': 'New wording', 'stars': 999,
                                             'category': 'New category', 'license': 'Updated metadata'}, 'recipe'))
        dependency = {'repository': 'owner/dependency', 'revision': 'a'*40, 'sha256': 'b'*64}
        self.assertNotEqual(key, cache_identity({**package, 'dependencies': [dependency]}, 'recipe'))
        locked = {**package, 'dependencies': [dependency]}
        self.assertNotEqual(cache_identity(locked, 'recipe'), cache_identity(
            {**locked, 'dependencies': [{**dependency, 'revision': 'c'*40}]}, 'recipe'))

    def test_build_recipe_excludes_service_and_catalog_but_tracks_build_inputs(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)
            for name in (*BUILD_FILES, 'fpm_build_recipe.json'):
                target = fixture / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / name, target)
            before = recipe_identity(fixture)
            for name in ('xfpm_modal.py', 'xfpm_worker.py', 'fpm_api.py', 'fpm_catalog.json'):
                (fixture / name).write_text('Unrelated change or another catalog entry')
            self.assertEqual(before, recipe_identity(fixture))
            config = json.loads((fixture / 'fpm_build_recipe.json').read_text())
            config['compiler_image'] = 'different compiler image'
            (fixture / 'fpm_build_recipe.json').write_text(json.dumps(config))
            self.assertNotEqual(before, recipe_identity(fixture))

    def test_catalog_extension_and_new_worker_reuse_existing_library(self):
        from xprecompile_fpm import build_catalog
        first = catalog()[0]
        second = {**first, 'id': 'another', 'repository': 'owner/another'}
        old = {'key': cache_identity(first, 'recipe'), 'artifact_image': 'existing-library',
               'image': 'old-worker', 'artifact_bytes': 1, 'revision': first['revision']}
        added = {'key': cache_identity(second, 'recipe'), 'artifact_image': 'new-library',
                 'artifact_bytes': 2, 'revision': second['revision']}
        fake_image = Mock()
        modal = types.SimpleNamespace(Image=types.SimpleNamespace(from_name=lambda name: name))
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / 'build.json'
            report.write_text(json.dumps({'packages': {first['id']: old}}))
            with patch.dict('sys.modules', {'modal': modal}), \
                 patch('xprecompile_fpm.catalog', return_value=[first, second]), \
                 patch('fpm_cache.recipe_identity', return_value='recipe'), \
                 patch('fpm_cache.worker_identity', return_value='new-worker'), \
                 patch('xprecompile_fpm.find_artifact', return_value=None), \
                 patch('xprecompile_fpm.build_package', return_value=added) as compile_library, \
                 patch('xprecompile_fpm.refresh_worker', return_value=fake_image) as refresh, \
                 patch('xprecompile_fpm.verify_cached', return_value={'build_seconds': 0.1}):
                result = build_catalog('app', 'base-image', 'new-worker', report_path=report)
            self.assertEqual(compile_library.call_count, 1)
            self.assertEqual(compile_library.call_args.args[2], second)
            self.assertEqual(refresh.call_args_list[0].args[1], 'existing-library')
            self.assertEqual(result[first['id']]['artifact_image'], 'existing-library')
            self.assertTrue(result[first['id']]['image'].startswith('fpm-run-new-worker-'))
            self.assertEqual(len(json.loads(report.read_text())['packages']), 2)

    def test_recover_remote_library_metadata_without_local_report(self):
        from xprecompile_fpm import find_artifact
        package = catalog()[0]
        metadata = {'key': cache_identity(package, 'recipe'), 'recipe': 'recipe',
                    'revision': package['revision'], 'repository': package['repository'],
                    'records': [{'sha256': package['archive_sha256']}]}
        sandbox = Mock()
        sandbox.stdout.read.return_value = json.dumps(metadata)
        modal = types.SimpleNamespace(Image=types.SimpleNamespace(from_name=lambda name: Mock()),
            Sandbox=types.SimpleNamespace(create=lambda *args, **kwargs: sandbox),
            exception=types.SimpleNamespace(NotFoundError=FileNotFoundError))
        with patch.dict('sys.modules', {'modal': modal}):
            entry = find_artifact('app', package, 'recipe')
            self.assertTrue(entry['artifact_image'].endswith(metadata['key']))
            sandbox.terminate.assert_called_once()
            metadata['revision'] = 'wrong'
            sandbox.stdout.read.return_value = json.dumps(metadata)
            with self.assertRaisesRegex(ValueError, 'does not match'):
                find_artifact('app', package, 'recipe')

    def test_worker_validates_immutable_pin_without_needing_a_catalog(self):
        package = catalog()[0]
        metadata = {**package, 'schema': 1}
        request = {'url': 'https://github.com/' + package['repository'], 'revision': package['revision']}
        self.assertTrue(cached_request_matches(request, metadata))
        for change in ({'workflow': 'package'}, {'compiler': 'ifx'}, {'revision': 'HEAD'},
                       {'url': 'https://github.com/unrelated/repository'}):
            self.assertFalse(cached_request_matches({**request, **change}, metadata))

    def test_recorded_validation_covers_current_pins_and_examples(self):
        import hashlib
        root = Path(__file__).resolve().parents[1]
        report = json.loads((root / 'docs/fpm-precompiled-validation.json').read_text())
        rows = {p['id']: p for p in report['packages']}
        self.assertEqual(set(rows), {p['id'] for p in catalog()})
        for package in catalog():
            row = rows[package['id']]
            source = (root / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text()
            self.assertEqual(row['revision'], package['revision'])
            self.assertEqual(row['verification']['demo_sha256'], hashlib.sha256(source.encode()).hexdigest())
            self.assertTrue(row['verification']['library_reused'])
            self.assertEqual(set(row['verification']['compiled_targets']), {'main.f90', 'playground-main'})

    def test_library_inventory_detects_rebuild_excludes_main_and_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            build = project / 'build/gfortran/consumer'
            build.mkdir(parents=True)
            (build / 'app_main.f90.o').write_bytes(b'main')
            (build / 'library.f90.o').write_bytes(b'library')
            (build / 'library.mod').write_bytes(b'module')
            (build / 'result.png').write_bytes(b'plot')
            before = library_inventory(project)
            self.assertEqual(len(before), 2)
            (build / 'app_main.f90.o').write_bytes(b'new main')
            self.assertEqual(before, library_inventory(project))
            (build / 'library.f90.o').write_bytes(b'new library')
            self.assertNotEqual(before, library_inventory(project))


if __name__ == '__main__':
    unittest.main()
