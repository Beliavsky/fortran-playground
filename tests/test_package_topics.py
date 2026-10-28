import json
from pathlib import Path
import tempfile
import unittest

from xpackage_topics import playground_topics, review_text, ROOT, REPORT


class PlaygroundTopicTests(unittest.TestCase):
    def test_catalog_coverage_and_separate_public_topic_sources(self):
        curated = playground_topics()
        packages = json.loads((ROOT / 'site/fpm/packages.json').read_text(encoding='utf-8'))
        author = json.loads((ROOT / 'fpm_catalog/topics.json').read_text(encoding='utf-8'))['repositories']
        self.assertEqual(set(curated), {p['id'] for p in packages})
        for package in packages:
            with self.subTest(package=package['id']):
                self.assertEqual(package['playground_topics'], curated[package['id']])
                self.assertEqual(package['topics'], author[package['repository'].lower()]['topics'])
        self.assertIn('automatic-differentiation', curated['forwarddiff'])
        self.assertIn('sparse-matrices', curated['y12m'])
        self.assertIn('ode', curated['dvode'])

    def test_review_page_is_current_and_lists_every_package_once(self):
        text = review_text()
        self.assertEqual((ROOT / REPORT).read_text(encoding='utf-8'), text)
        for name in playground_topics():
            self.assertEqual(text.count(f'| [{name}](https://github.com/'), 1, name)
        self.assertIn('| Playground topics | GitHub topics |', text)

    def test_validation_rejects_incomplete_or_ambiguous_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_text(json.dumps({'packages': [{'id': 'example'}]}))
            path = root / 'fpm_catalog/playground-topics.json'
            for data in ({'schema': 2, 'packages': {'example': ['ode']}},
                         {'schema': 1, 'packages': {}},
                         {'schema': 1, 'packages': {'example': ['ode'], 'unknown': ['ode']}},
                         *({'schema': 1, 'packages': {'example': topics}} for topics in
                           ([], ['ODE'], ['finite differences'], ['ode', 'ode'], ['-ode'], [None]))):
                with self.subTest(data=data):
                    path.write_text(json.dumps(data))
                    with self.assertRaises(ValueError):
                        playground_topics(root)
            path.write_text(json.dumps({'schema': 1, 'packages': {'example': ['ode', 'adaptive-methods']}}))
            self.assertEqual(playground_topics(root), {'example': ['adaptive-methods', 'ode']})


if __name__ == '__main__':
    unittest.main()
