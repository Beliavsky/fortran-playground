import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from xsite import build_site

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_source_and_results_share_responsive_workspace(self):
        from html.parser import HTMLParser

        class Panes(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack = []
                self.ancestors = {}

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if attrs.get('id') in {'fortran', 'output', 'diagnostics', 'compile', 'run', 'rerun', 'stop', 'first-error', 'fix-error', 'compiler', 'preset'}:
                    self.ancestors[attrs['id']] = list(self.stack)
                if tag not in {'input', 'link', 'meta', 'br'}:
                    self.stack.append(attrs.get('id') or attrs.get('class') or tag)

            def handle_endtag(self, tag):
                if self.stack:
                    self.stack.pop()

        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        panes = Panes()
        panes.feed(html)
        self.assertIn('source-pane', panes.ancestors['fortran'])
        for target in ('output', 'diagnostics'):
            self.assertIn('results-pane', panes.ancestors[target])
            self.assertIn('workspace', panes.ancestors[target])
        self.assertIn('workspace', panes.ancestors['fortran'])
        for target in ('compile', 'run', 'rerun', 'stop', 'first-error', 'fix-error'):
            self.assertIn('source-header', panes.ancestors[target])
            self.assertIn('source-pane', panes.ancestors[target])
            self.assertEqual(html.count(f'id="{target}"'), 1)
        for target in ('compiler', 'preset'):
            self.assertNotIn('workspace', panes.ancestors[target])
        css = (ROOT / 'site/app.css').read_text()
        self.assertIn('minmax(0, 3fr) minmax(0, 2fr)', css)
        self.assertIn('@media (max-width: 760px)', css)
        self.assertIn('overflow: auto', css)
        self.assertIn('flex: none; padding: 12px 16px', css)
        self.assertIn('flex-wrap: wrap', css)

    def test_build_versions_assets_and_preserves_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'site'
            version = build_site(ROOT / 'site', destination)
            self.assertIn(f'app.mjs?v={version}', (destination / 'index.html').read_text(encoding='utf-8'))
            self.assertIn(f'editors.mjs?v={version}', (destination / 'app.mjs').read_text(encoding='utf-8'))
            self.assertIn(f'config.mjs?v={version}', (destination / 'app.mjs').read_text(encoding='utf-8'))
            self.assertIn(f'quick_fix_controls.mjs?v={version}', (destination / 'app.mjs').read_text(encoding='utf-8'))
            self.assertIn(f'fixes.mjs?v={version}', (destination / 'quick_fix_controls.mjs').read_text(encoding='utf-8'))
            self.assertEqual((destination / 'config.mjs').read_text(), (ROOT / 'site/config.mjs').read_text())
            self.assertEqual(json.loads((destination / 'service.json').read_text()),
                             json.loads((ROOT / 'site/service.json').read_text()))
            self.assertTrue((destination / 'run/index.html').is_file())

    def test_no_transpiler_or_python_controls(self):
        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        client = (ROOT / 'site/app.mjs').read_text(encoding='utf-8')
        self.assertNotIn('id="python"', html)
        self.assertNotIn('pyodide', client)
        self.assertNotIn('manifest.json', client)
        self.assertIn("mode = 'fortran-edit'", client)
        for identifier in ('compile', 'run', 'rerun'):
            self.assertIn(f'id="{identifier}"', html)
        self.assertIn('id="standard"', html)
        self.assertIn('>Compiler default</option>', html)
        self.assertIn('id="standard-note"', html)
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
