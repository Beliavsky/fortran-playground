"""Cold-build collections, separate from the verified precompiled catalog."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import threading
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from fpm_sources import Preparer, validate_request as base_validate, github_repository, MAX_EXPANDED

R_REPOSITORY = 'Beliavsky/Fortran-from-R-packages'


def validate_request(payload):
    if not isinstance(payload, dict):
        return base_validate(payload)
    subdirectory = payload.get('subdirectory', '')
    if (not isinstance(subdirectory, str) or len(subdirectory) > 200
            or (subdirectory and (not re.fullmatch(r'[A-Za-z0-9_.-]+', subdirectory)
                                  or subdirectory in {'.', '..'}))):
        raise ValueError('Choose a top-level package directory.')
    result = base_validate({k: v for k, v in payload.items() if k != 'subdirectory'})
    if subdirectory:
        if github_repository(result['url']).lower() != R_REPOSITORY.lower():
            raise ValueError('Package subdirectories are currently supported for the translated R collection only.')
        result['subdirectory'] = subdirectory
    return result


def raw_fetch(url, *, limit, timeout):
    with urlopen(Request(url, headers={'User-Agent': 'Fortran-playground-FPM'}), timeout=timeout) as response:
        if urlsplit(response.url).hostname != 'raw.githubusercontent.com':
            raise ValueError('Unexpected source redirect.')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Source file exceeds its size limit.')
    return data


class TranslatedRPreparer(Preparer):
    """Fetch Git trees and verified blobs, without executing repository scripts."""
    def __init__(self, *args, raw_downloader=raw_fetch, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_downloader = raw_downloader
        self.source_lock = threading.Lock()
        self.hydrated = set()
        self.file_count = 0
        self.expanded_bytes = 0

    def hydrate(self, name):
        if name in self.hydrated:
            return
        entry = self.top_trees.get(name)
        if not entry:
            raise ValueError(f'{name}: no package directory at the selected revision.')
        tree = json.loads(self.download(f'https://api.github.com/repos/{R_REPOSITORY}/git/trees/{entry}?recursive=1', 4 * 1024 * 1024))
        if tree.get('truncated'):
            raise ValueError('Package source tree exceeds the retrieval limit.')
        files = []
        for item in tree['tree']:
            path = PurePosixPath(item['path'])
            if (path.is_absolute() or any(p in {'..', '.'} for p in path.parts)
                    or not path.parts or re.search(r'[\\:\x00]', item['path'])):
                raise ValueError('Unsafe package source path.')
            if item['type'] == 'tree':
                continue
            if item['type'] != 'blob' or item.get('mode') not in {'100644', '100755'}:
                raise ValueError('Source links and submodules are not supported.')
            if path.parts[0] in {'build', '.git'} or path.name == 'fpm.lock':
                continue
            size = item.get('size', -1)
            if not isinstance(size, int) or not 0 <= size <= 16 * 1024 * 1024:
                raise ValueError('Package source file exceeds its size limit.')
            self.expanded_bytes += size
            self.file_count += 1
            if self.expanded_bytes > MAX_EXPANDED or self.file_count > 10000:
                raise ValueError('Selected package sources exceed 64 MiB / 10000 files.')
            files.append(item)
        destination = self.r_root / name

        def retrieve(item):
            import time
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('Package preparation exceeded its time limit.')
            url = f'https://raw.githubusercontent.com/{R_REPOSITORY}/{self.commit}/{quote(name)}/{quote(item["path"], safe="/")}'
            data = self.raw_downloader(url, limit=item['size'], timeout=min(15, remaining))
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if len(data) != item['size'] or digest != item['sha']:
                raise ValueError('Package source checksum mismatch.')
            with self.source_lock:
                self.download_bytes += len(data)
                if self.download_bytes > 32 * 1024 * 1024:
                    raise ValueError('Combined package downloads exceed 32 MiB.')
            target = destination / item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(retrieve, files))
        self.hydrated.add(name)

    def manifest(self, root, *, development=False):
        root = Path(root).resolve()
        if root.is_relative_to(self.r_root):
            relative = root.relative_to(self.r_root)
            if not relative.parts:
                raise ValueError('Select a package directory, not the collection root.')
            self.hydrate(relative.parts[0])
        super().manifest(root, development=development)

    def prepare(self, payload):
        payload = validate_request(payload)
        revision = payload['revision']
        self.commit = revision if re.fullmatch('[a-f0-9]{40}', revision) else json.loads(self.download(
            f'https://api.github.com/repos/{R_REPOSITORY}/commits/{quote(revision or "HEAD", safe="")}', 1024 * 1024))['sha']
        if not re.fullmatch('[a-f0-9]{40}', self.commit):
            raise ValueError('Invalid collection commit.')
        tree = json.loads(self.download(f'https://api.github.com/repos/{R_REPOSITORY}/git/trees/{self.commit}', 1024 * 1024))
        if tree.get('truncated'):
            raise ValueError('Collection tree is incomplete.')
        self.top_trees = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'tree'}
        self.r_root = (self.directory / 'r').resolve()
        self.r_root.mkdir(parents=True)
        self.repositories[(R_REPOSITORY.lower(), self.commit)] = self.r_root
        self.records.append({'repository': R_REPOSITORY, 'revision': self.commit,
                             'subdirectory': payload['subdirectory']})
        root = self.r_root / payload['subdirectory']
        self.manifest(root, development=payload['workflow'] == 'package')
        return root.relative_to(self.directory).as_posix(), self.records


def source_preparer(directory, payload, **kwargs):
    return (TranslatedRPreparer if payload.get('subdirectory') else Preparer)(directory, **kwargs)
