"""Controlled FORD API documentation; independent of FPM compilation and caches."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote
import zipfile

from fpm_sources import extract_archive, fetch, github_repository

FORD_VERSION = '7.0.13'
RECIPE = 'ford-public-v5'
MAX_SOURCE = 32 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024
MAX_FILES = 1500
# Enforce the no-INCLUDE rule at FORD's own logical-statement boundary too,
# covering continued keywords and statements separated by semicolons.
FORD_DRIVER = """from ford.reader import FortranReader
from ford import run
def no_file_include(self):
    if self.pending and self.pending[0].lower().startswith('include '):
        raise ValueError('Source INCLUDE directives are unsupported in the documentation pilot.')
FortranReader.include = no_file_include
run()
"""

SKIP = {'.git', 'build', 'node_modules', 'vendor', 'third_party', 'third-party', '__pycache__'}
EXTENSIONS = {'.f90', '.f95', '.f03', '.f08', '.f', '.for', '.inc'}


def validate_request(data):
    if not isinstance(data, dict) or set(data) - {'url', 'revision', 'subdirectory'}:
        raise ValueError('Supply a GitHub URL, revision and optional package directory.')
    repo = github_repository(data.get('url'))
    revision = data.get('revision', '')
    directory = data.get('subdirectory', '')
    if not isinstance(revision, str) or not re.fullmatch(r'[A-Za-z0-9_./-]{0,200}', revision):
        raise ValueError('Invalid revision.')
    if (not isinstance(directory, str) or len(directory) > 200 or '\\' in directory or ':' in directory
            or (directory and (PurePosixPath(directory).is_absolute() or '..' in PurePosixPath(directory).parts))):
        raise ValueError('Use a repository-relative package directory.')
    return {'url': 'https://github.com/' + repo, 'revision': revision, 'subdirectory': directory}


def identity(repository, revision, directory=''):
    return hashlib.sha256(json.dumps([repository.lower(), revision, directory, FORD_VERSION, RECIPE]).encode()).hexdigest()


def snapshot(source, destination):
    """Copy source only: never carry repository FORD config, plugins or scripts."""
    source = Path(source).resolve()
    files, total = [], 0
    for directory, folders, names in os.walk(source, followlinks=False):
        folders[:] = sorted(n for n in folders if n not in SKIP and not n.startswith('.')
                            and not (Path(directory) / n).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if path.suffix.lower() not in EXTENSIONS or path.is_symlink():
                continue
            total += path.stat().st_size
            files.append(path)
            if len(files) > MAX_FILES or total > MAX_SOURCE:
                raise ValueError('Documentation source limit: 1500 files / 32 MiB.')
    if not files:
        raise ValueError('No supported Fortran source files were found.')
    for path in files:
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        # FORD's Markdown include extension and Fortran INCLUDE must not read
        # arbitrary files from the worker or a local user's home directory.
        if '{!' in text:
            raise ValueError('Markdown file includes are unsupported in the documentation pilot.')
        if re.search(r"(?im)(?:^|;)\s*(?:[0-9]+\s*)?(?:#\s*)?include\b", text):
            raise ValueError('Source INCLUDE directives are unsupported in the documentation pilot.')
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    return len(files)


def generate(source, cache, *, repository='local', revision='', directory='', runner=subprocess.run):
    """No compilation; source content participates in local cache identity."""
    try:
        installed = importlib.metadata.version('ford')
    except importlib.metadata.PackageNotFoundError:
        installed = None
    if installed != FORD_VERSION:
        raise ValueError('Install the documentation dependency: python -m pip install ford==' + FORD_VERSION)
    cache = Path(cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ford_') as temporary:
        work = Path(temporary)
        count = snapshot(Path(source), work / 'src')
        digest = hashlib.sha256()
        for p in sorted((work / 'src').rglob('*')):
            if p.is_file():
                digest.update(p.relative_to(work / 'src').as_posix().encode() + b'\0' + p.read_bytes() + b'\0')
        key = identity(repository, revision + ':' + digest.hexdigest(), directory)
        published = cache / key
        if (published / 'metadata.json').is_file():
            return {**json.loads((published / 'metadata.json').read_text()), 'cached': True}
        config = work / 'project.md'
        config.write_text('project: Fortran API documentation\nsrc_dir: src\noutput_dir: html\n'
            'preprocess: false\ngraph: false\nsearch: true\nsource: true\n'
            'display: public\n    protected\nwarn: true\nparallel: 0\n'
            'extensions: f90\n    F90\n    f95\n    F95\n    f03\n    f08\n'
            'fixed_extensions: f\n    F\n    for\n\n'
            'Automatically extracted API reference. This is not a compilation or numerical check.\n'
            'Preprocessing, external dependencies and repository-specific FORD settings are disabled.\n', encoding='utf-8')
        with (work / 'ford.log').open('w+', encoding='utf-8', errors='replace') as log:
            try:
                result = runner([sys.executable, '-c', FORD_DRIVER, str(config)], cwd=work, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                                stdout=log, stderr=subprocess.STDOUT, timeout=120)
            except subprocess.TimeoutExpired as error:
                raise ValueError('FORD generation exceeded 120 seconds.') from error
            log.seek(0)
            output = log.read(65536)
        html = work / 'html'
        if result.returncode or not (html / 'index.html').is_file():
            raise ValueError('FORD could not document this source snapshot.\n' + output[-12000:])
        # Keep styles and search usable in the downloaded ZIP and under the
        # generated-page sandbox. FORD otherwise loads these from public CDNs.
        assets = Path(__file__).resolve().parent / 'vendor/ford'
        shutil.copytree(assets, html / 'pilot-assets')
        for page in html.rglob('*.html'):
            relative = os.path.relpath(html / 'pilot-assets', page.parent).replace('\\', '/')
            text = page.read_text(encoding='utf-8')
            for url, name in [('https://unpkg.com/lunr/lunr.js', 'lunr.min.js'),
                ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css', 'bootstrap.min.css'),
                ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js', 'bootstrap.bundle.min.js')]:
                text = text.replace(url, relative + '/' + name)
            # MathJax is optional, network-dependent and excluded from the pilot.
            text = re.sub(r'<script[^>]+src="https://cdn.jsdelivr.net/npm/mathjax[^>]*>\s*</script>', '', text)
            text = re.sub(r'\s+(?:integrity|crossorigin)="[^"]*"', '', text)
            text = text.replace('search_database.json', 'search_database.js')
            page.write_text(text, encoding='utf-8')
        database = html / 'search/search_database.json'
        if database.exists(): database.rename(database.with_suffix('.js'))
        files = [p for p in html.rglob('*') if p.is_file()]
        if len(files) > 10000 or sum(p.stat().st_size for p in files) > MAX_OUTPUT:
            raise ValueError('Generated documentation exceeds 32 MiB / 10000 files.')
        metadata = dict(key=key, repository=repository, revision=revision, subdirectory=directory,
                        ford=FORD_VERSION, recipe=RECIPE, source_files=count, cached=False,
                        limitations='No preprocessing, INCLUDE directives, dependency documentation, custom FORD settings or compilation.',
                        log=output[-12000:])
        (html / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        with zipfile.ZipFile(html / 'documentation.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in files + [html / 'metadata.json']:
                archive.write(path, path.relative_to(html).as_posix())
        # Concurrent requests can finish the same immutable snapshot. Publish
        # only a completed directory; never expose partial HTML or ZIP files.
        staging = Path(tempfile.mkdtemp(prefix='publish-', dir=cache))
        try:
            shutil.copytree(html, staging, dirs_exist_ok=True)
            try:
                staging.rename(published)
            except OSError:
                if not (published / 'metadata.json').is_file():
                    raise
        finally:
            if staging.exists(): shutil.rmtree(staging)
        return metadata


def github_documentation(data, cache, *, downloader=fetch):
    data = validate_request(data)
    repo = github_repository(data['url'])
    revision = data['revision']
    if not re.fullmatch('[a-f0-9]{40}', revision):
        revision = json.loads(downloader('https://api.github.com/repos/' + repo + '/commits/'
                                        + quote(revision or 'HEAD', safe=''), limit=1024*1024, timeout=15))['sha']
    if not re.fullmatch('[a-f0-9]{40}', revision):
        raise ValueError('GitHub returned an invalid commit.')
    with tempfile.TemporaryDirectory(prefix='ford_download_') as temporary:
        root = extract_archive(downloader(f'https://codeload.github.com/{repo}/tar.gz/{revision}'),
                               Path(temporary), require_manifest=False)
        source = (root / data['subdirectory']).resolve()
        if not source.is_relative_to(root.resolve()) or not source.is_dir():
            raise ValueError('Package directory was not found.')
        return generate(source, cache, repository=repo, revision=revision, directory=data['subdirectory'])


def artifact(cache, key, name):
    if not re.fullmatch('[a-f0-9]{64}', key) or '\\' in name or ':' in name:
        raise ValueError('Invalid documentation path.')
    root = (Path(cache) / key).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Documentation file not found.')
    return path
