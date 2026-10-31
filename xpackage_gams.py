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
NUMERICAL_REPORT = Path('docs/gams-numerical.md')
QUADRATURE_REPORT = Path('docs/gams-quadrature.md')
ROOTS_REPORT = Path('docs/gams-roots.md')
LINEAR_ALGEBRA_REPORT = Path('docs/gams-linear-algebra.md')
ODE_REPORT = Path('docs/gams-ode.md')
INTERPOLATION_REPORT = Path('docs/gams-interpolation.md')
TRANSFORMS_REPORT = Path('docs/gams-transforms.md')
CONSTRAINED_REPORT = Path('docs/gams-constrained.md')
SPECIAL_FUNCTIONS_REPORT = Path('docs/gams-special-functions.md')
STATISTICS_REPORT = Path('docs/gams-statistics.md')
RANDOM_REPORT = Path('docs/gams-random.md')
DIFFERENTIATION_REPORT = Path('docs/gams-differentiation.md')
SYSTEMS_REPORT = Path('docs/gams-systems.md')
SPARSE_REPORT = Path('docs/gams-sparse.md')
CUBATURE_REPORT = Path('docs/gams-cubature.md')
SURFACES_REPORT = Path('docs/gams-surfaces.md')
STIFF_REPORT = Path('docs/gams-stiff.md')
POLYNOMIAL_REPORT = Path('docs/gams-polynomial.md')
CONVOLUTION_REPORT = Path('docs/gams-convolution.md')
REGRESSION_REPORT = Path('docs/gams-regression.md')
MATRIX_EQUATIONS_REPORT = Path('docs/gams-matrix-equations.md')
COVERAGE_REPORT = Path('docs/gams-coverage.md')
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
                or info['parent'] != ''.join(re.findall(r'[A-Z]|[0-9]+|[a-z]', code)[:-1])):
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


def g1_procedures(data):
    tree = class_tree(data)
    return [p for p in data.get('procedure_mappings', [])
            if any('G1' in ancestors(tree, code) for code in p['gams_codes'])]


def numerical_review(root=ROOT, data=None):
    root = Path(root)
    data = data or gams_data(root)
    review = json.loads((root / 'fpm_catalog/gams-numerical-review.json').read_text(encoding='utf-8'))
    expected = {name for name, codes in data['packages'].items() if set(codes) & set('ABCDEFGHIJKLMP')}
    if review.get('schema') != 1 or set(review.get('packages', {})) != expected:
        raise ValueError('Numerical GAMS review must cover every selected A-M/P package.')
    pins = {p['id']: p for p in json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    for name, entry in review['packages'].items():
        records = procedure_records(data, name)
        if (entry.get('revision') != pins[name]['revision']
                or entry.get('archive_sha256') != pins[name]['archive_sha256']
                or entry.get('status') not in ('procedure-reviewed', 'support-only')
                or not isinstance(entry.get('notes'), str) or not entry['notes']
                or entry.get('procedure_ids') != [p['id'] for p in records]
                or (entry['status'] == 'procedure-reviewed' and not records)
                or (entry['status'] == 'support-only' and records)):
            raise ValueError(f'{name}: stale or incomplete numerical GAMS review.')
        if entry['status'] == 'support-only' and not entry.get('evidence'):
            raise ValueError(f'{name}: support-only review needs source evidence.')
    return review


def numerical_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = {d['id']: d for d in driver_data(root, data)}
    review = numerical_review(root, data)
    packages = {p['id']: p for p in json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    reviewed = review['packages']
    mappings = [p for p in data['procedure_mappings'] if p['package_id'] in reviewed]
    supported = sum(p['status'] == 'support-only' for p in reviewed.values())
    tree = class_tree(data)
    lines = ['# Numerical package GAMS review', '',
             f'All {len(reviewed)} selected packages with a top-level A–M or P assignment have been reviewed '
             f'at their pinned revisions: {len(reviewed) - supported} have procedure mappings and '
             f'{supported} supplies supporting declarations rather than numerical procedures. '
             f'There are {len(mappings)} procedure records. This scope includes arithmetic, statistics, '
             'geometry, and supporting data utilities, alongside numerical solvers.', '',
             'This is an initial procedure-level coverage pass, not an exhaustive inventory of every routine '
             'or every overload. Specific assignments require evidence for the named procedure and configuration. '
             'Other package capabilities remain discovery classifications. Source review does not imply a new '
             'compilation test, accuracy certification, or benchmark.', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the additional detailed '
             'labels and hierarchy; the existing top-level and immediate classifications come from '
             '[NIST GAMS](https://gams.nist.gov/cgi-bin/serve.cgi). '
             'Labels such as “General” must be read with their ancestors. C1/C10 and L1/L10 are siblings, '
             'and explicit parent links preserve that distinction.', '',
             '## Coverage and remaining work', '',
             '“Discovery only” lists existing immediate package assignments without a matching procedure record. '
             'These are a review queue, not evidence that a capability is missing. No class is forced onto a '
             'package merely to fill a gap.', '',
             '| Package | Procedure records | Discovery only | Review scope |', '| --- | --- | --- | --- |']
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    for name, entry in reviewed.items():
        package = packages[name]
        records = procedure_records(data, name)
        mapped = {c for p in records for code in p['gams_codes'] for c in ancestors(tree, code)}
        remaining = set(data['subclass_assignments'].get(name, [])) - mapped
        url = f'https://github.com/{package["repository"]}/tree/{entry["revision"]}'
        codes = ', '.join(sorted(remaining, key=class_order)) or '—'
        scope = entry['notes'] if entry['status'] == 'support-only' else 'Selected APIs; see evidence below.'
        lines.append(f'| [{name}]({url}) | {len(records)} | {codes} | {cell(scope)} |')
    categories = sorted({packages[p['package_id']]['category'] for p in mappings})
    for category in categories:
        lines += ['', f'## {category}', '',
                  '| Package / public API | GAMS | Derivatives or callback requirements | Pinned evidence and author examples/tests | Qualifications |',
                  '| --- | --- | --- | --- | --- |']
        for p in sorted((p for p in mappings if packages[p['package_id']]['category'] == category),
                        key=lambda p: (p['package_id'], p['id'])):
            package = packages[p['package_id']]
            base = f'https://github.com/{package["repository"]}/blob/{p["revision"]}/'
            links = [f'[Source]({base}{e["path"]}#L{e["line"]})' for e in p['evidence']]
            links += [f'[Author example/test]({base}{e["path"]})' for e in p['author_examples']]
            if not p['author_examples']:
                links.append('No matching author example recorded')
            links.append(f'[Catalog main](../fpm_catalog/demos/{p["package_id"]}.f90)')
            if p.get('driver_id'):
                review_path = drivers[p['driver_id']].get('review_path', 'docs/gams-g1.md')
                links.append(f'[Verified driver]({Path(review_path).name})')
            codes = ', '.join(f'[{code}](https://gams.nist.gov/cgi-bin/serve.cgi/Class/{code})' for code in p['gams_codes'])
            values = [f'{p["package_id"]}: `{p["module"]}` / `{p["procedure"]}`', codes,
                      p['derivatives'], ' · '.join(links), p['notes']]
            lines.append('| ' + ' | '.join(cell(v) for v in values) + ' |')
    lines += ['', '## Evidence and next steps', '',
              '- Source archives were downloaded at catalog revisions and checked against the catalog archive SHA-256 hashes. '
              'Procedure and example records include paths, source SHA-256 hashes, and source line anchors.',
              '- Author examples and tests are usage candidates, not a promise that they run unchanged within sandbox limits. '
              'The catalog main may exercise only one of the package’s mapped APIs. '
              'The separately recorded [optimization drivers](gams-g1.md), [quadrature drivers](gams-quadrature.md), '
              '[scalar-root drivers](gams-roots.md), [linear-algebra drivers](gams-linear-algebra.md) '
              '[ODE drivers](gams-ode.md), [interpolation drivers](gams-interpolation.md) '
              '[transform drivers](gams-transforms.md), [constrained-optimization drivers](gams-constrained.md) '
              '[special-function drivers](gams-special-functions.md), [statistics drivers](gams-statistics.md), [random-generator drivers](gams-random.md), [differentiation drivers](gams-differentiation.md), [nonlinear-system drivers](gams-systems.md), [sparse/positive-definite drivers](gams-sparse.md), [cubature/rule drivers](gams-cubature.md), [surface-interpolation drivers](gams-surfaces.md), [stiff-ODE drivers](gams-stiff.md), [polynomial-root drivers](gams-polynomial.md), [convolution drivers](gams-convolution.md), [regression drivers](gams-regression.md) and [matrix-equation drivers](gams-matrix-equations.md) '
              'carry the driver-verification designation.',
              '- Generic APIs retain broader classes where real/complex arithmetic, matrix structure, derivatives, '
              'or constraints depend on configuration. Detailed optimization mappings state the derivative mode; '
              'derivative-free modes need separate records.',
              '- Next, refine the discovery-only queue, split overloaded APIs where useful, and adapt suitable author '
              'examples into independently checked drivers. Use common mathematical problems when comparing packages; '
              'one successful example is not a performance ranking.', '',
              '## Maintenance', '',
              'Edit procedure mappings in [gams.json](../fpm_catalog/gams.json) and update the coverage ledger '
              '[gams-numerical-review.json](../fpm_catalog/gams-numerical-review.json). '
              'Revision and archive pins must match the selected catalog. The ledger explicitly records supporting '
              'utilities and prevents a newly added numerical package from silently escaping review.', '',
              'Run `python xpackage_gams.py` to validate and regenerate the review pages, '
              '`python xfpm_examples.py` to publish search metadata, and `python xcatalog_export.py` '
              'to export the reusable classifications. These commands do not compile packages or redeploy Modal.', '']
    return '\n'.join(lines)


def driver_data(root=ROOT, data=None):
    root = Path(root)
    data = data or gams_data(root)
    manifest = json.loads((root / 'fpm_catalog/gams-drivers.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1 or not isinstance(manifest.get('drivers'), list):
        raise ValueError('Invalid GAMS driver manifest.')
    reports = {}
    mappings = {record['id']: record for record in data.get('procedure_mappings', [])}
    seen = set()
    for driver in manifest['drivers']:
        identity = driver.get('id')
        report_path = driver_validation_path(driver)
        if report_path not in reports:
            checks = json.loads((root / report_path).read_text(encoding='utf-8'))
            verified = {row['driver_id']: row for row in checks['drivers']}
            if checks.get('schema') != 1 or len(verified) != len(checks['drivers']):
                raise ValueError('Invalid or duplicate GAMS driver verification records.')
            reports[report_path] = verified
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
        report = reports[report_path].get(identity, {})
        runs = [s for s in report.get('stages', []) if s.get('name') == 'Run']
        if (not report.get('ok') or report.get('source_revision') != record['revision']
                or report.get('source_sha256') != checksum or not re.search(r'GNU Fortran.*16\.', report.get('compiler', ''))
                or not report.get('library_reused') or len(runs) != 1
                or not runs[0].get('ok') or runs[0].get('exit_code') != 0
                or 'PASS '+identity not in runs[0].get('stdout', '').splitlines()):
            raise ValueError(f'{identity}: current source requires a passing GNU 16 verification.')
    return manifest['drivers']


def driver_validation_path(driver):
    path = driver.get('validation_path', 'docs/gams-g1-validation.json')
    if not safe_path(path) or not path.startswith('docs/') or not path.endswith('.json'):
        raise ValueError('Driver verification report must be a relative docs JSON path.')
    return path


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
             'Browse the [standalone GAMS catalog](https://beliavsky.github.io/fortran-playground/gams/) '
             'for class pages, package details, pinned procedure evidence and playground links. '
             'It is generated from the same metadata during every Pages build; see [maintenance and local preview](gams-site.md).', '',
             f'{len(data["subclass_assignments"])} packages also have immediate subclass assignments. '
             f'The saved taxonomy contains {len(data["subclasses"])} immediate subclasses, retrieved from the '
             f'linked NIST parent pages on {data["taxonomy_retrieved_on"]}. B, O, P, Q, and Z have no published immediate subclasses. '
             'Broader assignments are retained where an immediate subclass does not fit or requires further review.', '',
             'The [G1 pilot](gams-g1.md) adds Univariate (G1a) and Multivariate (G1b), '
             'with pinned procedure mappings, author-example references, and sandbox-tested demonstrations.', '',
             'The [numerical package review](gams-numerical.md) extends source-reviewed procedure mappings '
             'across the selected numerical, statistical, geometry, and supporting packages, '
             'and records capabilities that still need procedure-level review.', '',
             'The [coverage report](gams-coverage.md) separates source-reviewed mappings from class-specific '
             'checked drivers and lists remaining gaps. Reaching a taxonomy leaf does not exhaust its procedures or use cases.', '',
             'These discovery assignments are based on saved descriptions, topics, bundled examples, and '
             'upstream documentation where reviewed. '
             'A class indicates relevant package functionality, not coverage of every problem in that class. '
             'Procedure mappings provide source-level evidence for specific APIs; other capabilities retain discovery classifications. '
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
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'G1' in ancestors(tree, d['gams_code'])]
    mappings = g1_procedures(data)
    lines = ['# GAMS G1 procedure review', '',
             'Unconstrained optimization is refined by dimension, smoothness and user-supplied derivatives, using the '
             '[Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). '
             f'This review covers {len(mappings)} procedure mappings in '
             f'{len({p["package_id"] for p in mappings})} selected packages. '
             'Assignments describe specific functionality at pinned revisions, not complete coverage of a class.', '',
             '## Detailed problem classes', '',
             '| Class | Problem | User-supplied derivatives |', '| --- | --- | --- |',
             '| [G1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1a1a) | Smooth univariate minimization | None |',
             '| [G1b1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1b1a) | Smooth multivariate minimization | None |',
             '| [G1b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1b1b) | Smooth multivariate minimization | First derivatives |', '',
             'Finite-difference mode and analytic-gradient mode are classified separately. For smooth nonlinear '
             'least squares, an analytic residual Jacobian supplies first-derivative information for the '
             'squared-residual objective. Those solvers retain their specialized residual/Jacobian interfaces. '
             'Broader mappings remain where a more specific review has not been made.', '',
             '## Reviewed procedures', '',
             '| Package | Module / procedure | Class | Derivatives | Source and author examples | Notes |',
             '| --- | --- | --- | --- | --- | --- |']
    for p in mappings:
        package = packages[p['package_id']]
        base = f'https://github.com/{package["repository"]}/blob/{p["revision"]}/'
        links = [f'[Source]({base}{e["path"]}#L{e["line"]})' for e in p['evidence']]
        links += [f'[Author example]({base}{e["path"]})' for e in p['author_examples']]
        cells = [p['package_id'], f'`{p["module"]}` / `{p["procedure"]}`',
                 ', '.join(p['gams_codes']), p['derivatives'], ' · '.join(links), p['notes']]
        lines.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    lines += ['', 'Nonlin’s Brent example finds a root; it is not evidence of univariate minimization. '
              'The NLopt author example reviewed uses constrained MMA; the unconstrained Rosenbrock driver is independently written. '
              'Neural-fortran training is network-specific, rather than a general objective callback API. '
              'ForTimize has no clear source license at the reviewed revision; its author example is linked, not copied.', '',
              '## Working demonstrations', '',
              'Author examples are adapted where suitable, with license notices retained. Independently written '
              'API drivers are identified below. Drivers use module callbacks, independent accuracy checks and '
              'readable output. Loading a link does not submit a job.', '',
              '| Driver | Problem / class | Driver origin | License |', '| --- | --- | --- | --- |']
    for d in drivers:
        package = packages[d['package_id']]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        original = (f'[Author example](https://github.com/{package["repository"]}/blob/{d["revision"]}/{d["author_example"]})'
                    if d.get('author_example') else 'Independent API driver')
        licenses = ', '.join(f'[License](../{path})' for path in d['license_files'])
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["problem_id"]} / {d["gams_code"]} | {original} | {d["license"]} · {licenses} |')
    lines += ['', f'All {len(drivers)} drivers passed the hosted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
              'The [saved verification results](gams-g1-validation.json) include source hashes and program output. '
              'Publishing checks that these hashes and package revisions still match.', '',
              'The sine driver minimizes sin(x) on [-4,0] and checks the solution against −π/2. '
              'Both Bard drivers fit the same 15 observations, start from (1,1,1), and check against '
              '(0.08241058, 1.133037, 2.343695), with maximum parameter error below 0.0002. '
              'Both require the residual norm to differ from 0.09063596 by less than 0.0000001. '
              'MINPACK estimates the Jacobian by finite differences; libdogleg uses an analytic Jacobian. '
              'Callback counts and individual sandbox timings are not a fair performance ranking.', '',
              '## Common Rosenbrock problem', '',
              'The three Rosenbrock drivers minimize `(1-x)^2 + 100*(y-x^2)^2`, starting from `(-1.2,1)`. '
              'They independently check the known minimizer `(1,1)` with maximum parameter error at most `1e-4`, '
              'objective at most `1e-10`, finite results and agreement with the solver-reported objective. '
              'The gradient-based drivers first check their analytic gradient against central differences. '
              'Solver termination settings differ across APIs; the independent acceptance checks are shared.', '',
              '| Driver | Maximum parameter error | Independent objective | Objective calls | Gradient calls |',
              '| --- | --- | --- | --- | --- |']
    validation = json.loads((Path(root)/'docs/gams-g1-validation.json').read_text(encoding='utf-8'))
    checks = {r['driver_id']: r for r in validation['drivers']}
    for d in drivers:
        if d['problem_id'] != 'rosenbrock-2':
            continue
        output = next(s['stdout'] for s in checks[d['id']]['stages'] if s['name'] == 'Run')
        def value(label):
            return next(line.split(':', 1)[1].strip() for line in output.splitlines() if line.startswith(label+':'))
        lines.append('| '+d['id']+' | '+' | '.join(value(label) for label in
                     ('Maximum parameter error', 'Independent objective', 'Objective callback calls', 'Gradient callback calls'))+' |')
    lines += ['', 'Counts describe the recorded runs, exclude the preliminary gradient checks and do not establish '
              'a general performance ranking. Derivative-free and analytic-gradient methods perform different work. '
              'All libraries were reused; only the supplied main programs and executables were compiled.', '',
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
              'With Modal installed and authenticated, verify selected drivers against the existing compiled images:', '',
              '```text',
              'python xverify_gams_drivers.py --drivers nonlin-rosenbrock-nm nonlin-rosenbrock-bfgs nlopt-rosenbrock-lbfgs',
              '```', '',
              'The verifier uses the local `.fpm-audit-cache/precompiled.json` build report and records results '
              'in `docs/gams-g1-validation.json`. It does not rebuild package libraries or deploy the service. '
              'These metadata and example changes require no backend deployment or package recompilation.', '']
    return '\n'.join(lines)


def quadrature_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'H2' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS quadrature drivers', '',
             'These examples connect specific integration procedures to finite-interval GAMS problem classes. '
             'They are checked consumer programs at the catalog source revisions, rather than tests of every '
             'quadrature rule or a performance benchmark.', '',
             '| Class | Problem | Procedures |', '| --- | --- | --- |',
             '| [H2a1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a1a1) | Automatic one-dimensional integration on a finite interval, integrand supplied as a procedure | QUADPACK `dqag`; quadrature-fortran `integration_class_1d%integrate` |',
             '| [H2a2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2a1) | Automatic finite-interval integration for special integrands supplied as procedures | QUADPACK `dqags`, demonstrated with integrable endpoint singularities |', '',
             '## Shared smooth-integral checks', '',
             'Both smooth drivers integrate `exp(x)` and `cos(20*x)` over `[0,1]`. Analytic reference values '
             'are `exp(1)-1` and `sin(20)/20`. They request accuracy `1e-10` and independently require absolute '
             'error at most `1e-9`. QUADPACK uses `dqag` key 1 (15-point Gauss-Kronrod); quadrature-fortran uses '
             'its adaptive 8-point Gaussian method. These algorithm settings differ even though the functions, '
             'intervals and independent acceptance checks are shared.', '',
             '## Endpoint singularities', '',
             'The `dqags` driver adapts the author\'s inverse-square-root test and adds a logarithmic variant: '
             '`integral(1/sqrt(x),0,1)=2` and `integral(log(x)/sqrt(x),0,1)=-4`. '
             'It requests absolute/relative accuracy `1e-10` and independently requires absolute error at most '
             '`1e-8`. The module callback rejects evaluation at the singular endpoint. The driver does not '
             'claim support for every special integrand in H2a2a1.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author test |', '| --- | --- | --- |']
    for d in drivers:
        package = packages[d['package_id']]
        base = f'https://github.com/{package["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Driver source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author test]({base}{d["author_example"]}) |')
    lines += ['', 'Loading a link selects code without submitting a job. The same drivers are available in the '
              'hosted and main local FPM playgrounds and in downloaded FPM projects. Author license notices '
              'are retained with the drivers.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
              'Existing package libraries were reused; only each main and executable were compiled. '
              'The [verification report](gams-quadrature-validation.json) locks the driver hashes and source revisions.', '',
              'Success is status `0` for QUADPACK and `1` for quadrature-fortran. The latter reports a signed '
              'error estimate. Estimates are printed separately from actual errors against the analytic references; '
              'they are not certified error bounds. Zero printed actual error means agreement at the working '
              'floating-point precision. Evaluation counts describe these runs and do not establish a general speed ranking.']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['', '### '+d['id'], '', '```text', output.rstrip(), '```']
    lines += ['', '## Maintenance', '',
              'After changing a driver, verify it again using existing compiled package images:', '',
              '```text',
              'python xverify_gams_drivers.py --drivers quadpack-smooth quadrature-fortran-smooth quadpack-endpoint-singular',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'The verifier requires Modal authentication and the local `.fpm-audit-cache/precompiled.json` '
              'build report. Each driver manifest entry identifies its verification report, allowing optimization '
              'and quadrature evidence to be maintained separately. Publication checks the correct report for '
              'every driver. These examples and classifications require no backend redeployment or library rebuild.', '']
    return '\n'.join(lines)


