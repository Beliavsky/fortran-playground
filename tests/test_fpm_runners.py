from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import threading
import time
import http.client
import unittest
from unittest.mock import Mock, patch

import fpm_runner
import fortran_fpm
import xfortran_run
import xplayground_run


def fixture(root):
    for directory in ('src', 'app', 'test'):
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / 'fpm.toml').write_text('name="test-package"\n')
    (root / 'src/math.f90').write_text('module sample\ncontains\ninteger function answer()\nanswer=42\nend function\nend module\n')
    (root / 'app/main.f90').write_text('program main\nuse sample\ninteger n\nread(*,*) n\nif(n+answer()/=43)error stop\nprint *,"APP PASS"\nend program\n')
    (root / 'test/check.f90').write_text('program check\nuse sample\nif(answer()/=42)error stop\nprint *,"TEST PASS"\nend program\n')


class LocalTests(unittest.TestCase):
    def test_validation_and_paths(self):
        for options in [{'action': 'install'}, {'profile': 'fast'}, {'target': '--runner'}, {'compile_timeout': -1},
                        {'source': ''}, {'source': 'program main', 'action': 'test'}, {'stdin': 'a', 'action': 'build'},
                        {'run_timeout': float('nan')}, {'output_limit': 0}, {'fail_fast': 'yes'}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                fortran_fpm.validate_options(options)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                fortran_fpm.project_directory(temporary)

    def test_continues_after_missing_compiler_and_fail_fast_skips(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); fixture(root)
            failure = {'compiler': 'gfortran', 'ok': False, 'status': 'FAIL'}
            success = {'compiler': 'ifx', 'ok': True, 'status': 'PASS'}
            with patch('fortran_fpm.execute_project', side_effect=[failure, success]) as execute:
                rows = fortran_fpm.compare_projects(root, ['gfortran', 'ifx'])
                self.assertEqual(execute.call_count, 2)
                self.assertTrue(rows[1]['ok'])
            with patch('fortran_fpm.execute_project', return_value=failure) as execute:
                rows = fortran_fpm.compare_projects(root, ['gfortran', 'ifx'], options={'fail_fast': True})
                self.assertEqual(execute.call_count, 1)
                self.assertEqual(rows[1]['status'], 'SKIP')

    @unittest.skipUnless(shutil.which('fpm') and shutil.which('gfortran'), 'FPM and GNU Fortran required')
    def test_native_project_tests_stdin_custom_main_and_original_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'package with spaces'; fixture(root)
            original = (root / 'fpm.toml').read_bytes()
            run = fortran_fpm.execute_project(root, 'gfortran', options={'stdin': '1\n'})
            self.assertTrue(run['ok'], run)
            self.assertIn('APP PASS', run['execution']['stdout'])
            tests = fortran_fpm.execute_project(root, 'gfortran', options={'action': 'test'})
            self.assertTrue(tests['ok'], tests)
            self.assertIn('TEST PASS', tests['execution']['stdout'])
            main = 'program main\nuse sample\nif(answer()/=42)error stop\nprint *,"CONSUMER PASS"\nend program\n'
            consumer = fortran_fpm.execute_project(root, 'gfortran', options={'source': main})
            self.assertTrue(consumer['ok'], consumer)
            self.assertIn('CONSUMER PASS', consumer['execution']['stdout'])
            self.assertEqual((root / 'fpm.toml').read_bytes(), original)
            self.assertFalse(list(root.glob('.fp-*')))
            cancelled = threading.Event(); cancelled.set()
            result = fortran_fpm.compare_projects(root, ['gfortran'], cancel=cancelled)
            self.assertEqual(result[0]['status'], 'SKIP')


class HostedTests(unittest.TestCase):
    def test_precompiled_result_is_reported_in_terse_output(self):
        result = {'ok': True, 'cache': {'package': 'fortran-lapack',
                  'compiler': 'GNU Fortran 16.2.0', 'library_reused': True}}
        row = fpm_runner.hosted_row('gfortran', result, 1.0)
        output = StringIO()
        with redirect_stdout(output):
            fpm_runner.print_row(row, terse=True)
        self.assertIn('Precompiled package: fortran-lapack', output.getvalue())
        self.assertIn('library reused', output.getvalue())

    def client(self, *, fail=False, legacy=False):
        client = Mock()
        self.submissions = []
        self.pending = True

        def request(path, payload=None, **kwargs):
            if path == 'health':
                return {'ok': True, 'fpm': '0.12.0', **({} if legacy else {'compilers': {'gfortran': 'GNU', 'ifx': 'Intel'}})}
            if path == 'jobs':
                self.submissions.append(payload)
                return {'id': 'private-job'}
            if path.endswith('/cancel'):
                return {}
            if self.pending:
                self.pending = False
                return {'state': 'running'}
            ok = not fail or len(self.submissions) > 1
            return {'state': 'done', 'result': {'ok': ok, 'compiler': 'test compiler', 'stages': [
                {'name': 'Build', 'ok': ok, 'seconds': 0.1, 'command': ['fpm', 'build'], 'stdout': '', 'stderr': ''},
                *([{'name': 'Run', 'ok': True, 'seconds': 0.1, 'command': ['fpm', 'run'], 'stdout': '42\n', 'stderr': ''}] if ok else [])]}}
        client.request.side_effect = request
        client.service_url = 'https://test.modal.run'
        return client

    def test_hosted_dispatch_uses_package_api_and_continues_after_failure(self):
        client = self.client(fail=True)
        with patch('xplayground_run.PlaygroundClient', return_value=client), patch('fpm_runner.time.sleep'), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = xplayground_run.main(['--fpm', 'https://github.com/example/project', '--compilers', 'gfortran', 'ifx', '--terse', '--diff'])
        self.assertEqual(code, 1)
        self.assertEqual(len(self.submissions), 2)
        self.assertEqual(self.submissions[0]['workflow'], 'package')
        self.assertEqual(self.submissions[1]['compiler'], 'ifx')
        self.assertFalse(any(call.args[0] == 'session' for call in client.request.call_args_list))

    def test_legacy_host_and_custom_main(self):
        client = self.client(legacy=True)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'main.f90'; source.write_text('program main\nend program\n')
            with patch('xplayground_run.PlaygroundClient', return_value=client), patch('fpm_runner.time.sleep'), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                code = xplayground_run.main(['--fpm', 'https://github.com/example/project', '--main', str(source), '--service-url', 'https://test.modal.run'])
            self.assertEqual(code, 0)
            self.assertNotIn('compiler', self.submissions[0])
            self.assertEqual(self.submissions[0]['workflow'], 'consumer')

    def test_poll_failure_cancels_without_repeating_submission(self):
        client = Mock()
        client.request.side_effect = [{'id': 'accepted'}, xplayground_run.ServiceError('offline'), {}]
        with self.assertRaises(xplayground_run.ServiceError):
            fpm_runner.run_hosted_job(client, {'compiler': 'gfortran'}, 10)
        self.assertEqual([call.args[0] for call in client.request.call_args_list], ['jobs', 'jobs/accepted', 'jobs/accepted/cancel'])

    def test_local_dispatch_does_not_read_hosted_configuration(self):
        with patch('fortran_fpm.compare_projects', return_value=[{'compiler': 'gfortran', 'status': 'PASS', 'ok': True}]) as compare, redirect_stdout(StringIO()):
            self.assertEqual(xfortran_run.main(['--fpm', '.', '--action', 'build']), 0)
            self.assertEqual(compare.call_args.kwargs['options']['action'], 'build')


class LocalServerTests(unittest.TestCase):
    def setUp(self):
        from xfortran_serve import LocalServer
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        fixture(self.root / 'package')
        with patch('xfortran_serve.discover', return_value={'gfortran': {'path': 'mock-gfortran', 'version': 'test'}}):
            self.server = LocalServer(self.root, port=0)
        self.server.fpm_path = 'mock-fpm'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.stop_jobs(); self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.temporary.cleanup()

    def request(self, path, data=None, *, token=True, origin=None):
        headers = {'Host': self.server.origin.removeprefix('http://')}
        if token: headers['X-Local-Token'] = self.server.token
        if data is not None:
            headers.update({'Origin': origin or self.server.origin, 'Content-Type': 'application/json'})
        client = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        client.request('GET' if data is None else 'POST', path, None if data is None else json.dumps(data), headers)
        response = client.getresponse(); content = response.read()
        value = json.loads(content) if response.headers['Content-Type'].startswith('application/json') else content
        status = response.status; client.close()
        return status, value

    def test_project_discovery_security_and_assets(self):
        self.assertEqual(self.request('/api/fpm/session', token=False)[0], 403)
        session = self.request('/api/fpm/session')[1]
        self.assertEqual(session['projects'], ['package'])
        self.assertEqual(self.request('/fpm/')[0], 200)
        self.assertEqual(self.request('/fpm/fpm.mjs')[0], 200)
        for project in ('../outside', '/absolute', 'C:/outside', 'package/../package', 'missing'):
            self.assertEqual(self.request('/api/fpm/jobs', {'project': project, 'compilers': ['gfortran']})[0], 400)
        self.assertEqual(self.request('/api/fpm/jobs', {}, origin='https://elsewhere.example')[0], 403)

    def test_job_polling_cancellation_and_shared_admission_slot(self):
        entered = threading.Event()

        def compare(project, names, *, options, cancel, update, **kwargs):
            update({'compiler': 'gfortran', 'status': 'RUNNING'}); entered.set()
            cancel.wait(timeout=5)
            return [{'compiler': 'gfortran', 'status': 'STOPPED', 'ok': False}]

        data = {'project': 'package', 'compilers': ['gfortran'], 'options': {'action': 'test'}}
        with patch('fortran_fpm.compare_projects', side_effect=compare):
            status, job = self.request('/api/fpm/jobs', data)
            self.assertEqual(status, 202)
            self.assertTrue(entered.wait(2))
            self.assertEqual(self.request('/api/fpm/jobs', data)[0], 409)
            self.assertEqual(self.request('/api/jobs', {'sources': [{'path': 'main.f90', 'source': 'end'}], 'compilers': ['gfortran']})[0], 409)
            self.assertEqual(self.request('/api/jobs/' + job['id'])[1]['state'], 'running')
            self.assertEqual(self.request('/api/jobs/' + job['id'] + '/cancel', {})[0], 200)
            for _ in range(30):
                result = self.request('/api/jobs/' + job['id'])[1]
                if result['state'] == 'done': break
                time.sleep(0.05)
            self.assertEqual(result['state'], 'done')
            self.assertEqual(result['rows'][0]['status'], 'STOPPED')

    @unittest.skipUnless(shutil.which('fpm') and shutil.which('gfortran'), 'FPM and GNU Fortran required')
    def test_native_worker_through_loopback_http(self):
        self.server.fpm_path = shutil.which('fpm')
        data = {'project': 'package', 'compilers': ['gfortran'], 'options': {'action': 'test'}}
        status, job = self.request('/api/fpm/jobs', data)
        self.assertEqual(status, 202)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            result = self.request('/api/jobs/' + job['id'])[1]
            if result['state'] == 'done': break
            time.sleep(0.1)
        self.assertEqual(result['state'], 'done')
        self.assertTrue(result['rows'][0]['ok'], result)
        self.assertIn('TEST PASS', result['rows'][0]['execution']['stdout'])
