import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from catalog_reviews import (PUBLISHER, SNAPSHOT, OVERRIDES, digest, validate_feed,
                             select_reviews, matching_review, load_reviews)
from xcatalog_reviews import refresh


def fixture():
    pin = 'a'*40
    source = {'path': 'src/solver.f90', 'url': 'https://github.com/example/solver/blob/'+pin+'/src/solver.f90',
              'sha256': 'b'*64}
    procedure = {'procedure': 'solve', 'role': 'public-entry-point', 'module': 'solver_mod',
                 'path': source['path'], 'line_start': 10, 'line_end': 30,
                 'signature': 'CALL solve(A,B)', 'summary': 'Scoped solver.',
                 'declarations': [{'path': source['path'], 'line_start': 11, 'line_end': 15}]}
    review = {'id': 'github:example/solver', 'repository': {'owner': 'example', 'name': 'solver',
              'url': 'https://github.com/example/solver'},
              'license': {'label': 'MIT scoped review', 'spdx_expression': 'MIT', 'revision': pin,
                          'reviewed_on': '2026-11-07', 'notes': 'License scope.', 'evidence': [source]},
              'classifications': [{'code': 'D2a1', 'level': 'source-reviewed', 'revision': pin,
                  'reviewed_on': '2026-11-07', 'notes': 'Only this interface was reviewed.',
                  'evidence': [source], 'procedures': [procedure]}]}
    feed = {'schema_version': 1, 'publisher': PUBLISHER,
            'source_repository': 'https://github.com/Beliavsky/fortran-gams-catalog', 'projects': [review]}
    feed['snapshot_id'] = digest(feed)
    packages = [{'id': 'solver', 'repository': 'EXAMPLE/Solver', 'revision': pin}]
    return feed, packages


