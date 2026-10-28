import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from io import StringIO

from xgithub_topics import refresh, TopicParser, github_metadata


class TopicTests(unittest.TestCase):
    def test_repository_api_reads_topics_and_stars_together(self):
        with patch('xgithub_topics.urlopen', return_value=StringIO(json.dumps(
                {'topics': ['fortran'], 'stargazers_count': 1234}))) as request:
            self.assertEqual(github_metadata('owner/repo'), {'topics': ['fortran'], 'stars': 1234})
            self.assertEqual(request.call_args.args[0].full_url, 'https://api.github.com/repos/owner/repo')

    def test_refresh_deduplicates_repositories_and_keeps_empty_topic_lists(self):
        requests = []
        def fetch(repository):
            requests.append(repository)
            return ['ode', 'fortran', 'ode'] if repository == 'owner/solver' else []
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'topics.json'
            data = refresh([{'repository': 'Owner/Solver'}, {'repository': 'owner/solver'},
                            {'repository': 'owner/other'}], path, fetch_topics=fetch)
            self.assertEqual(sorted(requests), ['owner/other', 'owner/solver'])
            self.assertEqual(data['repositories']['owner/solver']['topics'], ['fortran', 'ode'])
            self.assertEqual(data['repositories']['owner/other']['topics'], [])
            self.assertEqual(json.loads(path.read_text()), data)

    def test_failed_refresh_preserves_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'topics.json'
            path.write_bytes(b'previous complete snapshot')
            def fail(repository):
                raise OSError('rate limit')
            with self.assertRaises(OSError):
                refresh([{'repository': 'owner/repo'}], path, fetch_topics=fail)
            self.assertEqual(path.read_bytes(), b'previous complete snapshot')
            with self.assertRaises(ValueError):
                refresh([{'repository': 'owner/repo'}], path, fetch_topics=lambda repo: ['bad topic'])
            self.assertEqual(path.read_bytes(), b'previous complete snapshot')

    def test_public_page_parser_uses_topic_labels_not_readme_links(self):
        parser = TopicParser()
        parser.feed('<a href="/topics/unrelated">README link</a>'
                    '<a class="prc-TopicTag-TopicTag-ab" href="/topics/ode">ode</a>'
                    '<a href="/topics/fortran" class="topic-tag topic-tag-link">fortran</a>')
        self.assertEqual(parser.topics, {'ode', 'fortran'})

    def test_exact_stars_from_embedded_repository_metadata_and_legacy_counter(self):
        parser = TopicParser()
        parser.feed('<script type="application/json">' + json.dumps({'payload': {'sidebarAbout': {
            'topics': [{'name': 'ode'}], 'stargazerCount': 1234}}}) + '</script>')
        self.assertEqual(parser.stars, 1234)
        self.assertEqual(parser.topics, {'ode'})
        legacy = TopicParser()
        legacy.feed('<span id="repo-stars-counter-star" title="1,234">1.2k</span>')
        self.assertEqual(legacy.stars, 1234)
        unrelated = TopicParser()
        unrelated.feed('<p>"stargazerCount":99999</p><span>1.2k stars</span>')
        self.assertIsNone(unrelated.stars)

    def test_metadata_refresh_validates_counts_and_preserves_snapshot_on_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'topics.json'
            packages = [{'repository': 'owner/repo'}]
            data = refresh(packages, path, fetch_metadata=lambda repo: {'topics': ['fortran'], 'stars': 0})
            self.assertEqual(data['repositories']['owner/repo']['stars'], 0)
            self.assertEqual(data['repositories']['owner/repo']['stars_updated_at'], data['retrieved_at'])
            previous = path.read_bytes()
            for invalid in (-1, True, '123', 1.5, None):
                with self.subTest(stars=invalid), self.assertRaises(ValueError):
                    refresh(packages, path, fetch_metadata=lambda repo: {'topics': [], 'stars': invalid})
                self.assertEqual(path.read_bytes(), previous)

    def test_generated_catalog_uses_saved_topics_without_changing_pins(self):
        root = Path(__file__).resolve().parents[1]
        saved = json.loads((root / 'fpm_catalog/topics.json').read_text())['repositories']
        generated = json.loads((root / 'site/fpm/packages.json').read_text())
        original = json.loads((root / 'fpm_catalog.json').read_text())['packages']
        self.assertEqual(set(saved), {p['repository'].lower() for p in original})
        for package in original:
            entry = next(p for p in generated if p['id'] == package['id'])
            self.assertEqual(entry['topics'], saved[package['repository'].lower()]['topics'])
            metadata = saved[package['repository'].lower()]
            for field in ('stars', 'stars_updated_at'):
                self.assertEqual(entry.get(field), metadata.get(field))
            for field in ('revision', 'archive_sha256', 'dependencies'):
                self.assertEqual(entry.get(field), package.get(field))


if __name__ == '__main__':
    unittest.main()
