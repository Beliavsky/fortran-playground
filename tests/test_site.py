import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from xsite import build_site

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_build_versions_assets_and_preserves_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'site'
            version = build_site(ROOT / 'site', destination)
            self.assertIn(f'app.mjs?v={version}', (destination / 'index.html').read_text(encoding='utf-8'))
            self.assertIn(f'editors.mjs?v={version}', (destination / 'app.mjs').read_text(encoding='utf-8'))
            self.assertEqual(json.loads((destination / 'service.json').read_text()),
                             json.loads((ROOT / 'site/service.json').read_text()))
            self.assertTrue((destination / 'run/index.html').is_file())

    def test_no_transpiler_or_python_controls(self):
        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        client = (ROOT / 'site/app.mjs').read_text(encoding='utf-8')
        self.assertNotIn('id="python"', html)
        self.assertNotIn('pyodide', client)
        self.assertNotIn('manifest.json', client)
        self.assertIn("mode: 'fortran-edit'", client)
        self.assertIn("source: ''", client)

    def test_configuration_is_public_origin_only(self):
        from urllib.parse import urlparse
        config = json.loads((ROOT / 'site/service.json').read_text())
        self.assertEqual(set(config), {'url'})
        url = urlparse(config['url'])
        self.assertEqual(url.scheme, 'https')
        self.assertTrue(url.hostname.endswith('.modal.run'))
        self.assertFalse(url.username or url.password or url.query)

    @unittest.skipUnless(shutil.which('node') and shutil.which('gfortran'), 'node and gfortran required')
    def test_standalone_examples_compile_and_run(self):
        proc = subprocess.run(['node', '--input-type=module', '-e',
            "import {examples} from './site/examples.mjs'; console.log(JSON.stringify(examples));"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        examples = json.loads(proc.stdout)
        expected = {'sum': [385], 'matrix': [2, 6, 4, 8], 'roots': [2, 1]}
        with tempfile.TemporaryDirectory() as directory:
            for name, values in expected.items():
                with self.subTest(example=name):
                    source = Path(directory) / (name + '.f90')
                    executable = Path(directory) / (name + '.exe')
                    source.write_text(examples[name], encoding='utf-8')
                    subprocess.run(['gfortran', str(source), '-o', str(executable)],
                                   capture_output=True, text=True, check=True, timeout=30)
                    output = subprocess.run([str(executable)], capture_output=True, text=True,
                                            check=True, timeout=10).stdout
                    self.assertEqual([float(value) for value in output.split()], values)


if __name__ == '__main__':
    unittest.main()
