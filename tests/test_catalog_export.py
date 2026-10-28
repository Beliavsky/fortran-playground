import copy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from catalog_export import (ROOT, PUBLISHER, SCHEMA_NAME, FEED_NAME, build_export, canonical_json,
                            input_provenance, merge_catalog, publish_export, snapshot_id, validate_export)
from xcatalog_import import read_feed


class CatalogExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = build_export()

    def test_complete_deterministic_export_preserves_sources_and_pins(self):
        feed = self.feed
        self.assertEqual(canonical_json(feed), canonical_json(build_export()))
        packages = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
        topics = json.loads((ROOT / 'fpm_catalog/topics.json').read_text(encoding='utf-8'))['repositories']
        curated = json.loads((ROOT / 'fpm_catalog/playground-topics.json').read_text(encoding='utf-8'))['packages']
        self.assertEqual(len(feed['projects']), len(packages))
        by_id = {p['id']: p for p in feed['projects']}
        for package in packages:
            with self.subTest(package=package['id']):
                identity = 'github:' + package['repository'].lower()
                record = by_id[identity]
                self.assertEqual(record['github']['topics'], topics[package['repository'].lower()]['topics'])
                self.assertEqual(record['curation']['topics'], sorted(curated[package['id']]))
                self.assertEqual(record['license']['label'], package['license'])
                self.assertIsNone(record['license']['spdx_expression'])
                self.assertEqual(record['curation']['reviewed_revision'], package['revision'])
                self.assertEqual(record['playground']['package_revision'], package['revision'])
                self.assertIn('?package=' + package['id'], record['playground']['url'])
                self.assertFalse(record['playground']['live_service_checked'])
                self.assertNotIn('authors', record)
                for field in ('catalog_build', 'catalog_patches', 'dependencies', 'archive_sha256'):
                    self.assertNotIn(field, record)
        self.assertEqual(feed['taxonomies']['gams']['classes']['L6']['parent'], 'L')
        self.assertEqual(feed['taxonomies']['gams']['classes']['G1b']['parent'], 'G1')
        self.assertEqual(sum(len(p['curation'].get('procedures', [])) for p in feed['projects']), 11)
        self.assertEqual(len(feed['demonstrations']), 3)
        for driver in feed['demonstrations']:
            self.assertIn('&example=gams-', driver['url'])
            self.assertIn(driver['path'], {r['path'] for r in feed['provenance']['inputs']})
        merged = merge_catalog({'schema_version': 1, 'projects': []}, feed)
        self.assertEqual(merged['sources'][PUBLISHER]['demonstrations'], feed['demonstrations'])

    def test_provenance_distinguishes_clean_modified_and_unknown_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'metadata.json'
            path.write_bytes(b'{"value":1}\r\n')
            commit = 'a' * 40
            def git_result(command, **kwargs):
                return subprocess.CompletedProcess(command, 0, commit + '\n' if command[-1] == 'HEAD' else '', '')
            with patch('catalog_export.subprocess.run', side_effect=git_result) as git:
                clean = input_provenance(root, ['metadata.json'])
                self.assertEqual(clean['source_commit'], commit)
                self.assertFalse(clean['inputs_modified'])
                self.assertEqual(git.call_args_list[-1].args[0][-2:], ['--', 'metadata.json'])
            path.write_bytes(b'{"value":1}\n')
            with patch('catalog_export.subprocess.run', side_effect=git_result):
                lf = input_provenance(root, ['metadata.json'])
            self.assertEqual(clean['inputs'], lf['inputs'], 'Hashes are independent of Windows line endings')
            def dirty_result(command, **kwargs):
                return subprocess.CompletedProcess(command, 0, commit + '\n' if command[-1] == 'HEAD' else ' M metadata.json\n', '')
            with patch('catalog_export.subprocess.run', side_effect=dirty_result):
                dirty = input_provenance(root, ['metadata.json'])
            self.assertIsNone(dirty['source_commit'])
            self.assertEqual(dirty['base_commit'], commit)
            self.assertTrue(dirty['inputs_modified'])
            with patch('catalog_export.subprocess.run', side_effect=OSError('git unavailable')):
                unknown = input_provenance(root, ['metadata.json'])
            self.assertIsNone(unknown['source_commit'])
            self.assertIsNone(unknown['inputs_modified'])

    def test_merge_updates_only_owned_layer_and_preserves_local_projects(self):
        feed = copy.deepcopy(self.feed)
        identity = feed['projects'][0]['id']
        local = {'description': 'Catalog editor description', 'topics': ['my-topic'], 'notes': 'Keep these notes'}
        standalone = {'id': 'github:example/legacy-library', 'local': {
            'name': 'Legacy library', 'build_systems': ['make'], 'description': 'A non-FPM project'}, 'imports': {}}
        catalog = {'schema_version': 1, 'sources': {'other': {'keep': True}}, 'projects': [
            {'id': identity, 'local': local, 'imports': {'other': {'keep': True}}}, standalone]}
        original = copy.deepcopy(catalog)
        merged = merge_catalog(catalog, feed)
        self.assertEqual(catalog, original, 'Merge does not mutate its inputs')
        self.assertEqual(merged, merge_catalog(merged, feed), 'Importing the same snapshot is idempotent')
        projects = {p['id']: p for p in merged['projects']}
        self.assertEqual(projects[identity]['local'], local)
        self.assertEqual(projects[identity]['imports']['other'], {'keep': True})
        self.assertEqual(projects[standalone['id']], standalone)
        feed['projects'][0]['description'] = 'Updated upstream description'
        feed['projects'][0]['github']['stars'] = 999
        feed['snapshot_id'] = snapshot_id(feed)
        updated = merge_catalog(merged, feed)
        record = next(p for p in updated['projects'] if p['id'] == identity)
        self.assertEqual(record['local'], local)
        self.assertEqual(record['imports'][PUBLISHER]['github']['stars'], 999)
        self.assertEqual(updated['sources']['other'], {'keep': True})
        empty = copy.deepcopy(feed)
        empty['projects'] = []
        empty['demonstrations'] = []
        empty['snapshot_id'] = snapshot_id(empty)
        removed = merge_catalog(updated, empty)
        self.assertEqual({p['id'] for p in removed['projects']}, {identity, standalone['id']})
        self.assertNotIn(PUBLISHER, next(p for p in removed['projects'] if p['id'] == identity)['imports'])

    def test_format_does_not_require_fpm_or_playground_availability(self):
        feed = copy.deepcopy(self.feed)
        feed['projects'] = feed['projects'][:1]
        feed['demonstrations'] = []
        project = feed['projects'][0]
        project['build_systems'] = ['cmake', 'make']
        project['playground'] = None
        project['curation']['gams_codes'] = []
        feed['snapshot_id'] = snapshot_id(feed)
        self.assertIs(validate_export(feed), feed)

    def test_unknown_versions_duplicate_ids_and_invalid_hierarchy_fail(self):
        for mutate in (
            lambda d: d.update(schema_version=2),
            lambda d: d['projects'].append(copy.deepcopy(d['projects'][0])),
            lambda d: d['projects'][0].update(id='github:different/repo'),
            lambda d: d['projects'][0].update(repository=[]),
            lambda d: d['projects'][0]['curation'].update(gams_codes=['no-such-class']),
            lambda d: d['projects'][0]['curation'].update(gams_codes=['L6']),
            lambda d: d['taxonomies']['gams']['classes']['L6'].update(parent='L6'),
            lambda d: d['projects'][0]['github'].update(stars=True),
            lambda d: d['provenance'].update(inputs_modified=True, source_commit='a' * 40),
        ):
            broken = copy.deepcopy(self.feed)
            mutate(broken)
            broken['snapshot_id'] = snapshot_id(broken)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                validate_export(broken)
        changed = copy.deepcopy(self.feed)
        changed['projects'][0]['description'] = 'Changed without updating snapshot ID'
        with self.assertRaisesRegex(ValueError, 'snapshot_id'):
            validate_export(changed)

    def test_future_deeper_gams_hierarchy_uses_explicit_parents(self):
        feed = copy.deepcopy(self.feed)
        classes = feed['taxonomies']['gams']['classes']
        classes['G1b'] = {'label': 'Multivariate', 'parent': 'G1'}
        feed['projects'][0]['curation']['gams_codes'] = ['G', 'G1', 'G1b']
        feed['snapshot_id'] = snapshot_id(feed)
        validate_export(feed)
        classes['G1']['parent'] = 'G1b'
        feed['snapshot_id'] = snapshot_id(feed)
        with self.assertRaisesRegex(ValueError, 'Cycle'):
            validate_export(feed)

    @unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'optional JSON Schema validator not installed')
    def test_json_schema_matches_generated_export(self):
        from jsonschema import Draft202012Validator, FormatChecker
        schema = json.loads((ROOT / 'catalog' / SCHEMA_NAME).read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(self.feed)

    def test_cli_export_import_and_failed_import_are_atomic(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            exported = subprocess.run([sys.executable, str(ROOT / 'xcatalog_export.py'), '--output-dir', str(directory)],
                                      text=True, capture_output=True, timeout=30)
            self.assertEqual(exported.returncode, 0, exported.stderr)
            self.assertTrue((directory / SCHEMA_NAME).exists())
            catalog = directory / 'merged.json'
            command = [sys.executable, str(ROOT / 'xcatalog_import.py'), '--feed', str(directory / FEED_NAME),
                       '--catalog', str(catalog)]
            imported = subprocess.run(command, text=True, capture_output=True, timeout=30)
            self.assertEqual(imported.returncode, 0, imported.stderr)
            self.assertEqual(len(json.loads(catalog.read_text(encoding='utf-8'))['projects']), len(self.feed['projects']))
            previous = catalog.read_bytes()
            (directory / FEED_NAME).write_text('{"schema_version":999}', encoding='utf-8')
            failed = subprocess.run(command, text=True, capture_output=True, timeout=30)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('existing catalog preserved', failed.stderr)
            self.assertEqual(catalog.read_bytes(), previous)

    def test_import_helpers_work_without_the_playground_source_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name in ('xcatalog_import.py', 'catalog_export.py'):
                (directory / name).write_bytes((ROOT / name).read_bytes())
            publish_export(directory)
            imported = subprocess.run([sys.executable, str(directory / 'xcatalog_import.py'), '--feed',
                                      str(directory / FEED_NAME), '--catalog', str(directory / 'standalone.json')],
                                     cwd=directory, text=True, capture_output=True, timeout=30)
            self.assertEqual(imported.returncode, 0, imported.stderr)

    def test_https_feed_read_and_local_file_read(self):
        with patch('xcatalog_import.urlopen', return_value=BytesIO(canonical_json(self.feed))) as download:
            self.assertEqual(read_feed('https://example.org/catalog-v1.json'), self.feed)
            download.assert_called_once_with('https://example.org/catalog-v1.json', timeout=30)
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            read_feed('http://example.org/catalog-v1.json')


if __name__ == '__main__':
    unittest.main()
