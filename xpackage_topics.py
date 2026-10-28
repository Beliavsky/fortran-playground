"""Validate playground topics and generate the package-by-package review page offline."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPORT = Path('docs/fpm-package-topics.md')


def playground_topics(root=ROOT):
    root = Path(root)
    data = json.loads((root / 'fpm_catalog/playground-topics.json').read_text(encoding='utf-8'))
    if data.get('schema') != 1 or not isinstance(data.get('packages'), dict):
        raise ValueError('Invalid playground topic schema.')
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    expected = {p['id'] for p in packages}
    actual = set(data['packages'])
    if actual != expected:
        raise ValueError(f'Playground topics: missing {sorted(expected - actual)}, unknown {sorted(actual - expected)}.')
    for name, topics in data['packages'].items():
        if not isinstance(topics, list) or not topics or any(
                not isinstance(t, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', t) or len(t) > 50 for t in topics):
            raise ValueError(f'{name}: use a nonempty list of lowercase hyphen-separated topics.')
        if len(topics) != len(set(topics)):
            raise ValueError(f'{name}: duplicate playground topic.')
    return {name: sorted(topics) for name, topics in data['packages'].items()}


def review_text(root=ROOT):
    root = Path(root)
    curated = playground_topics(root)
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    github = json.loads((root / 'fpm_catalog/topics.json').read_text(encoding='utf-8'))
    counts = Counter(t for topics in curated.values() for t in topics)
    lines = ['# Playground topics by package', '',
             f'{len(packages)} selected packages; {len(counts)} distinct playground topics. '
             f'GitHub topics were retrieved on {github["retrieved_at"][:10]}.', '',
             'The playground topics below are editorial suggestions based on the saved package descriptions, '
             'categories, and GitHub labels. They describe the package, rather than claiming every feature '
             'is exercised by its example main program. They are not author-supplied GitHub topics.', '',
             'Search defaults to the union of both topic sources. Choose **Topics: GitHub only** '
             'to exclude playground topics from matching. Names, descriptions, owners, and categories remain searchable. '
             'The two sources are labeled separately on the page.', '',
             '## Maintaining the topics', '',
             'Edit [playground-topics.json](../fpm_catalog/playground-topics.json), keyed by package ID. '
             'Prefer an existing term for a shared concept, such as `ode`, `quadrature`, `least-squares`, '
             '`random-numbers`, or `file-io`; add specific algorithm or format names where useful. '
             'Avoid generic `fortran` and `fpm` labels in our list. Add an entry whenever a selected package is added.', '',
             'Run these commands from the repository root:', '', '```text',
             'python xpackage_topics.py', 'python xfpm_examples.py', '```', '',
             'The first command validates coverage and regenerates this page; use `--check` to check it without writing. '
             'The second updates the public search metadata. Both are offline and require no backend deployment or '
             'package recompilation. GitHub metadata refreshes never edit the playground topic file; '
             'regenerate this page after refreshing GitHub topics.', '']
    cell = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')
    topic_list = lambda items: ', '.join(f'`{t}`' for t in sorted(items)) or 'None supplied'
    for category in sorted({p['category'] for p in packages}, key=str.casefold):
        lines.extend([f'## {category}', '', '| Package and description | Playground topics | GitHub topics |',
                      '| --- | --- | --- |'])
        for p in sorted((p for p in packages if p['category'] == category), key=lambda p: p['id'].casefold()):
            author = github['repositories'].get(p['repository'].lower(), {}).get('topics', [])
            lines.append(f'| [{cell(p["id"])}](https://github.com/{p["repository"]}) — {cell(p["description"])} '
                         f'| {topic_list(curated[p["id"]])} | {topic_list(author)} |')
        lines.append('')
    lines.extend(['## Playground topic index', '',
                  'Counts below refer only to our topics; GitHub-only labels are not included.', '',
                  '| Topic | Packages |', '| --- | --- |'])
    lines.extend(f'| `{topic}` | {counts[topic]} |' for topic in sorted(counts))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated review page is out of date')
    args = parser.parse_args()
    text = review_text()
    path = ROOT / REPORT
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            parser.exit(1, 'Topic review page is out of date. Run python xpackage_topics.py.\n')
        print('Playground topics and review page verified.')
    else:
        path.write_text(text, encoding='utf-8')
        print(f'Wrote {REPORT.as_posix()}')


if __name__ == '__main__':
    main()
