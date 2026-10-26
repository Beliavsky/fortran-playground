from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from fortran_output_diff import compare_output, comparison_report, comparable, tolerances
import xfortran_run as local
import xplayground_run as hosted


def row(name, text):
    return {'compiler': name, 'status': 'PASS', 'ok': True,
            'execution': {'ok': True, 'exit_code': 0, 'stdout': text}, 'times': {}}


class OutputDiffTests(unittest.TestCase):
    def test_shared_browser_fixtures(self):
        cases = json.loads(Path(__file__).with_name('output_diff_cases.json').read_text(encoding='utf-8'))
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(compare_output(case['a'], case['b'], case['mode'], case.get('atol', '0'), case.get('rtol', '0'))['status'], case['status'])

    def test_validation_and_eligibility(self):
        for bad in ['-1', 'NaN', 'Infinity', '', 'garbage', '1e9999']:
            with self.assertRaises(ValueError): tolerances(bad)
        self.assertEqual(compare_output('x' * 1000001, '', 'exact')['status'], 'Not comparable')
        self.assertEqual(compare_output('1 ' * 20001, '2', 'numeric')['status'], 'Not comparable')
        first, second = row('gfortran', '1.0'), row('ifx', '1D0')
        failed = {**row('bad', '1D0'), 'status': 'FAIL'}
        truncated = row('truncated', '1D0'); truncated['execution']['truncated'] = True
        self.assertFalse(comparable(failed)); self.assertFalse(comparable(truncated))
        report = comparison_report([failed, first, second, truncated], 'numeric')
        self.assertIn('Reference: gfortran', report)
        self.assertIn('ifx: Numeric match', report)
        self.assertIn('bad: Not comparable', report)
        self.assertIn('truncated: Not comparable', report)
        self.assertIn('Reference: ifx', comparison_report([first, second], reference='ifx'))
        self.assertIn('unavailable', comparison_report([first, second], reference='missing'))

    def test_local_runner_optional_diff_and_no_extra_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'main.f90'; source.write_text('program p\nend\n')
            for arguments, text in [([], None), (['--diff'], 'Different'), (['--diff', 'numeric'], 'Numeric match')]:
                output = StringIO()
                with patch.object(local, 'discover', return_value={}), patch.object(local, 'compare', return_value=[row('gfortran', '1.0'), row('ifx', '1D0')]) as compare, redirect_stdout(output):
                    status = local.main([str(source), '--compilers', 'gfortran', 'ifx', *arguments])
                self.assertEqual(status, 0)
                self.assertEqual(compare.call_count, 1)
                if text: self.assertIn('ifx: ' + text, output.getvalue())
                else: self.assertNotIn('Output comparison:', output.getvalue())

    def test_hosted_runner_optional_diff_and_no_extra_jobs(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'main.f90'; source.write_text('program p\nend\n')
            for arguments, text in [([], None), (['--diff'], 'Different'), (['--diff', 'numeric'], 'Numeric match')]:
                client = Mock(service_url='https://execute.example.org')
                client.connect.return_value = {'compilers': ['gfortran', 'ifx'], 'compiler_options': {
                    name: {'presets': {'default': []}, 'extras': {}, 'standards': {}} for name in ['gfortran', 'ifx']}}
                client.run_job.side_effect = [(row('gfortran', '1.0'), 1), (row('ifx', '1D0'), 1)]
                output, error = StringIO(), StringIO()
                with patch.object(hosted, 'PlaygroundClient', return_value=client), redirect_stdout(output), redirect_stderr(error):
                    status = hosted.main([str(source), '--compilers', 'gfortran', 'ifx', '--terse', '--service-url', 'https://execute.example.org', *arguments])
                self.assertEqual(status, 0, error.getvalue())
                self.assertEqual(client.run_job.call_count, 2)
                if text: self.assertIn('ifx: ' + text, output.getvalue())
                else: self.assertNotIn('Output comparison:', output.getvalue())

    def test_invalid_cli_comparison_options_prevent_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'main.f90'; source.write_text('program p\nend\n')
            for arguments in [ ['--diff', 'numeric', '--diff-atol', '-1'],
                               ['--diff', '--diff-rtol', '1e-6'],
                               ['--diff-reference', 'ifx'],
                               ['--diff', '--diff-reference', 'missing'] ]:
                for runner in [local, hosted]:
                    with self.subTest(runner=runner.__name__, arguments=arguments):
                        output, error = StringIO(), StringIO()
                        target = 'discover' if runner is local else 'PlaygroundClient'
                        with patch.object(runner, target) as work, redirect_stdout(output), redirect_stderr(error):
                            status = runner.main([str(source), *arguments])
                        self.assertEqual(status, 2)
                        work.assert_not_called()


if __name__ == '__main__':
    unittest.main()
