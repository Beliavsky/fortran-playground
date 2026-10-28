import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest

from xpackage_gams import (gams_data, package_classes, review_text, subclass_module, ROOT, REPORT,
                          driver_data, g1_review_text, PILOT_REPORT)


class GamsFilterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_select = False
        self.code = None
        self.options = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'select':
            self.in_select = attrs.get('id') == 'package-gams'
        if self.in_select and tag == 'option':
            self.code = attrs.get('value', '')
            self.options[self.code] = ''

    def handle_endtag(self, tag):
        if tag == 'select':
            self.in_select = False
        if tag == 'option':
            self.code = None

    def handle_data(self, text):
        if self.in_select and self.code is not None:
            self.options[self.code] += text


class PackageGamsTests(unittest.TestCase):
    def test_public_assignments_cover_catalog_and_preserve_pins(self):
        data = gams_data()
        original = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
        public = json.loads((ROOT / 'site/fpm/packages.json').read_text(encoding='utf-8'))
        all_packages = {p['repository'].lower(): p for p in json.loads(
            (ROOT / 'site/fpm/all-packages.json').read_text(encoding='utf-8'))}
        self.assertEqual(set(data['packages']), {p['id'] for p in public})
        for package in original:
            with self.subTest(package=package['id']):
                entry = next(p for p in public if p['id'] == package['id'])
                self.assertEqual(entry['gams'], package_classes(data, package['id']))
                self.assertEqual(all_packages[package['repository'].lower()]['gams'], entry['gams'])
                for field in ('revision', 'archive_sha256', 'dependencies'):
                    self.assertEqual(entry.get(field), package.get(field))
        self.assertEqual(data['packages']['mersenne-twister-fortran'], ['L'])
        self.assertEqual(data['packages']['dvode'], ['I'])
        self.assertEqual(data['packages']['rational_number'], ['A'])
        self.assertEqual(data['packages']['minpack'], ['F', 'G', 'K'])
        self.assertEqual(data['subclass_assignments']['mersenne-twister-fortran'], ['L6'])
        self.assertEqual(data['subclass_assignments']['dvode'], ['I1'])
        self.assertEqual(data['subclass_assignments']['rational_number'], ['A2'])
        self.assertEqual(data['subclass_assignments']['minpack'], ['F2', 'G1', 'K1'])
        self.assertNotIn('datetime-fortran', data['subclass_assignments'])
        self.assertEqual(package_classes(data, 'datetime-fortran'), [
            {'code': 'R', 'label': data['classes']['R'], 'parent': None}])

    def test_subclass_tree_generated_module_and_natural_order(self):
        data = gams_data()
        self.assertEqual((ROOT / 'site/fpm/gams_classes.mjs').read_text(encoding='utf-8'), subclass_module(data))
        self.assertEqual(data['subclasses']['L6'], {'label': 'Random number generation', 'parent': 'L'})
        self.assertEqual(data['subclasses']['C10']['parent'], 'C')
        self.assertNotEqual(data['subclasses']['C10']['parent'], 'C1')
        self.assertEqual(data['subclasses']['L10']['parent'], 'L')
        self.assertNotEqual(data['subclasses']['L10']['parent'], 'L1')
        self.assertTrue(all(info['parent'] not in 'BOPQZ' for info in data['subclasses'].values()))
        self.assertEqual([c['code'] for c in package_classes(data, 'specfun')], ['C', 'C7', 'C10'])

    def test_filter_matches_all_twenty_official_labels(self):
        parser = GamsFilterParser()
        parser.feed((ROOT / 'site/fpm/index.html').read_text(encoding='utf-8'))
        self.assertEqual(parser.options, {'': 'All classes', **{
            code: f'{code} — {label}' for code, label in gams_data()['classes'].items()}})

    def test_review_page_is_current_and_lists_each_package_once(self):
        text = review_text()
        self.assertEqual((ROOT / REPORT).read_text(encoding='utf-8'), text)
        for name in gams_data()['packages']:
            self.assertEqual(text.count(f'| [{name}](https://github.com/'), 1, name)

    def test_validation_rejects_missing_unknown_and_duplicate_classes(self):
        data = gams_data()
        data['packages'] = {'example': ['D']}
        data['subclass_assignments'] = {'example': ['D2']}
        data['review_notes'] = {}
        data['procedure_mappings'] = []
        invalid = []
        for codes in ([], ['d'], ['D1'], ['T'], ['D', 'D'], [None]):
            broken = copy.deepcopy(data)
            broken['packages']['example'] = codes
            invalid.append(broken)
        for assignments in ({}, {'unknown': ['D']}):
            broken = copy.deepcopy(data)
            broken['packages'] = assignments
            invalid.append(broken)
        broken = copy.deepcopy(data)
        del broken['classes']['Z']
        invalid.append(broken)
        for codes in (['D99'], ['d2'], ['D2', 'D2'], ['G1'], ['D'], [], [None]):
            broken = copy.deepcopy(data)
            broken['subclass_assignments']['example'] = codes
            invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclasses']['D2']['parent'] = 'G'
        invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclasses']['D1a'] = {'label': 'Too deep for this schema', 'parent': 'D'}
        invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclass_assignments']['unknown'] = ['D2']
        invalid.append(broken)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_text(json.dumps({'packages': [{'id': 'example'}]}))
            path = root / 'fpm_catalog/gams.json'
            for metadata in invalid:
                with self.subTest(metadata=metadata['packages']):
                    path.write_text(json.dumps(metadata))
                    with self.assertRaises(ValueError):
                        gams_data(root)
            path.write_text(json.dumps(data))
            self.assertEqual(gams_data(root), data)

    def test_g1_procedures_and_verified_drivers(self):
        data = gams_data()
        mappings = data['procedure_mappings']
        self.assertEqual(len(mappings), 11)
        self.assertEqual(len({m['package_id'] for m in mappings}), 7)
        self.assertEqual(data['detailed_classes']['G1a']['parent'], 'G1')
        self.assertEqual(data['detailed_classes']['G1b']['parent'], 'G1')
        self.assertIn('G1a', {c['code'] for c in package_classes(data, 'fmin')})
        self.assertIn('G1b', {c['code'] for c in package_classes(data, 'minpack')})
        self.assertNotIn('G1a', {c['code'] for c in package_classes(data, 'nonlin')})
        self.assertEqual({d['id'] for d in driver_data()},
                         {'fmin-sine', 'minpack-bard', 'libdogleg-bard'})
        self.assertEqual((ROOT / PILOT_REPORT).read_text(encoding='utf-8'), g1_review_text())
        examples = json.loads((ROOT / 'site/fpm/examples.json').read_text(encoding='utf-8'))
        for driver in driver_data():
            example = next(e for e in examples if e.get('gams_driver_id') == driver['id'])
            self.assertEqual(example['revision'], driver['revision'])
            self.assertEqual(example['source'], (ROOT / driver['path']).read_text(encoding='utf-8'))

    def test_g1_rejects_stale_procedure_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_bytes((ROOT / 'fpm_catalog.json').read_bytes())
            data = gams_data()
            data['procedure_mappings'][0]['revision'] = '0' * 40
            (root / 'fpm_catalog/gams.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'stale revision'):
                gams_data(root)

    def test_changed_driver_requires_new_verification(self):
        data = gams_data()
        drivers = driver_data(data=data)
        paths = ['fpm_catalog/gams-drivers.json', 'docs/gams-g1-validation.json']
        paths += list({p for d in drivers for p in [d['path'], *d['license_files']]})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in paths:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / path).read_bytes())
            self.assertEqual(driver_data(root, data), drivers)
            path = root / drivers[0]['path']
            path.write_text(path.read_text(encoding='utf-8') + '\n! Changed source\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'passing GNU 16 verification'):
                driver_data(root, data)


if __name__ == '__main__':
    unittest.main()
