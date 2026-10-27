"""Local catalog execution shares the hosted UI, with fresh local builds."""
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from local_fpm_catalog import compact_sources, execute_catalog, validate_local_request
from xfortran_serve import LocalServer
from test_fpm_service import archive

MAIN = 'program main\nuse fixture\ninteger i\nread *,i\nprint *,answer()+i\nend program\n'


def fixture():
    source = ('module fixture\ncontains\ninteger function answer()\nanswer=39\n'
              'end function\nend module\n')
    data = archive({'fpm.toml': 'name="fixture"\nversion="1.0.0"\n', 'src/fixture.f90': source,
                    'app/main.f90': 'program own\nuse fixture\nprint *,answer()\nend program\n',
                    'test/check.f90': 'program check\nuse fixture\nif(answer()/=40) stop 1\nprint *,"TEST PASS"\nend\n'})
    from fpm_catalog_patches import patch_digest
    package = {'id': 'fixture', 'repository': 'test/fixture', 'revision': 'a'*40,
               'archive_sha256': hashlib.sha256(data).hexdigest(),
               'catalog_patches': {'adapter_sha256': patch_digest(), 'edits': [{
                   'path': 'src/fixture.f90', 'sha256': hashlib.sha256(source.encode()).hexdigest(),
                   'before': 'answer=39', 'after': 'answer=40'}]}}
    return package, data


def payload(**extra):
    return {'url': 'https://github.com/test/fixture', 'revision': 'a'*40,
            'source': MAIN, 'stdin': '2\n', **extra}


