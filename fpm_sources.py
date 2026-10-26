"""Bounded GitHub-only FPM source preparation. Never executes package commands."""
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import time
import tomllib
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

MAX_ARCHIVE = 16 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
MAX_FILES = 10000
MAX_PACKAGES = 12


def github_repository(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError('Supply a public GitHub repository URL.')
    url = urlsplit(value)
    parts = url.path.strip('/').split('/')
    if (url.scheme != 'https' or url.netloc.lower() != 'github.com' or url.query or url.fragment
            or len(parts) != 2 or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) for part in parts)):
        raise ValueError('Use https://github.com/OWNER/REPOSITORY and enter the revision separately.')
    repository = '/'.join(parts).removesuffix('.git')
    if any(part in {'.', '..', ''} for part in repository.split('/')):
        raise ValueError('Invalid GitHub repository.')
    return repository


def validate_request(payload):
    if not isinstance(payload, dict) or set(payload) - {'url', 'revision', 'workflow', 'action', 'target', 'source', 'stdin'}:
        raise ValueError('Invalid FPM request.')
    github_repository(payload.get('url'))
    defaults = {'revision': '', 'workflow': 'consumer', 'action': 'run', 'target': '', 'source': '', 'stdin': ''}
    result = {**defaults, **payload}
    for key in defaults:
        if not isinstance(result[key], str):
            raise ValueError(f'{key} must be text.')
    if result['workflow'] not in {'consumer', 'package'} or result['action'] not in {'build', 'run', 'test'}:
        raise ValueError('Choose a supported workflow and action.')
    if result['workflow'] == 'consumer' and result['action'] == 'test':
        raise ValueError('Test applies to the package workflow.')
    if not re.fullmatch(r'[A-Za-z0-9_./-]{0,200}', result['revision']):
        raise ValueError('Invalid revision: use a branch, tag, or commit.')
    if result['target'] and not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}', result['target']):
        raise ValueError('Invalid application or test target name.')
    for key in ('source', 'stdin'):
        if len(result[key].encode('utf-8')) > 100000 or '\x00' in result[key]:
            raise ValueError(f'{key} exceeds 100 KB or contains a NUL character.')
    if result['workflow'] == 'consumer' and not result['source'].strip():
        raise ValueError('Enter a main program that uses the package.')
    return result


def extract_archive(data, destination, *, require_manifest=True):
    """Extract regular files only; validate the entire archive before writing."""
    if len(data) > MAX_ARCHIVE:
        raise ValueError('Package download exceeds 16 MiB.')
    with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as archive:
        members = []
        size = 0
        roots = set()
        seen = set()
        for member in archive:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or '..' in path.parts or not path.parts or '\\' in member.name
                    or ':' in member.name or not (member.isfile() or member.isdir())):
                raise ValueError('Package archive contains an unsafe path, link, or special file.')
            if path in seen or member.size > 16 * 1024 * 1024 or member.size < 0:
                raise ValueError('Package archive contains duplicate or oversized files.')
            seen.add(path)
            size += member.size
            members.append(member)
            roots.add(path.parts[0])
            if size > MAX_EXPANDED or len(members) > MAX_FILES:
                raise ValueError('Package archive exceeds the 64 MiB / 10000-entry limit.')
        if len(roots) != 1:
            raise ValueError('Expected one package archive root.')
        destination.mkdir(parents=True, exist_ok=True)
        archive.extractall(destination, members=members, filter='data')
    root = destination / roots.pop()
    if require_manifest and not (root / 'fpm.toml').is_file():
        raise ValueError('This repository has no fpm.toml at its root.')
    return root


def fetch(url, limit=MAX_ARCHIVE, timeout=15):
    # URLs are constructed here, never accepted verbatim from dependency tables.
    request = Request(url, headers={'User-Agent': 'Fortran-playground-FPM', 'Accept': 'application/vnd.github+json'})
    with urlopen(request, timeout=timeout) as response:
        if urlsplit(response.url).hostname not in {'api.github.com', 'codeload.github.com'}:
            raise ValueError('Unexpected source download redirect.')
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError('Source download exceeds its size limit.')
    return content


