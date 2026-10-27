"""Refresh the translated R discovery catalog; never compile any packages.

Run explicitly when updating the pinned collection, not during normal site builds.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import quote
from urllib.request import urlopen

from fpm_collections import R_REPOSITORY

ROOT = Path(__file__).resolve().parent


def generate(revision='main'):
    def read(path):
        with urlopen(path, timeout=30) as response:
            return response.read()
    # A Git tree SHA identifies a directory, not the commit required by raw URLs.
    commit = json.loads(read(f'https://api.github.com/repos/{R_REPOSITORY}/commits/{quote(revision, safe="")}'))['sha']
    base = f'https://raw.githubusercontent.com/{R_REPOSITORY}/{commit}'
    index = read(base + '/PROJECT_INDEX.md').decode()
    names = sorted(set(re.findall(r'\[`([^`]+)`\]\([^)]*/\)', index)), key=str.lower)
    # Shared runtime packages are dependencies, not translated R packages.
    names = [n for n in names if not n.startswith('rfortran-')]

    def package(name):
        manifest = tomllib.loads(read(f'{base}/{name}/fpm.toml').decode('utf-8-sig'))
        return {'id': name, 'repository': R_REPOSITORY, 'revision': commit,
                'subdirectory': name, 'description': manifest.get('description') or f'Fortran translation of {name}',
                'categories': manifest.get('categories', []), 'keywords': manifest.get('keywords', []),
                'category': next(iter(manifest.get('categories', [])), 'Other'),
                'verification': 'Not verified in the playground'}
    with ThreadPoolExecutor(max_workers=12) as pool:
        packages = list(pool.map(package, names))
    output = ROOT / 'site/fpm/translated-r.json'
    output.write_text(json.dumps(packages, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Indexed {len(packages)} translated R packages at {commit}; no builds performed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='main')
    generate(parser.parse_args().revision)
