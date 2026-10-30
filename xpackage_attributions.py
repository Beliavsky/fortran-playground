"""Validate curated public name attributions and generate a review table offline."""
import argparse
import json
from pathlib import Path
from html import escape
from catalog_export import BASE_URL, owner_display_name, validate_attributions
from xgithub_owners import load_owners

ROOT = Path(__file__).resolve().parent
REPORT = Path('docs/name-attributions.md')
OWNER_REPORT = Path('docs/github-name-mappings.md')


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
        'See the [combined GitHub/name mapping table](github-name-mappings.md) for all selected repository owners, '
        'including public profile names and curated records.', '',
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


def owner_report_text(root=ROOT):
    root = Path(root)
    owners = load_owners(root)
    manual = load_attributions(root)
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    grouped = {}
    for package in packages:
        grouped.setdefault(package['repository'].split('/')[0].lower(), []).append(package)

    def cell(value):
        return escape(str(value), quote=False).replace('|', '&#124;').replace('\n', ' ')

    lines = ['# GitHub accounts and public name mappings', '',
        f'All **{len(grouped)} repository owners** in the selected precompiled package catalog. '
        'This table combines saved public GitHub profiles and curated name attributions; '
        'names may identify people, organizations or projects. Repository ownership does not imply sole authorship.', '',
        'The catalog name follows the same rules as the website: confirmed manual account mapping, '
        'public GitHub display name, then account name. `fortran-lang` uses its account name. '
        'Inferred account mappings and source-author credits appear separately and do not rename an account. '
        'See the [detailed manual review](name-attributions.md) for scope and reasoning.', '',
        '| GitHub account | Catalog name | Account type | Name source / review date | Other attribution / review notes | Evidence | Packages |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for key, owned in sorted(grouped.items()):
        profile = owners.get(key, {})
        curated = manual['owner_names'].get(key, {})
        login = profile.get('login', owned[0]['repository'].split('/')[0])
        # Preserve the catalog's account casing when no profile was fetched.
        name = owner_display_name(key, {'login': login, **profile}, curated)
        if key == 'fortran-lang':
            source = 'Preferred account label'
        elif curated.get('status') == 'confirmed':
            source = 'Confirmed manual mapping; '+curated['reviewed_on']
        elif profile.get('display_name'):
            source = 'Public GitHub profile; '+profile['retrieved_at'][:10]
        elif profile:
            source = 'Account fallback; profile checked '+profile['retrieved_at'][:10]
        else:
            source = 'Account fallback; no saved profile'
        notes = []
        evidence = []
        if profile:
            evidence.append(f'[Profile source]({profile["source_url"]})')
        if curated:
            if curated['status'] == 'inferred':
                notes.append('Proposed account name: '+curated['name']+' (inferred; not applied)')
            public = profile.get('display_name')
            if public and public.casefold() != curated['name'].casefold():
                notes.append('Review: manual and GitHub names differ')
            evidence.extend(f'[{cell(item["description"])}]({item["url"]})' for item in curated['evidence'])
        for package in owned:
            identity = 'github:'+package['repository'].lower()
            for record in manual['project_authors'].get(identity, []):
                notes.append('Source credit: '+record['name']+' ('+record['status']+'; '+package['id']+')')
                evidence.extend(f'[{cell(item["description"])}]({item["url"]})' for item in record['evidence'])
        account = f'[{cell(login)}](https://github.com/{login})'
        count = len(owned)
        catalog = f'[{count} {"package" if count == 1 else "packages"}]({BASE_URL}/gams/authors/{key}/)'
        fields = [account, cell(name), cell(profile.get('account_type', 'Not recorded')), cell(source),
                  cell('; '.join(notes) or '—'), '; '.join(dict.fromkeys(evidence)) or '—', catalog]
        lines.append('| '+' | '.join(fields)+' |')
    lines += ['', '## Updating this table', '',
        'Generated from [owners.json](../fpm_catalog/owners.json), '
        '[name-attributions.json](../fpm_catalog/name-attributions.json) and '
        '[fpm_catalog.json](../fpm_catalog.json). Edit those sources, not this table. '
        'After refreshing profiles, changing manual attributions or adding packages, run:', '',
        '```text', 'python xpackage_attributions.py', 'python xpackage_attributions.py --check', '```', '',
        'Both attribution review tables are generated offline. No backend deployment or package compilation is needed.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for report, expected in [(REPORT, report_text()), (OWNER_REPORT, owner_report_text())]:
        path = ROOT / report
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != expected:
                raise SystemExit(f'{report} is stale; run python xpackage_attributions.py.')
            print('Verified', report)
        else:
            path.write_text(expected, encoding='utf-8')
            print('Wrote', report)


if __name__ == '__main__':
    main()
