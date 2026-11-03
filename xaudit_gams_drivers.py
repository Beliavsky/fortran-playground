"""Generate a planning audit of mapped GAMS procedures without class-matched drivers.

This reads tracked catalog metadata and retained evidence links. It submits no
jobs, changes no classifications, and does not claim new numerical verification.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from xpackage_gams import ancestors, class_order, class_tree, gams_data

ROOT = Path(__file__).resolve().parent
POLICY = 'fpm_catalog/gams-driver-priorities.json'
INPUTS = ['fpm_catalog.json', 'fpm_catalog/gams.json',
          'fpm_catalog/gams-drivers.json', POLICY]


def audit(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    manifest = json.loads((root/'fpm_catalog/gams-drivers.json').read_text(encoding='utf-8'))
    policy = json.loads((root/POLICY).read_text(encoding='utf-8'))
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {r['id']: r for r in data['procedure_mappings']}
    tree = class_tree(data)
    by_procedure = defaultdict(list)
    for driver in manifest['drivers']:
        by_procedure[driver['procedure_id']].append(driver)
    if policy.get('schema') != 1:
        raise ValueError('Unsupported audit policy schema.')
    for ident in set(policy['unchecked_dispositions']) | set(policy['class_claim_reviews']):
        if ident not in records:
            raise ValueError('Unknown reviewed procedure: '+ident)
    candidates = []
    seen = set()
    for item in policy['next_candidates']:
        ident, code = item['procedure_id'], item['gams_code']
        if (ident, code) in seen or ident not in records or code not in records[ident]['gams_codes']:
            raise ValueError('Duplicate or unmapped candidate: '+ident)
        if item.get('source_path') and item['source_path'] not in {e['path'] for e in records[ident]['evidence']}:
            raise ValueError('Candidate source is not recorded evidence: '+ident)
        seen.add((ident, code))
        if any(code in ancestors(tree, d['gams_code']) for d in by_procedure[ident]):
            continue  # Completed since the planning review; retain curation history.
        candidates.append(dict(rank=len(candidates)+1, **item))
    unchecked, claims = [], []
    for record in records.values():
        drivers = by_procedure[record['id']]
        package = packages[record['package_id']]
        base = f'https://github.com/{package["repository"]}/blob/{record["revision"]}/'
        row = {
            'procedure_id': record['id'], 'package_id': record['package_id'],
            'revision': record['revision'], 'module': record['module'],
            'procedure': record['procedure'], 'gams_codes': record['gams_codes'],
            'notes': record['notes'],
            'sources': [dict(url=base+e['path']+'#L'+str(e.get('line', 1)), **e) for e in record['evidence']],
            'author_examples': [dict(url=base+e['path'], **e) for e in record.get('author_examples', [])],
            'retained_paths': sorted({p.rstrip('.,;:') for p in re.findall(r'docs/[\w./-]+', record['notes'])
                                      if (root/p.rstrip('.,;:')).exists()}),
            'drivers': [{'id': d['id'], 'gams_code': d['gams_code'], 'path': d['path'],
                         'review_path': d.get('review_path')} for d in drivers]
        }
        if not drivers:
            disposition = policy['unchecked_dispositions'].get(record['id'], {
                'status': 'needs-triage', 'action': 'Review pinned source, existing probes and author examples before ranking.'})
            explicit_paths = disposition.get('retained_paths', [])
            if any(not (root/p).exists() for p in explicit_paths):
                raise ValueError('Missing retained evidence for '+record['id'])
            unchecked.append({**row, **disposition,
                              'retained_paths': sorted(set(row['retained_paths']) | set(explicit_paths))})
        else:
            for code in record['gams_codes']:
                if not any(code in ancestors(tree, d['gams_code']) for d in drivers):
                    claims.append(dict(**row, unmatched_code=code,
                        action=policy['class_claim_reviews'].get(record['id'],
                            'Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically.')))
    used = {c for r in records.values() for c in r['gams_codes']}
    uncovered = sorted((c for c in used if not any(c in ancestors(tree, d['gams_code'])
                                                for d in manifest['drivers'])), key=class_order)
    return {
        'schema': 1, 'reviewed_on': policy['reviewed_on'], 'scope': policy['scope'],
        'hash_normalization': 'utf-8-lf',
        'input_sha256': {name: hashlib.sha256((root/name).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
                         for name in INPUTS},
        'counts': {'procedure_records': len(records), 'checked_drivers': len(manifest['drivers']),
                   'procedures_with_drivers': sum(bool(drivers) for drivers in by_procedure.values()),
                   'procedures_without_drivers': len(unchecked),
                   'unchecked_packages': len({r['package_id'] for r in unchecked}),
                   'additional_class_claims': len(claims),
                   'directly_mapped_classes': len(used), 'classes_without_drivers': len(uncovered),
                   'unchecked_by_status': dict(sorted(Counter(r['status'] for r in unchecked).items()))},
        'uncovered_classes': [{'code': c, 'label': tree[c]['label'],
                               'procedure_ids': [r['id'] for r in records.values() if c in r['gams_codes']]}
                              for c in uncovered],
        'next_candidates': candidates,
        'unchecked_procedures': sorted(unchecked, key=lambda r: r['procedure_id']),
        'additional_class_claims': sorted(claims, key=lambda r: (class_order(r['unmatched_code']), r['procedure_id']))
    }


def markdown(report):
    counts = report['counts']
    lines = ['# GAMS driver coverage audit and next priorities', '',
        'Planning review: '+report['reviewed_on']+'. This is an audit of the current pinned selected-package records, '
        'not a new compilation run, an exhaustive package API inventory, or a ranking of software quality.', '',
        f"There are **{counts['checked_drivers']} checked drivers for {counts['procedures_with_drivers']} of "
        f"{counts['procedure_records']} source-reviewed procedure records**. "
        f"**{counts['procedures_without_drivers']} records across {counts['unchecked_packages']} packages** have no dedicated checked driver. "
        f"Another **{counts['additional_class_claims']} mapped procedure/class claims** belong to procedures with a driver for a different class or configuration.", '',
        'A missing driver does not mean the package cannot compile: ordinary catalog examples have separate evidence. '
        'A driver under one class does not automatically establish every other classification of its procedure. '
        'Conversely, a cross-class mismatch is not automatically a missing algorithm test; it may need a mapping or presentation review.', '',
        '## Recommended next numerical candidates', '',
        'These are ranked **candidates to probe**, not newly verified examples. Prefer a new API or derivative mode over another variation of an already checked routine. '
        'Use author examples for API setup and add independent references; do not weaken existing failed assertions to make a batch pass. '
        'There is no requirement to fill a batch of ten.', '',
        '| Priority | Package / mapped procedure | GAMS | New coverage and independent oracle |',
        '| ---: | --- | --- | --- |']
    all_rows = {r['procedure_id']: r for r in report['unchecked_procedures']+report['additional_class_claims']}
    for item in report['next_candidates']:
        record = all_rows[item['procedure_id']]
        source = next(e['url'] for e in record['sources']
                      if e['path'] == item.get('source_path', record['sources'][0]['path']))
        lines.append(f"| {item['rank']} | [{record['package_id']}: {item['title']}]({source}) | "
                     f"{item['gams_code']} | {item['reason']} {item['oracle']} |")
    for item in report['next_candidates']:
        record = all_rows[item['procedure_id']]
        examples = ' / '.join(f"[Author example/test]({e['url']})" for e in record['author_examples']) or 'No matching author example is recorded; review the pinned API directly.'
        lines += ['', f"### {item['rank']}. {item['title']}", '',
                  f"Mapped record: `{item['procedure_id']}`. {examples}", '', item['precautions']]
    lines += ['', '## The remaining uncovered mapped class', '',
        'Counts are limited to classes used by our procedure mappings. Unused taxonomy branches are not counted as covered or exhausted.']
    for entry in report['uncovered_classes']:
        lines += ['', f"- **{entry['code']} — {entry['label']}**: "+', '.join('`'+s+'`' for s in entry['procedure_ids'])+'.']
    if any(entry['code'] == 'L13b' for entry in report['uncovered_classes']):
        lines += ['', 'At this review, PCA is the outstanding class gap: the stdlib consumer exceeded the hosted link file-size limit and obtained no numerical results; '
        'the forpca consumer produced incorrect variances at the pinned revision. Investigate a selective stdlib link or an upstream repair before retrying. '
        'An independently reviewed PCA application using a working SVD API could be another route, but it would not verify either existing PCA API.']
    lines += ['',
        '## Disposition of records with no dedicated driver', '',
        '| Status | Records | Meaning |', '| --- | ---: | --- |']
    meanings = {'ready-to-probe': 'No retained blocker is recorded; attempt an independent API consumer.',
        'retained-failure': 'A recorded counterexample or runtime failure needs diagnosis/repair or a separately scoped API.',
        'sandbox-limit': 'No numerical result; service/link constraints blocked the probe.',
        'graphics-promotion': 'Ordinary headless artifact example exists; add a dedicated checked graphics problem if useful.',
        'scope-review': 'Review private/overlapping API claims before adding a consumer.',
        'workflow-review': 'Full application workflow differs from the checked supporting solver.',
        'needs-triage': 'New record not yet assigned a planning disposition.'}
    for status, n in counts['unchecked_by_status'].items():
        lines.append(f'| {status} | {n} | {meanings[status]} |')
    grouped = defaultdict(list)
    for record in report['unchecked_procedures']:
        for code in record['gams_codes']:
            grouped[code].append(record)
    for code in sorted(grouped, key=class_order):
        lines += ['', '### '+code, '', '| Procedure / pinned evidence | Status and next action |', '| --- | --- |']
        for record in grouped[code]:
            retained = ' '.join(f'[Retained evidence]({p.removeprefix("docs/")})' for p in record['retained_paths'])
            lines.append(f"| [{record['package_id']}: `{record['procedure_id']}`]({record['sources'][0]['url']}) | "
                         f"**{record['status']}**. {record['action']} {retained} |")
    lines += ['', 'Records assigned to multiple classes appear more than once above; do not sum those rows. '
        'The [machine-readable audit](gams-driver-audit.json) preserves original qualifications, exact pins, source hashes, author links and disposition for every record.', '',
        'The audit cross-checks older retained-probe reports as well as the procedure notes. In particular, the two high-level fortran-lapack records do not mention their historical linking failures in their notes; '
        'their dispositions above include the saved evidence and keep them off the immediate candidate list.', '',
        '## Additional class claims on procedures that already have a driver', '',
        'Review these before treating them as new-driver requests. A checked descendant also satisfies its ancestor in this audit; '
        'siblings do not. No classification or checked status was changed by this audit.', '',
        '| Mapped class | Procedure | Existing driver classes | Review action |', '| --- | --- | --- | --- |']
    for record in report['additional_class_claims']:
        drivers = ', '.join(f"[{d['gams_code']}](../{d['path']})" for d in record['drivers'])
        lines.append(f"| {record['unmatched_code']} | `{record['procedure_id']}` | {drivers} | {record['action']} |")
    lines += ['', '## Further expansion after these candidates', '',
        'The mapped ledger is representative, not a full procedure inventory. Additional valuable work can come from new APIs in already compiled packages, '
        'especially common problems enabling accuracy comparisons across libraries. Review each new API and its GAMS mapping before adding a checked driver. '
        'The five graphics promotions are useful but lower priority than the distinct numerical APIs/modes above; artifact existence alone is insufficient.', '',
        'Retained failures can exist outside the procedure ledger. For example, the [Fstats interpolation probes](gams-candidates/fstats-interpolation/README.md) '
        'include an unpublished spline mismatch and Hermite reinitialization failure; the successful fresh-object Hermite driver does not erase those limitations.', '',
        '## Maintenance', '', '```text', 'python xaudit_gams_drivers.py', 'python xaudit_gams_drivers.py --check', '```', '',
        'Edit the planning judgments in [gams-driver-priorities.json](../fpm_catalog/gams-driver-priorities.json). '
        'Counts and lists are computed from the current classifications and driver manifest; UTF-8/LF-normalized input SHA256 hashes identify the snapshot across Windows and Linux. '
        'Completed candidate/class pairs drop out of the next-candidate list. New unchecked records receive needs-triage rather than being silently classified as failures. '
        'The script submits no compiler jobs, rebuilds no library and requires no backend deployment. '
        'See [coverage](gams-coverage.md) and [numerical review](gams-numerical.md) for the broader catalog.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = audit()
    outputs = {'docs/gams-driver-audit.json': json.dumps(report, indent=2, ensure_ascii=False)+'\n',
               'docs/gams-driver-audit.md': markdown(report)}
    for name, text in outputs.items():
        path = ROOT/name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                raise SystemExit(name+': stale; run python xaudit_gams_drivers.py')
        else:
            path.write_text(text, encoding='utf-8')
    print('GAMS driver audit '+('verified.' if args.check else 'written.'))
    print(json.dumps(report['counts'], indent=2))


if __name__ == '__main__':
    main()