class ReviewImportTests(unittest.TestCase):
    def test_exact_identity_and_pin_preserve_input_and_report_other_cases(self):
        feed, packages = fixture()
        original = copy.deepcopy(feed)
        packages += [{'id': 'fork', 'repository': 'another/solver', 'revision': 'a'*40},
                     {'id': 'stale', 'repository': 'example/solver', 'revision': 'c'*40}]
        result = select_reviews(feed, packages)
        self.assertEqual(set(result['packages']), {'solver'})
        self.assertEqual(result['report']['matched'], ['solver'])
        self.assertEqual(result['report']['no_independent_review'], ['fork'])
        self.assertEqual(result['report']['revision_mismatches'][0]['package_id'], 'stale')
        self.assertEqual(feed, original)
        project = {'id': 'github:example/solver', 'playground': {'package_id': 'solver', 'package_revision': 'c'*40}}
        self.assertIsNone(matching_review(project, result['packages']))

    def test_partial_match_never_silently_imports_stale_license(self):
        feed, packages = fixture()
        feed['projects'][0]['license']['revision'] = 'c'*40
        feed['projects'][0]['license']['evidence'] = [{**feed['projects'][0]['license']['evidence'][0],
            'url': 'https://github.com/example/solver/blob/'+'c'*40+'/src/solver.f90'}]
        feed['snapshot_id'] = digest(feed)
        result = select_reviews(feed, packages)
        self.assertIsNone(result['packages']['solver']['license'])
        self.assertEqual(len(result['report']['revision_mismatches']), 1)

    def test_invalid_refresh_is_atomic_and_transport_rejects_http(self):
        feed, packages = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'feed.json';target = Path(tmp)/'saved.json'
            source.write_text(json.dumps(feed), encoding='utf-8')
            refresh(str(source), target, packages)
            saved = target.read_bytes()
            feed['projects'][0]['classifications'][0]['procedures'][0]['declarations'][0]['line_end'] = -1
            feed['snapshot_id'] = digest(feed)
            source.write_text(json.dumps(feed), encoding='utf-8')
            with self.assertRaises(ValueError):
                refresh(str(source), target, packages)
            self.assertEqual(saved, target.read_bytes())
            with self.assertRaises(ValueError):
                refresh('http://example.com/reviews.json', target, packages)

    def test_imported_execution_claims_and_changed_hash_are_rejected(self):
        feed, _ = fixture()
        feed['projects'][0]['classifications'][0]['procedures'][0]['local_driver'] = {}
        feed['snapshot_id'] = digest(feed)
        with self.assertRaises(ValueError):
            validate_feed(feed)
        with self.assertRaises(ValueError):
            validate_feed([])
        feed, _ = fixture()
        feed['projects'][0]['license']['label'] = 'Changed without hash'
        with self.assertRaises(ValueError):
            validate_feed(feed)

    def test_local_overrides_survive_refresh_and_can_hide_a_review(self):
        feed, packages = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);snapshot = root/SNAPSHOT;override = root/OVERRIDES
            snapshot.parent.mkdir(parents=True)
            source = root/'feed.json';source.write_text(json.dumps(feed), encoding='utf-8')
            refresh(str(source), snapshot, packages)
            override.write_text(json.dumps({'schema_version': 1, 'packages': {'solver': None}}), encoding='utf-8')
            refresh(str(source), snapshot, packages)
            self.assertEqual(load_reviews(root), {})
            replacement = copy.deepcopy(feed['projects'][0]);replacement['license']['notes'] = 'Local correction.'
            override.write_text(json.dumps({'schema_version': 1, 'packages': {'solver': replacement}}), encoding='utf-8')
            self.assertEqual(load_reviews(root)['solver']['license']['notes'], 'Local correction.')

    def test_rendering_is_scoped_and_does_not_add_a_checked_driver(self):
        from catalog_export import build_export
        from xgams_site import generate_gams_site
        feed, _ = fixture()
        exported = build_export()
        project = copy.deepcopy(next(p for p in exported['projects'] if p['name'] == 'stdlib'))
        review = feed['projects'][0]
        review['id'] = project['id'];review['repository'] = project['repository']
        pin = project['playground']['package_revision']
        review['license']['revision'] = pin
        for item in review['license']['evidence']:
            item['url'] = project['repository']['url']+'/blob/'+pin+'/'+item['path']
        for claim in review['classifications']:
            claim['revision'] = pin
        exported['projects'] = [project]
        exported['demonstrations'] = []
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            with patch('urllib.request.urlopen', side_effect=AssertionError('Build must be offline')):
                generate_gams_site(destination, exported, reviews={'stdlib': review})
            package = (destination/'packages/stdlib/index.html').read_text(encoding='utf-8')
            self.assertIn('<h2>Calling sequences</h2>', package)
            self.assertIn('solver_mod::solve', package)
            self.assertIn('src/solver.f90#L11-L15', package)
            self.assertIn('MIT scoped review', package)
            self.assertNotIn('Checked drivers:', package)
            matching = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            other = (destination/'G1a1a/index.html').read_text(encoding='utf-8')
            self.assertIn('solver_mod::solve', matching)
            self.assertIn('solver_mod::solve', matching.split('data-search="', 1)[1].split('"', 1)[0])
            self.assertNotIn('solver_mod::solve', other)
            # Link only an existing checked example for this interface and scope.
            native = project['curation']['procedures'][0]
            native.update(module='solver_mod', procedure='solve', gams_codes=['D2a1'])
            template = build_export()['demonstrations'][0]
            selected = {**template, 'id': 'test-matching', 'name': 'test-matching',
                        'package_id': 'stdlib', 'procedure_id': native['id'],
                        'gams_code': 'D2a1', 'url': 'https://example.org/matching'}
            unrelated = {**selected, 'id': 'test-other', 'name': 'test-other',
                         'gams_code': 'G1b1b', 'url': 'https://example.org/other'}
            exported['demonstrations'] = [selected, unrelated]
            generate_gams_site(destination, exported, reviews={'stdlib': review})
            package = (destination/'packages/stdlib/index.html').read_text(encoding='utf-8')
            calls = package.split('<h2>Calling sequences</h2>', 1)[1].split('</section>', 1)[0]
            self.assertIn('Open checked example in playground: test-matching', calls)
            self.assertIn('https://example.org/matching', calls)
            self.assertNotIn('https://example.org/other', calls)


if __name__ == '__main__':
    unittest.main()
