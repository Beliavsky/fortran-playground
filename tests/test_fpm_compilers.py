import base64
from io import BytesIO
from pathlib import Path
import tarfile
import tempfile
import unittest

from fpm_compilers import COMPILERS, compiler_flags
from fpm_probe import probe_message
from fpm_sources import validate_request
from xfpm_worker import targets


class CompilerTests(unittest.TestCase):
    def test_fpm_detection_names_and_requested_compiler_are_explicit(self):
        self.assertEqual(set(COMPILERS), {'gfortran', 'gfortran17', 'ifx', 'flang'})
        self.assertEqual(Path(COMPILERS['flang']['command']).name, 'flang-new')
        self.assertEqual(Path(COMPILERS['gfortran17']['command']).name, 'gfortran')
        for name in COMPILERS:
            flags = compiler_flags(name)
            self.assertEqual(flags[flags.index('--compiler') + 1], COMPILERS[name]['command'])
            for action in ('build', 'run', 'test'):
                message = probe_message(name, action)
                self.assertEqual(validate_request(message['request'])['compiler'], name)
                with tarfile.open(fileobj=BytesIO(base64.b64decode(message['bundle']))) as archive:
                    names = archive.getnames()
                    self.assertIn('bundle/package/src/answer.c', names)
                    self.assertIn('bundle/package/test/check.f90', names)

    def test_target_discovery_handles_non_gnu_build_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            for compiler in ('gfortran', 'ifx', 'flang-new'):
                executable = project / 'build' / (compiler + '_123') / 'app' / compiler
                executable.parent.mkdir(parents=True)
                executable.write_text('fixture')
                executable.chmod(0o755)
            self.assertEqual(targets(project, 'app'), ['flang-new', 'gfortran', 'ifx'])