class CatalogExecutionTests(unittest.TestCase):
    def test_package_target_patterns_are_execution_settings(self):
        _, data = fixture()
        with tempfile.TemporaryDirectory() as temporary, patch('local_fpm_catalog.catalog', return_value=[]), \
                patch('local_fpm_catalog.execute_project', return_value={'ok': True, 'status': 'PASS', 'stages': []}) as execute:
            for action in ('run', 'example'):
                result = execute_catalog(temporary, payload(workflow='package', action=action, target='demo_* other'),
                                         downloader=lambda *a, **k: data)
                self.assertTrue(result['ok'])
                self.assertEqual(execute.call_args.kwargs['options']['target'], 'demo_* other')
                self.assertEqual(execute.call_args.kwargs['options']['action'], action)

    def test_short_paths_preserve_external_and_nested_dependency_references(self):
        import tomllib
        with tempfile.TemporaryDirectory() as temporary:
            sources = Path(temporary).resolve()
            root = sources / 'packages/0' / ('long-package-' + 'a'*40)
            helper = sources / 'packages/1' / ('long-helper-' + 'b'*40)
            nested = root / 'nested'
            nested.mkdir(parents=True); helper.mkdir(parents=True)
            (root / 'fpm.toml').write_text('name="root"\n[dependencies]\n'
                + 'helper={path=' + json.dumps(Path(os.path.relpath(helper, root)).as_posix()) + '}\n'
                + 'nested={path="nested"}\n')
            (nested / 'fpm.toml').write_text('name="nested"\n[dependencies]\nhelper={path='
                + json.dumps(Path(os.path.relpath(helper, nested)).as_posix()) + '}\n')
            (helper / 'fpm.toml').write_text('name="helper"\n')
            (helper / 'code.f90').write_text('unchanged source')
            moved = compact_sources(sources, [root, helper])
            for manifest in [moved[root] / 'fpm.toml', moved[root] / 'nested/fpm.toml']:
                spec = tomllib.loads(manifest.read_text())['dependencies']['helper']
                self.assertEqual((manifest.parent / spec['path']).resolve(), moved[helper])
            self.assertEqual((moved[helper] / 'code.f90').read_text(), 'unchanged source')
            self.assertFalse(root.exists())

    def test_fresh_source_builds_patch_and_preserve_existing_projects(self):
        package, data = fixture()
        roots = []

        def execute(root, compiler, **kwargs):
            roots.append(root)
            self.assertIn('answer=40', (root / 'src/fixture.f90').read_text())
            self.assertEqual(kwargs['options']['source'], MAIN)
            self.assertEqual(kwargs['options']['stdin'], '2\n')
            self.assertEqual(kwargs['options']['compile_timeout'], 0)
            return {'ok': True, 'status': 'PASS', 'compiler_version': 'GNU 16', 'stages': [
                {'command': ['fpm', 'build'], 'ok': True, 'stdout': '', 'stderr': '', 'seconds': 0.1},
                {'command': ['fpm', 'run'], 'ok': True, 'stdout': '42\n', 'stderr': '', 'seconds': 0.1}]}

        with tempfile.TemporaryDirectory() as temporary, patch('local_fpm_catalog.catalog', return_value=[package]), \
                patch('local_fpm_catalog.execute_project', side_effect=execute):
            workspace = Path(temporary)
            existing = workspace / 'existing-project'
            existing.mkdir(); (existing / 'object.o').write_bytes(b'preserve')
            for _ in range(2):
                result = execute_catalog(workspace, payload(), downloader=lambda *a, **k: data)
                self.assertTrue(result['ok'])
                self.assertEqual(result['build_mode'], 'from-scratch')
                self.assertNotIn('cache', result)
                self.assertEqual([s['name'] for s in result['stages']], ['Build', 'Run'])
                self.assertFalse(roots[-1].exists())
            self.assertNotEqual(roots[0], roots[1])
            self.assertEqual((existing / 'object.o').read_bytes(), b'preserve')

    def test_compiler_choices_and_source_download_cancellation(self):
        self.assertEqual(validate_local_request(payload(compiler='lfortran'))['compiler'], 'lfortran')
        for compiler in ('ofort', 'unknown', []):
            with self.assertRaises(ValueError):
                validate_local_request(payload(compiler=compiler))
        package, data = fixture()
        cancelled = threading.Event(); cancelled.set()
        with tempfile.TemporaryDirectory() as temporary, patch('local_fpm_catalog.catalog', return_value=[package]), \
                self.assertRaisesRegex(InterruptedError, 'cancelled'):
            execute_catalog(temporary, payload(), cancel=cancelled,
                            downloader=lambda *a, **k: self.fail('cancelled download must not start'))

    def test_catalog_flags_are_local_and_non_gnu_recipes_are_rejected(self):
        from fpm_catalog_build import adapter_digest
        package, data = fixture()
        package['catalog_build'] = {'adapter_sha256': adapter_digest(),
            'environment': {'FPM_FFLAGS': '-fopenmp'}, 'apt_packages': ['libblas-dev=3.12.1-6']}
        with tempfile.TemporaryDirectory() as temporary, patch('local_fpm_catalog.catalog', return_value=[package]), \
                patch('local_fpm_catalog.execute_project', return_value={'ok': True, 'status': 'PASS'}) as execute:
            result = execute_catalog(temporary, payload(), downloader=lambda *a, **k: data)
            self.assertEqual(execute.call_args.kwargs['build_environment'], {'FPM_FFLAGS': '-fopenmp'})
            self.assertTrue(any('libblas-dev' in note for note in result['notes']))
            with self.assertRaisesRegex(ValueError, 'GNU-specific'):
                execute_catalog(temporary, payload(compiler='ifx'),
                                downloader=lambda *a, **k: self.fail('must reject before downloading'))

    @unittest.skipUnless(shutil.which('fpm') and shutil.which('gfortran'), 'local FPM and GNU Fortran required')
    def test_real_main_stdin_and_package_tests(self):
        package, data = fixture()
        with tempfile.TemporaryDirectory() as temporary, patch('local_fpm_catalog.catalog', return_value=[package]):
            for request, expected in [(payload(), '42'),
                (payload(workflow='package', action='test', stdin='', source=''), 'TEST PASS')]:
                result = execute_catalog(temporary, request, downloader=lambda *a, **k: data,
                    overrides={'gfortran': shutil.which('gfortran')}, fpm_path=shutil.which('fpm'))
                self.assertTrue(result['ok'], result)
                self.assertIn(expected, result['stages'][-1]['stdout'])


class CatalogHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        compilers = {name: {'path': 'compiler', 'version': name} for name in
                     ('gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort')}
        with patch('xfortran_serve.discover', return_value=compilers):
            self.server = LocalServer(self.temporary.name, port=0)
        self.server.fpm_path = 'fpm'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.stop_jobs(); self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.temporary.cleanup()

    def request(self, path, data=None, *, token=True, origin=None):
        headers = {'X-Local-Token': self.server.token} if token else {}
        if data is not None:
            headers.update({'Origin': origin or self.server.origin, 'Content-Type': 'application/json'})
        client = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        client.request('GET' if data is None else 'POST', path,
                       None if data is None else json.dumps(data), headers)
        response = client.getresponse(); body = response.read(); status = response.status
        value = json.loads(body) if response.headers['Content-Type'].startswith('application/json') else body.decode()
        client.close()
        return status, value

    def test_shared_page_secondary_page_assets_and_security(self):
        main = self.request('/fpm/')[1]
        self.assertIn('data-execution="local"', main)
        self.assertIn('id="available-package"', main)
        self.assertIn('/fpm/projects/', main)
        self.assertNotIn('modal.run', main)
        self.assertNotIn('30 jobs per address', main)
        self.assertIn('Local FPM projects', self.request('/fpm/projects/')[1])
        self.assertIn('id="compiler-choices"', self.request('/fpm/projects/')[1])
        for name in ('fpm/fpm.mjs', 'fpm/project_export.mjs', 'fpm/fpm.css', 'editors.mjs',
                     'indentation.mjs', 'plots.mjs', 'service_config.mjs', 'config.mjs', 'style.css'):
            self.assertEqual(self.request('/fpm/ui/' + name)[0], 200)
        from fpm_cache import catalog
        self.assertEqual(len(self.request('/fpm/packages.json')[1]), len(catalog()))
        self.assertGreater(len(self.request('/fpm/all-packages.json')[1]), len(catalog()))
        self.assertGreaterEqual(len(self.request('/fpm/translated-r.json')[1]), 596)
        self.assertIn('run.py', self.request('/fpm/project-runtime.json')[1])
        self.assertEqual(self.request('/fpm/ui/../../fpm_catalog.json')[0], 404)
        self.assertEqual(self.request('/api/fpm/catalog/health', token=False)[0], 403)
        health = self.request('/api/fpm/catalog/health')[1]
        self.assertTrue(health['local'])
        self.assertIn('lfortran', health['compilers'])
        self.assertNotIn('ofort', health['compilers'])
        self.assertEqual(self.request('/api/fpm/catalog/jobs', payload(), origin='https://other.example')[0], 403)

    def test_poll_cancel_and_shared_job_admission(self):
        entered = threading.Event()
        def execute(*args, cancel, **kwargs):
            entered.set(); cancel.wait(5)
            return {'ok': False, 'error': 'Cancelled', 'stages': [], 'local': True}
        with patch('local_fpm_catalog.execute_catalog', side_effect=execute):
            status, job = self.request('/api/fpm/catalog/jobs', payload())
            self.assertEqual(status, 202)
            self.assertTrue(entered.wait(2))
            self.assertEqual(self.request('/api/fpm/catalog/jobs', payload())[0], 409)
            identifier = job['id']
            self.assertEqual(self.request('/api/fpm/catalog/jobs/' + identifier, token=False)[0], 403)
            self.assertEqual(self.request('/api/fpm/catalog/jobs/' + identifier + '/cancel', {})[0], 200)
            for _ in range(40):
                result = self.request('/api/fpm/catalog/jobs/' + identifier)[1]
                if result['state'] == 'done':
                    break
                time.sleep(0.05)
            self.assertEqual(result['state'], 'done')
            self.assertEqual(result['result']['error'], 'Cancelled')

    @unittest.skipUnless(shutil.which('fpm') and shutil.which('gfortran'), 'local FPM and GNU Fortran required')
    def test_real_compile_and_run_through_catalog_http(self):
        package, data = fixture()
        with patch('local_fpm_catalog.catalog', return_value=[package]), \
                patch('local_fpm_catalog.fetch', return_value=data):
            status, job = self.request('/api/fpm/catalog/jobs', payload())
            self.assertEqual(status, 202)
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                result = self.request('/api/fpm/catalog/jobs/' + job['id'])[1]
                if result['state'] == 'done':
                    break
                time.sleep(0.1)
            self.assertEqual(result['state'], 'done')
            self.assertTrue(result['result']['ok'], result)
            self.assertIn('42', result['result']['stages'][-1]['stdout'])
            self.assertEqual(list(Path(self.temporary.name).iterdir()), [])
