import asyncio
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from fpm_api import Service, ServiceError
from fpm_sources import Preparer, extract_archive, github_repository, validate_request


def archive(files):
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as stream:
        for name, text in files.items():
            member = tarfile.TarInfo('repo/' + name)
            content = text.encode()
            member.size = len(content)
            member.mode = 0o644
            stream.addfile(member, BytesIO(content))
    return buffer.getvalue()


PAYLOAD = {'url': 'https://github.com/example/library', 'source': 'program main\nend program'}


class SourceTests(unittest.TestCase):
    def test_urls_and_requests(self):
        self.assertEqual(github_repository('https://github.com/owner/repo.git/'), 'owner/repo')
        for value in ['http://github.com/a/b', 'https://github.com@127.0.0.1/a/b',
                      'https://github.com/a/b/tree/main', 'https://github.com/a/..',
                      'file:///etc/passwd', 'https://github.com/a/b?x=1']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                github_repository(value)
        self.assertEqual(validate_request(PAYLOAD)['action'], 'run')
        for change in [{'source': ''}, {'source': 'x' * 100001}, {'stdin': '\0'},
                       {'action': 'install'}, {'target': '--runner'}, {'source': 42}, {'extra': 1}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_request({**PAYLOAD, **change})
        self.assertEqual(validate_request({**PAYLOAD, 'workflow': 'package', 'action': 'test', 'source': ''})['action'], 'test')

    def test_archive_rejects_unsafe_paths_duplicates_links_and_expansion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertTrue((extract_archive(archive({'fpm.toml': 'name="demo"'}), root / 'ok') / 'fpm.toml').exists())
            for path in ['../escape', '/absolute', 'folder\\escape', 'C:/escape']:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    extract_archive(archive({path: 'bad'}), root / 'bad')
            buffer = BytesIO()
            with tarfile.open(fileobj=buffer, mode='w:gz') as stream:
                member = tarfile.TarInfo('repo/link')
                member.type = tarfile.SYMTYPE
                member.linkname = '/etc/passwd'
                stream.addfile(member)
            with self.assertRaises(ValueError):
                extract_archive(buffer.getvalue(), root / 'bad')

    def preparer(self, temporary, manifests):
        captured = []

        def writer(value):
            captured.append(deepcopy(value))
            # Tests inspect rewritten dependency tables directly. Repeated
            # manifests hit the resolver's memoization before being read again.
            return 'name = ' + json.dumps(value['name']) + '\n'

        def download(url, **kwargs):
            if '/commits/' in url:
                return json.dumps({'sha': 'a' * 40}).encode()
            repo = url.split('codeload.github.com/')[1].split('/tar.gz/')[0]
            return archive(manifests[repo])

        return Preparer(temporary, downloader=download, writer=writer), captured

    def test_transitive_and_target_dependencies_pinned_and_rewritten(self):
        manifests = {
            'example/library': {'fpm.toml': 'name="library"\n[dependencies]\nhelper={git="https://github.com/example/helper",tag="v1"}\n'
                               '[[test]]\nname="checks"\n[test.dependencies]\nhelper={git="https://github.com/example/helper",tag="v1"}'},
            'example/helper': {'fpm.toml': 'name="helper"\n[dependencies]\nbase={path="nested"}',
                               'nested/fpm.toml': 'name="base"'},
        }
        with tempfile.TemporaryDirectory() as temporary:
            preparer, captured = self.preparer(temporary, manifests)
            root, records = preparer.prepare({**PAYLOAD, 'workflow': 'package', 'action': 'test'})
            self.assertEqual(len(records), 2)
            self.assertTrue(all(record['revision'] == 'a' * 40 for record in records))
            library = next(item for item in captured if item['name'] == 'library')
            self.assertIn('path', library['dependencies']['helper'])
            self.assertIn('path', library['test'][0]['dependencies']['helper'])
            self.assertNotIn('git', library['dependencies']['helper'])

    def test_consumer_ignores_development_dependencies_and_rejects_registry_and_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            preparer, captured = self.preparer(temporary, {'example/library': {'fpm.toml':
                'name="library"\n[dev-dependencies]\nunused="*"'}})
            preparer.prepare(PAYLOAD)
            self.assertNotIn('dev-dependencies', captured[-1])
        for dependency in ['thing="*"', 'thing={path="../../../../outside"}', 'thing={git="https://evil.example/code"}',
                           'thing={git="https://github.com/example/library"}']:
            with tempfile.TemporaryDirectory() as temporary:
                preparer, _ = self.preparer(temporary, {'example/library': {'fpm.toml':
                    'name="library"\n[dependencies]\n' + dependency}})
                with self.subTest(dependency=dependency), self.assertRaises(ValueError):
                    preparer.prepare(PAYLOAD)


class MemoryStore:
    def __init__(self): self.data = {}
    async def get(self, key, default): return deepcopy(self.data.get(key, default))
    async def put(self, key, value): self.data[key] = deepcopy(value)
    async def pop(self, key): self.data.pop(key, None)


class Runner:
    def __init__(self): self.calls = {}; self.result = None
    async def start(self, identifier, payload):
        self.calls[identifier] = payload
        return identifier
    async def poll(self, identifier): return self.result


class AdmissionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store, self.runner, self.now = MemoryStore(), Runner(), 100000
        self.service = Service(self.store, self.runner, clock=lambda: self.now)

    async def test_two_slots_completion_releases_slot_and_cancel_does_not_release_early(self):
        first, second = await asyncio.gather(self.service.submit('a', PAYLOAD), self.service.submit('b', PAYLOAD))
        await self.service.job(first['id'], cancel=True)
        self.assertTrue(self.store.data['cancel:' + first['id']])
        with self.assertRaises(ServiceError) as error:
            await self.service.submit('c', PAYLOAD)
        self.assertEqual(error.exception.status, 429)
        self.runner.result = {'ok': True, 'stages': []}
        result = await self.service.job(second['id'])
        self.assertEqual(result['state'], 'done')
        await self.service.submit('c', PAYLOAD)

    async def test_address_and_daily_limits_owner_and_expiration(self):
        self.runner.result = {'ok': True, 'stages': []}
        for _ in range(30):
            await self.service.submit('same', PAYLOAD)
        with self.assertRaises(ServiceError):
            await self.service.submit('same', PAYLOAD)
        self.now += 601
        await self.service.submit('same', PAYLOAD)
        board = self.store.data['board']
        board['daily'] = 100
        with self.assertRaises(ServiceError):
            await self.service.submit('another', PAYLOAD)
        self.service.owner_key = 'private-owner-key'
        job = await self.service.submit('owner', PAYLOAD, 'private-owner-key')
        self.assertEqual(self.store.data['board']['daily'], 100)
        with self.assertRaises(ServiceError):
            await self.service.job('x' * 43)
        self.now += 1801
        with self.assertRaises(ServiceError):
            await self.service.job(job['id'])


if __name__ == '__main__':
    unittest.main()
