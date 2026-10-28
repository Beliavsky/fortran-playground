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
    def test_large_build_message_drains_before_stdin_buffer_overflows(self):
        from xprecompile_fpm import write_build_message
        class BoundedWriter:
            def __init__(self):
                self.buffer = bytearray()
                self.received = bytearray()
                self.eof = False
                self.drains = 0
            def write(self, data):
                self.buffer.extend(data)
                if len(self.buffer) > 65536:
                    raise BufferError('Writer buffer exceeded')
            def drain(self):
                self.received.extend(self.buffer)
                self.buffer.clear()
                self.drains += 1
            def write_eof(self):
                self.assert_empty = not self.buffer
                self.eof = True
        writer = BoundedWriter()
        message = {'bundle': 'a' * 3000000, 'source': 'print *, "caf\u00e9"'}
        write_build_message(writer, message)
        self.assertTrue(writer.eof)
        self.assertTrue(writer.assert_empty)
        self.assertGreater(writer.drains, 2)
        self.assertTrue(writer.received.endswith(b'\n'))
        self.assertEqual(json.loads(writer.received), message)

    def incremental_entry(self, package):
        import hashlib
        source = (Path(__file__).resolve().parents[1] / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text(encoding='utf-8')
        key = cache_identity(package, 'recipe')
        return {'key': key, 'artifact_image': 'library-' + key, 'image': 'fpm-run-worker-' + key,
                'artifact_bytes': 1, 'revision': package['revision'],
                'verification': {'library_reused': True, 'build_seconds': 0.1,
                                 'demo_sha256': hashlib.sha256(source.encode()).hexdigest()}}

    def incremental_build(self, packages, previous, *, names=None, **options):
        from contextlib import ExitStack
        from xprecompile_fpm import build_catalog
        added = self.incremental_entry(packages[-1])
        image = Mock()
        modal = types.SimpleNamespace(Image=types.SimpleNamespace(from_name=Mock(return_value=image)))
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            report = Path(temporary) / 'build.json'
            report.write_text(json.dumps({'packages': previous}))
            stack.enter_context(patch.dict('sys.modules', {'modal': modal}))
            stack.enter_context(patch('xprecompile_fpm.catalog', return_value=packages))
            stack.enter_context(patch('fpm_cache.recipe_identity', return_value='recipe'))
            stack.enter_context(patch('fpm_cache.worker_identity', return_value='worker'))
            calls = {}
            for name, value in [('find_artifact', None), ('build_package', added), ('refresh_worker', image),
                                ('verify_cached', added['verification'])]:
                calls[name] = stack.enter_context(patch('xprecompile_fpm.' + name, return_value=value))
            result = build_catalog('app', 'base', 'base-name', names, report, **options)
            saved = json.loads(report.read_text())
        return result, saved, calls, modal.Image.from_name

    def test_unchanged_deployment_starts_no_package_jobs(self):
        package = catalog()[0]
        old = self.incremental_entry(package)
        result, _, calls, lookup = self.incremental_build([package], {package['id']: old})
        self.assertEqual(result[package['id']], old)
        for call in calls.values():
            call.assert_not_called()
        lookup.assert_not_called()

    def test_new_batch_only_compiles_new_package_and_retains_existing_routing(self):
        first, second = catalog()[:2]
        old = self.incremental_entry(first)
        for names in (None, [second['id']]):
            with self.subTest(names=names):
                result, saved, calls, _ = self.incremental_build([first, second], {first['id']: old}, names=names)
                calls['build_package'].assert_called_once()
                self.assertEqual(calls['build_package'].call_args.args[2], second)
                calls['verify_cached'].assert_called_once()
                self.assertEqual(result[first['id']], old)
                self.assertEqual(set(saved['packages']), {first['id'], second['id']})
                self.assertEqual(set(result), {first['id'], second['id']})

    def test_worker_or_example_change_and_reverify_keep_libraries(self):
        package = catalog()[0]
        for change, options in [({}, {'reverify': True}), ({'image': 'old-worker'}, {}),
                                ({'verification': {'library_reused': True, 'demo_sha256': 'old-example'}}, {})]:
            with self.subTest(change=change, options=options):
                old = {**self.incremental_entry(package), **change}
                _, _, calls, _ = self.incremental_build([package], {package['id']: old}, **options)
                calls['build_package'].assert_not_called()
                calls['find_artifact'].assert_not_called()
                calls['verify_cached'].assert_called_once()
                self.assertEqual(calls['refresh_worker'].call_count, int('image' in change))

    def test_force_rebuild_is_explicit(self):
        package = catalog()[0]
        _, _, calls, _ = self.incremental_build([package], {package['id']: self.incremental_entry(package)}, rebuild=True)
        calls['build_package'].assert_called_once()
        calls['find_artifact'].assert_not_called()
        calls['verify_cached'].assert_called_once()

    def test_catalog_has_pins_checksums_sources_and_descriptions(self):
        root = Path(__file__).resolve().parents[1]
        packages = catalog()
        self.assertIn('fortran-lapack', [p['id'] for p in packages])
        self.assertEqual(len({p['id'] for p in packages}), len(packages))
        generated = json.loads((root / 'site/fpm/packages.json').read_text(encoding='utf-8'))
        for package in packages:
            self.assertRegex(package['revision'], r'^[0-9a-f]{40}$')
            self.assertRegex(package['archive_sha256'], r'^[0-9a-f]{64}$')
            self.assertNotIn('\n', package['description'])
            demo = root / 'fpm_catalog/demos' / (package['id'] + '.f90')
            source = demo.read_text(encoding='utf-8')
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
            for name in ('xfpm_modal.py', 'xfpm_worker.py', 'fortran_image.py', 'fpm_api.py', 'fpm_catalog.json'):
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
                 patch('xprecompile_fpm.verify_cached', return_value={'build_seconds': 0.1, 'library_reused': True}):
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
            source = (root / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text(encoding='utf-8')
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
