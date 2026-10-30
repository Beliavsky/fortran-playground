"""Validate curated public name attributions and generate a review table offline."""
import argparse
import json
from pathlib import Path
from catalog_export import validate_attributions
from xgithub_owners import load_owners

ROOT = Path(__file__).resolve().parent
REPORT = Path('docs/name-attributions.md')


def load_attributions(root=ROOT):
    path = Path(root) / 'fpm_catalog/name-attributions.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {
        'schema': 1, 'owner_names': {}, 'project_authors': {}}
    return validate_attributions(data)


def report_text(root=ROOT):
    data = load_attributions(root)
    owners = load_owners(root)
    def cell(value):
        return str(value).replace('|', '&#124;').replace('\n', ' ')
    def sources(record):
        return '; '.join(f'[{cell(item["description"])}]({item["url"]})' for item in record['evidence'])
    lines = ['# Curated public name attributions', '',
        'These records document public project credits and proposed or confirmed account-name mappings. '
        'They are maintained separately from automatically refreshed GitHub profiles. '
        'A source author credit does not by itself establish who controls a GitHub account or sole authorship of a package.', '',
        'Only **confirmed** manual account mappings override owner display names. '
        'Inferred account mappings remain a review queue; confirmed project credits are displayed with their stated scope. '
        'Search includes confirmed project credits without treating them as account identities.', '',
        '## Account-name mappings', '',
        '| Account | Proposed name | Status | Scope / reasoning | GitHub display name | Profile conflict | Reviewed | Evidence |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for key, record in sorted(data['owner_names'].items()):
        public = owners.get(key, {}).get('display_name')
        conflict = bool(public and public.casefold() != record['name'].casefold())
        fields = [f'[{key}](https://github.com/{key})', record['name'], record['status'],
                  record['scope']+' '+record['rationale'], public or 'Not supplied',
                  'Review: names differ' if conflict else 'None recorded', record['reviewed_on'], sources(record)]
        lines.append('| '+' | '.join(cell(value) for value in fields)+' |')
    lines += ['', '## Project/source author credits', '',
              '| Project | Credited name | Status | Scope / reasoning | Reviewed | Evidence |',
              '| --- | --- | --- | --- | --- | --- |']
    for key, records in sorted(data['project_authors'].items()):
        for record in records:
            fields = [f'[{key.removeprefix("github:")}](https://github.com/{key.removeprefix("github:")})', record['name'],
                      record['status'], record['scope']+' '+record['rationale'], record['reviewed_on'], sources(record)]
            lines.append('| '+' | '.join(cell(value) for value in fields)+' |')
    lines += ['', '## Maintenance', '',
        'Edit [name-attributions.json](../fpm_catalog/name-attributions.json). Record explicit public credits, '
        'scope, reasoning, a review date and evidence links; prefer links pinned to commits and source lines. '
        'Use account mappings only when the evidence connects the person to the account. '
        'Names, initials or an account spelling alone are not sufficient. '
        'Your existing software list can supply attribution leads, with primary project evidence recorded where available.', '',
        'Do not collect unrelated personal details or infer identities from private information. '
        'Keep organization names distinct from individual project credits. '
        'If a manually mapped name differs from the current GitHub display name, review the conflict rather than changing either source automatically.', '',
        'Run `python xpackage_attributions.py` to regenerate this table, or add `--check` to validate it without writing. '
        'GitHub refreshes never edit the manual file. The Pages build exports the records and renders name attribution evidence automatically; '
        'no package compilation or backend redeployment is needed.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = report_text()
    path = ROOT / REPORT
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != expected:
            raise SystemExit('Name attribution review table is stale; run python xpackage_attributions.py.')
        print('Public name attributions and review table verified.')
    else:
        path.write_text(expected, encoding='utf-8')
        print('Wrote', REPORT)


if __name__ == '__main__':
    main()
