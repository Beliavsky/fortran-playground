"""Refresh saved GitHub topics and star counts; never build or deploy packages."""
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


def github_metadata(repository):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Fortran-playground-topic-refresh'}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request(f'https://api.github.com/repos/{repository}', headers=headers)
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    return {'topics': data['topics'], 'stars': data['stargazers_count']}


def github_topics(repository):
    return github_metadata(repository)['topics']


class TopicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.topics = set()
        self.stars = None
        self.json_script = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'script':
            self.json_script = attrs.get('type') == 'application/json'
        if attrs.get('id') == 'repo-stars-counter-star':
            title = attrs.get('title', '').replace(',', '')
            if title.isdigit():
                self.stars = int(title)
        classes = attrs.get('class', '').lower()
        match = re.fullmatch(r'/topics/([a-z0-9-]+)', attrs.get('href', ''))
        if tag == 'a' and match and ('topictag' in classes or 'topic-tag' in classes):
            self.topics.add(match[1])

    def handle_endtag(self, tag):
        if tag == 'script':
            self.json_script = False

    def handle_data(self, data):
        if not self.json_script:
            return
        try:
            payload = json.loads(data).get('payload', {})
            about = payload.get('sidebarAbout') or payload.get('codeViewRepoRoute', {}).get('overview', {}).get('sidebarAboutData', {})
            if 'stargazerCount' in about:
                self.stars = about['stargazerCount']
                self.topics.update(topic['name'] for topic in about.get('topics', []))
        except (ValueError, TypeError, AttributeError, KeyError):
            pass


def github_html_metadata(repository):
    # Optional public-page fallback for operators without API credentials.
    with urlopen(f'https://github.com/{repository}', timeout=30) as response:
        parser = TopicParser()
        parser.feed(response.read().decode('utf-8'))
    if parser.stars is None:
        raise ValueError(f'{repository}: exact star count missing from public page; try the API.')
    return {'topics': sorted(parser.topics), 'stars': parser.stars}


def github_html_topics(repository):
    return github_html_metadata(repository)['topics']


def refresh(packages, output=DEFAULT_OUTPUT, *, fetch_topics=None, fetch_metadata=github_metadata,
            source='GitHub repository metadata API'):
    repositories = sorted({p['repository'].lower() for p in packages})
    if any(not re.fullmatch(r'[a-z0-9_.-]+/[a-z0-9_.-]+', repo) for repo in repositories):
        raise ValueError('Invalid catalog repository.')

    updated = datetime.now(timezone.utc).isoformat()
    def collect(repository):
        metadata = {'topics': fetch_topics(repository)} if fetch_topics else fetch_metadata(repository)
        topics = metadata['topics']
        if not isinstance(topics, list) or any(not isinstance(t, str) or not re.fullmatch(r'[a-z0-9-]{1,50}', t) for t in topics):
            raise ValueError(f'{repository}: invalid GitHub topics response.')
        record = {'topics': sorted(set(topics))}
        if not fetch_topics:
            stars = metadata['stars']
            if type(stars) is not int or stars < 0:
                raise ValueError(f'{repository}: invalid GitHub star count.')
            record.update(stars=stars, stars_updated_at=updated)
        return repository, record

    # A failed refresh preserves the complete previous snapshot, including
    # empty topic lists, rather than silently deleting metadata on API errors.
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = dict(pool.map(collect, repositories))
    snapshot = {'schema': 1, 'retrieved_at': updated,
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
    parser.add_argument('--html', action='store_true', help='Read topics and exact star counts from public repository pages instead of the API')
    args = parser.parse_args()
    packages = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    try:
        data = refresh(packages, args.output,
                       **({'fetch_metadata': github_html_metadata, 'source': 'GitHub repository public pages'} if args.html else {}))
    except Exception as error:
        parser.exit(1, f'Metadata refresh failed; previous snapshot preserved: {error}\n'
                       'For GitHub API rate limits, set GITHUB_TOKEN or GH_TOKEN and retry.\n')
    print(f'Refreshed topics and stars for {len(data["repositories"])} repositories. Run python xfpm_examples.py to update the site catalog.')


if __name__ == '__main__':
    main()
