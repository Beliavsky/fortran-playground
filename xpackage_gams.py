"""Validate GAMS parent/subclass assignments and generate their review page offline."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parent
REPORT = Path('docs/fpm-gams.md')
PILOT_REPORT = Path('docs/gams-g1.md')
GAMS_URL = 'https://gams.nist.gov/cgi-bin/serve.cgi'


def gams_data(root=ROOT):
    root = Path(root)
    data = json.loads((root / 'fpm_catalog/gams.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 2 or data.get('source') != GAMS_URL:
        raise ValueError('Invalid GAMS metadata schema or source.')
    classes = data.get('classes')
    if not isinstance(classes, dict) or set(classes) != set('ABCDEFGHIJKLMNOPQRSZ') or any(
            not isinstance(label, str) or not label.strip() for label in classes.values()):
        raise ValueError('GAMS metadata must define the 20 top-level classes.')
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    expected = {p['id'] for p in packages}
    assignments = data.get('packages')
    if not isinstance(assignments, dict):
        raise ValueError('GAMS package assignments must be a mapping.')
    actual = set(assignments)
    if actual != expected:
        raise ValueError(f'GAMS assignments: missing {sorted(expected - actual)}, unknown {sorted(actual - expected)}.')
    for name, codes in assignments.items():
        if not isinstance(codes, list) or not codes or any(
                not isinstance(code, str) or code not in classes for code in codes):
            raise ValueError(f'{name}: use a nonempty list of top-level GAMS codes.')
        if len(codes) != len(set(codes)):
            raise ValueError(f'{name}: duplicate GAMS class.')
    subclasses = data.get('subclasses')
    if not isinstance(subclasses, dict):
        raise ValueError('GAMS subclasses must be a mapping.')
    for code, info in subclasses.items():
        if not re.fullmatch(r'[A-SZ][1-9][0-9]*', code) or not isinstance(info, dict) or (
                info.get('parent') != code[0] or code[0] not in classes
                or not isinstance(info.get('label'), str) or not info['label'].strip()):
            raise ValueError(f'{code}: invalid immediate GAMS subclass.')
    refined = data.get('subclass_assignments')
    if not isinstance(refined, dict) or set(refined) - expected:
        raise ValueError('GAMS subclass assignments contain unknown packages or are not a mapping.')
    for name, codes in refined.items():
        if not isinstance(codes, list) or not codes or any(
                not isinstance(code, str) or code not in subclasses
                or subclasses[code]['parent'] not in assignments[name] for code in codes):
            raise ValueError(f'{name}: subclass must exist and belong to an assigned parent class.')
        if len(codes) != len(set(codes)):
            raise ValueError(f'{name}: duplicate GAMS subclass.')
    notes = data.get('review_notes', {})
    if not isinstance(notes, dict) or set(notes) - expected or any(
            not isinstance(note, str) or not note.strip() for note in notes.values()):
        raise ValueError('Invalid GAMS review notes.')
    detailed = data.get('detailed_classes', {})
    if not isinstance(detailed, dict) or set(detailed) & (set(classes) | set(subclasses)):
        raise ValueError('Invalid or overlapping detailed GAMS classes.')
    tree = class_tree(data)
    for code, info in detailed.items():
        if (not re.fullmatch(r'[A-SZ][1-9][0-9]*(?:[a-z][0-9]*)+', code)
                or not isinstance(info, dict) or not isinstance(info.get('label'), str) or not info['label']
                or info.get('parent') not in tree or info['parent'] == code
                or not code.startswith(info['parent']) or len(code) <= len(info['parent'])):
            raise ValueError(f'{code}: invalid detailed GAMS class or parent.')
        ancestors(tree, code)
    mappings = data.get('procedure_mappings', [])
    if not isinstance(mappings, list):
        raise ValueError('Procedure mappings must be a list.')
    pins = {p['id']: p.get('revision') for p in packages}
    seen = set()
    for record in mappings:
        if not isinstance(record, dict) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', record.get('id', '')):
            raise ValueError('Invalid procedure mapping ID.')
        name = record.get('package_id')
        if record['id'] in seen or name not in pins or record.get('revision') != pins[name]:
            raise ValueError(f'{record["id"]}: duplicate ID, unknown package or stale revision.')
        seen.add(record['id'])
        if any(not isinstance(record.get(key), str) or not record[key] for key in ('module', 'procedure', 'derivatives')):
            raise ValueError(f'{record["id"]}: missing procedure identity or derivative requirements.')
        codes = record.get('gams_codes')
        if not isinstance(codes, list) or not codes or len(codes) != len(set(codes)):
            raise ValueError(f'{record["id"]}: invalid procedure classifications.')
        assigned = set(assignments[name] + refined.get(name, []))
        for code in codes:
            if code not in tree or not (set(ancestors(tree, code)) - set(detailed)).issubset(assigned):
                raise ValueError(f'{record["id"]}: classification lacks assigned ancestors.')
        if record.get('review_level') != 'source-reviewed' or not record.get('evidence'):
            raise ValueError(f'{record["id"]}: source review evidence required.')
        for item in record['evidence'] + record.get('author_examples', []):
            if (not isinstance(item, dict) or not safe_path(item.get('path'))
                    or not re.fullmatch(r'[0-9a-f]{64}', item.get('sha256', ''))):
                raise ValueError(f'{record["id"]}: invalid pinned source evidence.')
    return data


def package_classes(data, name):
    codes = data['packages'][name] + data['subclass_assignments'].get(name, [])
    for record in procedure_records(data, name):
        codes += record['gams_codes']
    tree = class_tree(data)
    expanded = {ancestor for code in codes for ancestor in ancestors(tree, code)}
    return [{'code': code, **tree[code]} for code in sorted(expanded, key=class_order)]


def class_tree(data):
    return {**{code: {'label': label, 'parent': None} for code, label in data['classes'].items()},
            **data['subclasses'], **data.get('detailed_classes', {})}


def ancestors(tree, code):
    result = []
    while code is not None:
        if code not in tree or code in result:
            raise ValueError('Invalid or cyclic GAMS hierarchy.')
        result.append(code)
        code = tree[code]['parent']
    return result


def safe_path(value):
    return (isinstance(value, str) and value and '\\' not in value and ':' not in value
            and not PurePosixPath(value).is_absolute() and '..' not in PurePosixPath(value).parts)


def procedure_records(data, name):
    return [record for record in data.get('procedure_mappings', []) if record['package_id'] == name]


def driver_data(root=ROOT, data=None):
    root = Path(root)
    data = data or gams_data(root)
    manifest = json.loads((root / 'fpm_catalog/gams-drivers.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1 or not isinstance(manifest.get('drivers'), list):
        raise ValueError('Invalid GAMS driver manifest.')
    checks = json.loads((root / 'docs/gams-g1-validation.json').read_text(encoding='utf-8'))
    verified = {row['driver_id']: row for row in checks['drivers']}
    mappings = {record['id']: record for record in data.get('procedure_mappings', [])}
    seen = set()
    for driver in manifest['drivers']:
        identity = driver.get('id')
        record = mappings.get(driver.get('procedure_id'))
        if (not identity or identity in seen or record is None or record.get('driver_id') != identity
                or driver.get('package_id') != record['package_id'] or driver.get('revision') != record['revision']
                or driver.get('gams_code') not in record['gams_codes']):
            raise ValueError(f'{identity}: driver and pinned procedure disagree.')
        seen.add(identity)
        for path in [driver.get('path'), *driver.get('license_files', [])]:
            if not safe_path(path) or not (root / path).is_file():
                raise ValueError(f'{identity}: missing source or license file.')
        checksum = hashlib.sha256((root / driver['path']).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        report = verified.get(identity, {})
        if (not report.get('ok') or report.get('source_revision') != record['revision']
                or report.get('source_sha256') != checksum or not re.search(r'GNU Fortran.*16\.', report.get('compiler', ''))):
            raise ValueError(f'{identity}: current source requires a passing GNU 16 verification.')
    return manifest['drivers']


def class_order(code):
    return tuple((0, int(part)) if part.isdigit() else (1, part) for part in re.findall(r'[A-Za-z]+|[0-9]+', code))


def subclass_module(data):
    return '// Generated by xfpm_examples.py from fpm_catalog/gams.json; do not edit.\n' + (
        'export const gamsSubclasses = ' + json.dumps({**data['subclasses'], **data.get('detailed_classes', {})}, indent=2) + ';\n')


def review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    counts = Counter(c['code'] for name in data['packages'] for c in package_classes(data, name))
    lines = ['# GAMS classifications for selected packages', '',
             f'All {len(packages)} selected packages have one or more top-level assignments from the '
             f'[NIST GAMS classification scheme]({GAMS_URL}). The assignments are maintained by the playground; '
             'they are not NIST or package-author endorsements.', '',
             f'{len(data["subclass_assignments"])} packages also have immediate subclass assignments. '
             f'The saved taxonomy contains {len(data["subclasses"])} immediate subclasses, retrieved from the '
             f'linked NIST parent pages on {data["taxonomy_retrieved_on"]}. B, O, P, Q, and Z have no published immediate subclasses. '
             'Broader assignments are retained where an immediate subclass does not fit or requires further review.', '',
             'The [G1 pilot](gams-g1.md) adds Univariate (G1a) and Multivariate (G1b), '
             'with pinned procedure mappings, author-example references, and sandbox-tested demonstrations.', '',
             'These discovery assignments are based on saved descriptions, topics, bundled examples, and '
             'upstream documentation where reviewed. '
             'A class indicates relevant package functionality, not coverage of every problem in that class. '
             'The G1 pilot provides procedure-level evidence; other branches remain discovery classifications. '
             'Comparative benchmarks remain future work.', '',
             '## Searching', '',
             'Choose **GAMS class** in the hosted or main local FPM page. It combines with the text search, '
             'Category, topic-source choice, and sort order. Choose **All classes** to clear it. '
             'Choose **Subclass** after selecting a parent. A parent includes all packages assigned under it; '
             'a subclass matches only explicit reviewed assignments, not packages known only at the parent level. '
             'The explicit search syntax `GAMS D` (or `GAMS: D2`) uses the same hierarchy; ordinary searches also include '
             'the assigned class descriptions. GAMS classification is independent of the GitHub-only topic setting.', '',
             'Selected package details link to the NIST definitions. Other collections are not comprehensively '
             'classified: the translated R collection hides the filter, and the retained All collection includes '
             'assignments only for selected packages. Unclassified entries are excluded when a class is selected. '
             'Changing collections clears the class filter. Browsing and filtering do not submit jobs or contact NIST; '
             'opening a definition link visits NIST.', '',
             '## Classes', '', '| Code | NIST class | Selected packages |', '| --- | --- | --- |']
    labels = {code: info['label'] for code, info in class_tree(data).items()}
    for code in sorted(labels, key=class_order):
        label = labels[code]
        lines.append(f'| [{code}]({GAMS_URL}/Class/{code}) | {label} | {counts[code]} |')
    lines.extend(['', 'Counts overlap because a package may implement several kinds of problems. '
                  'All 20 parents and their immediate subclasses remain available, including classes with no current assignments. '
                  'Each package is counted once per class. C1 and C10, like L1 and L10, are siblings; '
                  'shared code prefixes do not imply an ancestor relationship.', '',
                  '## Classification choices', '',
                  '- Random-number generators use **L**, whose L6 subclass is random number generation. '
                  '[M](https://gams.nist.gov/cgi-bin/serve.cgi/Class/M) is reserved for simulation and stochastic modeling; '
                  'a stochastic optimization algorithm is classified under G rather than M just because it uses random numbers.',
                  '- Least-squares approximation and smoothing can appear under **K**, alongside **D**, **G**, or **L** '
                  'when the package also provides linear solvers, optimization, or statistical regression.',
                  '- Numeric expression parsers use **C/N**. Evaluating strings is not evidence of symbolic algebra under **O**.',
                  '- **P** includes geometric operations and graph algorithms; **N** includes graph storage and other data structures.',
                  '- **R** includes precision-support constants, error handling, and date/time services. '
                  'Domain-specific physical constants and thermodynamic properties use **Z**.', '',
                  '- Date/time services retain R: there is no immediate date/time subclass. '
                  'General programming support can retain S without being forced into transformation, static analysis, or dynamic analysis.',
                  '- H1 includes numerical derivative APIs, including automatic differentiation; '
                  'this assignment does not imply finite-difference implementation.', '',
                  '## Packages', '', '| Package at catalog revision | GAMS classes | Description | Review notes and example |', '| --- | --- | --- | --- |'])
    for package in sorted(packages, key=lambda p: p['id'].casefold()):
        classes = ', '.join(f'[{c["code"]} — {c["label"]}]({GAMS_URL}/Class/{c["code"]})'
                            for c in package_classes(data, package['id']))
        description = package['description'].replace('|', '\\|').replace('\n', ' ')
        source = f'https://github.com/{package["repository"]}/tree/{package["revision"]}'
        note = data.get('review_notes', {}).get(package['id'], '').replace('|', '\\|')
        example = f'[Catalog example](../fpm_catalog/demos/{package["id"]}.f90)'
        lines.append(f'| [{package["id"]}]({source}) | {classes} | {description} | {note} {example} |')
    lines.extend(['', 'The linked examples are aids for further review; one example does not validate every assigned capability.', '',
                  '## Procedure mappings and drivers', '',
                  'For deeper classifications, identify the actual module and procedure at the pinned revision. '
                  'Check author-provided examples and tests before writing a driver. Reuse or adapt them when suitable, '
                  'recording the original path, revision, license, and modifications. A shared mathematical problem '
                  'and external accuracy criteria are still needed for comparisons across packages.', ''])
    lines.extend(['', '## Maintaining assignments', '',
                  'Edit [gams.json](../fpm_catalog/gams.json). Keep assignments separate from GitHub topics and '
                  'playground topics, and add an entry whenever a selected package is added. Use multiple classes '
                  'only for functionality the package provides. Keep root assignments in `packages`, immediate '
                  'assignments in `subclass_assignments`, official labels/parents in `subclasses`, and '
                  'qualifications in `review_notes`. Deeper labels belong in `detailed_classes`; '
                  '`procedure_mappings` records their pinned source evidence and derivative requirements. '
                  'A child assignment must have its ancestors assigned.', '', '```text',
                  'python xpackage_gams.py', 'python xfpm_examples.py', '```', '',
                  'The first command validates complete catalog coverage and regenerates this page. '
                  'Use `python xpackage_gams.py --check` to check it without writing. The second regenerates '
                  'the public catalog assets. Both commands are offline; neither builds packages nor redeploys '
                  'the execution service. Class labels in the HTML filter and generated subclass module are '
                  'checked against this metadata by tests.', ''])
    return '\n'.join(lines)


def g1_review_text(root=ROOT):
    data = gams_data(root)
    packages = {p['id']: p for p in json.loads((Path(root) / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    drivers = driver_data(root, data)
    lines = ['# GAMS G1 procedure review', '',
             'This pilot refines unconstrained optimization into '
             '[G1a: Univariate](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1a) and '
             '[G1b: Multivariate](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1b). '
             'It covers 11 procedure mappings in seven selected packages. '
             'Assignments describe specific functionality at pinned revisions, not complete coverage of a class.', '',
             '## Reviewed procedures', '',
             '| Package | Module / procedure | Class | Derivatives | Source and author examples | Notes |',
             '| --- | --- | --- | --- | --- | --- |']
    for p in data['procedure_mappings']:
        package = packages[p['package_id']]
        base = f'https://github.com/{package["repository"]}/blob/{p["revision"]}/'
        links = [f'[Source]({base}{e["path"]}#L{e["line"]})' for e in p['evidence']]
        links += [f'[Author example]({base}{e["path"]})' for e in p['author_examples']]
        cells = [p['package_id'], f'`{p["module"]}` / `{p["procedure"]}`',
                 ', '.join(p['gams_codes']), p['derivatives'], ' · '.join(links), p['notes']]
        lines.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    lines += ['', 'Nonlin’s Brent example finds a root; it is not evidence of univariate minimization. '
              'The NLopt author example reviewed uses constrained MMA, so it is not offered as a G1 driver. '
              'Neural-fortran training is network-specific, rather than a general objective callback API. '
              'ForTimize has no clear source license at the reviewed revision; its author example is linked, not copied.', '',
              '## Working demonstrations', '',
              'These drivers adapt author examples, retain their license notices, move callbacks into modules, '
              'and add independent accuracy checks and readable output. Loading a link does not submit a job.', '',
              '| Driver | Problem / class | Original example | License |', '| --- | --- | --- | --- |']
    for d in drivers:
        package = packages[d['package_id']]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        original = f'https://github.com/{package["repository"]}/blob/{d["revision"]}/{d["author_example"]}'
        licenses = ', '.join(f'[License](../{path})' for path in d['license_files'])
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["problem_id"]} / {d["gams_code"]} | [Original]({original}) | {d["license"]} · {licenses} |')
    lines += ['', 'All three drivers passed the hosted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
              'The [saved verification results](gams-g1-validation.json) include source hashes and program output. '
              'Publishing checks that these hashes and package revisions still match.', '',
              'The sine driver minimizes sin(x) on [-4,0] and checks the solution against −π/2. '
              'Both Bard drivers fit the same 15 observations, start from (1,1,1), and check against '
              '(0.08241058, 1.133037, 2.343695), with maximum parameter error below 0.0002. '
              'Both require the residual norm to differ from 0.09063596 by less than 0.0000001. '
              'MINPACK estimates the Jacobian by finite differences; libdogleg uses an analytic Jacobian. '
              'Callback counts and individual sandbox timings are not a fair performance ranking.', '',
              'The examples are also available in the hosted and main local FPM playground example menu. '
              'For local use, load a driver and download the complete FPM project, or use its source as '
              'an application in an FPM project depending on the linked pinned package.', '',
              '## Maintenance and portability', '',
              'Procedure evidence, revision pins, derivative requirements, author-example paths, and raw upstream '
              'SHA-256 hashes are recorded in [gams.json](../fpm_catalog/gams.json). '
              'Driver provenance and licenses are in [gams-drivers.json](../fpm_catalog/gams-drivers.json). '
              'Driver hashes normalize UTF-8 line endings to LF. '
              'The portable catalog export includes both the procedure mappings and demonstrations.', '',
              'Run `python xpackage_gams.py` and `python xfpm_examples.py` after changing reviewed metadata. '
              'Changed drivers must be verified again on GNU Fortran 16 before publication. '
              'These metadata and example changes require no backend deployment or package recompilation.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated review page is out of date')
    args = parser.parse_args()
    for report, text in ((REPORT, review_text()), (PILOT_REPORT, g1_review_text())):
        path = ROOT / report
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                parser.exit(1, f'{report} is out of date. Run python xpackage_gams.py.\n')
        else:
            path.write_text(text, encoding='utf-8')
            print(f'Wrote {report.as_posix()}')
    if args.check:
        print('GAMS assignments and review pages verified.')


if __name__ == '__main__':
    main()
