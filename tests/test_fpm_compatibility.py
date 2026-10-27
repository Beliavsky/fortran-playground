from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from fpm_collections import source_preparer, validate_request
from fpm_compilers import preprocessing_flag
from test_fpm_service import archive
from xfpm_discovery_audit import classify


class CompatibilityTests(unittest.TestCase):
    def test_portable_metapackages_survive_preparation_in_all_dependency_tables(self):
        data = archive({'fpm.toml': '''name="fixture"
[dependencies]
openmp="*"
blas="*"
[dev-dependencies]
openmp="*"
[[example]]
name="demo"
[example.dependencies]
blas="*"
'''})
        payload = {'url': 'https://github.com/example/fixture', 'revision': 'a'*40, 'workflow': 'package'}
        with tempfile.TemporaryDirectory() as temporary:
            preparer = source_preparer(temporary, payload, downloader=lambda *a, **k: data)
            root, _ = preparer.prepare(payload)
            manifest = tomllib.loads((Path(temporary) / root / 'fpm.toml').read_text())
            self.assertEqual(manifest['dependencies'], {'openmp': '*', 'blas': '*'})
            self.assertEqual(manifest['dev-dependencies'], {'openmp': '*'})
            self.assertEqual(manifest['example'][0]['dependencies'], {'blas': '*'})
        for dependency in ['stdlib="*"', 'hdf5="*"', 'openmp=">=1.0"']:
            data = archive({'fpm.toml': 'name="fixture"\n[dependencies]\n' + dependency})
            with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'registry'):
                source_preparer(temporary, payload, downloader=lambda *a, **k: data).prepare(payload)

    def test_preprocess_is_boolean_and_flags_match_toolchains(self):
        self.assertTrue(validate_request({'url': 'https://github.com/a/b', 'workflow': 'package', 'preprocess': True})['preprocess'])
        for value in ['true', 1, None]:
            with self.assertRaises(ValueError):
                validate_request({'url': 'https://github.com/a/b', 'preprocess': value})
        self.assertEqual(preprocessing_flag('gfortran'), '-cpp')
        self.assertEqual(preprocessing_flag('ifx'), '-fpp')
        self.assertEqual(preprocessing_flag('ifx', windows=True), '/fpp')
        self.assertEqual(preprocessing_flag('lfortran'), '--cpp')

    def test_audit_reads_compiler_diagnostics_from_stdout_as_well_as_stderr(self):
        for diagnostic, expected in [('cannot find -lopenblas', 'missing_library_or_module'),
                                     ('Illegal preprocessor directive', 'preprocessing_required'),
                                     ('[-Werror=implicit-interface]', 'implicit_interface_error')]:
            self.assertEqual(classify({'stages': [{'stdout': diagnostic, 'stderr': ''}]}), expected)

    def test_worker_passes_preprocess_flags_to_build_and_run(self):
        import xfpm_worker as worker
        from fpm_compilers import COMPILERS
        calls = []
        def stage(command, *args, **kwargs):
            calls.append(command)
            return {'ok': True, 'command': command, 'stdout': '', 'stderr': '', 'seconds': 0, 'exit_code': 0}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'fpm.toml').write_text('name="fixture"')
            with patch.dict(worker.os.environ, {'FPM_COMPILER': 'gfortran'}), \
                    patch.object(worker, 'extract_archive', return_value=root), \
                    patch.object(worker, 'stage', side_effect=stage), \
                    patch.object(worker, 'targets', side_effect=lambda p, kind: ['demo'] if kind == 'example' else []), \
                    patch.object(worker, 'collect_plots', return_value={}), \
                    patch.object(worker.subprocess, 'check_output', return_value=COMPILERS['gfortran']['version']):
                result = worker.execute({'bundle': '', 'root': '.', 'request': {'url': 'https://github.com/a/b',
                    'workflow': 'package', 'action': 'example', 'preprocess': True}})
            self.assertTrue(result['ok'])
            self.assertEqual(result['target_groups'], {'app': [], 'example': ['demo'], 'test': []})
            self.assertEqual(len(calls), 2)
            for command in calls:
                self.assertEqual(command[command.index('--flag') + 1], '-cpp')


if __name__ == '__main__':
    unittest.main()
