"""Refresh public GitHub owner display names; ordinary site builds stay offline."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from catalog_export import validate_owners

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / 'fpm_catalog/owners.json'
VOID_TAGS = {'meta', 'img', 'link', 'br', 'hr', 'input', 'source', 'wbr', 'area', 'base', 'col', 'embed', 'param', 'track'}


def load_owners(root=ROOT):
    path = Path(root) / 'fpm_catalog/owners.json'
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Invalid GitHub owner metadata schema.')
    return validate_owners(data.get('owners'))


def github_owner(login):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Fortran-playground-owner-refresh'}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request('https://api.github.com/users/' + login, headers=headers), timeout=25) as response:
        data = json.load(response)
    name = data.get('name')
    return {'login': data['login'], 'display_name': ' '.join(name.split()) or None if isinstance(name, str) else None,
            'account_type': data['type'], 'profile_url': data['html_url']}


class ProfileParser(HTMLParser):
    """Read only the profile heading, never names mentioned in README content."""
    def __init__(self):
        super().__init__()
        self.level = 0
        self.capture = None
        self.parts = []
        self.name = None
        self.account_type = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = attrs.get('class', '').split()
        if tag in VOID_TAGS:
            return
        self.level += 1
        if self.account_type is None:
            if tag == 'span' and 'p-name' in classes and attrs.get('itemprop') == 'name':
                self.account_type = 'User'
                self.capture = self.level
            elif tag == 'h1' and {'h2', 'lh-condensed'} <= set(classes):
                self.account_type = 'Organization'
                self.capture = self.level

    def handle_data(self, text):
        if self.capture is not None:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.capture == self.level:
            self.name = ' '.join(''.join(self.parts).split()) or None
            self.capture = None
        self.level -= 1


def github_html_owner(login):
    url = 'https://github.com/' + login
    with urlopen(Request(url, headers={'User-Agent': 'Fortran-playground-owner-refresh'}), timeout=25) as response:
        if response.url.rstrip('/').lower() != url:
            raise ValueError('Profile redirected to a different account; review the repository owner.')
        raw = response.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError('Profile page exceeds the metadata size limit.')
    parser = ProfileParser()
    parser.feed(raw.decode('utf-8'))
    if parser.account_type is None or parser.capture is not None:
        raise ValueError('Public profile heading not found; keeping saved metadata.')
    return {'login': login, 'display_name': parser.name, 'account_type': parser.account_type,
            'profile_url': url, 'source_url': url}


def refresh(packages, output=DEFAULT_OUTPUT, *, fetch_owner=github_owner, only=None, missing=False):
    output = Path(output)
    snapshot = json.loads(output.read_text(encoding='utf-8')) if output.exists() else {'schema': 1, 'owners': {}}
    if snapshot.get('schema') != 1:
        raise ValueError('Invalid GitHub owner metadata schema.')
    records = dict(validate_owners(snapshot.get('owners')))
    selected = {p['repository'].split('/')[0].lower() for p in packages}
    if any(not re.fullmatch(r'[a-z0-9_.-]+', owner) for owner in selected):
        raise ValueError('Invalid catalog GitHub owner.')
    requested = {o.lower() for o in only} if only else selected
    if requested - selected:
        raise ValueError('Requested owner is not in the selected catalog.')
    if missing:
        requested -= records.keys()
    updated = datetime.now(timezone.utc).isoformat()
    rate_limited = threading.Event()

    def collect(login):
        if rate_limited.is_set():
            return login, None, 'Skipped after GitHub rate limit; retry later.'
        try:
            record = {**fetch_owner(login), 'retrieved_at': updated}
            record.setdefault('source_url', 'https://api.github.com/users/' + login)
            validate_owners({login: record})
            return login, record, None
        except Exception as error:
            if isinstance(error, HTTPError) and error.code in (403, 429):
                rate_limited.set()
            return login, None, f'{type(error).__name__}: {error}'

    errors = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for login, record, error in pool.map(collect, sorted(requested)):
            if error:
                errors[login] = error
            else:
                records[login] = record
    # A failed request keeps the last successful record, including a saved name.
    # A successful response without a public name clears it instead of inventing one.
    snapshot = {'schema': 1, 'owners': dict(sorted(records.items()))}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_bytes((json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    temporary.replace(output)
    return snapshot, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Fetch public profile metadata from GitHub')
    parser.add_argument('--missing', action='store_true', help='Fetch only accounts without a saved record')
    parser.add_argument('--owners', nargs='+', help='Refresh only these catalog accounts')
    parser.add_argument('--html', action='store_true', help='Read public GitHub profile headings instead of the API')
    args = parser.parse_args()
    packages = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    if args.refresh:
        snapshot, errors = refresh(packages, only=args.owners, missing=args.missing,
                                   fetch_owner=github_html_owner if args.html else github_owner)
        for owner, error in errors.items():
            print(f'{owner}: no update; saved metadata retained when available; {error}')
    else:
        snapshot = {'owners': load_owners()}
        errors = {}
    selected = {p['repository'].split('/')[0].lower() for p in packages}
    saved = {k: v for k, v in snapshot['owners'].items() if k in selected}
    print(f'{len(saved)}/{len(selected)} catalog owners cached; {sum(v["display_name"] is not None for v in saved.values())} public display names.')
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
