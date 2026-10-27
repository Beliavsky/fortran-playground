"""Downloaded projects use the same locked preparation without a Modal service."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import tomllib
import unittest
from unittest.mock import patch, Mock

from fpm_catalog_build import adapter_digest
from fpm_catalog_patches import patch_digest
from fpm_project_run import prepare, run
from test_fpm_service import archive

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def fixture(self, project):
        runtime = json.loads((ROOT / 'site/fpm/project-runtime.json').read_text(encoding='utf-8'))
        for name, text in runtime.items():
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        code = 'module library\nuse helper\ncontains\ninteger function answer()\nanswer = base + 1\nend function\nend module\n'
        root = archive({'fpm.toml': 'name="actual-library"\nversion="VERSION"\n[dependencies]\nhelper="*"\n',
                        'src/library.f90': code, 'LICENSE': 'test license'})
        helper = archive({'fpm.toml': 'name="helper"\nversion="1.0.0"',
                          'src/helper.f90': 'module helper\ninteger, parameter :: base=40\nend module\n'})
        package = {'id': 'catalog-label', 'repository': 'test/library', 'revision': 'a'*40,
                   'archive_sha256': hashlib.sha256(root).hexdigest(),
                   'dependencies': [{'repository': 'test/helper', 'revision': 'b'*40,
                                     'sha256': hashlib.sha256(helper).hexdigest()}],
                   'catalog_build': {'adapter_sha256': adapter_digest(),
                       'manifest_versions': {'test/library': '0.0.0'},
                       'registry': {'helper': {'git': 'https://github.com/test/helper', 'rev': 'b'*40}},
                       'environment': {'FPM_FFLAGS': '-fcheck=all'}},
                   'catalog_patches': {'adapter_sha256': patch_digest(), 'edits': [{
                       'path': 'src/library.f90', 'sha256': hashlib.sha256(code.encode()).hexdigest(),
                       'before': 'base + 1', 'after': 'base + 2'}]}}
        settings = {'schema': 1, 'request': {'url': 'https://github.com/test/library', 'revision': 'a'*40},
                    'package': package}
        (project / 'playground.json').write_text(json.dumps(settings), encoding='utf-8')
        (project / 'app').mkdir()
        (project / 'app/main.f90').write_text('program main\nuse library\nif(answer()/=42) stop 1\nprint *,answer()\nend program\n')
        def download(url, **kwargs):
            return helper if '/test/helper/' in url else root
        return settings, download

    def test_locked_patched_project_and_local_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            settings, download = self.fixture(project)
            root = prepare(project, settings, downloader=download)
            manifest = tomllib.loads((project / 'fpm.toml').read_text())
            self.assertEqual(set(manifest['dependencies']), {'actual-library'})
            self.assertIn('base + 2', (root / 'src/library.f90').read_text())
            self.assertEqual((root / 'LICENSE').read_text(), 'test license')
            self.assertEqual(tomllib.loads((root / 'fpm.toml').read_text())['version'], '0.0.0')
            (project / 'app/main.f90').write_text('edited main')
            (root / 'src/library.f90').write_text('edited dependency')
            with patch('fpm_sources.fetch', side_effect=AssertionError('must not download again')):
                self.assertEqual(prepare(project, settings), root)
            self.assertEqual((project / 'app/main.f90').read_text(), 'edited main')
            self.assertEqual((root / 'src/library.f90').read_text(), 'edited dependency')

    def test_bad_archive_checksum_does_not_publish_sources_or_change_main(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            settings, download = self.fixture(project)
            settings['package']['archive_sha256'] = '0'*64
            original = (project / 'app/main.f90').read_bytes()
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                prepare(project, settings, downloader=download)
            self.assertFalse((project / 'dependencies').exists())
            self.assertEqual((project / 'app/main.f90').read_bytes(), original)

    def test_runner_applies_flags_stdin_and_preserves_return_code(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            settings, download = self.fixture(project)
            prepare(project, settings, downloader=download)
            (project / 'stdin.txt').write_bytes(b'5\n7\n')
            args = argparse.Namespace(prepare_only=False, build_only=False, compiler='gfortran')
            with patch.dict(os.environ, {'FPM_FFLAGS': '-O0'}), patch('shutil.which', return_value='fpm'), \
                    patch('subprocess.run', return_value=Mock(returncode=7)) as command:
                self.assertEqual(run(project, args), 7)
                self.assertEqual(command.call_args.kwargs['input'], b'5\n7\n')
                self.assertIn('-fcheck=all', command.call_args.kwargs['env']['FPM_FFLAGS'])
                self.assertIn('-O0', command.call_args.kwargs['env']['FPM_FFLAGS'])
            args.compiler = 'ifx'
            with self.assertRaisesRegex(ValueError, 'GNU compiler flags'):
                run(project, args)

    @unittest.skipUnless(shutil.which('gfortran') and shutil.which('fpm'), 'local gfortran and fpm required')
    def test_real_local_fpm_build_of_exported_tools(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            settings, download = self.fixture(project)
            prepare(project, settings, downloader=download)
            result = subprocess.run([os.sys.executable, '-X', 'utf8', 'run.py'], cwd=project,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('42', result.stdout)