class Preparer:
    def __init__(self, directory, *, downloader=fetch, writer=None):
        self.directory = Path(directory).resolve()
        self.downloader = downloader
        self.writer = writer
        self.records = []
        self.repositories = {}
        self.visiting = set()
        self.prepared = set()
        self.deadline = time.monotonic() + 60
        self.download_bytes = 0

    def download(self, url, limit=MAX_ARCHIVE):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError('Package preparation exceeded 60 seconds.')
        data = self.downloader(url, limit=limit, timeout=min(15, remaining))
        self.download_bytes += len(data)
        if self.download_bytes > 32 * 1024 * 1024:
            raise ValueError('Combined package downloads exceed 32 MiB.')
        return data

    def repository(self, url, revision='', *, development=False):
        repo = github_repository(url)
        key = (repo.lower(), revision)
        if key in self.repositories:
            root = self.repositories[key]
            self.manifest(root, development=development)
            return root
        if len(self.records) >= MAX_PACKAGES:
            raise ValueError('Dependency graph exceeds 12 repositories.')
        ref = quote(revision or 'HEAD', safe='')
        commit = json.loads(self.download(f'https://api.github.com/repos/{repo}/commits/{ref}', 1024 * 1024))['sha']
        if not re.fullmatch('[a-f0-9]{40}', commit):
            raise ValueError('GitHub returned an invalid commit.')
        data = self.download(f'https://codeload.github.com/{repo}/tar.gz/{commit}')
        container = self.directory / 'packages' / str(len(self.records))
        root = extract_archive(data, container).resolve()
        paths = list(self.directory.rglob('*'))
        if len(paths) > 20000 or sum(p.stat().st_size for p in paths if p.is_file()) > MAX_EXPANDED:
            raise ValueError('Combined dependency sources exceed 64 MiB / 20000 entries.')
        self.repositories[key] = root
        import hashlib
        self.records.append({'repository': repo, 'revision': commit, 'sha256': hashlib.sha256(data).hexdigest()})
        # Never import upstream objects or dependency locks into a clean build.
        shutil.rmtree(root / 'build', ignore_errors=True)
        (root / 'fpm.lock').unlink(missing_ok=True)
        self.manifest(root, development=development)
        return root

    def manifest(self, root, *, development=False):
        root = root.resolve()
        key = (root, development)
        if key in self.prepared or (root, True) in self.prepared:
            return
        if root in self.visiting:
            raise ValueError('Cyclic package dependencies are not supported.')
        if len(self.prepared) + len(self.visiting) >= 32:
            raise ValueError('Too many package manifests.')
        self.visiting.add(root)
        shutil.rmtree(root / 'build', ignore_errors=True)
        (root / 'fpm.lock').unlink(missing_ok=True)
        original = root / 'fpm.toml'
        text = original.read_text(encoding='utf-8')
        if len(text.encode()) > 1000000:
            raise ValueError('Package manifest is too large.')
        manifest = tomllib.loads(text)
        if not isinstance(manifest.get('name'), str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_-]*', manifest['name']):
            raise ValueError('Invalid FPM package name.')
        # FPM can inspect development dependencies during build/run as well.
        # Only package workflow retains them; library consumers do not need them.
        if not development:
            manifest.pop('dev-dependencies', None)
        tables = [manifest.get('dependencies', {})]
        if development:
            tables.append(manifest.get('dev-dependencies', {}))
            for kind in ('test', 'executable', 'example'):
                for target in manifest.get(kind, []):
                    tables.append(target.get('dependencies', {}))
        for table in tables:
            if not isinstance(table, dict):
                raise ValueError('Invalid dependency table.')
            for name, spec in table.items():
                if not isinstance(spec, dict) or not ({'git', 'path'} & spec.keys()):
                    raise ValueError(f'{name}: registry dependencies and metapackages are not supported yet; use a GitHub git dependency.')
                if 'git' in spec:
                    if set(spec) - {'git', 'branch', 'tag', 'rev', 'preprocess'} or 'path' in spec:
                        raise ValueError(f'{name}: unsupported git dependency settings.')
                    refs = [spec[k] for k in ('branch', 'tag', 'rev') if k in spec]
                    if len(refs) > 1 or any(not isinstance(ref, str) or len(ref) > 200 for ref in refs):
                        raise ValueError(f'{name}: invalid dependency revision.')
                    dependency = self.repository(spec['git'], refs[0] if refs else '')
                else:
                    if set(spec) - {'path', 'preprocess'} or not isinstance(spec['path'], str):
                        raise ValueError(f'{name}: invalid path dependency.')
                    dependency = (root / spec['path']).resolve()
                    # Relative dependencies must remain within this downloaded repo.
                    containing = next(container for container in self.repositories.values() if root.is_relative_to(container))
                    if not dependency.is_relative_to(containing):
                        raise ValueError(f'{name}: path dependency leaves its repository.')
                    self.manifest(dependency)
                import os
                table[name] = {'path': Path(os.path.relpath(dependency, root)).as_posix(),
                               **({'preprocess': spec['preprocess']} if 'preprocess' in spec else {})}
        if self.writer is None:
            import tomli_w
            self.writer = tomli_w.dumps
        original.write_text(self.writer(manifest), encoding='utf-8')
        self.visiting.remove(root)
        self.prepared.add(key)

    def prepare(self, payload):
        payload = validate_request(payload)
        root = self.repository(payload['url'], payload['revision'], development=payload['workflow'] == 'package')
        # Bound combined expansion, not just each individual archive.
        paths = list(self.directory.rglob('*'))
        if len(paths) > 20000 or sum(p.stat().st_size for p in paths if p.is_file()) > MAX_EXPANDED:
            raise ValueError('Combined dependency sources exceed 64 MiB / 20000 entries.')
        return root.relative_to(self.directory).as_posix(), self.records