def roots_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data) if d['gams_code'] == 'F1b']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS scalar-root drivers', '',
             'These consumer programs solve two nonpolynomial scalar equations using roots-fortran Brent, '
             'nonlin Brent and nonlin safeguarded Newton. They map to '
             '[F1b: nonpolynomial single equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F1b). '
             'F1b has no deeper derivative-specific classes; the procedure records distinguish derivative requirements.', '',
             '## Shared checks', '',
             '| Equation | Bracket | Reference root |', '| --- | --- | --- |',
             '| `sin(x)/x = 0` | `[1.5,5]` | `pi` |',
             '| `exp(x)-2 = 0` | `[0,2]` | `log(2)` |', '',
             'Each driver requests function/variable tolerances `1e-12` and independently requires both root error '
             'and absolute residual at most `1e-9`. It checks convergence, finite results, bracket membership and '
             'agreement between the returned residual and a fresh function evaluation. Counters include solver '
             'callbacks only. The Newton driver supplies an analytic derivative, checks it against a central '
             'difference at the bracket midpoint, resets the counters and verifies that the solver uses it. '
             'nonlin chooses its initial point from the bracket; these drivers do not assume that its input '
             'root variable controls the initial iterate.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure | Author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        author = f'[Example]({base}{d["author_example"]})' if d['author_example'] else 'Original driver using the public object API'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) | {author} |')
    lines += ['', 'The nonlin drivers adapt the author examples, including the `sin(x)/x` equation; MIT '
              'notices are retained. Loading a link selects code without submitting a job. These examples '
              'also appear in the main local FPM playground and downloaded FPM projects.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing '
              'package libraries were reused; only the mains and executables were rebuilt. The '
              '[verification report](gams-roots-validation.json) records source hashes, revisions and run output. '
              'Evaluation counts describe these two cases, rather than a general performance ranking. '
              'Zero printed error means agreement at working precision.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers roots-fortran-brent nonlin-roots-brent nonlin-roots-newton',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def linear_algebra_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'D' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS linear-algebra drivers', '',
             'These real64 consumer programs compare fortran-lapack and stdlib on the same small '
             'dense systems and unconstrained least-squares problems, with additional fortran-lapack '
             'matrix-decomposition examples. Procedure mappings describe the '
             'reviewed real configurations; other overloads require their own evidence.', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [D2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a1) | Real nonsymmetric general linear systems | `linear_algebra:solve`; `stdlib_linalg:solve` |',
             '| [D9a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9a1) | Unconstrained linear least squares, L2 solution | `linear_algebra:lstsq`; `stdlib_linalg:lstsq` |',
             '| [D4a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D4a1) | Ordinary real symmetric eigenproblems | fortran-lapack `la_lapack:syev`, real64 overload |',
             '| [D5](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D5) | Orthogonalization, demonstrated by reduced QR | fortran-lapack `linear_algebra:qr` |',
             '| [D6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D6) | Singular value decomposition | fortran-lapack `la_lapack:gesvd`, real64 overload |', '',
             '## Shared dense-system checks', '',
             'Both solve drivers use the 3-by-3 systems from stdlib `example_solve1` and fortran-lapack '
             '`test_dsolve`, with reference solutions `[5,3,-2]` and `[-2,-2,3]`. They preserve the original '
             'matrix and right-hand side, check solver status and finite solutions, and require maximum '
             'solution error at most `1e-10`. The independently computed scaled residual is '
             '`||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)` and must be at most `1e-12`. '
             'Matrix infinity norm means the maximum absolute row sum.', '',
             '## Shared least-squares checks', '',
             'Use `t=[-2,-1,0,1,2]`, noise `e=[1,-2,2,-2,1]`, and observations `b=1+2*t+e`. '
             'The noise is orthogonal to the constant and linear columns. The full-rank design `[1,t]` '
             'therefore has reference coefficients `[1,2]`. A second design `[1,t,t]` has duplicate columns; '
             'the SVD-based solvers should return the minimum-norm coefficients `[1,1,1]`. Both have rank 2 '
             'and residual sum of squares 14.', '',
             'The drivers check solver status, finite coefficients, numerical rank and coefficient error '
             'at most `1e-10`. They independently require `max(abs(transpose(A)*(A*x-b))) <= 1e-10` and '
             'residual sum of squares within `1e-10` of 14. A nonzero residual is expected for these '
             'inconsistent systems; a small normal-equation residual alone would not identify the '
             'minimum-norm solution in the rank-deficient case. The known coefficient check does.', '',
             '## Symmetric eigenvalue checks', '',
             'The real symmetric matrix has a 2-by-2 block `[[2,1],[1,2]]` and a third diagonal '
             'entry 4, giving eigenvalues `[1,3,4]`. A second case changes that entry to 3, giving '
             'a repeated eigenvalue `[1,3,3]`. The driver queries workspace and calls the lower-level '
             '`syev` interface, checking `info=0`, finite factors and eigenvalue error at most `1e-12`. '
             'It independently checks `A*V=V*diag(lambda)`, reconstruction of A and orthonormality '
             'of V, each within `1e-12`. Matrix residuals use Frobenius norm divided by '
             '`max(1,||A||_F)`; orthogonality uses the unscaled Frobenius norm.', '',
             '## Reduced QR and its least-squares application', '',
             'For `t=[-1,0,1,2]`, the full-rank design is `[1,t,t**2]`. The reduced QR driver '
             'checks reconstruction, column orthonormality and the lower-triangular entries of R '
             'within `1e-12`. It then solves the triangular system for observations '
             '`b=A*[1,-2,0.5]+[-0.1,0.3,-0.3,0.1]`. The added noise is orthogonal to all design '
             'columns, so the coefficients are known independently and the residual sum of squares '
             'is 0.2. Coefficient error, normal-equation residual and residual-sum error must each '
             'be within `1e-12`.', '',
             'A second QR case replaces the third column with twice the second. Factorization '
             'identities must still pass, and the final diagonal entry of R must be near zero '
             'relative to matrix scale. The driver skips the triangular solve for this known '
             'dependent-column case; it does not treat unpivoted QR as a general rank-revealing method.', '',
             '## Reduced SVD checks', '',
             'The 4-by-3 matrix has an upper 2-by-2 block filled with 1.5, entry `(3,3)=2` and '
             'other entries zero. Its singular values are `[3,2,0]`. A second case sets row 4 '
             'to `[1,-1,0]`, giving `[3,2,sqrt(2)]`. The driver queries workspace and calls '
             'lower-level `gesvd` for reduced factors. It checks successful status, finite factors, '
             'nonnegative descending singular values and agreement with the known spectrum within '
             '`1e-12`. Reconstruction and left/right orthogonality must each be within `1e-12`, '
             'using the same residual scaling as the eigenvalue driver. The numerical rank threshold '
             'is `4*epsilon*max(singular_values)`, giving ranks 2 and 3 in these two cases.', '',
             'These decomposition checks allow valid factor sign choices and arbitrary bases in '
             'repeated or null subspaces. They compare reconstruction and invariant properties, '
             'rather than requiring a particular vector listing.', '',
             '## Observed high-level link limit', '',
             'On 2026-10-30, the high-level `linear_algebra:eigh` and `linear_algebra:svd` '
             'versions compiled their mains but failed to link under the hosted 16 MiB per-file '
             'limit with GNU Fortran 16.2.0/FPM 0.12.0 and the existing precompiled fortran-lapack '
             'image at revision `e5e45fdd5a38bfab06d1f703f12b787937aa33bb`. The linker reported:', '',
             '```text', 'collect2: fatal error: ld terminated with signal 25 [File size limit exceeded]', '```', '',
             'Saved reproducers: [high-level eigh](gams-candidates/fortran-lapack-eigh.f90) and '
             '[high-level svd](gams-candidates/fortran-lapack-svd.f90). These are failed hosted '
             'probes for that image, with no successful hosted-run designation. They may be useful '
             'for local reproduction or discussing executable size with the package author. '
             'The menu examples use the lower-level `syev`/`gesvd` APIs, which passed under the '
             'same limits and with the same precompiled library. Sandbox limits were unchanged.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     + (f'[Author example]({base}{d["author_example"]})' if d['author_example'] else 'Original lower-level API driver') + ' |')
    lines += ['', 'The dense examples reuse both authors\' problem data and retain both license notices. '
              'The least-squares examples adapt author API usage to shared deterministic data. These drivers '
              'appear in hosted and main local FPM example menus and downloaded projects. Loading a link '
              'selects source without submitting a job.', '',
              '## Recorded results', '',
              f'All {len(drivers)} passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'the existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-linear-algebra-validation.json) records source hashes, pins and '
              'saved output. These small examples establish checked usage, rather than comprehensive '
              'accuracy or performance comparisons. The packages may share underlying algorithms; this '
              'is not evidence of independent implementations. Zero printed error means agreement at working precision.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'These examples require no backend redeployment or package library rebuild.', '']
    return '\n'.join(lines)


def ode_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'I1' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS ODE initial-value drivers', '',
             'These consumer programs connect specific nonstiff initial-value solvers to the same analytic '
             'three-state problem. They test the named configuration, rather than every method offered by '
             'each package or performance on stiff equations.', '',
             '| Class | Configuration | Procedure |', '| --- | --- | --- |',
             '| [I1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1a) | One-step methods for general nonstiff or mildly stiff IVPs | DOP853 `dop853_class%integrate`; rklib `rk4_class%integrate` |',
             '| [I1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1b) | Multistep methods for general nonstiff or mildly stiff IVPs | DDEABM `ddeabm_class%integrate` |', '',
             '## Shared analytic problem', '',
             '```text', "u' = -u,   q' = v,   v' = -q", '(u,q,v)(0) = (1,1,0)',
             '(u,q,v)(t) = (exp(-t),cos(t),-sin(t))', '```', '',
             'Each driver advances from 0 to `2*pi`, checking all three states at ten equally spaced output '
             'times. It requires finite values, nonnegative decay state, maximum absolute state error at most '
             '`1e-8` and oscillator energy error `abs(q*q+v*v-1)` at most `2e-8`. Checking the analytic '
             'state also detects phase errors that an energy check could miss. These bounds apply at the '
             'reported checkpoints, rather than every internal step.', '',
             'DOP853 and DDEABM request absolute and relative tolerances `1e-10`. DOP853 must return '
             'status 1; DDEABM must return 2 or 3, both of which mean the requested time was reached. '
             'Both drivers also check the returned output time. A positive intermediate-step status is '
             'insufficient. DDEABM keeps its history across output requests; DOP853 is called for each '
             'successive interval.', '',
             'rklib uses classical fixed-step RK4 with step `0.01`, shortened at each requested endpoint, '
             'and requires status 0. Its API returns the state for the supplied final time, rather than '
             'a separate actual-time output. Fixed-step and adaptive tolerance settings are different '
             'accuracy controls; matching the problem and acceptance checks does not make their settings equivalent.', '',
             '## RK4 step refinement', '',
             'A separate RK4 experiment integrates the same problem directly to `2*pi` with nominal '
             'steps `2*pi/100` and `2*pi/200`. Both runs must complete with finite states, and their '
             'coarse/fine endpoint-error ratio must lie between 12 and 20. Fourth-order convergence '
             'suggests a ratio approaching 16 in this range. These coarser runs are separate from the '
             '`1e-8` checkpoint acceptance test. Floating-point endpoint rounding can produce a tiny '
             'additional final step, so callback counts need not equal four times the nominal step count.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author callback and integration API patterns to the shared analytic '
              'problem, without plotting dependencies; license notices are retained. They appear in '
              'hosted and main local FPM example menus and downloaded FPM projects. Loading a link '
              'selects source without submitting a job.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'the existing package libraries. Only the mains and executables were rebuilt. The '
              '[verification report](gams-ode-validation.json) records source hashes, revisions and saved '
              'output. RHS callback counts cover solver evaluations, including startup and rejected '
              'steps where applicable; analytic reference checks are excluded. RK4 refinement counts '
              'are reported separately. Counts for this simple problem are not a general efficiency ranking.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers dop853-decay-oscillator ddeabm-decay-oscillator rklib-decay-oscillator',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def interpolation_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'E1' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS one-dimensional interpolation drivers', '',
             'These consumer programs connect specific interpolation procedures to '
             '[E1a: polynomial splines (piecewise polynomials)](https://gams.nist.gov/cgi-bin/serve.cgi/Class/E1a). '
             'This GAMS class covers both piecewise linear and piecewise cubic methods; the procedure '
             'records and driver settings distinguish them. The examples do not exercise higher-dimensional APIs.', '',
             '| Package | Shared-data method | Additional check |', '| --- | --- | --- |',
             '| finterp | `linear_interp_1d%evaluate`, piecewise linear | Agreement with an independent piecewise-linear reference |',
             '| PCHIP | `dpchim` slopes and `dpchfe` values, shape-preserving cubic Hermite | Sampled monotonicity and local bounds; agreement with the linear method is not required |',
             '| bspline-fortran | `bspline_1d`, order 2 (degree 1) | Piecewise-linear reference, then a separate order-4 cubic/derivative reproduction check |', '',
             '## Shared data and checks', '',
             'All drivers use the nonuniform grid `x=[0,0.25,0.5,1,2,3]`. Case 1 tabulates the affine '
             'function `f(x)=2*x-1`; case 2 uses steep monotone values `[0,0.01,0.02,0.9,0.95,1]`.', '',
             'The programs check successful initialization/evaluation and finite outputs. They require '
             'interpolation at all six original nodes within `1e-12`. At 21 sample positions in each '
             'interval, including its endpoints, they check that the output stays between that interval\'s '
             'two data values and does not decrease, allowing `1e-12` rounding tolerance. This is a '
             'finite sampling check, rather than a proof of shape preservation for arbitrary data.', '',
             'For affine data, every sampled value must agree with `2*x-1` within `1e-12`. The finterp '
             'and order-2 B-spline drivers also require agreement with the independently constructed '
             'piecewise-linear values within `1e-12`. PCHIP prints its difference from that reference '
             'without treating the difference as an error: the cubic interpolant generally takes different '
             'interior values. The drivers make no extrapolation requests. Each shared case performs '
             '111 value evaluations: six original nodes plus five intervals with 21 samples each.', '',
             '## Cubic B-spline reproduction', '',
             'The B-spline driver separately interpolates `p(x)=1-2*x+0.5*x**2+x**3` with order 4, '
             'meaning cubic polynomial pieces. At 101 positions on `[0,3]`, it compares values with '
             '`p(x)` and first derivatives with `-2+x+3*x**2`, each within `1e-10`. '
             'This checks polynomial reproduction and the derivative evaluation API. It does not '
             'claim that general cubic B-spline interpolation preserves monotone shape.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author example/test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain the package license notices. '
              'They use shared deterministic data instead of the larger author test harnesses. The '
              'drivers appear in hosted and main local FPM example menus and downloaded projects. '
              'Loading a link selects source without submitting a job.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'the existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-interpolation-validation.json) records source hashes, pins '
              'and saved output. Zero printed error means agreement at working precision. These '
              'small examples establish checked usage, rather than general accuracy or speed rankings.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers finterp-shape-interpolation pchip-shape-interpolation bspline-fortran-shape-interpolation',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def transforms_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'J1' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS transform drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [J1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a2) | One-dimensional complex Fourier transforms | FFTPACK `fft, ifft`; KISS FFT `fft%perform` |',
             '| [J1a3](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a3) | One-dimensional sine and cosine transforms | FFTPACK `dct(type=2), idct(type=2)` |', '',
             'These are the deepest categories in the recorded GAMS taxonomy for the demonstrated '
             'complex and cosine transforms. They do not exhaust integral transforms: multidimensional '
             'transforms, convolution, Laplace and Hilbert transforms are separate opportunities.', '',
             '## Complex FFT checks', '',
             'The shared input is `x(j)=(j+1)/8 + i*(-1)**j/4`, for zero-based `j`, at lengths 7 and 8. '
             'Its components are exactly representable in both single and double precision. Each driver '
             'independently sums the negative-exponent DFT in real64 and compares every complex frequency '
             'bin. It also checks finite values, inverse recovery after dividing by `N`, and Parseval\'s '
             'identity `sum(abs(X)**2)/N = sum(abs(x)**2)`.', '',
             'FFTPACK uses its double-precision `rk` kind and limits forward, inverse and relative energy '
             'errors to `1e-11`. The pinned KISS FFT binding uses C `float`: forward error must be at '
             'most `1e-5`, inverse error at most `1e-6` and relative energy error at most `1e-6`. '
             'The precision difference is explicit, rather than interpreting it as an algorithm ranking. '
             'KISS forward and inverse plans are each initialized once per length and finalized on block exit.', '',
             '## Cosine transform checks', '',
             'The DCT-II driver uses the real input `(j+1)/8` at lengths 7 and 8. In this FFTPACK API, '
             'the forward convention is `X(k)=4*sum_j x(j)*cos(pi*(j+1/2)*k/N)`. The inverse is '
             'unnormalized: divide `idct(dct(x,type=2),type=2)` by `4*N`. The driver independently '
             'evaluates the cosine sum and requires both forward and recovered-input errors at most '
             '`1e-11`, with finite outputs. Other libraries may use different normalization conventions.', '',
             'A round trip alone could hide matching sign or scaling mistakes; independent forward '
             'references check the documented convention. These short deterministic cases do not '
             'establish accuracy or performance for all transform sizes.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author example/test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain license notices. They appear '
              'in hosted and main local FPM example menus and downloaded projects. Loading a link '
              'selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-transforms-validation.json) records hashes, source pins and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers fftpack-complex-transform kissfft-f-complex-transform fftpack-cosine-transform',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def constrained_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'G2' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS constrained-optimization drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [G2h1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h1a2) | Smooth simple-bound optimization with user first derivatives | L-BFGS-B `setulb`; NLopt `LD_LBFGS` with explicit bounds |',
             '| [G2h3b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h3b1b) | Smooth nonlinear equality/inequality optimization with user objective and constraint first derivatives | SLSQP `slsqp_solver%optimize`, analytic mode |', '',
             'Both are deepest recorded GAMS classes for the demonstrated configurations. Other constrained '
             'optimization classes and other procedures in these classes still need checked drivers; '
             'see the [coverage report](gams-coverage.md).', '',
             '## Shared bound-constrained quadratic', '',
             'Minimize `f(x)=(x1-2)**2+(x2+1)**2` subject to `0<=x1<=1` and `0<=x2<=2`, starting '
             'at `[0.25,1]`. Projection of the unconstrained minimizer `[2,-1]` onto the box gives the '
             'unique solution `[1,0]`, with objective 2. One variable is on its upper bound and the other '
             'on its lower bound.', '',
             'The two drivers check their analytic gradient against central differences before solving. '
             'They require actual convergence, finite results, parameter/objective error at most `1e-8`, '
             'maximum bound violation at most `1e-10`, agreement of reported and independent objectives '
             'within `1e-10`, and projected-gradient residual at most `1e-8`. The latter is '
             '`max(abs(x-clip(x-gradient(f),lower,upper)))`. At a boundary solution, the ordinary gradient '
             'need not be zero.', '',
             'L-BFGS-B uses reverse communication and must return a convergence task. NLopt must return '
             'one of its convergence codes 1 through 4; an evaluation/time limit does not count as success. '
             'The NLopt bound configuration has a separate procedure record from its unconstrained '
             'Rosenbrock example. These packages are not asserted to use identical algorithms.', '',
             '## Equality plus nonlinear inequality', '',
             'The SLSQP driver minimizes the same objective over a different feasible set: '
             '`c1=x1+x2-1=0`, `c2=1-x1**2-x2**2>=0`, with inactive safety bounds `[-2,2]` '
             'and feasible start `[0.5,0.5]`. Equalities come first in the callback; SLSQP inequalities '
             'use the nonnegative convention. Analytic mode (`gradient_mode=0`) supplies both the '
             'objective gradient and constraint Jacobian, which are sanity-checked by central differences.', '',
             'On the line `x1+x2=1`, the circle restricts `x1` to `[0,1]`, and the objective becomes '
             '`2*(x1-2)**2`. The unique constrained solution is therefore `[1,0]`, with objective 2. '
             'The driver requires solver status 0, finite values and parameter/objective errors at most '
             '`1e-7`. It independently checks primal feasibility, stationarity and complementarity '
             'within `1e-7`, using the exact multipliers `lambda=2` and `mu=2>=0`:', '',
             '```text', 'gradient(f) - lambda*gradient(c1) - mu*gradient(c2) = 0',
             'mu*c2 = 0', '```', '',
             'The multipliers are known from this test problem, not reported by SLSQP. The convex '
             'problem gives an independently known global solution; a successful run of a general '
             'nonlinear optimizer is not by itself a global-optimality guarantee.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        author = f'[Author example]({base}{d["author_example"]})' if d['author_example'] else 'Original public-API driver'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · {author} |')
    lines += ['', 'The L-BFGS-B and SLSQP drivers adapt author API patterns and retain license notices. '
              'All three appear in hosted and main local FPM example menus and downloaded projects. '
              'Loading a link selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-constrained-validation.json) records hashes, pins and saved output. '
              'Evaluation counts exclude derivative sanity checks and describe these simple cases, rather '
              'than establishing a general speed ranking.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers lbfgsb-box-quadratic nlopt-box-quadratic slsqp-circle-equality',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def special_functions_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    tree = class_tree(data)
    drivers = [d for d in driver_data(root, data) if 'C' in ancestors(tree, d['gams_code'])]
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS special-function drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [C7a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7a) | Gamma, log-Gamma and reciprocal-Gamma at positive real arguments | Fullerton `fgamma`, `log_gamma`, `reciprocal_gamma` |',
             '| [C7c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7c) | Psi/digamma at positive real arguments | Fullerton `digamma` |',
             '| [C10b1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10b1) | Modified Bessel I/K, real arguments and integer orders; tested orders 0 and 1 | fortran-bessels `besseli0`, `besseli1`, `besselk0`, `besselk1` |', '',
             'These demonstrate selected positive arguments and named procedures. They do not exhaust '
             'their GAMS classes or cover arbitrary orders, complex arguments, poles or extreme-argument regimes. '
             'See the [coverage report](gams-coverage.md) for remaining procedure-class gaps.', '',
             '## Gamma-family references and precision', '',
             'The pinned Fullerton APIs use default real, which has 6 decimal digits of precision in the '
             'verified GNU build. Calls retain that precision; reference calculations and error measurements '
             'use real64. This avoids requiring double-precision accuracy from a single-precision API.', '',
             'At `x=[0.5,1,1.5,2,2.5,5,10]`, Gamma references are built independently from factorials '
             'and half-integer values using `sqrt(pi)`. See [NIST DLMF special values](https://dlmf.nist.gov/5.4) '
             'and the [Gamma recurrence](https://dlmf.nist.gov/5.5.E1). The driver checks Gamma relative '
             'error, `abs(log_gamma(x)-log(reference))/max(1,abs(log(reference)))`, and '
             '`abs(reciprocal_gamma(x)*reference-1)`, all within `3e-6`. This independently checks all '
             'three outputs, rather than relying only on Gamma times reciprocal-Gamma being one.', '',
             '## Digamma references and identities', '',
             'At the same seven arguments, the digamma driver uses harmonic sums and the Euler constant: '
             '`psi(n)=H(n-1)-Euler`, `psi(1/2)=-Euler-2*log(2)`, with half-integer shifts formed '
             'arithmetically. These [special values](https://dlmf.nist.gov/5.4#ii) provide independent '
             'anchors with absolute error at most `5e-6`.', '',
             'Additional checks use the [recurrence](https://dlmf.nist.gov/5.5.E2) at '
             '`[0.25,0.5,1.5,3.25,10]` and [reflection relation](https://dlmf.nist.gov/5.5.E4) at '
             '`[0.125,0.25,0.375]`: `psi(x+1)-psi(x)=1/x` and '
             '`psi(1-x)-psi(x)=pi/tan(pi*x)`. Each absolute residual must be at most `5e-6`. '
             'All values and identity residuals must be finite.', '',
             '## Modified Bessel references and identities', '',
             'The fortran-bessels driver tests all four named functions at '
             '`[0.125,0.25,0.5,1,2,4,8]`. Its embedded reference table was independently generated with '
             'mpmath 1.3.0 at 80 decimal digits, printed with 23 significant digits and rounded into '
             'the package\'s `BK` kind. That kind has 15 decimal digits in the verified build. '
             'Every function must have relative table error at most `2e-12` and finite positive values.', '',
             'It independently sums the positive-term [I-function series](https://dlmf.nist.gov/10.25.E2) '
             'for orders 0 and 1 until both next terms are below working epsilon times their sums; '
             'relative agreement must be within `2e-12`. It also checks '
             '`abs(x*(I0*K1+I1*K0)-1)<=1e-11`, the order-zero '
             '[Wronskian identity](https://dlmf.nist.gov/10.28.E2). The table supplies independent '
             'anchors for K0/K1 as well; an identity by itself could hide correlated errors.', '',
             'The reference table can be regenerated separately from the playground:', '',
             '```python', 'import mpmath as mp', 'mp.mp.dps = 80',
             'for text in ("0.125", "0.25", "0.5", "1", "2", "4", "8"):',
             '    x = mp.mpf(text)',
             '    values = (mp.besseli(0,x), mp.besseli(1,x), mp.besselk(0,x), mp.besselk(1,x))',
             '    print(text, *(mp.nstr(v,23) for v in values))', '```', '',
             'mpmath is needed only to regenerate references. The self-contained Fortran driver and '
             'the backend do not depend on it.', '', '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author example/test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns, retain license notices and use deterministic '
              'reference checks instead of the larger author harnesses. They appear in hosted and main '
              'local FPM example menus and downloaded projects. Loading a link selects source without '
              'submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-special-functions-validation.json) records hashes, pins and '
              'saved output. These cases establish checked usage and selected-point agreement, rather '
              'than accuracy over each function\'s complete domain.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers fullerton-gamma-values fullerton-digamma-values bessels-modified-values',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def statistics_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-statistics-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS descriptive-statistics drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [L1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L1a1a) | Location of univariate data, demonstrated by real64 means | `stdlib_stats:mean`; `fstats:mean` |',
             '| [L1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L1a1b) | Dispersion of univariate data, demonstrated by real64 variances | `stdlib_stats:var`; `fstats:variance` |', '',
             'These are checked configurations of the named procedures, rather than coverage of all '
             'descriptive statistics, distributions or inference. GAMS categories are not exhausted; '
             'the [coverage report](gams-coverage.md) tracks remaining procedure-class gaps.', '',
             '## Shared datasets and independent answers', '',
             'Let `base=[1,2,3,4,5]`. All four drivers use the same finite real64 datasets:', '',
             '| Dataset | Mean | Sample variance | Population variance |', '| --- | ---: | ---: | ---: |',
             '| `base` | 3 | 2.5 | 2 |',
             '| `1e6+2*base` | 1000006 | 10 | 8 |',
             '| Five copies of `7.25` | 7.25 | 0 | 0 |',
             '| `-3*base` | -9 | 22.5 | 18 |', '',
             'The references follow directly from the small base dataset and shift/scale identities. '
             'The drivers do not obtain their expected answers from the package under test. '
             'They require finite results; variances must also be nonnegative. Mean error is '
             '`abs(computed-reference)/max(1,abs(reference))`, bounded by `64*epsilon(real64)`. '
             'Variance errors use the same scaling and must be at most `1e-12`. The shifted case '
             'checks a moderate offset, rather than every numerical-stability regime.', '',
             '## Sample versus population normalization', '',
             'Sample variance divides the sum of squared deviations by `N-1`; population '
             'variance divides by `N`. The stdlib driver explicitly requests '
             '`var(x,corrected=.true.)` and `var(x,corrected=.false.)`, respectively. '
             'The fstats API returns sample variance; its driver derives the population value '
             'by multiplying by `(N-1)/N`. This conversion is shown explicitly in the code and '
             'is not presented as a separate fstats population-variance API.', '',
             '## Subsets and array dimensions', '',
             'All four drivers use Fortran `pack` with mask `[T,F,T,F,T]` to select `[1,3,5]`. '
             'The known subset mean is 3 and sample variance is 4; these checks use absolute '
             'tolerance `1e-12`.', '',
             'The stdlib drivers also exercise native array masks. The variance driver checks '
             'masked population variance `8/3`. For the 5-by-2 matrix with columns `base` and '
             '`2*base`, `dim=1` must return means `[3,6]` and sample variances `[2.5,10]`, '
             'each within absolute tolerance `1e-12`. All supplemental outputs must be finite. '
             'These cases use explicitly selected finite observations.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author test |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'[Author test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns, retain license notices and use shared '
              'deterministic inputs instead of larger test harnesses. The fstats links point to '
              'its descriptive-statistics tests. All four appear in hosted and main local FPM '
              'example menus and downloaded projects. Loading a link selects source without '
              'submitting a job.', '', '## Recorded results', '',
              'All four passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              '[verification report](gams-statistics-validation.json) records hashes, pins and '
              'saved output. These cases establish selected-data correctness, rather than a '
              'general accuracy or speed ranking.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers stdlib-mean-checks fstats-mean-checks stdlib-sample-variance-checks fstats-sample-variance-checks',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def random_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-random-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS random-generator drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [L6a21](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L6a21) | Uniform pseudorandom generation | MT19937-64; rngff combined LCG |',
             '| [L6c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L6c) | Random-number support, demonstrated by seeding | stdlib `random_seed` with `dist_rand` |', '',
             'These deterministic sequence and API checks do not certify statistical quality or cryptographic suitability. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Mersenne Twister reference sequence', '',
             'The MT19937-64 driver seeds two generators with integer seed 5489. It checks 15 raw '
             '64-bit outputs at positions 1 through 10, 312, 313, 624, 625 and 1000 against '
             'independent C++11 `std::mt19937_64` output. The boundary positions exercise generator state refills. '
             'For all 1000 draws, the real64 output must equal `real(shiftr(bits,11),real64)*2**(-53)` '
             'exactly, be finite and lie in `[0,1)`. Reseeding must replay all 1000 values exactly.', '',
             'The [reference source](../fpm_catalog/gams-drivers/references/mt19937_64_reference.cpp) '
             'and [reference output](../fpm_catalog/gams-drivers/references/mt19937_64_reference.txt) '
             'are stored in the repository. Output was generated with g++ (GCC) '
             '17.0.0 20260510 (experimental), rather than copied from an upstream output table. '
             'The constants are embedded in the Fortran driver; running it requires no C++ compiler.', '',
             'To regenerate the independent reference:', '', '```text',
             'g++ -std=c++11 fpm_catalog/gams-drivers/references/mt19937_64_reference.cpp -o mt-reference',
             './mt-reference', '```', '',
             '## Combined linear congruential generator', '',
             'The rngff driver starts with seeds `[12345,67890]`. It independently evaluates '
             '`state=modulo([40014,40692]*state,[2147483563,2147483399])` using int64 arithmetic, '
             'whose products fit safely, rather than the package\'s int32 Schrage update. For 1000 '
             'draws, both states and the combined uniform value must match exactly; a second '
             'identically seeded object must replay every draw. Values must be finite in `[0,1)`.', '',
             'At the pinned revision the real64 overload widens a real32 draw. The reference '
             'explicitly reproduces that rounding; returning a real64 value does not provide '
             'real64 random precision. This behavior is printed by the example.', '',
             '## stdlib distribution seeding', '',
             'The stdlib driver uses `stdlib_random:random_seed` and `dist_rand(0_int64)`. '
             'This controls stdlib\'s distribution stream, separately from intrinsic `random_number`. '
             'Seed 1234567 must reproduce all 1024 integer draws exactly and return the same opaque '
             '`get` value. That value is neither treated as an echo of the original seed nor as '
             'a complete running-state checkpoint. For the second selected seed, 1234568, the '
             'sequence must differ. This last check concerns these two seeds, rather than proving '
             'distinct streams for every pair of seeds. No probabilistic moment thresholds are used.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author API patterns and retain license notices. They appear '
              'in hosted and main local FPM example menus and downloaded projects. Loading a link '
              'selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-random-validation.json) records source hashes, pins '
              'and saved output. These checks establish neither a performance ranking nor cross-version '
              'sequence guarantees for APIs that do not promise them.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers mt19937-64-reference-sequence rngff-lcg-reference-sequence stdlib-seed-replay',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def differentiation_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-differentiation-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS differentiation drivers', '',
             'All three drivers belong to [H1: Numerical differentiation](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H1). '
             'They use the same scalar function and evaluation points, making differences in API and '
             'method visible. This does not validate every derivative interface in these packages. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Shared problem and independent references', '',
             'For `f(x)=exp(x)*sin(x)`, elementary differentiation gives:', '',
             '```text', 'df/dx   = exp(x)*(sin(x)+cos(x))',
             'd2f/dx2 = 2*exp(x)*cos(x)', 'd3f/dx3 = 2*exp(x)*(cos(x)-sin(x))', '```', '',
             'Each driver evaluates at `x=[-0.5,0,0.5,1]` using real64 precision. Expected '
             'derivatives come from these formulas, independently of the package under test. '
             'The scaled error is `abs(computed-reference)/max(1,abs(reference))`. All checked '
             'results must be finite. The AD driver also checks the function value.', '',
             '## Configurations and acceptance criteria', '',
             '| Package | Method | Orders | Settings and maximum scaled errors |',
             '| --- | --- | --- | --- |',
             '| NumDiff | Adaptive finite differences using Neville extrapolation | 1, 2, 3 | Requested absolute errors `1e-8,1e-8,1e-6`; scaled-error bounds `1e-7,1e-7,1e-6` |',
             '| ForDiff | Forward and backward finite differences | 1 | Step `1e-5`; scaled-error bound `5e-5` |',
             '| ForDiff | Central finite differences | 1 | Step `1e-5`; scaled-error bound `1e-9` |',
             '| ForDiff | Complex step | 1 | Step `1e-20`; scaled-error bound `5e-14` |',
             '| AD_dnSVM | Forward automatic differentiation using overloaded scalar type | 0 through 3 | One independent variable; scaled-error bound `5e-14` |', '',
             'NumDiff uses the allowed interval `[-0.5,1]`, so the two endpoint cases require '
             'one-sided formulas. Every call must return status zero and a nonnegative error '
             'estimate within the requested absolute tolerance. The analytic error must also '
             'fit the estimate plus `64*epsilon*max(1,abs(reference))` for rounding. An initial '
             'trial requesting `1e-8` for all orders could not satisfy the third-derivative '
             'request at the lower endpoint. The published driver explicitly requests `1e-6` '
             'for third derivatives and retains the status and independent accuracy checks.', '',
             'ForDiff follows the author\'s scalar example and supplies separate real and complex '
             'callbacks. Complex step requires a complex analytic extension of the function; '
             'it is not generally valid for callbacks containing operations such as `abs` or '
             'branches that discard the imaginary perturbation. This driver does not validate '
             'the vector overloads or choose optimal step sizes automatically.', '',
             'AD_dnSVM follows the author\'s `Variable` pattern, requesting `nderiv=3`, and extracts '
             '`get_d0`, `get_d1`, `get_d2` and `get_d3`. It checks the one-element derivative '
             'tensor sizes and compares ordinary derivatives, without factorial rescaling. '
             'Multivariate mixed partials are outside this example.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain license notices. NumDiff and '
              'ForDiff use module callbacks to avoid executable-stack trampolines. These drivers '
              'appear in hosted and main local FPM menus and downloaded projects. Loading a '
              'link selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-differentiation-validation.json) records source hashes, '
              'pins and saved output. Different methods, tolerances and derivative orders make '
              'these demonstrations unsuitable as a general accuracy or performance ranking.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers numdiff-analytic-derivatives fordiff-analytic-derivatives ad-dnsvm-analytic-derivatives',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def systems_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-systems-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS nonlinear-system drivers', '',
             'These three drivers demonstrate [F2: Systems of nonlinear equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F2). '
             'The task is to find a zero of a vector function. The related Rosenbrock optimization '
             'drivers minimize a scalar objective and have separate GAMS assignments. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Shared problem and independent checks', '',
             'All three solve the square two-variable system:', '', '```text',
             'F1(x,y) = 1-x', 'F2(x,y) = 10*(y-x**2)',
             'J(x,y)  = [[-1, 0], [-20*x, 10]]', '```', '',
             'The exact root is `(1,1)`: the first equation fixes `x=1`, and the second then '
             'fixes `y=1`. Each driver starts from both `(-1.2,1)` and `(2,2)`. '
             'The analytic Jacobian is nonsingular everywhere (determinant `-10`), '
             'but that alone does not guarantee convergence of every iteration strategy.', '',
             'Every run requires finite returned values, a successful termination condition, '
             '`max(abs(x-[1,1])) <= 1e-8` and an independently recomputed residual infinity norm '
             '`max(abs([1-x,10*(y-x**2)])) <= 1e-8`. MINPACK and nonlin also return a residual '
             'vector; it must agree with the recomputed vector within `1e-12`. These extra '
             'checks prevent a small step or stationary point alone from being accepted as a root.', '',
             '## Configurations and termination', '',
             '| Package and procedure | Configuration | Accepted termination |', '| --- | --- | --- |',
             '| MINPACK `hybrd1` | Powell hybrid method; finite-difference Jacobian; `tol=1e-10`; documented workspace size | `info=1`, plus root/residual checks |',
             '| nonlin `newton_solver%solve` | Newton with backtracking; both default finite-difference and supplied analytic Jacobians; function tolerance `1e-10`, variable/gradient tolerances `1e-12`; at most 2000 function evaluations | Function or variable-change convergence, plus root/residual checks |',
             '| nlesolver-fortran `nlesolver_type%solve` | Dense analytic Jacobian; backtracking (`step_mode=2`); Broyden updates disabled; function tolerance `1e-10`, variable tolerance `1e-12`; at most 200 iterations | Initialization status `0`, then solve status `1` (required accuracy achieved), plus root/residual checks |', '',
             'The nonlin driver uses separate function-helper objects so the finite-difference '
             'case has no analytic Jacobian attached. All four nonlin runs reported function '
             'convergence in the saved verification. nlesolver-fortran adapts callback and '
             'status patterns from the author sparse test, while explicitly selecting dense '
             'mode for this small system. Its sparse solvers are not exercised here.', '',
             'Iteration and evaluation counts are shown to explain the API. Package counters '
             'and algorithms differ; for example, a reported function count need not account '
             'for every evaluation used to approximate a Jacobian. These outputs are not a '
             'controlled speed comparison. Other starting points, ill-conditioned or singular '
             'systems, larger dimensions and general convergence guarantees are outside this review.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author API patterns, retain license notices and use module '
              'callbacks to avoid executable-stack trampolines. They appear in hosted and main '
              'local FPM menus and downloaded projects. Loading a link selects source without '
              'submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-systems-validation.json) records source hashes, '
              'pins and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers minpack-rosenbrock-system nonlin-rosenbrock-system nlesolver-rosenbrock-system',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def sparse_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-sparse-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS sparse and positive-definite linear-system drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [D2b4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2b4) | Real symmetric sparse systems | `minres_solver`; `qdldl_type%analyze/factor/solve` |',
             '| [D2b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2b1b) | Real symmetric positive-definite systems | KISS `cg_dense` |', '',
             'These examples distinguish the matrix requirements and storage used by each API. '
             'GAMS categories are not exhausted; the [coverage report](gams-coverage.md) tracks '
             'the remaining class-specific driver gaps.', '',
             '## Shared symmetric indefinite problem', '',
             'MINRES and qdldl-fortran solve the same five-variable system for two right-hand sides:', '',
             '```text', 'A = [[4, 1,  0,  1,  0],',
             '     [1, 5, -1,  2,  0],', '     [0,-1,  6, -1,  1],',
             '     [1, 2, -1, -2,  0],', '     [0, 0,  1,  0, -3]]', '',
             'x1 = [ 1, -2, 3, -1,  2]', 'x2 = [-1,0.5, 2,  1, -2]', 'b1 = A*x1; b2 = A*x2', '```', '',
             'This is a quasi-definite block matrix `[[H,B^T],[B,-C]]`. The leading 3-by-3 '
             '`H` is symmetric with positive diagonal and strictly diagonally dominant; '
             '`C=diag(2,3)` is positive definite. The full matrix has three positive and '
             'two negative eigenvalues and no zero eigenvalues. This supplies an independent '
             'inertia check without calling another eigensolver.', '',
             'The solver representation stores the 11 upper-triangle nonzeros. Both drivers '
             'use a separate explicit dense matrix to construct right-hand sides and check '
             'residuals. MINRES additionally checks its sparse operator product against this '
             'dense reference before solving.', '',
             '## Solver configurations', '',
             'MINRES receives a module matrix-vector callback, zero shift, symmetry checking '
             'enabled, no preconditioning, relative tolerance `1e-12` and at most 100 iterations. '
             'Only stop reasons 1 or 2 (residual convergence) are accepted for these nonzero '
             'right-hand sides. An identity preconditioner callback is supplied for the API '
             'but preconditioning is disabled. Singular least-squares behavior, shifts and '
             'preconditioners are not demonstrated.', '',
             'qdldl-fortran performs symbolic analysis and numeric factorization once for each '
             'of natural, RCM and AMD orderings. Each factorization is reused to solve both '
             'right-hand sides. Analysis, factorization and solve must each report success, '
             'and computed inertia must be `(3,2,0)`. Static regularization and iterative '
             'refinement are explicitly disabled because this matrix already satisfies the '
             'quasi-definite requirement. The method does not pivot; these checks do not '
             'extend its guarantees to arbitrary symmetric indefinite matrices.', '',
             '## Positive-definite conjugate-gradient problem', '',
             'KISS solves a separate 20-by-20 symmetric tridiagonal matrix with diagonal 4 '
             'and off-diagonals -1. Positive diagonal and strict diagonal dominance establish '
             'positive definiteness. The driver uses `cg_dense`, so the matrix is stored '
             'densely even though its entries form a sparse stencil. This illustrates the '
             'reviewed dense API and is not a sparse-storage performance example.', '',
             'The known solutions are `x(i)=i/20` and `x(i)=(-1)**i`. Right-hand sides are '
             'constructed independently with `b(i)=4*x(i)-x(i-1)-x(i+1)`, omitting neighbors '
             'outside the interval. Each solve starts at zero, with `rtol=1e-12`, '
             '`atol=1e-14` and `maxiter=200`; returned `info` must be zero. Other KISS '
             'iterative methods and indefinite matrices are outside this driver.', '',
             '## Common acceptance criteria', '',
             'All three require finite solutions, maximum absolute solution error at most '
             '`1e-9`, and scaled normwise backward error at most `1e-11`:', '', '```text',
             'eta = ||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)', '```', '',
             'The matrix infinity norm is the maximum absolute row sum. Each example prints '
             'the absolute residual as well as the solution and backward errors. These '
             'small deterministic cases check the recorded configurations; they do not '
             'measure large-system scalability or rank packages by speed.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author API patterns and retain license notices. They appear '
              'in hosted and main local FPM menus and downloaded projects. Loading a link '
              'selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-sparse-validation.json) records hashes, pins '
              'and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers minres-indefinite-solve qdldl-quasidefinite-solve kiss-positive-definite-solve',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def cubature_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-cubature-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS cubature and quadrature-rule drivers', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [H2b1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2b1a1) | Automatic multidimensional integration over hyperrectangles | DCUHRE |',
             '| [H2c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2c) | Integration service routines: nodes and weights | `gauss_jacobi`; `cubature` |', '',
             'A rule generator returns nodes and weights; the driver forms its own weighted '
             'sums. An adaptive integrator selects subdivisions and evaluates callbacks to '
             'meet a requested tolerance. The classifications preserve this distinction. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Adaptive box integrals', '',
             'DCUHRE integrates two components together: `sum(x**2)` and `exp(sum(x))`. '
             'The boxes are `[0,1]^2` and `[-1,0] x [0,2] x [1,2]`. Their references follow '
             'from separation into one-dimensional antiderivatives:', '', '```text',
             'Integral sum(x**2) = sum_j ((b_j**3-a_j**3)/3 * product_{i!=j}(b_i-a_i))',
             'Integral exp(sum(x)) = product_j (exp(b_j)-exp(a_j))', '```', '',
             '| Box | Quadratic reference | Exponential reference |', '| --- | --- | --- |',
             '| Unit square | `2/3` | `(e-1)**2` |',
             '| Shifted 3D box | `8` | `(1-exp(-1))*(exp(2)-1)*(exp(2)-exp(1))` |', '',
             'The driver uses real64, default local rule (`key=0`), no restart, absolute '
             'tolerance `1e-10`, relative tolerance `1e-9`, a maximum of 20000 evaluations '
             'and workspace length 10000. A module callback supplies both components. '
             'It requires `ifail=0`, a positive evaluation count within budget, finite results '
             'and finite nonnegative error estimates within the requested criterion. '
             'Independently computed scaled analytic errors must be at most `1e-8`.', '',
             'These are smooth finite-domain examples. Error estimates are inspected, but '
             'are not proved to bound true errors for arbitrary integrands. Singularities, '
             'oscillatory integrands, restarts and all local-rule choices are not validated.', '',
             '## Gauss-Jacobi moments and weight convention', '',
             'The GaussJacobiQuad driver generates four-point rules with both `recurrence` '
             'and `gw` methods for `(alpha,beta)=(0,0)` and `(1,0)`. The convention is '
             '`weight(x)=(1-x)**alpha*(1+x)**beta` on `[-1,1]`. Thus the cases use weight '
             '`1` and `1-x`; the asymmetric second case also checks the sign convention.', '',
             'For each of the four rules, the driver checks all monomials `x**k`, '
             '`k=0,...,7`, for 32 moment checks. Let `m(k)=2/(k+1)` for even `k`, and '
             '`m(k)=0` for odd `k`. Exact references are `m(k)` for weight 1 and '
             '`m(k)-m(k+1)` for weight `1-x`. Every node must be finite and strictly '
             'inside `(-1,1)`; weights must be finite and positive. Maximum scaled '
             'moment error is `1e-11`. The driver prints the nodes and weights.', '',
             'This checks selected orders and moderate parameters; it does not establish '
             'accuracy for high-order rules, parameters near -1, or large alpha/beta.', '',
             '## Reference-element cubature moments', '',
             'The fortran_cubatures driver adapts the author monomial-test pattern. It checks '
             'positive finite weights, finite nodes inside the reference element, and the '
             'following polynomial spaces:', '',
             '| Element | Domain | Requested degree | Moments checked |', '| --- | --- | --- | ---: |',
             '| Triangle | `x,y>=0`, `x+y<=1` | Total degree 5 | 21 |',
             '| Tetrahedron | `x,y,z>=0`, `x+y+z<=1` | Total degree 4 | 35 |',
             '| Quadrilateral | `[-1,1]^2` | Degree 5 in each coordinate | 36 |', '',
             'For a unit d-simplex, the exact monomial integral is '
             '`product(e_i!)/(d+sum(e_i))!`. The driver evaluates these small factorials '
             'directly. Square references are products of the one-dimensional moments '
             '`m(k)` above. Constant moments also check the measures `1/2`, `1/6` and '
             '`4`. All 92 scaled moment errors must be at most `1e-12`. Other elements, '
             'degrees, physical-element coordinate mappings and finite-element assembly '
             'are outside this example.', '',
             'All three use scaled error `abs(computed-reference)/max(1,abs(reference))`. '
             'The small deterministic problems do not constitute a general accuracy or '
             'performance comparison.', '', '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain license notices. DCUHRE '
              'retains the pinned ACM non-commercial terms; the two rule-generator examples '
              'retain their MIT notices. They appear in hosted and main local FPM menus and '
              'downloaded projects. Loading a link selects source without submitting a job.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-cubature-validation.json) records hashes, pins '
              'and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers dcuhre-box-integrals gauss-jacobi-polynomial-moments cubatures-simplex-moments',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def surfaces_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-surfaces-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS gridded surface-interpolation drivers', '',
             'Both examples demonstrate [E2a: Interpolation on multivariate gridded data](https://gams.nist.gov/cgi-bin/serve.cgi/Class/E2a). '
             'They use the same nonuniform rectangular grid and datasets. The B-spline driver '
             'adds a polynomial surface with analytic partial derivatives. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Shared grid and surfaces', '', '```text',
             'x = [-1, -0.6, 0, 0.3, 1, 2]', 'y = [-2, -0.75, 0, 0.5, 1.5]',
             'case 1: f(x,y) = 1 + 2*x - 3*y + 0.5*x*y',
             'case 2: f(x,y) = x**2 + 2*y**2 + x*y', '```', '',
             'Data have shape `(6,5)`, with `f(i,j)` corresponding to `(x(i),y(j))`. '
             'The different grid lengths and nonuniform spacing make coordinate orientation '
             'and interval selection visible. Every initialization and evaluation must report '
             'success, and every returned value must be finite.', '',
             'For each case, the drivers first check all 30 original grid nodes. They then '
             'sample each of the 20 cells on a 5-by-5 fractional grid, including cell edges '
             'and corners, for 500 cell evaluations. Shared boundary points are intentionally '
             'visited in neighboring cells; this is a check count, not 500 distinct locations.', '',
             '## Independent bilinear references', '',
             'Let `s,t` be the fractional coordinates in a cell. Both examples compare to '
             'the explicit four-corner formula:', '', '```text',
             '(1-s)*(1-t)*f(i,j) + s*(1-t)*f(i+1,j)',
             '  + (1-s)*t*f(i,j+1) + s*t*f(i+1,j+1)', '```', '',
             'They also check that sampled values remain between the minimum and maximum '
             'of the four corners. Node errors, formula errors and bound violations must '
             'be at most `1e-11` in absolute value. Case 1 must additionally reproduce its '
             'analytic bilinear surface to `1e-11` at all sampled cell points.', '',
             'Case 2 is curved: bilinear interpolation generally does not equal the generating '
             'quadratic surface between nodes. Its independent reference is the four-corner '
             'formula, not an assertion of exact quadratic reproduction. No analytic-surface '
             'error is printed for that case.', '',
             'finterp uses `linear_interp_2d%initialize/evaluate`. bspline-fortran uses '
             '`bspline_2d` with orders `(2,2)`, which gives linear pieces in each coordinate. '
             'The local corner bounds concern these bilinear configurations; they do not '
             'establish shape preservation of higher-order tensor splines.', '',
             '## Bicubic reproduction and partial derivatives', '',
             'The B-spline example then reinitializes with orders `(4,4)` (cubic degree '
             'in each coordinate) and values of:', '', '```text',
             'p(x,y) = 1 + x**2 + 2*y**2 + x**3*y - x*y**3 + 0.5*x**2*y**2',
             'px      = 2*x + 3*x**2*y - y**3 + x*y**2',
             'py      = 4*y + x**3 - 3*x*y**2 + x**2*y',
             'pxy     = 3*x**2 - 3*y**2 + 2*x*y', '```', '',
             'It evaluates the value, x partial, y partial and mixed xy partial at 121 '
             'points on an 11-by-11 query grid spanning the full domain, including boundaries. '
             'This gives 484 evaluations. Each scaled error '
             '`abs(computed-reference)/max(1,abs(reference))` must be at most `1e-10`. '
             'The derivative requests use `(idx,idy)=(0,0),(1,0),(0,1),(1,1)`.', '',
             'All drivers use real64. These finite deterministic examples do not validate '
             'extrapolation, missing data, arbitrary knots, all derivative orders, scattered '
             'data or general interpolation error estimates. They are not a performance ranking.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author test |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][-1]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain the package license notices, '
              'including the B-spline NIST/CMLIB notice. They appear in hosted and main local '
              'FPM menus and downloaded projects. Loading a link selects source without '
              'submitting a job.', '', '## Recorded results', '',
              'Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-surfaces-validation.json) records hashes, pins '
              'and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers finterp-bilinear-surface bspline-tensor-surface',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def stiff_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-stiff-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS stiff-ODE drivers', '',
             'These three examples demonstrate the stiff ODE part of '
             '[I1a2: Stiff and mixed algebraic-differential equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a2). '
             'They do not establish DAE support or validate every method in these packages. '
             'GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).', '',
             '## Shared autonomous two-scale system', '', '```text',
             'dy1/dt = -1000*y1 + 999*y2', 'dy2/dt = -y2', 'y(0) = [2,1]', '',
             'y1(t) = exp(-t) + exp(-1000*t)', 'y2(t) = exp(-t)',
             'y1(t)-y2(t) = exp(-1000*t)', '```', '',
             'The constant Jacobian has eigenvalues -1000 and -1, giving fast and slow '
             'decaying modes with time scales 0.001 and 1. The exact solution follows '
             'directly from the two differential equations. Each real64 driver advances '
             'through `t=[0.001,0.01,0.1,1]`, so the first point includes the fast '
             'transient and the later points follow its decay.', '',
             'Every output requires finite time/state values, successful solver status and '
             'absolute time error at most `1e-12`. Maximum scaled state error '
             '`max(abs(y-exact)/max(1,abs(exact)))` must be at most `2e-6`. The absolute '
             'error in the fast-mode identity `y1-y2=exp(-1000*t)` must be at most `4e-6`. '
             'References use the analytic exponentials, not output from another solver. '
             'These are checks at the four requested times, not uniform error bounds '
             'between output points.', '',
             '## Configurations and status checks', '',
             '| Package | Configuration | Required success |', '| --- | --- | --- |',
             '| DVODE | `dvode_t%solve`, `MF=22`: BDF and an internally approximated full Jacobian; scalar `rtol=1e-8`, `atol=1e-10`; real/integer workspaces 100/40 | State `2` at each output |',
             '| ODEPACK | `lsoda_class%integrate`: automatic Adams/BDF switching; internal Jacobian; `rtol=1e-8`, `atol=[1e-10]`; maximum 5000 internal steps per call | State `2` at each output; at least one reported BDF method indicator |',
             '| stiff3 | Third-order autonomous Rosenbrock solver; analytic constant Jacobian; `eps=1e-8`, weights `[1,1]`, initial suggested half-step `1e-6` | Status `0` at each output |', '',
             'DVODE and LSODA initialize once, then continue the solution through successive '
             'output requests. The DVODE state and work arrays are retained. stiff3 advances '
             'the returned state/time over each successive interval and carries forward '
             'the suggested step size; the simple API is called anew for each interval.', '',
             'stiff3 uses its own weighted error test based on '
             '`w(i)*abs(estimated_error(i))/(1+abs(y(i)))` and `eps`. This is not an '
             'identical tolerance contract to the `rtol/atol` controls of DVODE and LSODA. '
             'The analytic Jacobian is supplied only to stiff3 in these examples.', '',
             'LSODA reports its current method indicator through `info(meth=...)`: '
             '`1=Adams`, `2=BDF`. The saved run reports Adams at 0.001 and 0.01, '
             'then BDF at 0.1 and 1. The driver requires observation of BDF mode, '
             'without fixing a particular switching time or requiring an exact history '
             'of internal steps.', '',
             'Step/evaluation counters are printed as API examples. DVODE and LSODA '
             'counters are cumulative; stiff3 statistics are for each interval. Different '
             'methods, Jacobian configurations, counters and error tests make these outputs '
             'unsuitable as a controlled performance or accuracy ranking.', '',
             '## Scope and sources', '',
             'The examples adapt author callback and invocation patterns to a common small '
             'linear ODE. Nonlinear stiffness, large sparse Jacobians, DAEs, events, '
             'discontinuities and all failure modes are outside this validation. '
             'The separate [nonstiff ODE review](gams-ode.md) covers other configurations.', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'License notices, including the ODEPACK LLNL public-domain notice, '
              'are retained. Module callbacks avoid executable-stack trampolines. '
              'The drivers appear in hosted and main local FPM menus and downloaded '
              'projects. Loading a link selects source without submitting a job.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were rebuilt. '
              'The [verification report](gams-stiff-validation.json) records hashes, pins '
              'and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers dvode-stiff-two-scale lsoda-stiff-two-scale stiff3-stiff-two-scale',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def polynomial_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-polynomial-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS polynomial-root drivers', '',
             'These three examples demonstrate [F1a: Polynomial equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F1a) '
             'using polyroots-fortran. Two newly reviewed procedures, `rpoly` and `cpolyroots`, '
             'have their own pinned evidence and entries in the numerical-review ledger. '
             'The three APIs are demonstrated separately. GAMS categories are not exhausted; '
             'see the [coverage report](gams-coverage.md).', '',
             '## Algorithms and input conventions', '',
             '| Procedure | Coefficients | Method | Required status |', '| --- | --- | --- | --- |',
             '| `polyroots` | Real | Real companion-matrix eigenvalues through LAPACK | `info=0` |',
             '| `rpoly` | Real | Jenkins-Traub all-roots solver | `istat=0`; partial results are not accepted |',
             '| `cpolyroots` | Complex | Complex companion-matrix eigenvalues through LAPACK | `info=0` |', '',
             'All three take coefficients in decreasing powers and run with real64 arithmetic. '
             'The real APIs return separate real/imaginary arrays; the driver combines them '
             'only after checking successful status. The complex API returns complex roots.', '',
             '## Known distinct roots', '',
             '| Case | Polynomial | Expected roots | APIs checked |', '| --- | --- | --- | --- |',
             '| 1 | `x**3-6*x**2+11*x-6` | `1,2,3` | All three |',
             '| 2 | `x*(x+2)*((x-1)**2+4) = x**4+x**2+10*x` | `-2,0,1+2i,1-2i` | All three |',
             '| 3 | Product of the three complex factors `(x-r)` listed here | `1+i,-2+0.5i,0.25-i` | `cpolyroots` |', '',
             'The last case has coefficients '
             '`[1, 0.75-0.5i, -1.25-0.125i, 2.125-2.125i]`. The driver constructs '
             'them by multiplying the known factors. All components are simple binary '
             'fractions; the reference roots are specified independently of the solver.', '',
             'Each case is repeated after multiplying every coefficient by `1`, `1e80` '
             'and `1e-80`. This leaves the mathematical roots unchanged. The two real '
             'drivers each perform six solver calls, and the complex driver performs nine. '
             'These scales test selected coefficient-scaling behavior without approaching '
             'the representable extremes of real64.', '',
             '## Order-independent matching and residual checks', '',
             'Every returned root must have finite real and imaginary parts. For each '
             'distinct expected root, the driver chooses the nearest unused computed root '
             'and marks it used. Its scaled distance '
             '`abs(computed-expected)/max(1,abs(expected))` must be at most `1e-9`. '
             'This checks one-to-one coverage without assuming returned order. The simple '
             'matching is appropriate for these well-separated roots; it is not a general '
             'clustered-root assignment algorithm.', '',
             'Each computed root is also substituted into the original scaled coefficient '
             'array using complex Horner evaluation. The normalized residual is:', '', '```text',
             'eta(z) = abs(p(z)) / sum_k(abs(a_k)*abs(z)**(n-k))', '```', '',
             'Here `a_0,...,a_n` are the coefficients in decreasing powers. The denominator '
             'is accumulated with a separate real Horner recurrence. Every normalized '
             'residual must be finite and at most `2e-12`. For the exact zero root with '
             'zero constant coefficient, both numerator and denominator are zero; that '
             'specific case is recorded as zero residual. A zero denominator with a '
             'nonzero numerator is rejected.', '',
             'A small polynomial residual alone does not establish accurate individual '
             'roots of an ill-conditioned polynomial, which is why the known-root check '
             'is separate. Repeated roots, tightly clustered roots, high degrees, every '
             'overload, root polishing and invalid inputs are outside this validation. '
             'These examples do not rank the methods by general accuracy or speed.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author test |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author test]({base}{d["author_example"]}) |')
    lines += ['', 'The programs adapt author API patterns and retain the full upstream license '
              'notices. They appear as separate examples in hosted and main local FPM menus '
              'and downloaded projects. Loading a link selects source without submitting a job.', '',
              '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing the existing polyroots-fortran library. Only the mains and executables '
              'were rebuilt. The [verification report](gams-polynomial-validation.json) '
              'records hashes, pins and full output, including each computed root. '
              'The summaries below retain the case, scale and maximum errors.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        summary = '\n'.join(line for line in output.splitlines()
                            if line.startswith(('Polynomial case', 'Max scaled', 'PASS ')))
        lines += ['### '+d['id'], '', '```text', summary, '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers polyroots-real-reference rpoly-real-reference cpolyroots-complex-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def convolution_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-convolution-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    fast = next(d for d in drivers if d['package_id']=='fastconv')
    fast_base = f'https://github.com/{packages["fastconv"]["repository"]}/blob/{fast["revision"]}/'
    lines = ['# Checked GAMS discrete-convolution drivers', '',
             'Both examples demonstrate [J2: Convolutions](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J2). '
             'They check the results with a direct summation independent of the library '
             'implementation. GAMS categories are not exhausted; see the '
             '[coverage report](gams-coverage.md).', '',
             '## Signals, kernels and reference', '',
             'The signal length is 37. Case 1 is an impulse at one-based sample 10. '
             'Case 2 is `sin(0.2*i)+(-1)**i*0.1*i`, for `i=1,...,37`. '
             'Both drivers test kernel lengths `[1,2,3,4,5,8,16,17]`. For length 1 '
             'the kernel is `[1]`; otherwise `h(j)=(-1)**j/(j+1)`. The asymmetric '
             'odd and even kernels check orientation and alignment, which a symmetric '
             'smoothing kernel could hide. Reusing the filter object also checks kernel '
             'replacement across lengths.', '',
             'A separate real64 nested loop constructs full linear convolution, with '
             'zero extension outside the inputs:', '', '```text',
             'full(i+j-1) += x(i)*h(j), for i=1,...,N and j=1,...,M',
             'size(full) = N+M-1', '```', '',
             'All outputs must have the expected lengths and finite values. The scaled '
             'output error is `max(abs(computed-reference))/max(1,max(abs(reference)))`.', '',
             '## spectrum: full and central results', '',
             'The spectrum driver uses real64 inputs and checks the default full result '
             'against the direct sum. Swapping signal and kernel must give the same full '
             'convolution. It separately checks the sum identity '
             '`sum(full)=sum(x)*sum(h)`, using scaled error at most `1e-11`.', '',
             'For `SPCTRM_CENTRAL_CONVOLUTION`, the pinned implementation returns the '
             'length of the longer input. In these cases the length is 37. The selected '
             'segment starts at one-based index `floor(M/2)+1` of the direct full result, '
             'where M is the shorter input length. This states the even-kernel alignment '
             'explicitly. Both input orders are tested for the central result too. '
             'Central results include boundary effects from zero extension; they are '
             'not the same as a valid-overlap convolution.', '',
             'All four output comparisons per signal/kernel case use tolerance `1e-11`. '
             'There are 16 signal/kernel combinations and 64 library calls. The driver '
             'does not require plotting or the author example plotting dependencies.', '',
             '## fastconv: valid overlap and native precision', '',
             'The default `conv1d_t` is the padded optimized implementation. The driver '
             'calls `set_kernel` and explicitly sets `preserve_shape=.false.`. The output '
             'length is `N-M+1`, and the reference is the one-based slice `full(M:N)`. '
             'The library reverses the supplied kernel internally; the caller supplies '
             'the mathematical kernel in its natural order.', '',
             'At this pin fastconv uses real32. The driver rounds the signal and kernel '
             'to real32 before calling it, then converts those actual arguments to '
             'real64 for independent accumulation. It compares all 16 outputs with '
             'scaled tolerance `2e-6`. This avoids treating input rounding as a library '
             'calculation error and does not imply real64 output precision.', '',
             '### Known shape-preserving boundary limitation', '',
             'The shape-preserving mode is excluded for a source-confirmed reason. '
             'At the reviewed pin, `apply` allocates the output without initializing it; '
             'the padded and reference convolution paths assign only the valid interior '
             'slice when `preserve_shape=.true.`. Boundary entries remain undefined. '
             'The author README example also prints an uninitialized boundary value. '
             'The checked driver uses valid overlap and does not read those entries.', '',
             f'Sources: [allocation and apply]({fast_base}src/conv1d/conv1d.f90), '
             f'[padded path]({fast_base}src/conv1d/pad.F90), '
             f'[reference path]({fast_base}src/conv1d/ref.F90), '
             f'[author README]({fast_base}README.md). These links identify the pinned '
             'implementation; no claim is made about later revisions.', '',
             '## Scope and sources', '',
             'The examples cover selected real-valued 1D operations, not empty inputs, '
             'kernels longer than the fastconv signal, multidimensional convolution, '
             'deconvolution, arbitrary padding policies or performance benchmarks. '
             'The precision and output conventions differ, so these are not a direct '
             'speed or accuracy ranking.', '',
             '| Driver | Pinned procedure and author usage |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author usage]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author API patterns and retain license notices. '
              'The fastconv reference is its README usage pattern, with the correct '
              'real32 kind import and the valid mode explicitly selected. These examples '
              'appear in hosted and main local FPM menus and downloaded projects. '
              'Loading a link selects source without submitting a job.', '', '## Recorded results', '',
              'Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were '
              'rebuilt. The [verification report](gams-convolution-validation.json) '
              'records hashes, pins and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers spectrum-convolution-reference fastconv-convolution-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def regression_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-regression-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS regression drivers', '',
             'Both examples demonstrate [L8: Regression](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L8), '
             'with different response and error models. They are not interchangeable '
             'ordinary linear least-squares examples. GAMS categories are not exhausted; '
             'see the [coverage report](gams-coverage.md).', '',
             '## Orthogonal line fitting with odrpack95', '',
             'The model is `y=a+b*x`, with unit error weights in both coordinates. '
             'This minimizes squared perpendicular distances, unlike vertical-residual '
             'ordinary least squares. The driver supplies analytic model derivatives '
             'through the public callback interface (`job=20`) and disables printing '
             'inside the solver (`iprint=0`).', '',
             '| Case | x observations | y observations | Initial coefficients |', '| --- | --- | --- | --- |',
             '| 1 | `0,1,2,3,4,5` | `1+2*x+[0.1,-0.1,0.1,-0.1,0.1,-0.1]` | `[0,1]` |',
             '| 2 | `10,11,12,13,14,15` | `-3-1.5*x+[0.2,-0.1,0.1,-0.2,0.05,-0.05]` | `[0,-1]` |', '',
             'Let `xc=x-mean(x)`, `yc=y-mean(y)`, `Sxx=sum(xc**2)`, '
             '`Syy=sum(yc**2)` and `Sxy=sum(xc*yc)`. For these nonvertical lines with '
             'nonzero cross-moment, the total least-squares references are:', '', '```text',
             'd = sqrt((Syy-Sxx)**2 + 4*Sxy**2)',
             'b = (Syy-Sxx+d)/(2*Sxy)', 'a = mean(y)-b*mean(x)',
             'minimum orthogonal SSE = (Sxx+Syy-d)/2', '```', '',
             'These formulas handle both signs of slope used here. The driver requires '
             'ODR status 1, 2 or 3, finite coefficients and objective, maximum absolute '
             'coefficient error at most `1e-5`, and absolute objective error at most '
             '`1e-8`. It independently recomputes the objective from original observations '
             'as `sum((y-a-b*x)**2)/(1+b**2)`. Covariance estimates, weighted or nonlinear '
             'ODR, vertical lines and every stopping condition are outside this example.', '',
             '## Grouped-binomial logistic regression with lib_statistics', '',
             'The model is `log(p/(1-p))=beta0+beta1*x`. Each dataset has six groups, '
             '20 trials per group, and three groups at each of two predictor levels. '
             'Because there are two model coefficients and two distinct predictor levels, '
             'the maximum-likelihood fit matches the aggregated success fraction at '
             'each level exactly.', '',
             '| Case | Predictor levels | Successes in the six groups | Level probabilities |',
             '| --- | --- | --- | --- |',
             '| 1 | `-1,1` | `[3,5,7,13,15,17]` | `1/4,3/4` |',
             '| 2 | `0,2` | `[3,5,7,13,15,17]` | `1/4,3/4` |',
             '| 3 | `-1,1` | `[2,4,6,10,12,14]` | `1/5,3/5` |', '',
             'Writing the two logits as `l0,l1` and predictor levels as `x0,x1`, '
             'the references are `beta1=(l1-l0)/(x1-x0)` and '
             '`beta0=l0-beta1*x0`. Cases 1 and 2 check a predictor translation and '
             'its effect on intercept and covariance. Case 3 gives a different, '
             'asymmetric pair of probabilities. Group proportions vary around their '
             'level averages, avoiding a zero residual-variance case.', '',
             'The driver independently evaluates Pearson chi-square and binomial deviance:', '',
             '```text', 'Pearson = sum((s-n*p)**2/(n*p*(1-p)))',
             'Deviance = 2*sum(s*log(s/(n*p)) + (n-s)*log((n-s)/(n*(1-p))))', '```', '',
             'All chosen success counts lie strictly between zero and the number of '
             'trials, so the displayed logarithms are well defined. Residual degrees of '
             'freedom must be `6-2=4`. The reference Fisher information is '
             '`I=sum(n*p*(1-p)*[1,x]^T*[1,x])`, formed from the known probabilities '
             'and inverted using the explicit 2-by-2 inverse.', '',
             'At this pin the API inflates covariance by '
             '`max(1,Pearson chi-square/ndf)`, as described in its source header. '
             'The driver checks that convention, rather than assuming unscaled '
             'binomial covariance. The variance inflation factors are `16/15` for '
             'cases 1 and 2 and `25/24` for case 3. Standard-error references are '
             'the square roots of the reference covariance diagonal.', '',
             'Required termination is `ier=0`. Coefficients, probabilities, standard '
             'errors, covariance, chi-square and deviance must be finite; fitted '
             'probabilities must lie strictly between zero and one and standard errors '
             'must be positive. Absolute tolerances are `1e-6` for coefficients, '
             'probabilities, chi-square and deviance, and `1e-5` for covariance and '
             'standard errors. The covariance tolerance allows the API iterative '
             'approximation. Multiple predictors, separation, weighted survey models, '
             'zero-trial groups and every error branch are outside this validation.', '',
             'Both drivers use real64. These are deterministic API and numerical checks, '
             'not a comparison of methods for the same statistical model or a speed ranking.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and provenance |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        author = (f'[Author example]({base}{d["author_example"]})' if d.get('author_example')
                  else 'Original public-API driver; no upstream test copied')
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / {author} |')
    lines += ['', 'The odrpack95 driver adapts the author callback pattern and retains its MIT '
              'notice. The logistic caller is independently written. Both appear in hosted '
              'and main local FPM menus and downloaded projects. Loading a link selects '
              'source without submitting a job.', '', '## Recorded results', '',
              'Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
              'reusing existing package libraries. Only the mains and executables were '
              'rebuilt. The [verification report](gams-regression-validation.json) '
              'records hashes, pins and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers odrpack-line-total-least-squares logistic-grouped-binomial-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def matrix_equations_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-matrix-equations-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS Lyapunov and Sylvester drivers', '',
             'These three SLICOT drivers demonstrate [D8: Other matrix equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D8). '
             'The SB04MD and SB04QD procedure mappings add pinned source evidence and '
             'numerical-review ledger entries. GAMS categories are not exhausted; '
             'see the [coverage report](gams-coverage.md).', '',
             '## Equations and known solutions', '',
             '| Procedure | Equation solved | Solution size |', '| --- | --- | --- |',
             '| SB03MD, continuous | `op(A)^T*X + X*op(A) = scale*C` | 3-by-3 symmetric |',
             '| SB03MD, discrete | `op(A)^T*X*op(A) - X = scale*C` | 3-by-3 symmetric |',
             '| SB04MD | `A*X + X*B = C` | 2-by-3 |',
             '| SB04QD | `X + A*X*B = C` | 2-by-3 |', '',
             'For each selected equation, the driver chooses a known matrix and constructs '
             'the right-hand side by matrix multiplication. After the solve it separately '
             'checks the recovered solution and the original equation residual. This '
             'does not use output from another solver as a reference.', '',
             '## Continuous and discrete Lyapunov configurations', '', '```text',
             'A_continuous = [[-1, 2, 0], [-2,-1,0.5], [0,0,-3]]',
             'A_discrete   = [[0.2,0.3,0], [-0.3,0.2,0.1], [0,0,0.5]]',
             'X1 = [[2,0.5,-0.25], [0.5,1,0.2], [-0.25,0.2,1.5]]',
             'X2 = 0.5*X1 + identity(3)', '```', '',
             'The continuous coefficient matrix has eigenvalues `-1+2i,-1-2i,-3`; '
             'the discrete matrix has eigenvalues `0.2+0.3i,0.2-0.3i,0.5`. Thus '
             'the selected continuous matrix is stable and the selected discrete '
             'matrix has spectral radius below one. The complex conjugate pairs '
             'exercise real Schur blocks beyond purely diagonal examples.', '',
             'Each equation is checked with `TRANA=N` (`op(A)=A`) and `TRANA=T` '
             '(`op(A)=A^T`). For the first right-hand side, `FACT=N` computes the '
             'Schur factors. For the second, `FACT=F` reuses the returned Schur '
             'matrix and orthogonal factor while replacing the right-hand side. '
             'This gives eight solver calls. `JOB=X` requests only the solution; '
             'the driver does not read separation or forward-error outputs.', '',
             'SB03MD overwrites its right-hand-side array with a scaled solution. '
             'The driver requires finite `0<scale<=1`, compares `X_returned/scale` '
             'with the known unscaled solution and evaluates the original equation '
             'with `scale*C` on its right-hand side. The selected calls return '
             '`scale=1`; overflow-driven scaling below one is not independently '
             'exercised. Maximum absolute symmetry error must be at most `1e-12`.', '',
             '## Rectangular Sylvester configurations', '', '```text',
             'A_continuous = [[-1,0.75], [0,-2]]',
             'B_continuous = [[-3,1,0], [0,-4,-0.5], [0,0,-5]]',
             'A_discrete = [[0.2,0.1], [0,0.4]]',
             'B_discrete = [[0.3,-0.2,0], [0,0.5,0.1], [0,0,0.6]]',
             'X1 = [[1,-2,0.5], [3,1,-1]]',
             'X2 = [[-1,0,2], [0.5,-2,1]]', '```', '',
             'The first case uses the listed coefficients and X1. The second uses '
             'their transposes and X2, retaining a 2-by-3 solution. The continuous '
             'spectra have no pair whose sum is zero; the discrete eigenvalue '
             'products are positive and less than one, so `1+lambda(A)*lambda(B)` '
             'is nonzero. These choices give unique solutions without intentionally '
             'ill-conditioned or singular equations.', '',
             'Both routines overwrite coefficient and right-hand-side arrays. The '
             'driver preserves originals and restores them before evaluating the '
             'residual; using returned transformed coefficients would check a '
             'different equation. The real workspace length is 1000 and integer '
             'workspace length is `4*N`. Each routine must return `INFO=0`.', '',
             '## Acceptance criteria and limits', '',
             'All outputs checked here use real64. The scaled solution error is '
             '`max(abs(computed-known))/max(1,max(abs(known)))`, bounded by `1e-10`. '
             'The scaled residual is `max(abs(LHS-RHS))/max(1,max(abs(RHS)))`, '
             'bounded by `1e-12`. Lyapunov residuals use the returned scaled '
             'solution and `scale*C`; Sylvester residuals use the unscaled equation. '
             'Solutions and residual measures must be finite.', '',
             'This residual normalization is not claimed to be a condition estimate '
             'or a complete normwise backward-error analysis. Near-singular equations, '
             'all warning/error branches, condition/error estimates, generalized '
             'matrix equations, model reduction and the rest of SLICOT are outside '
             'this validation. The examples do not benchmark performance.', '',
             '## Sources and playground links', '',
             '| Driver | Pinned procedure and author example |', '| --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines.append(f'| [Load {d["id"]}]({url}) / [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                     f'[Author example]({base}{d["author_example"]}) |')
    lines += ['', 'The drivers adapt author invocation patterns and retain BSD notices. '
              'They appear in hosted and main local FPM menus and downloaded projects. '
              'Loading a link selects source without submitting a job.', '', '## Recorded results', '',
              'All three passed in the restricted GNU Fortran 16.2.0 sandbox with '
              'FPM 0.12.0, reusing the existing SLICOT library and compatible LP64 '
              'BLAS/LAPACK. Only the mains and executables were rebuilt. '
              'The [verification report](gams-matrix-equations-validation.json) '
              'records hashes, pins and saved output.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers slicot-lyapunov-known-matrix slicot-continuous-sylvester slicot-discrete-sylvester',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required.', '']
    return '\n'.join(lines)


def coverage_data(root=ROOT, data=None):
    """Count maintained assignments separately from class-specific checked demonstrations."""
    data = data or gams_data(root)
    drivers = driver_data(root, data)
    records = data['procedure_mappings']
    tree = class_tree(data)
    top = []
    for code, label in data['classes'].items():
        top.append({'code': code, 'label': label,
                    'package_ids': sorted(name for name, codes in data['packages'].items() if code in codes),
                    'procedure_ids': [r['id'] for r in records
                                      if any(code in ancestors(tree, c) for c in r['gams_codes'])],
                    'checked_procedure_ids': sorted({d['procedure_id'] for d in drivers
                                                     if code in ancestors(tree, d['gams_code'])}),
                    'driver_ids': [d['id'] for d in drivers if code in ancestors(tree, d['gams_code'])]})
    specific = []
    for code in sorted({c for r in records for c in r['gams_codes']}, key=class_order):
        specific.append({'code': code, 'label': tree[code]['label'],
                         'procedure_ids': [r['id'] for r in records if code in r['gams_codes']],
                         'checked_procedure_ids': sorted({d['procedure_id'] for d in drivers if d['gams_code'] == code}),
                         'driver_ids': [d['id'] for d in drivers if d['gams_code'] == code]})
    return {'top_level': top, 'procedure_classes': specific,
            'procedure_count': len(records), 'driver_count': len(drivers),
            'checked_procedure_count': len({d['procedure_id'] for d in drivers})}


def coverage_review_text(root=ROOT):
    coverage = coverage_data(root)
    top = coverage['top_level']
    specific = coverage['procedure_classes']
    covered = sum(bool(row['driver_ids']) for row in top)
    unchecked = sum(not row['driver_ids'] for row in specific)
    lines = ['# GAMS classification and checked-driver coverage', '',
             '**The GAMS categories are not exhausted.** Some procedures already map to the deepest '
             'available GAMS class, but that does not mean all procedures or problem configurations '
             'in that class have been demonstrated.', '',
             f'The selected catalog has {coverage["procedure_count"]} source-reviewed procedure records. '
             f'{coverage["driver_count"]} independently checked drivers cover '
             f'{coverage["checked_procedure_count"]} of those records and {covered} of the 20 top-level '
             f'GAMS classes. Among the {len(specific)} maintained classes used directly by procedure '
             f'records, {unchecked} still have no class-specific checked driver.', '',
             'These counts concern the dedicated GAMS drivers. The ordinary precompiled-package '
             'demonstrations have their own build/run verification and are not counted as class-specific drivers here.', '',
             '## What these counts mean', '',
             '- Package assignments are discovery classifications and may describe capabilities beyond the reviewed procedures.',
             '- A source-reviewed procedure has pinned API/source evidence. This alone does not mean a matching driver has been run.',
             '- A checked driver demonstrates its recorded procedure and problem class with saved successful sandbox evidence. '
             'It does not cover every overload or input.',
             '- Reaching a taxonomy leaf, such as F1b or E1a, means there is no finer GAMS category in the recorded taxonomy. '
             'Additional procedures, drivers and non-GAMS descriptors can still distinguish useful capabilities.', '',
             'This is coverage of our maintained selected-package records, **not a complete inventory of the GAMS taxonomy '
             'or all Fortran software**. A class with a checked driver is not marked exhausted. Empty categories may lack '
             'a suitable selected package; other categories have many source-reviewed procedures awaiting drivers.', '',
             '## Top-level coverage', '',
             'Procedure and driver counts include descendants. A procedure assigned to multiple categories may appear '
             'in multiple rows, so the rows should not be summed.', '',
             '| Class | Description | Assigned packages | Reviewed procedures | Procedures with checked drivers | Drivers |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for row in top:
        code = row['code']
        lines.append(f'| [{code}](https://beliavsky.github.io/fortran-playground/gams/{code}/) | {row["label"]} | '
                     f'{len(row["package_ids"])} | {len(row["procedure_ids"])} | '
                     f'{len(row["checked_procedure_ids"])} | {len(row["driver_ids"])} |')
    lines += ['', '## Direct procedure-class coverage', '',
              'These are the most specific classes currently recorded for procedures, not necessarily leaves of the '
              'full GAMS taxonomy. Counts are exact class matches. For example, an analytic-gradient driver does '
              'not check a derivative-free configuration of the same generic procedure.', '',
              '| Class | Label (read with ancestors) | Reviewed procedures | Procedures with checked drivers | Drivers |',
              '| --- | --- | ---: | ---: | ---: |']
    for row in specific:
        code = row['code']
        lines.append(f'| [{code}](https://beliavsky.github.io/fortran-playground/gams/{code}/) | {row["label"]} | '
                     f'{len(row["procedure_ids"])} | {len(row["checked_procedure_ids"])} | {len(row["driver_ids"])} |')
    lines += ['', 'See the [numerical review](gams-numerical.md) for named procedures and pinned source evidence, '
              'and [classification review](fpm-gams.md) for package assignments. Classes with reviewed procedures '
              'and zero checked drivers are a useful next-driver queue. The numerical review also lists discovery '
              'assignments without matching procedure records.', '', '## Maintenance', '',
              'This page is regenerated from the same classifications, driver manifest and successful verification '
              'reports used by the playground and portable catalog. It is checked by:', '',
              '```text', 'python xpackage_gams.py', 'python xpackage_gams.py --check', '```', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated review page is out of date')
    args = parser.parse_args()
    for report, text in ((REPORT, review_text()), (PILOT_REPORT, g1_review_text()),
                         (NUMERICAL_REPORT, numerical_review_text()), (QUADRATURE_REPORT, quadrature_review_text()),
                         (ROOTS_REPORT, roots_review_text()), (LINEAR_ALGEBRA_REPORT, linear_algebra_review_text()),
                         (ODE_REPORT, ode_review_text()), (INTERPOLATION_REPORT, interpolation_review_text()),
                         (TRANSFORMS_REPORT, transforms_review_text()), (CONSTRAINED_REPORT, constrained_review_text()),
                         (SPECIAL_FUNCTIONS_REPORT, special_functions_review_text()),
                         (STATISTICS_REPORT, statistics_review_text()),
                         (RANDOM_REPORT, random_review_text()),
                         (DIFFERENTIATION_REPORT, differentiation_review_text()),
                         (SYSTEMS_REPORT, systems_review_text()),
                         (SPARSE_REPORT, sparse_review_text()),
                         (CUBATURE_REPORT, cubature_review_text()),
                         (SURFACES_REPORT, surfaces_review_text()),
                         (STIFF_REPORT, stiff_review_text()),
                         (POLYNOMIAL_REPORT, polynomial_review_text()),
                         (CONVOLUTION_REPORT, convolution_review_text()),
                         (REGRESSION_REPORT, regression_review_text()),
                         (MATRIX_EQUATIONS_REPORT, matrix_equations_review_text()),
                         (COVERAGE_REPORT, coverage_review_text())):
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
