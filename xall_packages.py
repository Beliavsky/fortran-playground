"""Refresh the static discovery catalog; never compile or deploy packages."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import tomllib
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from xgithub_topics import github_html_topics

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://raw.githubusercontent.com/Beliavsky/Fortran-packages-list/master/README.md'
OUTPUT = ROOT / 'fpm_catalog/all-packages.json'


def parse_packages(markdown):
    """Only leading package links count; links within descriptions are references."""
    records = {}
    category = ''
    for line in markdown.splitlines():
        if line.startswith('## '):
            category = line[3:].strip()
        match = re.match(r'^\[([^]]+)\]\(https://github.com/([\w.-]+/[\w.-]+)/?\)\s*[:,]?\s*(.*)', line)
        if not category or not match:
            continue
        name, repository, description = match.groups()
        description = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', description)
        description = unescape(re.sub(r'<[^>]*>', '', description)).strip()
        key = repository.lower()
        if key in records:
            if category not in records[key]['categories']:
                records[key]['categories'].append(category)
            continue
        records[key] = {'id': key, 'name': name, 'repository': repository, 'revision': '',
                        'description': description, 'category': category, 'categories': [category]}
    if not records:
        raise ValueError('No package entries found; previous catalog preserved.')
    return sorted(records.values(), key=lambda p: p['repository'].lower())


def manifest_status(repository):
    request = Request(f'https://raw.githubusercontent.com/{repository}/HEAD/fpm.toml',
                      headers={'User-Agent': 'Fortran-playground-catalog'})
    try:
        with urlopen(request, timeout=20) as response:
            manifest = response.read(2 * 1024 * 1024 + 1)
        if len(manifest) > 2 * 1024 * 1024:
            return 'unknown'
        tomllib.loads(manifest.decode('utf-8-sig'))
        return 'available'
    except HTTPError as error:
        return 'missing' if error.code == 404 else 'unknown'
    except (tomllib.TOMLDecodeError, UnicodeError):
        return 'invalid'
    except OSError:
        return 'unknown'


def refresh(output=OUTPUT, *, recheck=False):
    with urlopen(SOURCE, timeout=30) as response:
        data = response.read()
    packages = parse_packages(data.decode('utf-8'))
    output = Path(output)
    previous = {p['repository'].lower(): p for p in json.loads(output.read_text(encoding='utf-8'))['packages']} if output.exists() else {}
    selected = {p['repository'].lower() for p in json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    topics = json.loads((ROOT / 'fpm_catalog/topics.json').read_text(encoding='utf-8'))['repositories']
    checked_at = datetime.now(timezone.utc).isoformat()

    def inspect(package):
        key = package['repository'].lower()
        old = previous.get(key, {})
        if old and not recheck and old.get('fpm_status') != 'unknown':
            return {**package, **{k: old[k] for k in ('fpm_status', 'checked_at', 'topics') if k in old}}
        status = 'available' if key in selected else manifest_status(package['repository'])
        labels = topics.get(key, {}).get('topics')
        if labels is None:
            try:
                labels = github_html_topics(package['repository'])
            except Exception:
                labels = old.get('topics', [])
        return {**package, 'fpm_status': status, 'checked_at': checked_at, 'topics': labels}

    records = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(inspect, p) for p in packages]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 25 == 0:
                print(f'Checked {len(records)}/{len(packages)} repositories', flush=True)
    snapshot = {'schema': 1, 'source': 'https://beliavsky.github.io/Fortran-packages-list/',
                'source_sha256': hashlib.sha256(data).hexdigest(), 'retrieved_at': checked_at,
                'packages': sorted(records, key=lambda p: p['id'])}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temporary.replace(output)
    counts = {status: sum(p['fpm_status'] == status for p in records) for status in ('available', 'missing', 'invalid', 'unknown')}
    print(f'Saved {len(records)} packages: {counts}. Run python xfpm_examples.py to update site assets.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recheck', action='store_true', help='Refresh manifest checks and topics for existing entries too')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    refresh(args.output, recheck=args.recheck)
