import json
from pathlib import Path
import tempfile
import unittest

from xgithub_topics import refresh, TopicParser


class TopicTests(unittest.TestCase):
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

    def test_generated_catalog_uses_saved_topics_without_changing_pins(self):
        root = Path(__file__).resolve().parents[1]
        saved = json.loads((root / 'fpm_catalog/topics.json').read_text())['repositories']
        generated = json.loads((root / 'site/fpm/packages.json').read_text())
        original = json.loads((root / 'fpm_catalog.json').read_text())['packages']
        self.assertEqual(set(saved), {p['repository'].lower() for p in original})
        for package in original:
            entry = next(p for p in generated if p['id'] == package['id'])
            self.assertEqual(entry['topics'], saved[package['repository'].lower()]['topics'])
            for field in ('revision', 'archive_sha256', 'dependencies'):
                self.assertEqual(entry.get(field), package.get(field))


if __name__ == '__main__':
    unittest.main()
