from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fpm_targets import parse_targets, select_targets, discover_targets
from fpm_collections import validate_request
from fortran_fpm import validate_options


class TargetTests(unittest.TestCase):
    def test_compiled_buckets_take_precedence_over_manifest_and_custom_folders_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm.toml').write_text('name="fixture"\n[[executable]]\nname="demo_app"\nsource-dir="example"\n'
                                         '[[example]]\nname="sample"\nsource-dir="samples"\n')
            for directory, name in [('example', 'demo_app'), ('samples', 'sample'), ('app', 'ordinary')]:
                folder = root / 'build/compiler' / directory
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / (name + '.exe')
                path.write_bytes(b'fixture')
            self.assertEqual(discover_targets(root, 'app', windows=True), ['ordinary'])
            self.assertEqual(discover_targets(root, 'example', windows=True), ['demo_app', 'sample'])

    def test_examples_require_package_workflow(self):
        self.assertEqual(validate_request({'url': 'https://github.com/a/b', 'workflow': 'package',
                                          'action': 'example'})['action'], 'example')
        for validate, options in [(validate_options, {'source': 'program main', 'action': 'example'}),
                                  (validate_request, {'url': 'https://github.com/a/b', 'source': 'program main', 'action': 'example'})]:
            with self.assertRaises(ValueError):
                validate(options)

    def test_lists_quotes_commas_and_globs(self):
        available = ['demo_a', 'demo_b', 'other']
        for value in ['demo_*', '"demo_*"', "'demo_*'", 'demo_?', 'demo_a demo_b',
                      'demo_a,demo_b', '"demo_a demo_b"', 'demo_* demo_a']:
            with self.subTest(value=value):
                self.assertEqual(select_targets(value, available), ['demo_a', 'demo_b'])
                self.assertEqual(validate_options({'target': value})['target'], value)
                self.assertEqual(validate_request({'url': 'https://github.com/a/b', 'workflow': 'package',
                                                   'target': value})['target'], value)
        self.assertEqual(select_targets('*', available), available)
        self.assertEqual(parse_targets('   '), [])
        with self.assertRaisesRegex(ValueError, 'No available target matches'):
            select_targets('demo_a missing*', available)

    def test_reject_options_paths_shell_syntax_and_unbounded_lists(self):
        for value in ['--runner', '../demo', '/demo', 'a;echo', '$(echo)', '`echo`', 'demo[ab]',
                      '"demo', '""', 123, '* ' * 33, 'a' * 2049]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_targets(value)

    def test_hosted_worker_passes_expanded_names_in_one_invocation(self):
        # Exercise the real worker selection path without launching a sandbox.
        import xfpm_worker as worker
        from fpm_compilers import COMPILERS
        commands = []
        def stage(command, directory, timeout, stdin=''):
            commands.append((command, timeout, stdin))
            return {'ok': True, 'seconds': 0, 'command': command, 'exit_code': 0, 'stdout': '', 'stderr': ''}
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            (bundle / 'fpm.toml').write_text('name="fixture"')
            payload = {'url': 'https://github.com/a/b', 'workflow': 'package', 'action': 'run', 'target': '"demo_*" other'}
            with patch.dict(worker.os.environ, {'FPM_COMPILER': 'gfortran'}), \
                 patch.object(worker, 'extract_archive', return_value=bundle), \
                 patch.object(worker, 'stage', side_effect=stage), \
                 patch.object(worker, 'targets', return_value=['demo_a', 'demo_b', 'other']), \
                 patch.object(worker, 'collect_plots', return_value={}), \
                 patch.object(worker.subprocess, 'check_output', return_value=COMPILERS['gfortran']['version']):
                result = worker.execute({'request': payload, 'bundle': '', 'root': '.'})
            self.assertTrue(result['ok'], result)
            self.assertEqual(commands[-1][0][-4:], ['--target', 'demo_a', 'demo_b', 'other'])
            self.assertEqual(commands[-1][1], 30)

    def test_worker_examples_and_nothing_run_status(self):
        import xfpm_worker as worker
        from fpm_compilers import COMPILERS
        commands = []
        def stage(command, directory, timeout, stdin=''):
            commands.append(command)
            return {'ok': True, 'seconds': 0, 'command': command, 'exit_code': 0, 'stdout': '', 'stderr': ''}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm.toml').write_text('name="fixture"')
            payload = {'url': 'https://github.com/a/b', 'workflow': 'package', 'action': 'example', 'target': 'demo*'}
            with patch.dict(worker.os.environ, {'FPM_COMPILER': 'gfortran'}), \
                 patch.object(worker, 'extract_archive', return_value=root), \
                 patch.object(worker, 'stage', side_effect=stage), \
                 patch.object(worker, 'targets', return_value=['demo_sample']) as names, \
                 patch.object(worker, 'collect_plots', return_value={}), \
                 patch.object(worker.subprocess, 'check_output', return_value=COMPILERS['gfortran']['version']):
                result = worker.execute({'request': payload, 'bundle': '', 'root': '.'})
                self.assertTrue(result['ok'], result)
                self.assertEqual(result['target_groups']['example'], ['demo_sample'])
                self.assertEqual(result['stages'][-1]['name'], 'Examples')
                self.assertIn('--example', commands[-1])
                names.return_value = []
                result = worker.execute({'request': {**payload, 'action': 'run'}, 'bundle': '', 'root': '.'})
                self.assertFalse(result['ok'])
                self.assertTrue(result['nothing_run'])
                self.assertTrue(result['build_ok'])
                self.assertEqual(len(result['stages']), 1)


if __name__ == '__main__':
    unittest.main()
