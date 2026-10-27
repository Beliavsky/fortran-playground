"""Refresh static GitHub topic metadata; never build or deploy packages."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / 'fpm_catalog/topics.json'


def github_topics(repository):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Fortran-playground-topic-refresh'}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request(f'https://api.github.com/repos/{repository}/topics', headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)['names']


class TopicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.topics = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = attrs.get('class', '').lower()
        match = re.fullmatch(r'/topics/([a-z0-9-]+)', attrs.get('href', ''))
        if tag == 'a' and match and ('topictag' in classes or 'topic-tag' in classes):
            self.topics.add(match[1])


def github_html_topics(repository):
    # Optional public-page fallback for operators without API credentials.
    with urlopen(f'https://github.com/{repository}', timeout=30) as response:
        parser = TopicParser()
        parser.feed(response.read().decode('utf-8'))
    return sorted(parser.topics)


def refresh(packages, output=DEFAULT_OUTPUT, *, fetch_topics=github_topics, source='GitHub repository topics API'):
    repositories = sorted({p['repository'].lower() for p in packages})
    if any(not re.fullmatch(r'[a-z0-9_.-]+/[a-z0-9_.-]+', repo) for repo in repositories):
        raise ValueError('Invalid catalog repository.')

    def collect(repository):
        topics = fetch_topics(repository)
        if not isinstance(topics, list) or any(not isinstance(t, str) or not re.fullmatch(r'[a-z0-9-]{1,50}', t) for t in topics):
            raise ValueError(f'{repository}: invalid GitHub topics response.')
        return repository, {'topics': sorted(set(topics))}

    # A failed refresh preserves the complete previous snapshot, including
    # empty topic lists, rather than silently deleting metadata on API errors.
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = dict(pool.map(collect, repositories))
    snapshot = {'schema': 1, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'source': source, 'repositories': records}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
    temporary.replace(output)
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--html', action='store_true', help='Read public repository topic labels instead of using the rate-limited API')
    args = parser.parse_args()
    packages = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    try:
        data = refresh(packages, args.output,
                       **({'fetch_topics': github_html_topics, 'source': 'GitHub repository topic labels'} if args.html else {}))
    except Exception as error:
        parser.exit(1, f'Topic refresh failed; previous snapshot preserved: {error}\n'
                       'For GitHub API rate limits, set GITHUB_TOKEN or GH_TOKEN and retry.\n')
    print(f'Refreshed topics for {len(data["repositories"])} repositories. Run python xfpm_examples.py to update the site catalog.')


if __name__ == '__main__':
    main()
