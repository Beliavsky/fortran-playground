import http.client
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import xfortran_run as runner
from xfortran_serve import LocalServer

MODULE = 'module sample\ncontains\ninteger function answer()\nanswer=42\nend function\nend module\n'
MAIN = 'program main\nuse sample\nprint *, answer()\nend program\n'


class ProcessTests(unittest.TestCase):
    def test_input_output_nonzero_and_bounded_capture(self):
        with tempfile.TemporaryDirectory() as temporary:
            stage = runner.run_process([sys.executable, '-c', 'import sys; print(sys.stdin.read()); sys.exit(2)'], temporary, threading.Event(), stdin='hello')
            self.assertFalse(stage['ok'])
            self.assertIn('hello', stage['stdout'])
            self.assertIn('exit code 2', stage['stderr'])
            stage = runner.run_process([sys.executable, '-c', 'print("x"*20000)'], temporary, threading.Event(), output_limit=32)
            self.assertEqual(len(stage['stdout']), 32)
            self.assertIn('truncated', stage['stderr'])

    def test_timeout_and_cancellation(self):
        with tempfile.TemporaryDirectory() as temporary:
            stage = runner.run_process([sys.executable, '-c', 'import time; time.sleep(30)'], temporary, threading.Event(), timeout=0.1)
            self.assertTrue(stage['timed_out'])
            self.assertFalse(stage['ok'])
            cancel = threading.Event()
            timer = threading.Timer(0.1, cancel.set); timer.start()
            try:
                stage = runner.run_process([sys.executable, '-c', 'import time; time.sleep(30)'], temporary, cancel, timeout=0)
                self.assertTrue(stage['cancelled'])
            finally:
                timer.cancel()

    def test_options_for_gnu_and_intel_platforms(self):
        compile_flags, link_flags = runner.flags_for('gfortran', {'optimization': 3, 'bounds_check': True, 'standard': '2018'}, {'compile': ['-Wall'], 'link': ['-lm']})
        self.assertIn('-O3', compile_flags); self.assertIn('-std=f2018', compile_flags)
        self.assertIn('-fcheck=bounds', compile_flags)
        self.assertNotIn('-lm', compile_flags); self.assertIn('-lm', link_flags)
        for platform, expected in [('nt', '/fpp'), ('posix', '-fpp')]:
            with patch.object(runner.os, 'name', platform):
                self.assertIn(expected, runner.flags_for('ifx', {'preprocess': True})[0])
        for bad in [{'unknown': True}, {'optimization': '3'}, {'warnings': 'yes'}]:
            with self.assertRaises(ValueError):
                runner.flags_for('gfortran', bad)

    def test_new_compiler_discovery_and_options(self):
        with patch('xfortran_run.shutil.which', side_effect=lambda name: name if name in ('gfortran', 'flang-new') else None), \
             patch('xfortran_run.run_process', return_value={'stdout': 'GNU Fortran (GCC) 17.0.0', 'stderr': ''}):
            self.assertEqual(runner.compiler_executable('gfortran17'), 'gfortran')
            self.assertEqual(runner.compiler_executable('flang'), 'flang-new')
        with patch('xfortran_run.shutil.which', return_value='gfortran'), \
             patch('xfortran_run.run_process', return_value={'stdout': 'GNU Fortran (GCC) 16.2.0', 'stderr': ''}):
            with self.assertRaisesRegex(ValueError, 'version 17 required'):
                runner.compiler_executable('gfortran17')
        settings = {'optimization': 3, 'preprocess': True}
        self.assertEqual(runner.flags_for('gfortran', settings), runner.flags_for('gfortran17', settings))
        self.assertIn('-O3', runner.flags_for('flang', settings)[0])
        self.assertIn('-std=f2018', runner.flags_for('flang', {'standard': '2018'})[0])
        with self.assertRaises(runner.UnsupportedOption): runner.flags_for('flang', {'standard': '2023'})
        self.assertIn('--fast', runner.flags_for('lfortran', settings)[0])
        self.assertIn('--cpp', runner.flags_for('lfortran', settings)[0])
        self.assertIn('--fast', runner.flags_for('ofort', {'optimization': 3})[0])
        for name, setting in [('flang', 'bounds_check'), ('lfortran', 'backtrace'), ('ofort', 'preprocess')]:
            with self.assertRaises(runner.UnsupportedOption): runner.flags_for(name, {setting: True})

    def test_new_compiler_commands_and_interpreter_timing(self):
        commands = []
        def process(command, *args, **kwargs):
            commands.append(command)
            return {'ok': True, 'command': command, 'stdout': '42\n', 'stderr': '', 'seconds': 0.01}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'main.f90'; path.write_text('program p\nend\n')
            for name in ['gfortran17', 'flang', 'lfortran', 'ofort']:
                commands.clear()
                with patch.object(runner, 'compiler_executable', return_value=name), patch.object(runner, 'run_process', side_effect=process):
                    row = runner.build_and_run([path], name)
                    self.assertTrue(row['ok'], row)
                    if name == 'ofort':
                        self.assertEqual(len(commands), 1)
                        self.assertIsNone(row['times']['compile'])
                        self.assertIsNotNone(row['times']['other'])
                    else:
                        self.assertEqual(len(commands), 3)
                        self.assertIn('-c', commands[0])
                        if name == 'flang': self.assertIn('-module-dir', commands[0])
                        if name == 'lfortran': self.assertIn('--separate-compilation', commands[0])
                    commands.clear()
                    row = runner.build_and_run([path], name, compile_only=True)
                    self.assertTrue(row['ok'], row)
                    self.assertNotIn('execution', row)
                    if name == 'ofort': self.assertIn('--check', commands[0])

    @unittest.skipUnless(shutil.which('ofort'), 'ofort required')
    def test_ofort_multi_source_syntax_check_and_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / 'sample.f90', root / 'main.f90']
            for path, source in zip(paths, [MODULE, MAIN]): path.write_text(source)
            for compile_only in (False, True):
                row = runner.build_and_run(paths, 'ofort', compile_only=compile_only, cwd=root)
                self.assertTrue(row['ok'], row)
                if not compile_only: self.assertEqual(row['execution']['stdout'].strip(), '42')

    def test_missing_compiler_and_fail_fast(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'main.f90'; path.write_text(MAIN)
            with patch.object(runner, 'compiler_executable', side_effect=ValueError('missing')):
                rows = runner.compare([path], ['gfortran', 'ifx'], fail_fast=True)
                self.assertEqual([row['status'] for row in rows], ['ERROR', 'SKIP'])
                rows = runner.compare([path], ['gfortran', 'ifx'])
                self.assertEqual([row['status'] for row in rows], ['ERROR', 'ERROR'])

    def test_intel_driver_commands_use_native_platform_syntax(self):
        commands = []
        def process(command, *args, **kwargs):
            commands.append(command)
            return {'ok': True, 'command': command, 'stdout': '', 'stderr': '', 'seconds': 0.01}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'main.f90'; path.write_text('program p\nend\n')
            with patch.object(runner, 'compiler_executable', return_value='ifx'), patch.object(runner, 'run_process', side_effect=process):
                result = runner.build_and_run([path], 'ifx', {'preprocess': True})
        self.assertTrue(result['ok'])
        if runner.os.name == 'nt':
            self.assertIn('/c', commands[0]); self.assertIn('/fpp', commands[0])
            self.assertTrue(any(arg.startswith('/module:') for arg in commands[0]))
            self.assertTrue(any(arg.startswith('/object:') for arg in commands[0]))
            self.assertTrue(any(arg.startswith('/exe:') for arg in commands[1]))
        else:
            self.assertIn('-c', commands[0]); self.assertIn('-module', commands[0]); self.assertIn('-fpp', commands[0])
            self.assertIn('-o', commands[1])


@unittest.skipUnless(shutil.which('gfortran'), 'gfortran required')
class BuildTests(unittest.TestCase):
    def test_command_line_lists_sources_and_prints_timings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / 'sample.f90', root / 'main.f90']
            for path, text in zip(paths, [MODULE, MAIN]): path.write_text(text)
            result = subprocess.run([sys.executable, str(Path(runner.__file__)), *map(str, paths), '--compiler', 'gfortran', '--O', '3', '--list', '--terse'],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('=== gfortran: PASS ===', result.stdout)
            self.assertIn('Other', result.stdout)
            self.assertIn('42', result.stdout)
            self.assertEqual(result.stdout.count(MODULE), 1)

    def test_separate_compilation_linking_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / 'sample.f90', root / 'main.f90']
            for path, text in zip(paths, [MODULE, MAIN]): path.write_text(text)
            result = runner.build_and_run(paths, 'gfortran', {'standard': '2018'}, cwd=root)
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['execution']['stdout'].strip(), '42')
            self.assertEqual(len(result['build']['commands']), 3)
            self.assertIn(str(paths[0]), result['build']['commands'][0])
            self.assertIn('-c', result['build']['commands'][0])
            self.assertFalse(list(root.glob('*.mod')))
            self.assertFalse(Path(result['build']['commands'][-1][-1]).exists())
            result = runner.build_and_run(paths, 'gfortran', compile_only=True)
            self.assertTrue(result['ok'], result); self.assertNotIn('execution', result)
            failure = runner.build_and_run(list(reversed(paths)), 'gfortran')
            self.assertFalse(failure['ok'])
            self.assertNotIn('execution', failure)

    def test_stdin_working_directory_and_preprocessing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); path = root / 'main.F90'
            path.write_text('#define VALUE 7\nprogram p\ninteger::n\nread(*,*) n\nopen(10,file="result.txt")\nwrite(10,*) n+VALUE\nclose(10)\nend\n')
            result = runner.build_and_run([path], 'gfortran', stdin='5\n', cwd=root)
            self.assertTrue(result['ok'], result)
            self.assertEqual((root / 'result.txt').read_text().strip(), '12')


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        (self.root / 'main.f90').write_text(MAIN)
        self.server = LocalServer(self.root, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()

    def tearDown(self):
        self.server.stop_jobs(); self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def request(self, path, payload=None, *, token=True, origin=None, host=None):
        headers = {'Host': host or self.server.origin.removeprefix('http://')}
        if token: headers['X-Local-Token'] = self.server.token
        if payload is not None:
            headers['Content-Type'] = 'application/json'; headers['Origin'] = origin or self.server.origin
        elif origin: headers['Origin'] = origin
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        connection.request('POST' if payload is not None else 'GET', path, json.dumps(payload) if payload is not None else None, headers)
        response = connection.getresponse(); body = response.read(); status = response.status; response_headers = dict(response.getheaders()); connection.close()
        policy = response_headers['Content-Security-Policy']
        self.assertIn("img-src 'self' data:;", policy)
        self.assertIn("script-src 'self';", policy)
        return status, json.loads(body) if response_headers['Content-Type'].startswith('application/json') else body

    def test_loopback_token_origin_host_and_asset_restrictions(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')
        self.assertEqual(self.request('/api/session', token=False)[0], 403)
        self.assertEqual(self.request('/api/session', origin='https://unrelated.example')[0], 403)
        self.assertEqual(self.request('/api/session', host='unrelated.example')[0], 403)
        status, result = self.request('/api/session'); self.assertEqual(status, 200)
        self.assertNotIn('token', result)
        self.assertEqual(self.request('/xfortran_run.py')[0], 404)
        self.assertEqual(self.request('/')[0], 200)
        for asset in ['editors.mjs', 'indentation.mjs', 'output_diff.mjs', 'output_diff_ui.mjs']:
            self.assertEqual(self.request('/' + asset)[0], 200)
        for asset in ['codemirror.js', 'fortran.js', 'codemirror.css', 'LICENSE']:
            self.assertEqual(self.request('/editor-vendor/' + asset)[0], 200)
        self.assertEqual(self.request('/editor-vendor/unknown.js')[0], 404)
        self.assertEqual(self.request('/api/jobs', {}, origin='https://unrelated.example')[0], 403)

    def test_workspace_paths_and_job_validation(self):
        self.assertEqual(self.request('/api/files')[1]['files'], ['main.f90'])
        self.assertEqual(self.request('/api/source?path=main.f90')[1]['source'], MAIN)
        for path in ['../outside.f90', '/absolute.f90', 'C:/outside.f90', 'folder/../../outside.f90', 'README.md']:
            with self.assertRaises(ValueError): self.server.workspace_path(path)
        self.assertEqual(self.request('/api/jobs', {'sources': []})[0], 400)

    def test_editor_tool_validation_missing_tools_and_failures(self):
        payload = {'path': 'main.f90', 'source': MAIN, 'indent': 3}
        self.assertEqual(self.request('/api/check', payload, token=False)[0], 403)
        self.assertEqual(self.request('/api/format', payload, origin='https://unrelated.example')[0], 403)
        for bad in [{'indent': 99}, {'source': ''}, {'path': '../outside.f90'}]:
            self.assertEqual(self.request('/api/format', {**payload, **bad})[0], 400)
        with patch('xfortran_serve.shutil.which', return_value=None):
            status, result = self.request('/api/check', payload)
            self.assertEqual(status, 400)
            self.assertIn('PATH', result['error'])
        with patch('xfortran_serve.shutil.which', return_value='tool'), patch('xfortran_serve.run_process', return_value={
                'ok': False, 'stdout': '', 'stderr': 'Timed out', 'seconds': 30, 'timed_out': True}):
            self.assertFalse(self.request('/api/format', payload)[1]['ok'])
            self.assertFalse(self.request('/api/check', payload)[1]['ok'])

    @unittest.skipUnless(shutil.which('fprettify') and shutil.which('fortitude'), 'local editor tools required')
    def test_real_local_format_and_check_preserve_workspace_files(self):
        source = 'program p\ninteger i\ndo i=1,2\nprint *,i\nend do\nend\n'
        payload = {'path': 'main.f90', 'source': source, 'indent': 4}
        status, result = self.request('/api/format', payload)
        self.assertEqual(status, 200)
        self.assertTrue(result['ok'], result)
        self.assertIn('\n    integer', result['formatted_source'])
        status, result = self.request('/api/check', payload)
        self.assertEqual(status, 200)
        self.assertTrue(result['ok'], result)
        self.assertTrue(any(item['code'] == 'T001' for item in result['diagnostics']), result)
        self.assertEqual((self.root / 'main.f90').read_text(), MAIN)

    def test_worker_failure_returns_terminal_compiler_results(self):
        self.server.compilers = {name: {'path': name} for name in ['gfortran', 'ifx']}
        payload = {'sources': [{'path': 'main.f90', 'source': MAIN}], 'compilers': ['gfortran', 'ifx']}
        with patch('xfortran_serve.compare', side_effect=OSError('Temporary source failed')):
            status, created = self.request('/api/jobs', payload)
            self.assertEqual(status, 202)
            self.server.jobs[created['id']]['thread'].join(timeout=5)
        job = self.request('/api/jobs/' + created['id'])[1]
        self.assertEqual(job['state'], 'done')
        self.assertEqual([row['status'] for row in job['rows']], ['ERROR', 'ERROR'])
        self.assertTrue(all(row['error'] == 'Temporary source failed' for row in job['rows']))

    @unittest.skipUnless(shutil.which('gfortran'), 'gfortran required')
    def test_web_snapshots_preserve_originals_and_includes(self):
        (self.root / 'value.inc').write_text('integer, parameter :: answer=42\n')
        payload = {'sources': [{'path': 'main.f90', 'source': 'program p\ninclude "value.inc"\nprint *, answer\nend\n'}], 'compilers': ['gfortran']}
        status, created = self.request('/api/jobs', payload); self.assertEqual(status, 202, created)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            job = self.request('/api/jobs/' + created['id'])[1]
            if job['state'] == 'done': break
            time.sleep(0.05)
        self.assertEqual(job['state'], 'done')
        self.assertTrue(job['rows'][0]['ok'], job)
        self.assertEqual(job['rows'][0]['execution']['stdout'].strip(), '42')
        self.assertEqual((self.root / 'main.f90').read_text(), MAIN)
        self.assertFalse(list(self.root.glob('*.mod')))

    @unittest.skipUnless(shutil.which('gfortran'), 'gfortran required')
    def test_server_cancels_running_program_and_rejects_overlapping_job(self):
        source = 'program p\ninteger::u\nopen(newunit=u,file="started.txt")\nwrite(u,*) "ready"\nclose(u)\ndo\nend do\nend\n'
        payload = {'sources': [{'path': 'loop.f90', 'source': source}], 'compilers': ['gfortran'], 'run_timeout': 0}
        status, created = self.request('/api/jobs', payload); self.assertEqual(status, 202)
        deadline = time.monotonic() + 15
        while not (self.root / 'started.txt').exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue((self.root / 'started.txt').exists())
        self.assertEqual(self.request('/api/jobs', payload)[0], 409)
        self.assertEqual(self.request('/api/jobs/' + created['id'] + '/cancel', {})[0], 200)
        while time.monotonic() < deadline:
            job = self.request('/api/jobs/' + created['id'])[1]
            if job['state'] == 'done': break
            time.sleep(0.05)
        self.assertEqual(job['state'], 'done')
        self.assertEqual(job['rows'][0]['status'], 'STOPPED')
        self.assertTrue(job['rows'][0]['execution']['cancelled'])


if __name__ == '__main__':
    unittest.main()
