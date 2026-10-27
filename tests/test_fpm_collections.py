import hashlib
import json
from pathlib import Path
import tempfile
import tomllib
import unittest

from fpm_collections import R_REPOSITORY, PortablePreparer, TranslatedRPreparer, source_preparer, validate_request
from fpm_sources import Preparer

COMMIT = 'a' * 40
PAYLOAD = {'url': 'https://github.com/' + R_REPOSITORY, 'revision': COMMIT,
           'subdirectory': 'sample', 'workflow': 'package', 'action': 'run'}


def fixture(dependency='../shared', mode='100644', corrupt=False):
    files = {'sample': {'fpm.toml': f'name="sample"\n[dependencies]\nshared={{path="{dependency}"}}\n',
                        'app/main.f90': 'program main\nuse shared\nprint *, answer\nend program\n'},
             'shared': {'fpm.toml': 'name="shared"\n',
                        'src/shared.f90': 'module shared\ninteger, parameter :: answer=42\nend module\n'},
             'unused': {'fpm.toml': 'name="unused"\n'}}
    trees = {name: hashlib.sha1(name.encode()).hexdigest() for name in files}
    requested = []

    def api(url, **kwargs):
        requested.append(url)
        ref = url.split('/git/trees/')[1].split('?')[0]
        if ref == COMMIT:
            value = {'tree': [{'path': name, 'type': 'tree', 'sha': sha} for name, sha in trees.items()]}
        else:
            name = next(name for name, sha in trees.items() if sha == ref)
            value = {'tree': [{'path': path, 'type': 'blob', 'mode': mode, 'size': len(text.encode()),
                               'sha': hashlib.sha1(b'blob ' + str(len(text.encode())).encode() + b'\0' + text.encode()).hexdigest()}
                              for path, text in files[name].items()]}
        return json.dumps(value).encode()

    def raw(url, **kwargs):
        requested.append(url)
        name, path = url.split(COMMIT + '/')[1].split('/', 1)
        return b'corrupt' if corrupt else files[name][path].encode()
    return api, raw, requested


class CollectionTests(unittest.TestCase):
    def test_selected_sources_and_recursive_siblings_only(self):
        api, raw, requested = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            prep = TranslatedRPreparer(temporary, downloader=api, raw_downloader=raw)
            relative, records = prep.prepare(PAYLOAD)
            root = Path(temporary) / relative
            manifest = tomllib.loads((root / 'fpm.toml').read_text())
            self.assertEqual(manifest['dependencies']['shared']['path'], '../shared')
            self.assertTrue((root.parent / 'shared/src/shared.f90').exists())
            self.assertFalse((root.parent / 'unused').exists())
            self.assertEqual(records[0]['revision'], COMMIT)
            self.assertFalse(any('/unused/' in url for url in requested))

    def test_reject_unsafe_paths_links_checksums(self):
        for kwargs, message in [({'dependency': '../../escape'}, 'leaves its repository'),
                                ({'mode': '120000'}, 'links'), ({'corrupt': True}, 'checksum')]:
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory() as temporary:
                api, raw, _ = fixture(**kwargs)
                with self.assertRaisesRegex(ValueError, message):
                    TranslatedRPreparer(temporary, downloader=api, raw_downloader=raw).prepare(PAYLOAD)

    def test_validation_and_existing_preparer(self):
        self.assertEqual(validate_request(PAYLOAD)['subdirectory'], 'sample')
        for value in ['..', '../sample', '/sample', 'C:\\sample', '.', 'a/b']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_request({**PAYLOAD, 'subdirectory': value})
        with self.assertRaises(ValueError):
            validate_request({**PAYLOAD, 'url': 'https://github.com/example/other'})
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIs(type(source_preparer(temporary, {})), PortablePreparer)
            self.assertIsInstance(source_preparer(temporary, {}), Preparer)
            self.assertIsInstance(source_preparer(temporary, PAYLOAD), TranslatedRPreparer)

    def test_local_compaction_preserves_subdirectory_and_sibling(self):
        from local_fpm_catalog import compact_sources
        api, raw, _ = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            prep = TranslatedRPreparer(directory, downloader=api, raw_downloader=raw)
            relative, _ = prep.prepare(PAYLOAD)
            original = directory / relative
            mapping = compact_sources(directory, prep.repositories.values())
            container = next(p for p in mapping if original.is_relative_to(p))
            root = mapping[container] / original.relative_to(container)
            self.assertTrue((root / 'fpm.toml').exists())
            self.assertTrue((root / '../shared/fpm.toml').resolve().exists())

    def test_catalog_metadata_is_separate_and_pinned(self):
        root = Path(__file__).resolve().parents[1]
        packages = json.loads((root / 'site/fpm/translated-r.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(packages), 596)
        self.assertEqual(len({p['id'] for p in packages}), len(packages))
        for package in packages:
            self.assertEqual(package['repository'], R_REPOSITORY)
            self.assertRegex(package['revision'], '^[a-f0-9]{40}$')
            self.assertTrue(package['description'])
            self.assertEqual(package['subdirectory'], package['id'])
            self.assertNotIn('archive_sha256', package)


if __name__ == '__main__':
    unittest.main()
