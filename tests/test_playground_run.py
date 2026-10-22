from contextlib import redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import xplayground_run as runner


ROOT = Path(__file__).resolve().parents[1]
MODULE = 'module greeting_mod\ncontains\nsubroutine hello()\nprint *, 42\nend subroutine\nend module\n'
MAIN = 'program main\nuse greeting_mod\ncall hello()\nend program\n'


def session():
    return {'token': 'private-token', 'compilers': ['gfortran', 'ifx'],
            'features': {'compile_only': True},
            'compiler_versions': {'gfortran': 'GNU test', 'ifx': 'Intel test'},
            'compiler_options': {name: {'presets': {'default': [], 'debug': ['-g']},
                'standards': {'2018': ['-std=f2018']},
                'additional_options': {'optimization': [[f'-O{level}'] for level in range(4)],
                    'debug': [['-g']], 'warnings': [['-Wall']] if name == 'gfortran' else [['-warn', 'all']],
                    'checks': [['-fcheck=bounds']] if name == 'gfortran' else [['-check', 'bounds']],
                    'backtrace': [['-fbacktrace']] if name == 'gfortran' else [['-traceback']]},
                'portable_options': {'optimization': {str(level): [f'-O{level}'] for level in range(4)},
                    'bounds_check': {'true': ['-fcheck=bounds'] if name == 'gfortran' else ['-check', 'bounds']},
                    'backtrace': {'true': ['-fbacktrace'] if name == 'gfortran' else ['-traceback']}},
                'extras': {'preprocess': ['-cpp'], 'warnings': ['-Wall']}}
                for name in ['gfortran', 'ifx']}}


class SourceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('gfortran'), 'GNU compiler required')
    def test_portable_gnu_flags_enable_bounds_checks(self):
        flags = runner.portable_arguments(session()['compiler_options']['gfortran'],
            {'optimization': 3, 'bounds_check': True, 'backtrace': True}, 'gfortran')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'bounds.f90'
            source.write_text('program bounds\nimplicit none\ninteger :: a(1) = [42], i\n'
                              'i = command_argument_count() + 1\nprint *, a(i)\nend program bounds\n')
            executable = root / 'bounds.exe'
            build = subprocess.run(['gfortran', *flags, str(source), '-o', str(executable)],
                                   capture_output=True, text=True, timeout=30)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            valid = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertEqual(valid.stdout.strip(), '42')
            invalid = subprocess.run([str(executable), 'trigger-bounds-error'],
                                     capture_output=True, text=True, timeout=10)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn('above upper bound', invalid.stderr)
            self.assertIn('backtrace', invalid.stderr.lower())

    def test_order_boundaries_bom_and_line_locations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, second = root / 'module.f90', root / 'main.f90'
            first.write_bytes(b'\xef\xbb\xbf' + MODULE.rstrip('\n').replace('\n', '\r\n').encode())
            second.write_bytes(MAIN.encode())
            source, sections = runner.combine_sources([first, second])
            self.assertLess(source.index('module greeting_mod'), source.index('program main'))
            self.assertIn('end module\n! --- Source:', source)
            self.assertNotIn('\r', source)
            self.assertNotIn('\ufeff', source)
            line = sections[1].first_line + 1
            notes = runner.diagnostic_locations(f'input_p.f90:{line}:4: error\ninput_p.f90({line}): error', sections)
            self.assertEqual(notes, [f'input_p.f90:{line} -> {second}:2'])
            self.assertEqual(runner.combine_sources([second])[0], MAIN)

    def test_input_errors_and_combined_byte_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, second = root / 'a.f90', root / 'b.f90'
            first.write_bytes(('! ' + '\u03bb'*49998 + '\n').encode())
            self.assertLessEqual(len(runner.combine_sources([first])[0].encode()), 100000)
            second.write_text('end\n')
            with self.assertRaisesRegex(ValueError, 'Combined source'):
                runner.combine_sources([first, second])
            with self.assertRaisesRegex(ValueError, 'more than once'):
                runner.combine_sources([second, second])
            first.write_bytes(b'\xff')
            with self.assertRaisesRegex(ValueError, 'UTF-8'):
                runner.combine_sources([first])
            first.write_text(' \n')
            with self.assertRaisesRegex(ValueError, 'empty'):
                runner.combine_sources([first])
            first.write_bytes(b'x'*100004)
            with self.assertRaisesRegex(ValueError, '100 KB'):
                runner.combine_sources([first])

    @unittest.skipUnless(shutil.which('gfortran'), 'gfortran required')
    def test_concatenated_module_and_main_compile_and_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [root / 'module.f90', root / 'main.f90']
            for path, text in zip(paths, [MODULE, MAIN]):
                path.write_text(text, encoding='utf-8')
            source, _ = runner.combine_sources(paths)
            (root / 'combined.f90').write_text(source, encoding='utf-8')
            executable = root / 'program.exe'
            compilation = subprocess.run(['gfortran', '-std=f2018', 'combined.f90', '-o', str(executable)],
                cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(compilation.returncode, 0, compilation.stderr)
            output = subprocess.run([str(executable)], cwd=root, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, check=True, timeout=10).stdout
            self.assertEqual(output.strip(), '42')


class ClientTests(unittest.TestCase):
    def client(self):
        return runner.PlaygroundClient('https://execute.example.org', 'https://my-site.example.org')

    def test_requests_use_application_token_and_explicit_origin(self):
        client = self.client()
        response = Mock()
        response.__enter__ = Mock(side_effect=lambda: BytesIO(json.dumps(session()).encode()))
        response.__exit__ = Mock(return_value=False)
        with patch.object(runner, 'urlopen', return_value=response) as open_url:
            client.connect()
            request = open_url.call_args.args[0]
            self.assertEqual(request.get_header('Origin'), 'https://my-site.example.org')
            client.request('jobs', {'compiler': 'gfortran'})
            request = open_url.call_args.args[0]
            self.assertEqual(request.get_header('X-p2f-token'), 'private-token')
            self.assertEqual(request.get_header('Content-type'), 'application/json')
            self.assertEqual(json.loads(request.data), {'compiler': 'gfortran'})

    def test_quota_error_is_not_retried(self):
        client = self.client()
        error = HTTPError('https://execute.example.org/api/jobs', 429, 'Too many', {},
                          BytesIO(b'{"error":"Daily allowance reached"}'))
        with patch.object(runner, 'urlopen', side_effect=error) as request:
            with self.assertRaisesRegex(runner.ServiceError, 'HTTP 429: Daily allowance reached'):
                client.request('jobs', {})
            request.assert_called_once()

    def test_polling_payload_and_compile_only(self):
        client = self.client()
        result = {'ok': True, 'build': {'ok': True}}
        with patch.object(client, 'request', side_effect=[{'id': 'job'}, {'state': 'running'},
                {'state': 'done', 'result': result}]) as request, patch.object(runner.time, 'sleep'):
            returned, elapsed = client.run_job('end\n', 'gfortran', {'preprocess': True}, compile_only=True)
        self.assertEqual(returned, result)
        self.assertGreaterEqual(elapsed, 0)
        self.assertEqual(request.call_args_list[0].args, ('jobs', {
            'source': '', 'fortran_source': 'end\n', 'mode': 'fortran-compile',
            'compiler': 'gfortran', 'automatic': False, 'compiler_options': {'preprocess': True}}))
        self.assertEqual(request.call_count, 3)

    def test_ctrl_c_and_timeout_cancel_pending_job(self):
        client = self.client()
        with patch.object(client, 'request', side_effect=[{'id': 'job'}, KeyboardInterrupt(), {}]) as request:
            with self.assertRaises(KeyboardInterrupt):
                client.run_job('end\n', 'gfortran', {})
            self.assertEqual(request.call_args.args, ('jobs/job/cancel', {}))
        with patch.object(client, 'request', side_effect=[{'id': 'job'}, {}]) as request, \
                patch.object(runner.time, 'monotonic', side_effect=[0, 0, 2]):
            with self.assertRaisesRegex(runner.ServiceError, 'timed out'):
                client.run_job('end\n', 'gfortran', {}, timeout=1)
            self.assertEqual(request.call_args.args, ('jobs/job/cancel', {}))

    def test_service_origin_validation(self):
        self.assertEqual(runner.origin_url('https://example.org:8443/'), 'https://example.org:8443')
        for url in ['http://example.org', 'https://example.org/api', 'https://user:secret@example.org',
                    'https://example.org/?key=value', 'https://example.org/#x', 'https://example.org:bad']:
            with self.assertRaises(ValueError):
                runner.origin_url(url)


class CommandTests(unittest.TestCase):
    def invoke(self, root, client, *options):
        first, second = root / 'module.f90', root / 'main.f90'
        first.write_text(MODULE)
        second.write_text(MAIN)
        stdout, stderr = StringIO(), StringIO()
        with patch.object(runner, 'PlaygroundClient', return_value=client), redirect_stdout(stdout), redirect_stderr(stderr):
            status = runner.main([str(first), str(second), '--service-url', 'https://execute.example.org', *options])
        return status, stdout.getvalue(), stderr.getvalue()

    def client(self):
        client = Mock(service_url='https://execute.example.org')
        client.connect.return_value = session()
        client.run_job.side_effect = [({'ok': False, 'error': 'Compilation failed'}, 1.0),
                                      ({'ok': True, 'execution': {'stdout': '42\n', 'seconds': 0.1}}, 1.1)]
        return client

    def test_multiple_compilers_continue_after_compilation_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            status, stdout, stderr = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx', '--preprocess')
            self.assertEqual(status, 1)
            self.assertIn('Summary:', stdout)
            self.assertIn('Compilation failed', stderr)
            self.assertEqual([call.args[1] for call in client.run_job.call_args_list], ['gfortran', 'ifx'])
            for call in client.run_job.call_args_list:
                self.assertLess(call.args[0].index('module greeting_mod'), call.args[0].index('program main'))
                self.assertTrue(call.args[2]['preprocess'])
            self.assertNotIn('private-token', stdout + stderr)

    def test_terse_keeps_output_warnings_and_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = [({'ok': True, 'compiler_version': 'GNU test',
                'build': {'ok': True, 'seconds': 0.2,
                          'stdout': 'Build: gfortran input_p.f90\nWarning: stdout diagnostic\nBuild: PASS\n',
                          'stderr': 'input_p.f90:3: Warning: unused variable\n'},
                'execution': {'ok': True, 'seconds': 0.1, 'stdout': '42\n', 'stderr': 'program stderr\n'}}, 1.0)]
            status, stdout, stderr = self.invoke(Path(temporary), client, '--terse')
            self.assertEqual(status, 0)
            for text in ['=== gfortran: PASS ===', '42\n', 'Warning: stdout diagnostic',
                         'Source location:', 'Summary: times in seconds']:
                self.assertIn(text, stdout)
            for text in ['Service:', 'Combined source:', 'input_p.f90 lines', 'Submitting',
                         'GNU test', 'Build:', 'Compilation (', 'Program output (', 'Total client time:']:
                self.assertNotIn(text, stdout)
            self.assertIn('Warning: unused variable', stderr)
            self.assertIn('program stderr', stderr)

    def test_terse_keeps_failure_diagnostics_and_stops(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = [({'ok': False, 'error': 'Compilation failed',
                'build': {'ok': False, 'stdout': 'Build: FAIL\n',
                          'stderr': 'input_p.f90:3: Error: invalid code\n', 'seconds': 0.2}}, 1.0)]
            status, stdout, stderr = self.invoke(Path(temporary), client, '--terse', '--fail-fast',
                                                 '--compilers', 'gfortran', 'ifx')
            self.assertEqual(status, 1)
            self.assertIn('=== gfortran: FAIL ===', stdout)
            self.assertIn('Build: FAIL', stdout)
            self.assertIn('Source location:', stdout)
            self.assertIn('Stopping after failure (--fail-fast)', stdout)
            self.assertIn('Summary:', stdout)
            self.assertIn('Error: invalid code', stderr)
            self.assertIn('Compilation failed', stderr)
            client.run_job.assert_called_once()

    def test_terse_keeps_service_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = runner.ServiceError('HTTP 429: quota reached')
            status, stdout, stderr = self.invoke(Path(temporary), client, '--terse')
            self.assertEqual(status, 2)
            self.assertEqual(stdout, '')
            self.assertIn('HTTP 429: quota reached', stderr)

    def test_portable_options_and_optimization_aliases(self):
        for alias in ('--optimization', '--O', '-O'):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx',
                            alias, '3', '--bounds-check', '--backtrace')
                self.assertEqual(client.run_job.call_args_list[0].args[2]['additional'],
                                 ['-O3', '-fcheck=bounds', '-fbacktrace'])
                self.assertEqual(client.run_job.call_args_list[1].args[2]['additional'],
                                 ['-O3', '-check', 'bounds', '-traceback'])

    def test_common_options_cli_overrides_and_specific_arguments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'options.json'
            config.write_text(json.dumps({'common': {'optimization': 0, 'bounds_check': True, 'backtrace': True},
                                          'gfortran': ['-Wall'], 'ifx': ['-warn', 'all']}))
            client = self.client()
            self.invoke(root, client, '--compilers', 'gfortran', 'ifx', '--options-file', str(config),
                        '--O', '2', '--no-bounds-check', '--no-backtrace')
            self.assertEqual(client.run_job.call_args_list[0].args[2]['additional'], ['-O2', '-Wall'])
            self.assertEqual(client.run_job.call_args_list[1].args[2]['additional'], ['-O2', '-warn', 'all'])
            client = self.client()
            self.invoke(root, client, '--options-file', str(config))
            self.assertEqual(client.run_job.call_args.args[2]['additional'],
                             ['-O0', '-fcheck=bounds', '-fbacktrace', '-Wall'])

    def test_invalid_common_options_prevent_all_submissions(self):
        for common in [[], {'optimization': True}, {'optimization': '3'}, {'optimization': 4},
                       {'optimization': None}, {'bounds_check': 1}, {'backtrace': 'yes'}, {'typo': True}]:
            with self.subTest(common=common), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                config = root / 'options.json'
                config.write_text(json.dumps({'common': common}))
                client = self.client()
                status, _, _ = self.invoke(root, client, '--options-file', str(config))
                self.assertEqual(status, 2)
                client.run_job.assert_not_called()

    def test_unsupported_portable_options_prevent_all_submissions(self):
        for key, option in [('optimization', ('--O', '3')), ('bounds_check', ('--bounds-check',)),
                            ('backtrace', ('--backtrace',))]:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                client.connect.return_value['compiler_options']['ifx']['portable_options'].pop(key)
                status, _, stderr = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx', *option)
                self.assertEqual(status, 2)
                self.assertIn(f'ifx does not support portable option {key}', stderr)
                client.run_job.assert_not_called()

    def test_portable_options_conflict_with_presets_and_specific_flags(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            client = self.client()
            client.connect.return_value['compiler_options']['gfortran']['presets']['debug'] = ['-O0', '-g']
            status, _, stderr = self.invoke(root, client, '--preset', 'debug', '--O', '3')
            self.assertEqual(status, 2)
            self.assertIn('gfortran: Conflicting optimization', stderr)
            client.run_job.assert_not_called()
            config = root / 'options.json'
            config.write_text('{"common": {"optimization": 2}, "ifx": ["-O3"]}')
            client = self.client()
            status, _, stderr = self.invoke(root, client, '--compilers', 'gfortran', 'ifx', '--options-file', str(config))
            self.assertEqual(status, 2)
            self.assertIn('ifx: Conflicting optimization', stderr)
            client.run_job.assert_not_called()

    def test_options_file_sends_each_compilers_arguments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'options.json'
            config.write_text(json.dumps({'gfortran': ['-O2', '-Wall'], 'ifx': ['-O2', '-warn', 'all']}))
            client = self.client()
            status, stdout, _ = self.invoke(root, client, '--compilers', 'gfortran', 'ifx', '--options-file', str(config))
            self.assertEqual(status, 1)
            self.assertEqual(client.run_job.call_args_list[0].args[2]['additional'], ['-O2', '-Wall'])
            self.assertEqual(client.run_job.call_args_list[1].args[2]['additional'], ['-O2', '-warn', 'all'])
            self.assertIn('User-code options: -O2 -warn all', stdout)
            client = self.client()
            _, stdout, _ = self.invoke(root, client, '--terse', '--options-file', str(config))
            self.assertNotIn('User-code options:', stdout)

    def test_options_file_missing_entry_uses_defaults(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'options.json'
            config.write_text('{"ifx": ["-O2"]}')
            client = self.client()
            self.invoke(root, client, '--options-file', str(config))
            self.assertNotIn('additional', client.run_job.call_args.args[2])

    def test_invalid_options_prevent_all_submissions(self):
        for config_value in [[], {'typo': []}, {'ifx': '-O2'}, {'ifx': ['-warn']},
                             {'ifx': ['-o', 'other.exe']}, {'ifx': ['-O2', '-O3']},
                             {'ifx': ['@options']}, {'ifx': ['-O2;echo bad']}]:
            with self.subTest(config=config_value), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                config = root / 'options.json'
                config.write_text(json.dumps(config_value))
                client = self.client()
                status, _, _ = self.invoke(root, client, '--compilers', 'gfortran', 'ifx', '--options-file', str(config))
                self.assertEqual(status, 2)
                client.run_job.assert_not_called()

    def test_options_rejected_by_older_service_and_against_preset(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'options.json'
            config.write_text('{"gfortran": ["-O2"]}')
            client = self.client()
            client.connect.return_value['compiler_options']['gfortran'].pop('additional_options')
            status, _, stderr = self.invoke(root, client, '--options-file', str(config))
            self.assertEqual(status, 2)
            self.assertIn('unavailable', stderr)
            client.run_job.assert_not_called()
            client = self.client()
            client.connect.return_value['compiler_options']['gfortran']['presets']['debug'] = ['-O0', '-g']
            status, _, stderr = self.invoke(root, client, '--options-file', str(config), '--preset', 'debug')
            self.assertEqual(status, 2)
            self.assertIn('Conflicting optimization', stderr)
            client.run_job.assert_not_called()

    def test_all_options_validated_before_submission(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            status, _, stderr = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'lfortran')
            self.assertEqual(status, 2)
            self.assertIn('unavailable', stderr)
            client.run_job.assert_not_called()
            status, _, stderr = self.invoke(Path(temporary), client, '--fast-math')
            self.assertEqual(status, 2)
            self.assertIn('does not support', stderr)
            client.run_job.assert_not_called()

    def test_summary_reports_total_compile_and_run_in_seconds(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = [
                ({'ok': True, 'build': {'seconds': 0.276},
                  'execution': {'stdout': '42\n', 'seconds': 0.031}}, 1.904),
                ({'ok': True, 'build': {'seconds': 0.791},
                  'execution': {'seconds': 0.032}}, 2.619)]
            status, stdout, _ = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx')
            self.assertEqual(status, 0)
            self.assertIn('Times in seconds.', stdout)
            self.assertIn('Compilation (0.276):', stdout)
            self.assertIn('Program output (0.031):', stdout)
            self.assertIn('Total client time: 1.904\n', stdout)
            summary = stdout.split('Summary: times in seconds\n')[1]
            self.assertEqual([line.split() for line in summary.splitlines()], [
                ['Compiler', 'Result', 'Total', 'Compile', 'Run', 'Other'],
                ['gfortran', 'PASS', '1.904', '0.276', '0.031', '1.597'],
                ['ifx', 'PASS', '2.619', '0.791', '0.032', '1.796']])

    def test_summary_marks_unavailable_stage_times(self):
        for ok, options in [(False, ()), (True, ('--compile-only',))]:
            with self.subTest(ok=ok), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                client.run_job.side_effect = [({'ok': ok, 'build': {'ok': ok, 'seconds': 0.0}}, 1.0)]
                status, stdout, _ = self.invoke(Path(temporary), client, *options)
                self.assertEqual(status, 0 if ok else 1)
                row = stdout.splitlines()[-1].split()
                self.assertEqual(row, ['gfortran', 'PASS' if ok else 'FAIL', '1.000', '0.000', '-', '1.000'])

    def test_ofort_other_without_compilation_stage(self):
        cases = [
            ({'ok': True, 'interpreter': True, 'execution': {'seconds': 0.125}},
             (), ['ofort', 'PASS', '1.000', '-', '0.125', '0.875']),
            ({'ok': True, 'interpreter': True, 'build': {'ok': True, 'seconds': 0.2}},
             ('--compile-only',), ['ofort', 'PASS', '1.000', '0.200', '-', '0.800']),
            ({'ok': True, 'interpreter': True, 'execution': {'ok': True}},
             (), ['ofort', 'PASS', '1.000', '-', '-', '-']),
            ({'ok': True, 'interpreter': True, 'build': {'ok': True}},
             ('--compile-only',), ['ofort', 'PASS', '1.000', '-', '-', '-'])]
        for result, options, expected in cases:
            with self.subTest(result=result), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                client.connect.return_value['compilers'].append('ofort')
                client.run_job.side_effect = [(result, 1.0)]
                status, stdout, _ = self.invoke(Path(temporary), client, '--compiler', 'ofort', *options)
                self.assertEqual(status, 0)
                self.assertEqual(stdout.splitlines()[-1].split(), expected)

    def test_other_requires_all_expected_timings(self):
        for stages in [
                {'build': {'ok': True, 'seconds': 0.2}},
                {'build': {'ok': True, 'seconds': 0.2}, 'execution': {'ok': True}},
                {'build': {'ok': True}, 'execution': {'ok': True, 'seconds': 0.1}}]:
            with self.subTest(stages=stages), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                client.run_job.side_effect = [({'ok': True, **stages}, 1.0)]
                status, stdout, _ = self.invoke(Path(temporary), client)
                self.assertEqual(status, 0)
                self.assertEqual(stdout.splitlines()[-1].split()[-1], '-')

    def test_fail_fast_stops_on_build_or_execution_failure(self):
        for stage in ('build', 'execution'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary:
                client = self.client()
                client.run_job.side_effect = [({'ok': False, stage: {'ok': False, 'stderr': 'failed'}}, 1.0)]
                status, stdout, _ = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx', '--fail-fast')
                self.assertEqual(status, 1)
                client.run_job.assert_called_once()
                self.assertIn('Stopping after failure (--fail-fast)', stdout)
                self.assertIn('Summary:', stdout)
                self.assertNotIn('Submitting ifx', stdout)

    def test_fail_fast_continues_after_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = [({'ok': True}, 1.0), ({'ok': True}, 1.1)]
            status, stdout, _ = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx', '--fail-fast')
            self.assertEqual(status, 0)
            self.assertEqual(client.run_job.call_count, 2)
            self.assertNotIn('Stopping after failure', stdout)

    def test_service_failure_stops_remaining_compilers(self):
        with tempfile.TemporaryDirectory() as temporary:
            client = self.client()
            client.run_job.side_effect = runner.ServiceError('HTTP 429: quota reached')
            status, _, stderr = self.invoke(Path(temporary), client, '--compilers', 'gfortran', 'ifx')
            self.assertEqual(status, 2)
            self.assertIn('quota reached', stderr)
            client.run_job.assert_called_once()

    def test_help_needs_no_credentials_or_network(self):
        result = subprocess.run([sys.executable, str(ROOT / 'xplayground_run.py'), '--help'],
                                capture_output=True, text=True, check=True)
        self.assertIn('--compilers', result.stdout)
        self.assertIn('--fail-fast', result.stdout)
        self.assertIn('--terse', result.stdout)
        self.assertIn('--options-file', result.stdout)
        self.assertIn('--O', result.stdout)
        self.assertIn('--bounds-check', result.stdout)
        self.assertIn('--backtrace', result.stdout)
        self.assertIn('compilation order', result.stdout)


if __name__ == '__main__':
    unittest.main()
