import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from xsite import build_site
from xexamples import generate_examples

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_example_files_drive_catalog_and_asset_version(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / 'source'
            examples = site / 'examples'
            examples.mkdir(parents=True)
            destination = Path(directory) / 'built'
            (site / 'app.mjs').write_text("import {examples} from './examples.generated.mjs';", encoding='utf-8')
            first = examples / '01_first.f90'
            original = '! Example: First <example>\nprint *, "quotes ` ${literal} \\"\n'
            first.write_text(original, encoding='utf-8')
            (examples / 'README.txt').write_text('ignored', encoding='utf-8')
            version = build_site(site, destination)

            def catalog():
                module = (destination / 'examples.generated.mjs').read_text(encoding='utf-8')
                codes, labels = module.split('export const examples = ', 1)[1].split(';\nexport const exampleLabels = ')
                return json.loads(codes), json.loads(labels.removesuffix(';\n'))

            self.assertEqual(catalog(), ({'01_first': original}, {'01_first': 'First <example>'}))
            self.assertIn(f'examples.generated.mjs?v={version}', (destination / 'app.mjs').read_text())
            first.write_text('print *, 2\n', encoding='utf-8')
            (examples / '02_second_example.F08').write_text('print *, 3\n', encoding='utf-8')
            changed = build_site(site, destination)
            self.assertNotEqual(version, changed)
            self.assertEqual(catalog(), ({'01_first': 'print *, 2\n', '02_second_example': 'print *, 3\n'},
                                         {'01_first': 'first', '02_second_example': 'second example'}))
            first.unlink()
            self.assertNotEqual(changed, build_site(site, destination))
            self.assertEqual(list(catalog()[0]), ['02_second_example'])
            (examples / '02_second_example.F08').unlink()
            build_site(site, destination)
            self.assertEqual(catalog(), ({}, {}))

    def test_duplicate_example_stems_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            examples = site / 'examples'
            examples.mkdir()
            for extension in ('.f90', '.f08'):
                (examples / ('same' + extension)).write_text('end\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate example name'):
                generate_examples(site)

    def test_interpreter_choice_is_explicit(self):
        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        self.assertIn('ofort (interpreter, experimental)', html)
        self.assertIn('Compiler / interpreter', html)
        self.assertIn('no compiled python_mod helpers', html)

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
        self.assertIn("source: ['format', 'check'].includes(mode) ? source : ''", client)
        self.assertIn('id="format"', html)
        self.assertIn('id="check"', html)

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
        generate_examples(ROOT / 'site')
        proc = subprocess.run(['node', '--input-type=module', '-e',
            "import {examples} from './site/examples.generated.mjs'; console.log(JSON.stringify(examples));"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        examples = json.loads(proc.stdout)
        checks = json.loads((ROOT / 'tests/example_results.json').read_text(encoding='utf-8'))
        self.assertEqual(set(examples), set(checks), 'Every dropdown example needs expected results')
        with tempfile.TemporaryDirectory() as directory:
            for name, code in examples.items():
                work = Path(directory) / name
                work.mkdir()
                source = work / 'example.f90'
                executable = work / 'example.exe'
                source.write_text(code, encoding='utf-8')
                for mode, flags in [('default', []), ('checked', [
                        '-std=f2018', '-Wall', '-Wextra', '-Werror', '-pedantic', '-fcheck=all'])]:
                    with self.subTest(example=name, mode=mode):
                        compilation = subprocess.run(['gfortran', *flags, str(source), '-o', str(executable)],
                                                     cwd=work, capture_output=True, text=True, timeout=30)
                        self.assertEqual(compilation.returncode, 0, compilation.stdout + compilation.stderr)
                        result = subprocess.run([str(executable)], cwd=work, stdin=subprocess.DEVNULL,
                                                capture_output=True, text=True, timeout=10)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(result.stderr.strip(), '')
                        actual_lines = result.stdout.strip().splitlines()
                        expected_lines = checks[name]['output']
                        self.assertEqual(len(actual_lines), len(expected_lines), result.stdout)
                        for actual, expected in zip(actual_lines, expected_lines):
                            actual_tokens, expected_tokens = actual.split(), expected.split()
                            self.assertEqual(len(actual_tokens), len(expected_tokens), actual)
                            for got, wanted in zip(actual_tokens, expected_tokens):
                                try:
                                    expected_number = float(wanted)
                                except ValueError:
                                    self.assertEqual(got, wanted, actual)
                                else:
                                    self.assertTrue(math.isclose(float(got), expected_number,
                                        rel_tol=5e-7, abs_tol=checks[name].get('abs_tol', 1e-11)),
                                        f'{actual!r}: expected {wanted}, got {got}')


if __name__ == '__main__':
    unittest.main()
