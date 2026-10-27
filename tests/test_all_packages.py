import json
from pathlib import Path
import unittest
from unittest.mock import patch

from xall_packages import parse_packages, manifest_status

ROOT = Path(__file__).resolve().parents[1]


class DiscoveryTests(unittest.TestCase):
    def test_parser_merges_categories_and_ignores_reference_links(self):
        packages = parse_packages('''* [Contents](#one)
## Numerical
[Solver](https://github.com/Owner/solver): solves [ODEs](https://github.com/other/reference), by A
## Applications
[Solver again](https://github.com/owner/Solver): repeated
[Another](https://github.com/other/package): another package
[Not a repository](https://github.com/cran?q=fortran): ignore
''')
        self.assertEqual(len(packages), 2)
        solver = next(p for p in packages if p['id'] == 'owner/solver')
        self.assertEqual(solver['categories'], ['Numerical', 'Applications'])
        self.assertEqual(solver['description'], 'solves ODEs, by A')
        self.assertEqual(solver['revision'], '')
        with self.assertRaises(ValueError):
            parse_packages('Changed upstream format')

    def test_manifest_check_distinguishes_unavailable_and_invalid(self):
        from urllib.error import HTTPError
        for code, expected in [(404, 'missing'), (429, 'unknown'), (500, 'unknown')]:
            with patch('xall_packages.urlopen', side_effect=HTTPError('url', code, '', {}, None)):
                self.assertEqual(manifest_status('owner/repo'), expected)
        with patch('xall_packages.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value = b'name = "demo"\n'
            self.assertEqual(manifest_status('owner/repo'), 'available')
            request.return_value.__enter__.return_value.read.return_value = b'name = ['
            self.assertEqual(manifest_status('owner/repo'), 'invalid')

    def test_static_catalog_preserves_selected_pins_and_recipes(self):
        selected = json.loads((ROOT / 'site/fpm/packages.json').read_text(encoding='utf-8'))
        all_packages = json.loads((ROOT / 'site/fpm/all-packages.json').read_text(encoding='utf-8'))
        snapshot = json.loads((ROOT / 'fpm_catalog/all-packages.json').read_text(encoding='utf-8'))
        self.assertGreater(len(all_packages), len(selected))
        self.assertEqual(len({p['id'] for p in all_packages}), len(all_packages))
        self.assertEqual(len({p['repository'].lower() for p in all_packages}), len(all_packages))
        for package in selected:
            discovery = next(p for p in all_packages if p['repository'] == package['repository'])
            for key, value in package.items():
                self.assertEqual(discovery[key], value)
        for entry in snapshot['packages']:
            self.assertIn(entry['fpm_status'], ['available', 'missing', 'invalid', 'unknown'])
            self.assertTrue(entry['categories'])
            self.assertIsInstance(entry['topics'], list)
            self.assertTrue(any(p['repository'].lower() == entry['repository'].lower() for p in all_packages))


if __name__ == '__main__':
    unittest.main()
