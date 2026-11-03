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
SORTING_REPORT = Path('docs/gams-sorting.md')
NUMBER_THEORY_REPORT = Path('docs/gams-number-theory.md')
ARITHMETIC_REPORT = Path('docs/gams-arithmetic.md')
APPLIED_METHODS_REPORT = Path('docs/gams-applied-methods.md')
BOUNDARY_REPORT = Path('docs/gams-boundary.md')
RESAMPLING_MARKOV_REPORT = Path('docs/gams-resampling-markov.md')
FOURIER_GEOMETRY_REPORT = Path('docs/gams-fourier-geometry.md')
SPARSE_INTEGRAL_REPORT = Path('docs/gams-sparse-integral.md')
SPATIAL_NUFFT_REPORT = Path('docs/gams-spatial-nufft.md')
PDE_REPORT = Path('docs/gams-pde.md')
DATA_KINDS_REPORT = Path('docs/gams-data-kinds.md')
PRODUCTS_STATUS_REPORT = Path('docs/gams-products-status.md')
KRIGING_NETWORK_REPORT = Path('docs/gams-kriging-network.md')
LOOKUP_FASTMATH_REPORT = Path('docs/gams-lookup-fastmath.md')
CIRCUITS_BETA_REPORT = Path('docs/gams-circuits-beta.md')
INVERSE_TVD_REPORT = Path('docs/gams-inverse-tvd.md')
ROOTS_SPLINES_QUADRATURE_REPORT = Path('docs/gams-roots-splines-quadrature.md')
IO_BOUNDS_REPORT = Path('docs/gams-io-bounds.md')
OPTIMIZATION_SPACING_REPORT = Path('docs/gams-optimization-spacing.md')
RASTER_DISTRIBUTIONS_REPORT = Path('docs/gams-raster-distributions.md')
QUANTITIES_SPHERICAL_REPORT = Path('docs/gams-quantities-spherical.md')
DELAY_EMBEDDING_REPORT = Path('docs/gams-delay-embedding.md')
MATRIX_ROOTS_BOX_REPORT = Path('docs/gams-matrix-roots-box.md')
DISPERSION_REPORT = Path('docs/gams-dispersion.md')
RULES_DIFFERENCES_REPORT = Path('docs/gams-rules-differences.md')
QR_AUTODIFF_REPORT = Path('docs/gams-qr-autodiff.md')
DENSE_SPECTRA_REPORT = Path('docs/gams-dense-spectra.md')
LEAST_INTERPOLATION_REPORT = Path('docs/gams-least-interpolation.md')
RKF_QAGS_REPORT = Path('docs/gams-rkf-qags.md')
JACOBIAN_ROOTS_REPORT = Path('docs/gams-jacobian-roots.md')
HIGHER_AD_REPORT = Path('docs/gams-higher-ad.md')
MOMENTS_NUFFT2D_REPORT = Path('docs/gams-moments-nufft2d.md')
ITERATIVE_LS_REPORT = Path('docs/gams-iterative-ls.md')
SPECTRAL_WRAPPERS_REPORT = Path('docs/gams-spectral-wrappers.md')
REGRID_RK45_REPORT = Path('docs/gams-regrid-rk45.md')
FITPACK_POLYNOMIALS_REPORT = Path('docs/gams-fitpack-polynomials.md')
DIAGONAL_RESPONSE_REPORT = Path('docs/gams-diagonal-response.md')
RANKING_MAGIC_REPORT = Path('docs/gams-ranking-magic.md')
GEODESY_FORLAB_REPORT = Path('docs/gams-geodesy-forlab.md')
JACOBIAN_TRANSFORMS_REPORT = Path('docs/gams-jacobian-transforms.md')
EXPRESSION_EVALUATION_REPORT = Path('docs/gams-expression-evaluation.md')
CONVERSION_TRIANGULATION_REPORT = Path('docs/gams-conversion-triangulation.md')
GRAPH_SORTING_REPORT = Path('docs/gams-graph-sorting.md')
NEIGHBORS_SPARSE_REPORT = Path('docs/gams-neighbors-sparse.md')
ADAPTIVE_AD_REPORT = Path('docs/gams-adaptive-ad.md')
LU_ORBITS_REPORT = Path('docs/gams-lu-orbits.md')
DAE_FFT_REPORT = Path('docs/gams-dae-fft.md')
PROPACK_FMM_REPORT = Path('docs/gams-propack-fmm.md')
GMRES_INVERSE_REPORT = Path('docs/gams-gmres-inverse.md')
PERIODIC_CALCULUS_REPORT = Path('docs/gams-periodic-calculus.md')
EXPRESSIONS_SKY_REPORT = Path('docs/gams-expressions-sky.md')
UNSIGNED_BITSETS_REPORT = Path('docs/gams-unsigned-bitsets.md')
SPARSE_ADVECTION_REPORT = Path('docs/gams-sparse-advection.md')
PRODUCTS_PARTITIONS_REPORT = Path('docs/gams-products-partitions.md')
MULTIDIMENSIONAL_FFT_REPORT = Path('docs/gams-multidimensional-fft.md')
SPARSE_SPECTRA_REPORT = Path('docs/gams-sparse-spectra.md')
PROJECTION_LBFGS_REPORT = Path('docs/gams-projection-lbfgs.md')
GRADIENT_SWARM_REPORT = Path('docs/gams-gradient-swarm.md')
PROJECTION_TRAINING_REPORT = Path('docs/gams-projection-training.md')
DIRECTIONS_FITTING_REPORT = Path('docs/gams-directions-fitting.md')
RANDOM_REFERENCES_REPORT = Path('docs/gams-random-references.md')
TANGENTS_BLOCKS_REPORT = Path('docs/gams-tangents-blocks.md')
RADIAL_DENSE_REPORT = Path('docs/gams-radial-dense.md')
INFERENCE_PAIRS_REPORT = Path('docs/gams-inference-pairs.md')
HELMHOLTZ_STREAMS_REPORT = Path('docs/gams-helmholtz-streams.md')
FRICTION_TORCH_REPORT = Path('docs/gams-friction-torch.md')
PARETO_DIIS_REPORT = Path('docs/gams-pareto-diis.md')
DATA_TEN_REPORT = Path('docs/gams-data-ten.md')
STATE_TEN_REPORT = Path('docs/gams-state-ten.md')
INTEROP_TEN_REPORT = Path('docs/gams-interop-ten.md')
STORAGE_TEN_REPORT = Path('docs/gams-storage-ten.md')
WORKFLOWS_TEN_REPORT = Path('docs/gams-workflows-ten.md')
STATISTICS_SERVICES_TEN_REPORT = Path('docs/gams-statistics-services-ten.md')
FACTORIZATION_RULES_TEN_REPORT = Path('docs/gams-factorization-rules-ten.md')
SPECIAL_FUNCTIONS_TEN_REPORT = Path('docs/gams-special-functions-ten.md')
SYSTEMS_SPECTRA_TEN_REPORT = Path('docs/gams-systems-spectra-ten.md')
DISTRIBUTION_TEN_REPORT = Path('docs/gams-distribution-ten.md')
PCA_ORDERING_TEN_REPORT = Path('docs/gams-pca-ordering-ten.md')
ACTIVATIONS_TEN_REPORT = Path('docs/gams-activations-ten.md')
GRIDS_TEN_REPORT = Path('docs/gams-grids-ten.md')
COMPLEX_TEN_REPORT = Path('docs/gams-complex-ten.md')
COMPLEX_OPERATORS_TEN_REPORT = Path('docs/gams-complex-operators-ten.md')
STATISTICS_RANK_TEN_REPORT = Path('docs/gams-statistics-rank-ten.md')
GRIDS_SPECTRA_TEN_REPORT = Path('docs/gams-grids-spectra-ten.md')
INTEGRALS_TENSORS_TEN_REPORT = Path('docs/gams-integrals-tensors-ten.md')
TRANSFORMS_STRUCTURES_TEN_REPORT = Path('docs/gams-transforms-structures-ten.md')
FULLERTON_FUNCTIONS_TEN_REPORT = Path('docs/gams-fullerton-functions-ten.md')
ROOTS_STRUCTURED_TEN_REPORT = Path('docs/gams-roots-structured-ten.md')
ORDERING_RUNGE_TEN_REPORT = Path('docs/gams-ordering-runge-ten.md')
GAMMA_RELATIVE_TEN_REPORT = Path('docs/gams-gamma-relative-ten.md')
BANDED_PRODUCTS_TEN_REPORT = Path('docs/gams-banded-products-ten.md')
FORLAB_STATISTICS_TEN_REPORT = Path('docs/gams-forlab-statistics-ten.md')
NAFPACK_FACTORS_TEN_REPORT = Path('docs/gams-nafpack-factors-ten.md')
FSTATS_SUMMARIES_TEN_REPORT = Path('docs/gams-fstats-summaries-ten.md')
FSTATS_FITTING_TEN_REPORT = Path('docs/gams-fstats-fitting-ten.md')
NEXT_NUMERICAL_REPORT = Path('docs/gams-next-numerical.md')
FORTRANLIB_TABLES_REPORT = Path('docs/gams-fortranlib-tables.md')
COVERAGE_REPORT = Path('docs/gams-coverage.md')
EVIDENCE_REPORT = Path('docs/gams-mapping-evidence.md')
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


def class_evidence(tree, code, records, drivers):
    """Assess this class only; a driver for a sibling capability is not evidence."""
    matched = [p for p in records if any(code in ancestors(tree, c) for c in p['gams_codes'])]
    procedure_ids = {p['id'] for p in matched}
    checked = [d for d in drivers if d['procedure_id'] in procedure_ids
               and code in ancestors(tree, d['gams_code'])]
    status = 'verified' if checked else 'source-supported' if matched else 'uncertain'
    return {'status': status, 'procedures': matched, 'drivers': checked}


def mapping_evidence_text(root=ROOT):
    data = gams_data(root)
    tree = class_tree(data)
    drivers = driver_data(root, data)
    rows = []
    for name in sorted(data['packages']):
        records = procedure_records(data, name)
        package_drivers = [d for d in drivers if d['package_id'] == name]
        for cls in package_classes(data, name):
            result = class_evidence(tree, cls['code'], records, package_drivers)
            rows.append((name, cls['code'], result))
    counts = Counter(result['status'] for _, _, result in rows)
    lines = ['# Evidence for GAMS package mappings', '',
             'This report assesses each package/class pair, including inherited parent classes. '
             'A checked package default does not verify every classification.', '',
             '- **Verified:** a checked driver demonstrates a recorded procedure in this class or a descendant. '
             'Only the driver\'s tested configuration is verified.',
             '- **Source-supported:** a named procedure has pinned source evidence for this class, '
             'but no matching checked GAMS driver has been recorded.',
             '- **Uncertain:** the discovery classification has no matching procedure-level evidence '
             'in our records. This is a review queue, not a finding that the package lacks the capability.', '',
             'When a driver cannot be created, inspect the pinned implementation and author examples. '
             'Narrow or remove a classification that is unsupported; do not substitute an unrelated default '
             'example as evidence. Record missing dependencies, sandbox limits and upstream defects separately '
             'in the procedure or package review notes. A sandbox failure alone does not disprove an algorithm.', '',
             'Counts refer to package/class pairs and include parents: '+', '.join(
                 f'{counts[s]} {s}' for s in ('verified', 'source-supported', 'uncertain'))+'.', '',
             '## Mappings requiring source review', '',
             'Inspect these discovery assignments before making a specific algorithm claim. '
             'Their existing classifications remain visible, explicitly marked uncertain, until reviewed.', '',
             '| Package | Class | Description |', '| --- | --- | --- |']
    for name, code, result in rows:
        if result['status'] == 'uncertain':
            lines.append(f'| [{name}](https://beliavsky.github.io/fortran-playground/gams/packages/{name}/) | '
                         f'[{code}](https://beliavsky.github.io/fortran-playground/gams/{code}/) | {tree[code]["label"]} |')
    lines += ['', '## Procedure evidence and remaining driver work', '',
              'Statuses below apply to each recorded procedure/class pair. A driver for a different class '
              'of the same procedure does not verify this pair. Follow the procedure link for pinned source, '
              'author examples and limitations.', '',
              '| Package / procedure | Class | Evidence |', '| --- | --- | --- |']
    for record in sorted(data['procedure_mappings'], key=lambda p: (p['package_id'], p['id'])):
        for code in record['gams_codes']:
            result = class_evidence(tree, code, [record], drivers)
            url = f'https://beliavsky.github.io/fortran-playground/gams/packages/{record["package_id"]}/#{record["id"]}'
            lines.append(f'| [{record["package_id"]} / {record["id"]}]({url}) | {code} | {result["status"]} |')
    lines += ['', '## Maintenance', '',
              'Regenerate with `python xpackage_gams.py`; check with `python xpackage_gams.py --check`. '
              'The report and catalog labels use the same class-specific evidence rule. '
              'Saved successful driver verification is required before a driver enters the manifest.', '']
    return '\n'.join(lines)


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
             'The [mapping evidence report](gams-mapping-evidence.md) labels each class-specific mapping '
             'as verified, source-supported or uncertain and lists discovery assignments needing source review. '
             'If a claimed algorithm cannot be demonstrated, revisit the source evidence and narrow or remove '
             'unsupported mappings; document execution limits separately.', '',
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
              'The saved verification reports include source hashes and program output: '+', '.join(
                  f'[{Path(path).name}]({Path(path).name})'
                  for path in sorted({driver_validation_path(d) for d in drivers}))+'. '
              'Publishing checks that these hashes and package revisions still match.', '',
              'The sine driver minimizes sin(x) on [-4,0] and checks the solution against −π/2. '
              'Both Bard drivers fit the same 15 observations, start from (1,1,1), and check against '
              '(0.08241058, 1.133037, 2.343695), with maximum parameter error below 0.0002. '
              'Both require the residual norm to differ from 0.09063596 by less than 0.0000001. '
              'For the Bard problem, MINPACK lmdif1 estimates the Jacobian by finite differences; '
              'libdogleg uses an analytic Jacobian. The separate '
              '[lmder1 reference fits](gams-jacobian-roots.md) supply user Jacobians and have their own exact '
              'parameter and objective references. The '
              '[nonlin exact-fit driver](gams-jacobian-transforms.md) verifies the exact exponential '
              'subset with a specified initial step bound; its default-setting and nonzero-residual '
              'failures are preserved separately. '
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
              "in each selected driver's manifest-specified validation file. It does not rebuild package libraries or deploy the service. "
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
             'These examples connect specific integration and quadrature-rule procedures to GAMS problem classes. '
             'They are checked consumer programs at the catalog source revisions, rather than tests of every '
             'quadrature rule or a performance benchmark.', '',
             '| Class | Problem | Procedures |', '| --- | --- | --- |',
             '| [H2a1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a1a1) | Automatic one-dimensional integration on a finite interval, integrand supplied as a procedure | QUADPACK `dqag`; quadrature-fortran `integration_class_1d%integrate`; FGSL `fgsl_integration_qags` |',
             '| [H2a2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2a1) | Automatic finite-interval integration for special integrands supplied as procedures | QUADPACK `dqags`, demonstrated with integrable endpoint singularities |',
             '| [H2a2b2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2b2) | Nonautomatic integration of a stored spline | fitpack `fitpack_curve%integral` |', '',
             'The [stored-spline integration review](gams-sparse-integral.md) '
             'describes the fitpack polynomial antiderivative checks, reversed '
             'and zero-width intervals, and partition additivity.', '',
             'Rule generators in H2c have their own exact-moment checks. The '
             '[quadrature-moment and 2D-transform review](gams-moments-nufft2d.md) '
             'describes QDUtilLib Legendre and full-function-weight Hermite rules; '
             'other generator checks retain their recorded scope below.', '',
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
              f'All {len(drivers)} passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
              'Existing package libraries were reused; only each main and executable were compiled. '
              'The verification reports lock driver hashes and source revisions: '+', '.join(
                  f'[{Path(path).name}]({Path(path).name})'
                  for path in sorted({driver_validation_path(d) for d in drivers}))+'.', '',
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
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'The verifier requires Modal authentication and the local `.fpm-audit-cache/precompiled.json` '
              'build report. Each driver manifest entry identifies its verification report, allowing optimization '
              'and quadrature evidence to be maintained separately. Publication checks the correct report for '
              'every driver. These examples and classifications require no backend redeployment or library rebuild.', '']
    return '\n'.join(lines)


def roots_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data) if d['gams_code'] == 'F1b'
               and driver_validation_path(d) == 'docs/gams-roots-validation.json']
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
             'Additional forsolver Newton fixtures use their own equations and acceptance checks; see the '
             '[Jacobian and scalar-Newton review](gams-jacobian-roots.md). They are maintained separately '
             'from this shared bracketed-root comparison.', '',
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
             'matrix-decomposition examples, exact scalar products, BLAS products, sparse products, storage conversion and known pseudoinverses. Procedure mappings describe the '
             'reviewed real configurations; other overloads require their own evidence.', '',
             '| Class | Configuration | Procedures |', '| --- | --- | --- |',
             '| [D1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1) | Real scalar products, direct and blocked methods | fordot `dot_product` |',
             '| [D2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a1) | Real nonsymmetric general linear systems | `linear_algebra:solve`; `stdlib_linalg:solve` |',
             '| [D2a4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a4) | Real nonsymmetric sparse linear systems | Y12M `y12mb, y12mc, y12md` |',
             '| [D9a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9a1) | Unconstrained linear least squares, L2 solution | `linear_algebra:lstsq`; `stdlib_linalg:lstsq` |',
             '| [D4a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D4a1) | Ordinary real symmetric eigenproblems | fortran-lapack `la_lapack:syev`; ARPACK `DSAUPD/DSEUPD`; linalg_fortran `linalg%eigh` |',
             '| [D5](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D5) | Orthogonalization, demonstrated by reduced QR | fortran-lapack `linear_algebra:qr` |',
             '| [D6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D6) | Singular value decomposition | fortran-lapack `la_lapack:gesvd`, real64 overload |',
             '| [D1b6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b6) | Rectangular real matrix products | blas-interface `blas_gemm` |',
             '| [D1b4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b4) | Rectangular sparse matrix-vector products | fsparse `matvec`, COO/CSR real64 overloads |',
             '| [D9c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9c) | Generalized inverse | forinv `inv`, SVD method with explicit cutoff |', '',
             '## Exact scalar products', '',
             'The fordot driver checks 231 default and m1..m4 products over five '
             'lengths and three deterministic input patterns. Exact int64 '
             'numerators divided by 32 supply independent dyadic references. '
             'Valid distinct block counts 1, 3 and n cover unequal blocks and '
             'single-element blocks. See the [reference details and output](gams-products-status.md).', '',
             '## Shared dense-system checks', '',
             'Both solve drivers use the 3-by-3 systems from stdlib `example_solve1` and fortran-lapack '
             '`test_dsolve`, with reference solutions `[5,3,-2]` and `[-2,-2,3]`. They preserve the original '
             'matrix and right-hand side, check solver status and finite solutions, and require maximum '
             'solution error at most `1e-10`. The independently computed scaled residual is '
             '`||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)` and must be at most `1e-12`. '
             'Matrix infinity norm means the maximum absolute row sum.', '',
             '## Nonsymmetric sparse solves', '',
             'The Y12M driver uses two nonsymmetric 10-by-10 matrices, '
             'including a cyclic row permutation, and reuses one LU '
             'factorization for four right-hand sides per matrix. Independent '
             'manufactured solutions and scalar residuals determine acceptance. '
             'See the [fixtures, tolerances and output](gams-sparse-integral.md).', '',
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
             '## BLAS matrix multiplication', '',
             'The D1b6 driver computes a 3-by-2 times 2-by-4 product with '
             '`A(i,k)=2*i-3*k`, `B(k,j)=3*k-j` and `C0(i,j)=(i-j)/2`. '
             'Twelve calls cover all NN/NT/TN/TT storage/transpose combinations and '
             '`(alpha,beta)=[(1,0),(-2,0.5),(0,-1)]`. Independent scalar triple loops form '
             '`alpha*A*B+beta*C0`; no MATMUL or separate BLAS call supplies the reference. '
             'The zero-alpha case checks scaling of an existing output independently of the product. '
             'Every result must be finite with scaled maximum-entry error at most `1e-12`. '
             'The package is an interface to the installed BLAS implementation. Complex overloads, '
             'padded leading dimensions and other BLAS routines are outside the driver.', '',
             '## Sparse accumulated matrix-vector products', '',
             'The D1b4 driver uses the nonsymmetric 4-by-3 matrix with rows '
             '`[2,0,4]`, `[0,3,0]`, `[0,0,0]`, `[-1,0,5]`. '
             'Inputs `[1,-2,3]`, `[0,1,-1]` and zero give products '
             '`[14,-6,0,14]`, `[-4,3,0,-5]` and zero. Scalar row/column loops '
             'independently compute each reference. COO and CSR forms are checked with both zero '
             'and nonzero initial output `[0.5,-1,7,2]`, and every call is repeated to check '
             '`y := y+A*x` accumulation rather than replacement. All 24 calls must return finite '
             'vectors with absolute maximum-entry error at most `1e-12`.', '',
             'The empty third row must retain its initial output value. The test exercises the '
             'conversion helpers to prepare storage, but its verified problem class is D1b4; '
             'the separate D1b9 storage-conversion mapping is not marked verified by this driver. '
             'Symmetric-storage shortcuts, complex overloads and other sparse formats are outside the example.', '',
             '## Sparse storage conversion', '',
             'A separate D1b9 driver checks `dense2coo`, `coo2dense`, `coo2csr` and '
             '`csr2coo` with five matrices: a 5-by-4 matrix with entries '
             '`(2,1)=-2`, `(2,4)=0.5`, `(4,2)=3`, `(4,4)=-4`; its transpose; '
             'an all-zero 3-by-2 matrix; a fully populated 2-by-3 matrix '
             '`A(i,j)=(2*i+3*j)/2`; and the 1-by-1 matrix `[-7]`. '
             'The sparse fixtures include leading, interior and trailing empty rows '
             'and empty columns. All entries are moderate exact dyadic values.', '',
             'Independent scalar row/column loops check every COO coordinate/value '
             'against the original matrix, not just a round trip. Independently '
             'counted row entries determine every expected CSR row pointer. '
             'Dimensions, array sizes, nonzero counts, one-based indexing, CSR '
             'columns and values, and finite stored data must agree exactly. '
             'A separate scalar CSR reconstruction, CSR-to-COO conversion and '
             'both COO-to-dense restorations must recover the original matrix '
             'exactly. The caller zero-initializes dense outputs because '
             '`coo2dense` writes stored entries only. Fresh storage is used for '
             'each fixture. Duplicate coordinates, preallocated-storage reuse, '
             'complex/symmetric formats and threshold/subnormal behavior are '
             'outside this checked configuration. In particular, the pinned '
             '`dense2coo` source counts `abs(value)>tiny` but skips '
             '`abs(value)<tiny` while copying; equality at the threshold '
             'needs a separate bounds-checked investigation. No such values '
             'are included or certified here.', '',
             '## Known pseudoinverses and minimum-norm solutions', '',
             'The D9c driver uses `forinv:inv(method="gesvd",tol=1e-10)` for five cases. '
             'For the rank-one matrix `u*v^T`, `u=[1,2,3]`, `v=[1,2]`, '
             'the explicit pseudoinverse is `v*u^T/70`. Its application to `b=u` '
             'must produce the minimum-norm solution `[1/5,2/5]`. '
             'A full-rank tall matrix with orthogonal columns `[1,2,2]` and `[2,-1,0]` '
             'has pseudoinverse rows equal to those columns divided by 9 and 5 respectively. '
             'The wide transpose must have the transposed pseudoinverse. '
             'The remaining cases are `diag(2,0,4)`, with inverse `diag(1/2,0,1/4)`, '
             'and a zero 3-by-2 matrix, with a zero 2-by-3 pseudoinverse.', '',
             'Each case checks the explicit reference and all four Moore-Penrose conditions: '
             '`A*Aplus*A=A`, `Aplus*A*Aplus=Aplus`, symmetry of `A*Aplus`, and symmetry of '
             '`Aplus*A`. Maximum-entry errors are divided by `max(1,max(abs(reference)))` '
             'for the corresponding matrix and bounded by `1e-11`; all results/errors must be finite. '
             'The minimum-norm coefficient error is bounded by `1e-11`. '
             'Original matrices are preserved because the pinned ForSVD dependency can overwrite '
             'the SVD input despite its declared input intent. The cutoff is absolute in this API. '
             'This does not test default cutoff behavior, alternative methods, ill-conditioning, '
             'near-threshold numerical ranks or general rank selection.', '',
             '## Shared Dirichlet spectral problem', '',
             'ARPACK and linalg_fortran use the same 20-by-20 real symmetric tridiagonal '
             'matrix with diagonal 2 and off-diagonals -1. Its exact eigenvalues are '
             '`lambda_j=4*sin(j*pi/(2*(n+1)))^2` and normalized eigenvectors '
             '`v_i=sqrt(2/(n+1))*sin(i*j*pi/(n+1))`. '
             'The reviewed procedure mappings are refined from broad D4 to D4a1 '
             'for these real symmetric ordinary-problem APIs; no generalized or nonsymmetric '
             'eigenproblem claim is made.', '',
             'The ARPACK driver requests the three smallest and three largest eigenpairs '
             'in separate standard-mode runs (`SM`/`LM`, `BMAT=I`, `IPARAM(7)=1`). '
             'It supplies a reproducible nonzero initial residual, caps Arnoldi iterations '
             'at 1000 and operator calls at 10000, and requires successful convergence and '
             'extraction with all three requested pairs converged. Eigenvalue errors and '
             'Euclidean eigen-equation residuals must be at most `1e-9`; orthonormality '
             'error at most `1e-10`. Every vector must match its analytic sine direction '
             'up to sign, with `abs(abs(dot_product(computed,exact))-1)<=1e-8`.', '',
             'The dense linalg_fortran driver checks all 20 eigenpairs, with eigenvalue, '
             'equation-residual, orthonormality and maximum-entry reconstruction errors '
             'at most `1e-11`. It uses the same sign-independent sine-vector check and '
             'prints the six pairs corresponding to the ARPACK selections. Both drivers '
             'require finite eigenvalues/vectors. The dense API has no returned status '
             'in this invocation; answer checks determine acceptance. The shared mathematical '
             'problem supports comparisons of selected results, not a general speed ranking. '
             'Shift-invert, generalized, nonsymmetric and arbitrary-spectrum problems are not verified.', '',
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
             'The separate [PROPACK and FMM2D review](gams-propack-fmm.md) covers leading singular '
             'triplets with prescribed spectra and real Laplace kernel-matrix applications. '
             'The latter is not a checked complete PDE solver.', '',
             'The [GMRES and inverse review](gams-gmres-inverse.md) covers normal/transpose '
             'LightKrylov solves with known solutions and one-process NTPoly SPD inverses with '
             'analytic references and two-sided identity residuals.', '',
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
              'verification reports record source hashes, pins and saved output: '+', '.join(
                  f'[{Path(path).name}]({Path(path).name})'
                  for path in sorted({driver_validation_path(d) for d in drivers}))+'. '
              'These small examples establish checked usage, rather than comprehensive '
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
             'The DOP853, rklib and DDEABM consumers share the analytic three-state problem below. '
             'Other consumers in the recorded results use separately documented fixtures. '
             'Each proof concerns the named configuration, rather than every method offered by '
             'each package or performance on stiff equations. The '
             '[FLINT review](gams-adaptive-ad.md) covers four adaptive methods, three analytic systems, '
             'forward/backward intervals and repeated dense output. The '
             '[DASKR review](gams-dae-fft.md) covers index-one DAEs, supplied consistent initial data, '
             'dense direct solves and numerical/user Jacobians.', '',
             '| Class | Configuration | Procedure |', '| --- | --- | --- |',
             '| [I1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1a) | One-step methods for general nonstiff or mildly stiff IVPs | DOP853 `dop853_class%integrate`; rklib `rk4_class%integrate` |',
             '| [I1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1b) | Multistep methods for general nonstiff or mildly stiff IVPs | DDEABM `ddeabm_class%integrate` |',
             '| [I1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a2) | Stiff/DAE IVPs; checked dense-direct index-one configuration | DASKR `ddaskr` |', '',
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
             'The separate [interp1 exactness review](gams-least-interpolation.md), '
             '[REGRIDPACK review](gams-regrid-rk45.md) and '
             '[FITPACK polynomial review](gams-fitpack-polynomials.md) document their own fixtures. '
             'Their entries below do not inherit the shape-preservation checks.', '',
             '## Shared data and checks', '',
             'The three shape-comparison drivers use the nonuniform grid `x=[0,0.25,0.5,1,2,3]`. Case 1 tabulates the affine '
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
        author = f'[Author example/test]({base}{d["author_example"]})' if d['author_example'] else 'Independent API consumer'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · '
                     f'{author} |')
    lines += ['', 'The three shape-comparison programs adapt author API patterns and retain the package license notices. '
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
             '| [J1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1) | One-/two-dimensional nonuniform type-1 Fourier transforms | NUFFT `nufft1d1f90`; NUFFT2D `nufft2d1f90` |',
             '| [J1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a1) | One-dimensional real-input forward Fourier transforms | spectrum `rfft` |',
             '| [J1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a2) | One-dimensional complex Fourier transforms | FFTPACK `fft, ifft`; KISS FFT `fft%perform`; NAFPack `execute_fft_plan_sp` |',
             '| [J1a3](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a3) | One-dimensional sine and cosine transforms | FFTPACK `dct(type=2), idct(type=2)` |', '',
             'The real, complex and cosine transforms use the deepest recorded categories '
             'for those configurations. The nonuniform examples retain broader J1. '
             'They do not exhaust integral transforms: additional multidimensional configurations, '
             'transform types, convolution, Laplace and Hilbert transforms are separate opportunities.', '',
             'The [NAFPack plan review](gams-dae-fft.md) checks single-precision radix-two DIT/DIF '
             'plans with iterative/recursive implementations against direct complex sums.', '',
             '## Nonuniform Fourier sums', '',
             'The NUFFT driver checks 24 type-1 transforms of 80 nonuniform sources '
             'into 15, 16, 31 and 32 modes, with three deterministic strength patterns '
             'and both exponent signs. Every coefficient is checked against scalar '
             'trigonometric sums with the documented `1/nj` normalization. '
             'See the [spatial and nonuniform-transform review](gams-spatial-nufft.md) '
             'for tolerances, the zero-mode check and the retained package build patches.', '',
             'The two-dimensional NUFFT2D driver checks 144 transforms and all 22,416 coefficients against '
             'direct sums, with both signs, two tolerances and even/odd grids. See the '
             '[quadrature-moment and 2D-transform review](gams-moments-nufft2d.md) for its input patterns, '
             'normalization, acceptance checks and limits.', '',
             '## Real-input FFT checks', '',
             'The spectrum driver checks 42 forward transforms against scalar trigonometric '
             'sums and Parseval energy, including ten odd/even lengths, four deterministic '
             'signals per length and explicit zero padding/truncation. Its scaled '
             'tolerance is `1e-11`. Inverse transforms are not verified by this driver; '
             'see the [reference details and length-convention limitation](gams-fourier-geometry.md).', '',
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
    lines += ['', 'The programs record API provenance and license notices; the independently written '
              'spectrum and NUFFT drivers have their own MIT notices. They appear '
              'in hosted and main local FPM example menus and downloaded projects. Loading a link '
              'selects source without submitting a job.', '', '## Recorded results', '',
              f'All {len(drivers)} passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              'verification reports record hashes, source pins and saved output: '+', '.join(
                  f'[{Path(path).name}]({Path(path).name})'
                  for path in sorted({driver_validation_path(d) for d in drivers}))+'.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
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
             '| [G2h3b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h3b1b) | Smooth nonlinear equality/inequality optimization with user objective and constraint first derivatives | SLSQP `slsqp_solver%optimize`, analytic mode |',
             '| [G2a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2a) | Free-variable inequality-constrained linear programming | CONMAX `slnpro` |',
             '| [G2h1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h1a1) | Simple bounds, no derivatives supplied | PowellOpt `bobyqa` |',
             '| [G2i](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2i) | Bounded global search for a nonconvex problem | PIKAIA `pikaia_class%solve` |', '',
             'Each driver demonstrates its recorded configuration. Other constrained '
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
             '## Linear programming with an optimality certificate', '',
             'Three CONMAX problems maximize `-y` subject to `x+y>=a`, `x-y<=b`, with '
             '`(a,b)=[(2,4),(5,1),(-3,7)]`. Variables are free, so negative solution '
             'components are permitted. The exact solutions are `[(3,-1),(3,2),(2,-5)]`. '
             'The inequality rows are multiplied by positive scale pairs '
             '`[(1,1),(0.5,3),(4,0.25)]` without changing their feasible sets.', '',
             'For inequality matrix A, right side d and scales s1,s2, the nonnegative dual '
             'weights `lambda=[1/(2*s1),1/(2*s2)]` satisfy `transpose(A)*lambda=[0,-1]`. '
             'Their bound `dot_product(lambda,d)=(b-a)/2` is an independent upper bound on '
             'the maximized objective. The driver requires status 0, finite parameters/reported '
             'objective, solution error and feasibility violation at most `1e-9`, reported '
             'objective agreement and primal-dual gap at most `1e-9`. Original '
             'constraints are preserved because the solver overwrites its tableau. '
             'Infeasible/unbounded problems and general LP robustness are not tested.', '',
             '## Derivative-free box quadratic', '',
             'BOBYQA solves the same quadratic and box used by the derivative-based drivers, '
             'from `[0.25,1]`, `[0.9,0.1]` and `[0.1,1.8]`. No gradient is supplied to the '
             'optimizer. Five interpolation points, initial/final radii `0.1`/`1e-9`, '
             'and a maximum of 1000 objective calls are used. Every callback checks finite '
             'parameters and bound feasibility. After solving, the driver independently '
             'checks solution `[1,0]`, objective 2 and the projected-gradient residual, '
             'all within `1e-8`.', '',
             'The pinned BOBYQA API has no returned status flag. A normal return is '
             'insufficient: explicit answer checks must pass and the evaluation budget '
             'must not be exhausted. The reference gradient is used only after the solve. '
             'These convex cases do not verify arbitrary nonconvex objectives.', '',
             '## Seeded multimodal global search', '',
             'PIKAIA minimizes the two-dimensional Rastrigin objective '
             '`R(x)=sum(x_i^2+10*(1-cos(2*pi*x_i)))` on `[-2,2]^2` by maximizing '
             '`fitness=1/(1+R)`. Every term in R is nonnegative; the exact global '
             'minimum is zero at `[0,0]`, giving fitness 1. Three runs use '
             'seeds `[12345,6789,24680]`, population 100, 600 generations and seven '
             'decimal encoding digits. The convergence window is 601, longer than '
             'the generation budget, so a short plateau does not stop the test early.', '',
             'Initialization/solve status must be zero, callback/final points finite and '
             'within bounds, maximum parameter error at most `0.01`, objective at most '
             '`0.01` and reported fitness within `1e-10` of an independently recomputed '
             'value. Callback counts are printed. Fixed-seed finite-budget success '
             'does not guarantee global convergence or certify arbitrary nonconvex '
             'problems. No general global-optimality claim follows from solver status.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        author = f'[Author example]({base}{d["author_example"]})' if d['author_example'] else 'Original public-API driver'
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}) · {author} · '
                     f'[Verification]({Path(driver_validation_path(d)).name}) |')
    lines += ['', 'The L-BFGS-B and SLSQP drivers adapt author API patterns and retain license notices. '
              f'All {len(drivers)} appear in hosted and main local FPM example menus and downloaded projects. '
              'Loading a link selects source without submitting a job.', '', '## Recorded results', '',
              f'All {len(drivers)} passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
              'existing package libraries. Only each main and executable were rebuilt. The '
              'per-driver reports linked above record hashes, pins and saved output; the '
              '[original report](gams-constrained-validation.json) covers its six initial drivers. '
              'Evaluation counts exclude derivative sanity checks and describe these simple cases, rather '
              'than establishing a general speed ranking.', '']
    for d in drivers:
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        if d['id'] == 'opti-rastrigin-reference':
            lines += ['The [dedicated review](gams-gradient-swarm.md) explains the seeded tests; '
                      'the complete progress output remains in its verification report.', '']
            output = output[output.index('Swarm verification summary:'):]
        output = '\n'.join(line.rstrip() for line in output.splitlines())
        lines += ['### '+d['id'], '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers lbfgsb-box-quadratic nlopt-box-quadratic slsqp-circle-equality',
              'python xverify_gams_drivers.py --drivers conmax-linear-program-certificate bobyqa-box-reference pikaia-rastrigin-reference',
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
             '| [C10b1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10b1) | Modified Bessel I/K, real arguments and integer orders; tested orders 0 and 1 | fortran-bessels `besseli0`, `besseli1`, `besselk0`, `besselk1` |',
             '| [C10](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10) | Complex J/I sequences and half-order K | AMOS `f90_zbesj`, `f90_zbesi`, `f90_zbesk` |',
             '| [C14](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C14) | Carlson RF and complete elliptic K | `carlson_elliptic_module:drf` |',
             '| [C19](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C19) | Bernoulli numbers and integer power sums | `specfun_module:bernob` |', '',
             'These demonstrate selected arguments and named procedures. They do not exhaust '
             'their GAMS classes or cover all orders, branch cuts, poles or extreme-argument regimes. '
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
             'the backend do not depend on it.', '',
             '## Carlson elliptic-integral references', '',
             'The C14 driver checks three diagonal identities `RF(x,x,x)=1/sqrt(x)` at '
             '`x=[0.25,1,4]`, three positive triples `(0.25,1,4)`, `(1,2,4)`, `(2,3,5)`, '
             'and complete elliptic integrals `K(k)=RF(0,1-k^2,1)` at '
             '`k=[0,0.25,0.75,0.95]`. For positive triples, substitution `u=t^(-2)-1` '
             'in the [defining RF integral](https://dlmf.nist.gov/19.16.E1) gives a smooth integral '
             'from 0 to 1 with integrand `product(1+(x_i-1)*t^2)^(-1/2)`. '
             'Independent composite Simpson sums at 2048 and 4096 panels must agree; '
             'the fine sum is the reference. K references use 4096 panels in '
             '`integral_0^(pi/2) (1-k^2*sin(theta)^2)^(-1/2) dtheta`.', '',
             'Three cyclic-permutation and three scale checks supply secondary identities: '
             '`RF(y,z,x)=RF(x,y,z)` and `RF(4*x,4*y,4*z)=RF(x,y,z)/2`. '
             'All checked results/references must be finite, all RF statuses zero, and scaled error '
             '`abs(actual-reference)/max(1,abs(reference))` at most `2e-11`. '
             'This does not validate singular moduli, extreme scaling or other Carlson functions.', '',
             '## Bernoulli references and power sums', '',
             'The C19 driver checks `B0=1`, `B1=-1/2` and even `B2..B12` against '
             '`[1/6,-1/30,1/42,-1/30,5/66,-691/2730]`. '
             'It then evaluates the Bernoulli formula for `sum(m^p,m=0..n-1)` '
             'at powers 1..8 and `n=[3,10,20]`, comparing 24 results against direct int64 summation. '
             'The small integer powers, binomial coefficients and sums fit in int64. '
             'Finite scaled errors must be at most `3e-12`.', '',
             '**Pinned API limitation:** `bernob` leaves odd output positions above B1 unassigned. '
             'The driver never reads them: it supplies their known mathematical zeros locally '
             'for the power-sum application. This verifies returned even values and B0/B1, '
             'not a fully initialized Bernoulli output array. The implementation also writes '
             'B0..B2 unconditionally, so calls with `n<2` are outside the driver. '
             'These source-level restrictions are recorded in the procedure notes.', '',
             '## Complex AMOS Bessel references and pinned failure', '',
             'The C10 driver checks 39 complex values at `z=[0.5+0.25i,1+0.5i,2+0.75i]`. '
             'For starting orders `[0.3,0.5,1.25]`, it requests two successive J and I values '
             'and compares with independent [J](https://dlmf.nist.gov/10.2.E2) and '
             '[I](https://dlmf.nist.gov/10.25.E2) power series using intrinsic Gamma. '
             'A 100-term cap and explicit convergence requirement protect the references. '
             'K at order 1/2 is checked against '
             '[sqrt(pi/(2*z))*exp(-z)](https://dlmf.nist.gov/10.39.E2). '
             'Every status and underflow count must be zero; both components must be finite '
             'and complex scaled error at most `2e-12`. Only unscaled mode `KODE=1` is tested.', '',
             '**Pinned failure:** `J_0.3(2-0.75i)` returns approximately '
             '`-0.0312577+0.6118974i` instead of `0.4766625+0.3849523i`, a scaled discrepancy '
             'about 0.556. The independent series agrees with mpmath 1.3.0 at 80 decimal digits. '
             'The [failing source](gams-candidates/amosf90/lower-half-plane-series.f90) and '
             '[saved sandbox result with the high-precision reference](gams-candidates/amosf90/lower-half-plane-result.json) '
             'are retained for reporting upstream. The checked driver uses upper-right-quadrant arguments '
             'and explicitly excludes this known failing case; no package patch or tolerance relaxation '
             'is applied. This establishes selected checked usage, not full-domain AMOS correctness.', '',
             '## Sources and playground links', '',
             '| Driver | Class | Pinned procedure and author example |', '| --- | --- | --- |']
    for d in drivers:
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        evidence = records[d['procedure_id']]['evidence'][0]
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        author = f' · [Author example/test]({base}{d["author_example"]})' if d.get('author_example') else ''
        lines.append(f'| [Load {d["id"]}]({url}) · [Source](../{d["path"]}) | {d["gams_code"]} | '
                     f'[Procedure]({base}{evidence["path"]}#L{evidence["line"]}){author} |')
    lines += ['', 'The programs use author APIs, retain applicable license notices and use deterministic '
              'reference checks instead of the larger author harnesses. They appear in hosted and main '
              'local FPM example menus and downloaded projects. Loading a link selects source without '
              'submitting a job.', '', '## Recorded results', '',
              f'All {len(drivers)} passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
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
              'python xverify_gams_drivers.py --drivers carlson-rf-reference bernoulli-power-sums amos-complex-series',
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
             'The separate [forwarddiff review](gams-adaptive-ad.md) checks 1,749 scalar calls '
             'against analytic values and slopes on monomials and twelve smooth composite functions.', '',
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


def sorting_review_text(root=ROOT):
    root = Path(root)
    driver = next(d for d in driver_data(root) if d['id']=='stdlib-sorting-reference')
    report = json.loads((root/driver_validation_path(driver)).read_text(encoding='utf-8'))
    result = next(r for r in report['drivers'] if r['driver_id']==driver['id'])
    output = next(s['stdout'] for s in result['stages'] if s['name']=='Run')
    return '\n'.join(['# Class-specific playground links and checked stdlib sorting', '',
        'On a GAMS class page, **Try in playground** opens a checked driver matching '
        'that class when one is available. An exact-class driver is preferred; a '
        'driver in a descendant class is used otherwise. Class membership follows '
        'the explicit GAMS hierarchy. Package/owner pages retain their general '
        'package links. If no matching driver exists, a class card labels the '
        'fallback **Open default example**, rather than implying that the default '
        'program demonstrates the current class.', '',
        'The stdlib link on [N6: Sorting](https://beliavsky.github.io/fortran-playground/gams/N6/) '
        'now opens the [checked sorting example](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-sorting-reference). '
        'Loading the link selects code without submitting a job.', '',
        '## Checked sorting operations', '',
        'The driver uses `stdlib_sorting:sort` on int32 and real64 arrays. It '
        'checks exact ascending and descending answers for small arrays with '
        'negative and repeated values, integer-sort idempotence, and empty/singleton '
        'arrays. A separate 64-element integer case uses values '
        '`modulo(37*i,17)-8`; its sorted reference is constructed from counts '
        'in the known range -8 through 8, independently of another sorting routine.', '',
        'The real values are finite, exactly representable binary fractions. '
        'NaN ordering, signed-zero distinctions, stability and all other sorting '
        'interfaces are outside this driver. Author API patterns are adapted with '
        'the stdlib MIT notice retained.', '',
        f'[Driver source](../{driver["path"]}) / '
        f'[Pinned author test](https://github.com/fortran-lang/stdlib/blob/{driver["revision"]}/{driver["author_example"]}) / '
        '[Verification report](gams-sorting-validation.json)', '',
        'The driver passed in the restricted GNU Fortran 16.2.0 sandbox with '
        'FPM 0.12.0, reusing the existing stdlib library. Only the main and executable '
        'were compiled. The example appears in both hosted and main local FPM menus.', '',
        '```text', output.rstrip(), '```', '', '## Maintenance', '', '```text',
        'python xverify_gams_drivers.py --drivers stdlib-sorting-reference',
        'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
        'Publishing the updated Pages build is sufficient; no backend redeployment '
        'or package library rebuild is required.', ''])


def number_theory_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-number-theory-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS number-theory drivers', '',
             'Both currently selected packages in [B: Number theory](https://beliavsky.github.io/fortran-playground/gams/B/) '
             'now have class-specific checked drivers. Their primary class-page links load these drivers, '
             'rather than the package defaults. B has no finer classes in the recorded GAMS taxonomy; '
             'this does not exhaust the packages, their input domains or number theory.', '',
             '## Prime enumeration and primality', '',
             '`fortran-primes` uses `prime_numbers:primes` and `is_prime`. '
             'The driver checks 1021 int32 operands from -20 through 1000 against an independent trial-division function. '
             'It compares the complete ordered list through 1000 against independently generated primes and '
             'also checks the known count 168 and sum 76127. It checks the bounded range [100,200], '
             'an upper bound below two, and a reversed range.', '',
             'Eight int64 cases include negative/zero/unit operands, 2, 2147483647, '
             '10000000019, 10000000020 and 10000000021. Each is independently checked by trial division. '
             'The reference tests every divisor through the square root, using `d <= n/d` to avoid squaring overflow. '
             'The example adapts the author test API patterns; it does not compare with the package\'s own tables '
             'or another API from the same implementation.', '',
             'These checks do not establish correctness over the full int32/int64 domains. '
             'Factorization, next-prime queries and large enumeration workloads are outside this driver. '
             'The upstream MIT license and the pinned source\'s additional Primes.jl/CC BY-NC notices are retained.', '',
             '**Pinned API limitation:** an initial driver timed out after reaching the int64 case '
             '`3215031751` (the composite `151*751*28351`). '
             'The [failing source](gams-candidates/fortran-primes/large-int64-primality.f90), '
             '[sandbox result](gams-candidates/fortran-primes/large-int64-primality-result.json), '
             '[minimal reproducer](gams-candidates/fortran-primes/signed-int32-boundary.f90) and '
             '[isolated result](gams-candidates/fortran-primes/signed-int32-boundary-result.json) are retained. '
             'Source inspection shows that the `n<2**32` branch narrows `n` to signed int32; '
             'the modular-exponentiation loop then arithmetically shifts a negative exponent. '
             'The checked driver excludes this known failing case and explicitly notes the limitation. '
             'The B mapping remains justified by the demonstrated number-theory operations, '
             'without a claim of full-domain primality correctness.', '',
             '## Greatest common divisors and least common multiples', '',
             '`rpn-calculator-fortran` exposes `rat:gcd` and `lcm` independently of its interactive calculator. '
             'The driver checks every ordered pair of nonnegative operands from 0 through 64: '
             '4225 GCD calls and 4224 LCM calls. Its GCD reference enumerates common divisors; '
             'its LCM reference searches successive multiples of the larger operand. '
             'Neither reference calls a package routine or uses the package\'s Euclidean-GCD/LCM formula. '
             'Results are exact integer comparisons.', '',
             '**Pinned API limitation:** `lcm(0,0)` evaluates `0/gcd(0,0)` and therefore divides by zero. '
             'The driver excludes that call and states the restriction in its output. '
             'The implementation returns `gcd(0,0)=0`, which is checked as an API convention. '
             'LCM with exactly one zero operand is checked in both orders. Negative-operand sign conventions, '
             'overflow and the calculator\'s other numerical functions are outside this driver. '
             'The upstream MIT notice is retained.', '',
             '## Sources, links and recorded results', '',
             'Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
             'the existing package libraries. Only the mains and executables were compiled. '
             'The [verification report](gams-number-theory-validation.json) records source hashes and output. '
             'Loading the links selects code without submitting a job; the examples appear in hosted '
             'and main local FPM menus.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        if d.get('author_example'):
            lines += [f'[Pinned author test]({base}{d["author_example"]})', '']
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers primes-trial-division rpn-gcd-lcm-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'Other GAMS sections still have source-supported and uncertain mappings; '
              'see the [coverage report](gams-coverage.md) and [mapping evidence queue](gams-mapping-evidence.md).', '']
    return '\n'.join(lines)


def arithmetic_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-arithmetic-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS arithmetic, representation and bit-operation drivers', '',
             'These drivers cover specific configurations in A1 (Integer), A2 (Rational) and '
             'A6 (Change of representation), plus A3c/A4c arbitrary-precision real/complex arithmetic '
             'and N2 bit manipulation. The class-page links load the matching programs; '
             'the broader A page identifies the narrower demonstration. '
             'Arithmetic and the other GAMS sections are not exhausted.', '',
             '## Exact rational addition: A2', '',
             '`rational_number:ratNumAdd` is called for all operand pairs with numerators -4..4 '
             'and denominators 1..6, with simplification both disabled and enabled: 5832 calls. '
             'Each result has a positive denominator and is compared by exact int64 cross-products '
             'against `(p*s+r*q)/(q*s)`. All selected values and intermediate products fit comfortably '
             'within their integer kinds. Positive sums with simplification enabled must also equal '
             'the canonical numerator/denominator obtained by independently enumerating divisors.', '',
             '**Pinned representation limitation:** the `math:gcDenom` dependency returns zero '
             'when either operand is nonpositive. Thus negative or zero numerators can remain '
             'unreduced even when `simplify=.true.`. For example, `-1/3 + -1/6` is returned '
             'as `-9/18`, an exact representation of `-1/2`. The driver checks the value and '
             'does not claim canonical negative/zero representations. Zero denominators, '
             'integer overflow, real-to-rational conversion and other rational operations are outside this example.', '',
             '## Decimal-string integer arithmetic: A1', '',
             '`strith` signed addition and subtraction are compared with native integer arithmetic '
             'for every ordered operand pair in -20..20: 3362 operations. Five additional identities '
             'exercise decimal values beyond int64: adding one to thirty nines, borrowing across '
             'thirty zeroes, both subtraction orders for adjacent 20-digit integers, and cancellation '
             'of opposite 30-digit values. The expected decimal strings are explicit; no native integer '
             'is overflowed to construct a reference.', '',
             'The driver uses the pinned string constructor\'s explicit sign and fixed-width zero padding. '
             'This is fixed-capacity decimal arithmetic, not unlimited arbitrary precision. '
             'Capacity overflow, all comparison operators and the separate unsigned-formatting interface '
             'are not verified. This A1 driver does not mark the same procedure\'s A6 mapping verified.', '',
             '## Binary64 decimal round trips: A6', '',
             '`ryu:d2shortest` converts 132 finite IEEE binary64 bit patterns. Eleven exponent fields '
             '(0, 1, 2, 10, 511, 1022, 1023, 1024, 1535, 2045, 2046), six mantissas '
             '(0, 1, 2, 2^51-1, 2^51, 2^52-1), and both signs include signed zeros, '
             'subnormal/normal boundaries and the largest finite value. Intrinsic formatted input '
             'must recover the identical 64 bits; numerical equality alone would miss negative zero. '
             'The driver separately requires the author API\'s `0.0` and `-0.0` spellings.', '',
             'This verifies selected finite round trips with gfortran\'s reader, not all binary64 patterns, '
             'correctness of every reader, NaN/infinity spellings or mathematical shortest-length optimality. '
             'The new driver is independently written. Its MIT license covers the driver; '
             'the upstream package\'s unspecified licensing metadata remains unchanged.', '',
             '## Arbitrary-precision real addition: A3c', '',
             '`MPFUN2020-var1` is used with 120 requested decimal digits and explicit word precision '
             'on all constructors. Six additions are compared by exact multiprecision equality '
             'with explicit decimal integer or dyadic-fraction references. They include `10^80+1` '
             'in both operand orders, its negative counterpart, exact cancellation, '
             '`123456789012345678901234567890 + 987654321098765432109876543210 '
             '= 1111111110111111111011111111100`, and `0.125+0.375=0.5`. '
             'The long integer reference is supplied explicitly rather than computed through another package operation.', '',
             'The integer cases fit exactly within the requested precision. Ordinary binary64 arithmetic '
             'cannot retain the unit added to `10^80`. The example checks addition at one precision, '
             'not general accuracy, all exponent ranges, rounding behavior, other operations or performance. '
             'A small input helper appends `.0` to integer strings because the author\'s parser '
             'requires a decimal point. No binary64 conversion of the long decimal operands is used.', '',
             '## Arbitrary-precision complex addition: A4c', '',
             'Five MPFUN complex additions are checked by comparing both real and imaginary components '
             'exactly against explicit decimal references. The main cancellation problem is '
             '`(10^80,-10^80) + (-(10^80-1),10^80+2) = (1,2)`. '
             'Further cases reverse the signs, retain unit increments in both large components, '
             'add dyadic fractions and cancel to complex zero. The same 120-digit precision '
             'and decimal-point helper are used. These are independent mathematical identities '
             'and API consumers, not copied author quadrature programs. Multiplication, division, '
             'transcendental functions and all-input accuracy are outside the verification.', '',
             '## Binary-string bit manipulation: N2', '',
             '`bstrith` is checked against native integer references with 5120 exact string comparisons. '
             'For every 8-bit value 0..255, the driver checks left/right shifts by 1..7, complement, '
             'XOR with `10100101`, and modular increment/decrement. It also checks addition and '
             'subtraction for all 256 ordered pairs of 4-bit operands. References use intrinsic '
             '`ISHFT`, `IAND`, `IEOR` and bounded integer arithmetic modulo 16 or 256; '
             'subtraction is checked directly rather than just as the inverse of the package\'s addition.', '',
             'This demonstrates N2 with valid fixed-width strings. Out-of-range shifts, malformed inputs '
             'and wider strings are outside the driver. The same procedure\'s A1 mapping remains '
             'source-supported until it has a separately recorded matching driver.', '',
             '## Sources, links and recorded results', '',
             f'All {len(drivers)} passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
             'reusing the existing package libraries. Only the mains and executables were compiled. '
             'The [verification report](gams-arithmetic-validation.json) records source hashes and output. '
             'The drivers are independently written API consumers; author tests were inspected where available, '
             'and no upstream implementation or test code was copied. Their shared MIT notice applies '
             'to these new drivers, with upstream package terms recorded separately in the catalog. '
             'Loading the links selects code without submitting a job. The programs are available '
             'in hosted and main local FPM menus.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers rational-addition-reference strith-integer-reference ryu-binary64-roundtrip',
              'python xverify_gams_drivers.py --drivers mpfun-real-addition mpfun-complex-addition bstrith-bit-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'See the [coverage report](gams-coverage.md) and [mapping evidence queue](gams-mapping-evidence.md) '
              'for remaining work.', '']
    return '\n'.join(lines)


def applied_methods_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-applied-methods-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS fitting, time-series and iterated-integration drivers', '',
             '| Class | Problem | Package |', '| --- | --- | --- |',
             '| K1 | Least-squares approximation with a cubic-spline basis | splpak |',
             '| L10a2a | Time-series summary autocovariance and autocorrelation | fortsa |',
             '| H2b1a2 | Nonautomatic multidimensional/iterated integration | integrate_fortran |', '',
             'These class-specific links select checked drivers. They verify the configurations '
             'below, not every package capability. The GAMS categories are not exhausted.', '',
             '## Known least-squares spline fits', '',
             'The splpak driver fits 24 observations at 12 coordinates in [0,1], each coordinate '
             'occurring twice. Three datasets have known fitted functions: `2*x`, '
             '`1-3*x` with paired noise `+1/4,-1/4`, and the constant `-2.25` with '
             'nonuniform positive weights (equal within each pair). Ten spline nodes/coefficients '
             'and the author API\'s `xtrap=1` setting are used.', '',
             'For the noisy data, each equal-weight pair contributes '
             '`2*(fitted-true_line)^2 + 2*(1/4)^2` to the objective. Thus the known line is '
             'the least-squares fit and its training sum of squared errors is exactly '
             '`24*(1/4)^2=1.5`. This is a nonzero-residual check, not just interpolation of '
             'noiseless data. The other datasets have zero reference residual.', '',
             'Each fitted function and its first derivative are checked at 21 points, including '
             'both endpoints: 126 independent value/derivative comparisons. Maximum absolute '
             'value error must be at most `1e-8`; derivative error at most `1e-7`. '
             'Initialization/evaluation statuses must be zero, values finite, noisy SSE within '
             '`1e-8` of 1.5 and the noiseless training SSE at most `1e-14`. '
             'The driver destroys state between fits. General curved-function fitting, '
             'multidimensional fitting, extrapolation and ill-conditioned data are outside the example.', '',
             '## Autocovariance and autocorrelation references', '',
             'The fortsa driver uses the eight observations `[1,-1,2,-2,3,-3,4,-4]`, '
             'a shift by 10, a transformation `-2*base+3`, and a constant series 7. '
             'For every lag 0..7, scalar loops independently form '
             '`sum((x_i-mean)*(x_(i+lag)-mean))/N`. This is the biased normalization by N, '
             'not the lag-dependent denominator N-lag. Three base-series anchors are '
             '`gamma(0)=7.5`, `gamma(1)=-6.25`, `gamma(7)=-0.5`.', '',
             'The public `acvf`, `acvf_opt` direct method 0, and FFT method 1 each must agree '
             'with these independent sums: 12 covariance calls, each with eight outputs. '
             'For the three nonconstant datasets, `acvf2acf` is checked against '
             '`gamma(lag)/gamma(0)`: nine calls with eight outputs. All outputs must be finite '
             'and maximum absolute errors at most `1e-10`. Constant-series covariance is checked '
             'as zero; its undefined zero-variance correlation is deliberately not requested. '
             'Missing data, partial correlations, other estimators and ARIMA fitting are not verified.', '',
             '## Fixed-rule multidimensional polynomial moments', '',
             'The integrate_fortran driver supplies module callbacks to `gauss_leg_nd`. '
             'Its `js` entries are panel counts per dimension, not quadrature orders. '
             'Every panel uses the implementation\'s fixed six-point Gauss-Legendre rule; '
             'the caller chooses the panels and no adaptive error estimate is promised.', '',
             'Fifty checks integrate `x^p*y^q`, p,q=0..4, over `[-1,2]` times `[0,3]` '
             'using one and two panels per dimension. References are products of exact '
             'monomial antiderivatives. Sixteen more checks use p,q=0..3 over '
             '`0<=x<=1`, `0<=y<=1+x^2`, with the independent reference '
             '`sum(binomial(q+1,r)/((q+1)*(p+2*r+1)),r=0..q+1)`. '
             'This polynomial has x degree at most 11 after integrating y. '
             'A final 3D box check integrates `x^2*y^3*z` over '
             '`[-1,1]` times `[0,2]` times `[1,3]`, with exact value `32/3`.', '',
             'All 67 results must be finite with scaled error '
             '`abs(actual-reference)/max(1,abs(reference))<=1e-11`. '
             'The bounds callback reads x only for the second variable in the iterated case, '
             'after the first variable is defined. Singular, infinite-domain and highly '
             'oscillatory integrands, invalid panel counts and automatic accuracy selection '
             'are outside this verification.', '',
             '## Sources, playground links and saved output', '',
             'All three passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
             'reusing the existing package libraries. Only the mains and executables were compiled. '
             'The [verification report](gams-applied-methods-validation.json) records source hashes '
             'and actual output. The independently written drivers have their own MIT notice; '
             'upstream package licenses remain separate. Loading a link selects source without '
             'submitting a job; the examples appear in hosted and main local FPM menus.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        if d.get('author_example'):
            lines += [f'[Pinned author test]({base}{d["author_example"]})', '']
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers splpak-paired-noise-fit fortsa-autocorrelation-reference integrate-nd-polynomial-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining classes without checked drivers.', '']
    return '\n'.join(lines)


def boundary_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-boundary-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    twopnt = records['twopnt-solve']
    twopnt_source = f'https://github.com/{packages["twopnt"]["repository"]}/blob/{twopnt["revision"]}/src/twopnt_core.f90'
    lines = ['# Checked GAMS boundary-value spectral problem and retained failed probe', '',
             'The checked featom driver demonstrates a radial nonrelativistic boundary-value '
             'eigenproblem in I1b. A separate TWOPNT manufactured-problem probe failed its '
             'independent checks and is retained without a verified-driver designation. '
             'Boundary-value methods and GAMS categories are not exhausted.', '',
             '## Coulomb bound-state energies: featom', '',
             'The driver calls `total_energy` in its nonrelativistic point-Coulomb branch '
             'for nuclear charges Z=1 and Z=2. For principal quantum numbers n=1..3 '
             'and angular indices l=0..n-1, the exact energies are '
             '`E_n=-Z^2/(2*n^2)` Hartree. Twelve returned energies are compared with '
             'this independent formula, including the angular degeneracy within each n. '
             'Maximum absolute error must be at most `1e-7` Hartree.', '',
             'Both solves use eight radial elements, polynomial degree 20, 43 quadrature '
             'points per element, radial endpoint 100 and mesh grading parameter 100. '
             'Returned dimensions must support the first six levels, degrees of freedom '
             'must be positive, and the checked energies and first six wavefunctions '
             'must be finite. Finiteness alone does not verify wavefunction shape or '
             'normalization. Dirac/relativistic and self-consistent DFT branches, higher '
             'levels, mesh convergence and full-spectrum accuracy are not verified.', '',
             'The driver passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
             'reusing the existing package library. Only its main and executable were '
             'compiled. The [verification report](gams-boundary-validation.json) records '
             'source hashes and actual output. Its independent API-consumer source has '
             'its own MIT notice; upstream package terms remain separate.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        checks = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in checks['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## TWOPNT probe that was not accepted', '',
              'The manufactured problem is `u_second_derivative=-2` on [0,1], '
              '`u(0)=u(1)=0`, with exact profile `u=x*(1-x)`. The probe implements '
              'a derived `TwoPntBVProblem`, conservative three-point spatial residuals, '
              'the solver\'s finite-difference Jacobian and a zero initial guess. '
              'It intended to check fixed uniform grids of 9, 17 and 33 points, '
              'full-profile errors, endpoint conditions and a separately evaluated '
              'discrete equation residual.', '',
              'On the first nine-point grid, the pinned solver prints `SUCCESS` and '
              'returns a false error flag but leaves the zero initial guess unchanged. '
              'The profile error is 0.25 and residual error is 2, so the independent '
              'driver rejects the result. The later grids are not reached. '
              'This is an observed failure, not a successful boundary-value demonstration.', '',
              f'Inspection of the [pinned search routine]({twopnt_source}) shows a convergence '
              'exit for the trial iterate `v1` before the subsequent `v0=v1` assignment. '
              'The return therefore exposes the preceding iterate; for this linear '
              'problem the first Newton trial solves the equations, but the returned '
              'initial iterate does not. This source-based explanation is an inference '
              'supported by the retained run, not an upstream-confirmed diagnosis.', '',
              '[Failing source](gams-candidates/twopnt/poisson-returned-iterate.f90) / '
              '[Saved sandbox result](gams-candidates/twopnt/poisson-returned-iterate-result.json)', '',
              'The failed probe is absent from the checked-driver manifest and example menus. '
              'Its source-supported I1b mapping remains, with the limitation in its procedure '
              'notes. No library patch, cached-package rebuild or tolerance relaxation was applied. '
              'A corrected upstream implementation or a separately reviewed patch is needed '
              'before promoting this probe to a verified driver.', '',
              '## Related spectral checks', '',
              'The [linear-algebra review](gams-linear-algebra.md) gives matching ARPACK '
              'and linalg_fortran D4a1 drivers for the same 20-by-20 Dirichlet matrix, '
              'with analytic eigenvalues and eigenvectors. Those ordinary matrix '
              'eigenproblems are separate from featom\'s radial boundary-value formulation.', '',
              '## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers featom-coulomb-spectrum',
              'python xverify_gams_drivers.py --drivers arpack-poisson-eigenpairs linalg-poisson-eigenpairs',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'Publishing these checked examples requires no backend redeployment or package library rebuild.', '']
    return '\n'.join(lines)


def resampling_markov_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-resampling-markov-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS resampling and Markov-model drivers', '',
             'These L4 and M drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing the existing package libraries. Only their main '
             'programs and executables were compiled. GAMS categories are not exhausted.', '',
             '## Jackknife uncertainty: FJsample (L4)', '',
             'The driver checks five real datasets of sizes 2, 6, 4, 6 and 8, including '
             'constant values, negative values and a symmetric zero-mean sample. '
             'Each full-sample mean and leave-one-out mean returned by `Complement` '
             'is compared with separately enumerated scalar sums. For the sample mean, '
             '`jackError` must return `sqrt(s^2/n)`, where `s^2` is the unbiased '
             'sample variance, and zero bias.', '',
             'A second estimator squares the full and resampled means. Its uncertainty '
             'is checked against the direct leave-one-out jackknife sum, and its '
             'returned bias against the analytic identity `-s^2/(n*(n-1))`. '
             'All values must be finite; maximum absolute errors must be at most `1e-11`. '
             'This nonlinear check makes the bias convention observable: the package '
             'returns **full estimate minus mean resampled estimate**, without an '
             '`n-1` multiplier. Conventional estimated jackknife bias would be '
             '`-(n-1)*package_bias`; a conventionally bias-corrected estimate would be '
             '`full_estimate+(n-1)*package_bias`. The driver checks the documented '
             'package result rather than relabeling it as that conventional bias.', '',
             'The pinned author main was reviewed for the public calling sequence. '
             'Bootstrap, complex data, higher-order complements, general estimator '
             'accuracy and statistical coverage are not verified. L4 remains broad '
             'pending a suitable finer taxonomy match.', '',
             '## Stationary Markov models: econ-toolchain (M)', '',
             'Three two-state chains use transition pairs `(a,b)=(0.1,0.2)`, '
             '`(0.7,0.6)` and `(0.02,0.03)`. Their exact stationary probabilities '
             'are `[b,a]/(a+b)`. A three-state rank-one chain must recover '
             '`[0.1,0.3,0.6]`. The iteration must report convergence and return '
             'finite nonnegative probabilities, unit total probability and a '
             'stationary equation residual at most `1e-11`.', '',
             '`tauchen` discretizes three Gaussian AR(1) processes on 31 nodes '
             'spanning three stationary standard deviations. The tested '
             '`(mean,rho,innovation_sigma)` triples are `(0,0,0.2)`, '
             '`(1.5,0.8,0.1)` and `(-0.7,-0.5,0.3)`. Grid locations are checked '
             'against the specified mean and stationary variance. Each of 2883 '
             'transition probabilities is compared with an independent conditional '
             'normal CDF integral over midpoint cells, with infinite endpoint tails. '
             'The reference uses intrinsic `erf`; the package uses `erfc`. '
             'This checks the discretization formula, indexing and tails, rather '
             'than independently certifying the compiler\'s special functions.', '',
             'Rows must be nonnegative and sum to one. The driver explicitly '
             'transposes the row-stochastic Tauchen matrix for the column-stochastic '
             '`markov_steady_state` API, checks stationary residuals and the symmetric '
             'stationary mean, and compares the zero-correlation equilibrium with '
             'the independently computed identical row distribution. Every check '
             'uses an absolute tolerance of `1e-11`; the iteration tolerance is '
             '`1e-14` with a 10000-iteration limit. These deterministic tests do '
             'not verify random sampling, nonergodic chains, arbitrary-parameter '
             'convergence or the continuous process\'s full stationary distribution.', '',
             '## Pinned evidence and actual output', '',
             'The [verification report](gams-resampling-markov-validation.json) '
             'records source hashes and actual sandbox output. These independent '
             'API consumers have their own MIT notice; upstream package terms '
             'remain separate. Loading a link selects the checked driver without '
             'submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        for example in records[d['procedure_id']]['author_examples']:
            lines += [f'[Pinned author example/test]({base}{example["path"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers econ-markov-reference fjsample-jackknife-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining classes without checked drivers.', '']
    return '\n'.join(lines)


def fourier_geometry_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fourier-geometry-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS real Fourier and geodesic drivers', '',
             'These J1a1 and P examples passed the restricted GNU Fortran 16.2.0 '
             'sandbox with FPM 0.12.0, reusing the existing package libraries. '
             'Only their mains and executables were compiled. The '
             '[verification report](gams-fourier-geometry-validation.json) '
             'records source hashes, pinned revisions and actual output. '
             'GAMS categories are not exhausted.', '',
             '## Real-input Fourier transforms: spectrum (J1a1)', '',
             'The driver checks `rfft` on four deterministic signals at each length '
             '`3,4,5,6,7,8,11,12,15,16`: a shifted unit impulse, the constant 2, '
             'a mixed dyadic sequence, and `1+2*cos(theta)-0.5*sin(theta)`. '
             'Two further calls check explicit zero padding from five to eight '
             'samples and truncation from five to three, for 42 forward transforms.', '',
             'Every complex coefficient in the returned half spectrum is '
             'compared with independent scalar cosine/sine sums for the '
             'unnormalized forward DFT `sum_j x_j*exp(-2*pi*i*k*j/n)`. '
             'The maximum complex coefficient error divided by '
             '`max(1,sum(abs(x)))` must be at most `1e-11`. The half-spectrum '
             'length must equal `floor(n/2)+1`; real and imaginary parts must be '
             'finite. DC, and Nyquist for even n, must have imaginary part at '
             'most `1e-11`. Parseval energy weights the DC and even-n Nyquist '
             'coefficients once and the other positive-frequency coefficients '
             'twice; its scaled error must also be at most `1e-11`.', '',
             'The author FFT tests were reviewed for the public API and conventions. '
             'This independently written driver verifies forward transforms only. '
             'The pinned `irfft` implementation infers the full length from '
             'half-spectrum length parity, which cannot distinguish both original '
             'parities. Its optional length parameter adjusts the input '
             'half-spectrum rather than explicitly naming the original real '
             'length. Inverse reconstruction needs separate review and is '
             'not certified by this driver. Windows, STFT and performance are '
             'also outside this example.', '',
             '## Direct and inverse geodesics: geodesic-fortran (P)', '',
             'Six spherical routes cover northern and southern latitudes, '
             'a dateline crossing, high latitudes and an equatorial quarter '
             'circle. Independent haversine distances and analytic initial '
             'bearings supply references. Three WGS84 equatorial arcs use '
             'the exact reference `a*abs(delta_longitude)` in radians, including '
             'eastward wrapping and westward travel. Three WGS84 meridian paths '
             'span latitudes `[-40,20]`, `[30,70]` and `[80,85]` degrees. '
             'They use independent composite Simpson integration of the meridional '
             'radius of curvature `a*(1-e2)/(1-e2*sin(latitude)^2)^(3/2)`. '
             'Results with 2048 and 4096 panels must agree within `1e-7` metres; '
             'the finer integral supplies the distance reference. Refinement '
             'agreement is an empirical check, not a formal quadrature error bound.', '',
             'The sphere radius and WGS84 semimajor axis are 6378137 metres; '
             'ellipsoidal flattening is `1/298.257223563`. Across all 12 cases '
             'inverse distances must agree within `1e-6` metres and initial '
             'bearings within `1e-9` degrees. Direct calculations use independently '
             'computed distances and bearings, not inverse outputs; endpoints '
             'must agree within `1e-9` degrees. Longitude and bearing differences '
             'are compared modulo 360 degrees. Used outputs must be finite. '
             'General oblique ellipsoidal paths, exact antipodal/coincident '
             'degeneracies, reduced lengths, geodesic scales and areas are '
             'not verified. Only the requested distance, bearing and endpoint '
             'outputs are inspected.', '',
             '## Checked links and output', '',
             'The source files are independent API consumers with their own MIT '
             'notice; upstream package licenses remain separate. Loading these '
             'links selects checked source without submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})', '']
        for example in records[d['procedure_id']]['author_examples']:
            lines += [f'[Pinned author example/test]({base}{example["path"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers spectrum-real-dft-reference geodesic-reference',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'See also the [sparse conversion review](gams-linear-algebra.md#sparse-storage-conversion) '
              'and [remaining coverage](gams-coverage.md).', '']
    return '\n'.join(lines)


def sparse_integral_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-sparse-integral-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked sparse LU and stored-spline integration drivers', '',
             'These D2a4 and H2a2b2 drivers passed the restricted GNU Fortran 16.2.0 '
             'sandbox with FPM 0.12.0, reusing the existing precompiled libraries. '
             'Only their main programs and executables were compiled. The '
             '[verification report](gams-sparse-integral-validation.json) records '
             'source hashes, pins and actual output. GAMS categories are not exhausted.', '',
             '## Sparse LU and factor reuse: Y12M (D2a4)', '',
             'The base 10-by-10 matrix has `A(i,i)=4+i/4`, upper diagonal `-0.5`, '
             'lower diagonal `-1.25`, and corner entries `A(1,10)=-0.75`, '
             '`A(10,1)=0.25`. A second fixture cyclically permutes its rows as '
             '`B(i,:)=A(mod(i,10)+1,:)`, removing most diagonal entries. '
             'Both matrices are nonsymmetric and use independently packed coordinate triples.', '',
             '`y12mb` prepares storage, `y12mc` factors once and `y12md` solves '
             'four right-hand sides per matrix. Exact solutions are ones, '
             '`x_i=(-1)^i*i/4`, zero and the fourth unit vector. Scalar loops '
             'form `b=A*x` from a preserved original matrix. Subsequent solves '
             'set `iflag(5)=3` to reuse the factors. Every returned status must '
             'be zero and every solution finite.', '',
             'Scaled solution error `max(abs(x-x_exact))/max(1,max(abs(x_exact)))` '
             'must be at most `1e-11`. Independently evaluated backward error '
             '`||A*x-b||_inf/max(1,||A||_inf*||x||_inf+||b||_inf)` must be '
             'at most `1e-12`; the matrix norm is the maximum absolute row sum. '
             'Storage capacity is 1000 entries; pivot/storage flags are explicit '
             'in the source. Singular matrices, extreme conditioning, insufficient '
             'storage and error-code branches are not verified.', '',
             '## Stored spline integrals: fitpack (H2a2b2)', '',
             'Four zero-smoothing cubic interpolants represent `1`, `x`, `x^2` '
             'and `x^3` on irregular nodes `[-2,-1.7,-1,-0.25,0,0.4,1,1.6,2]`. '
             'Fit/evaluation statuses must succeed. Each polynomial is reproduced '
             'at 17 evenly spaced points, including off-knot locations, within '
             '`1e-11` absolute error, with finite outputs.', '',
             'For each polynomial, six integration intervals are checked: '
             '`[-2,2]`, `[-0.7,1.3]`, `[-2,-0.25]`, `[0.4,2]`, '
             '`[1.3,-0.7]` and `[0.2,0.2]`. Exact references use '
             '`x^(degree+1)/(degree+1)`. Three additional calls check '
             '`[-2,0.15]`, `[0.15,2]` and `[-2,2]`, with analytic references '
             'for the parts and an additivity check. All 36 integral calls '
             'must be finite and agree within `1e-11`, including reversed '
             'and zero-width intervals. Curves are destroyed after each case. '
             'This verifies integration of the represented spline, not adaptive '
             'callback quadrature, extrapolation or smoothing approximation accuracy.', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own MIT notice. '
             'Author examples/tests were reviewed for usage; upstream package '
             'licenses remain separate. Loading a link selects source without '
             'submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    pca = records['forpca-pca']
    base = f'https://github.com/{packages["forpca"]["repository"]}/blob/{pca["revision"]}/'
    lines += ['## Rejected forpca variance probe', '',
              'Five observations have means `[10,-4]` and orthogonal centered '
              'columns `[-4,-2,0,2,4]` and `[1,-2,2,-2,1]`. Their unbiased '
              'covariance is exactly `diag(10,3.5)`, so principal variances '
              'are `[10,3.5]` and explained percentages '
              '`[74.074074...,25.925926...]`.', '',
              'SVD mode returned `[100,12.25]` and percentages '
              '`[89.086860...,10.913140...]`. The independent eigenvalue check '
              'fails. The sandbox compiled the probe and reused the package '
              'library: this is a numerical output failure, not a service limit.', '',
              f'The [pinned source]({base}src/forpca.f90#L135) takes an '
              'SVD of the covariance matrix, then sets `latent=S**2/(ncol-1)`. '
              'Covariance singular values already equal its nonnegative '
              'eigenvalues; squaring them again explains this two-variable '
              'result. This is a source-based diagnosis, not an upstream-confirmed fix. '
              'The ordinary catalog demo checks a principal direction and '
              'an independently formed rank-one reconstruction, which do '
              'not certify latent variances or explained percentages.', '',
              '[Probe source](gams-candidates/forpca/covariance-variances.f90) / '
              '[Actual sandbox result](gams-candidates/forpca/covariance-variances-result.json)', '',
              'The failed probe is absent from the checked-driver manifest '
              'and menus. The L13b and D6 procedure mappings remain '
              'source-supported. Eigen mode, score/reconstruction outputs '
              'and any corrected upstream version need separate verification. '
              'No package patch or library rebuild was performed.', '',
              '## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers y12m-sparse-reference fitpack-spline-integral',
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'Publishing these drivers needs no backend redeployment or package library rebuild. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def spatial_nufft_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-spatial-nufft-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked spatial search, scattered interpolation and nonuniform Fourier drivers', '',
             'These N5, E2 and J1 drivers passed the restricted GNU Fortran 16.2.0 '
             'sandbox with FPM 0.12.0, reusing the existing precompiled packages. '
             'Only their mains and executables were compiled. The '
             '[verification report](gams-spatial-nufft-validation.json) records '
             'source hashes, package pins and actual output. GAMS categories '
             'are not exhausted.', '',
             '## Exhaustive neighbor references: kdtree2 (N5)', '',
             'The 48 three-dimensional points have coordinates '
             '`[mod(7*i,53),mod(11*i,59),mod(13*i,61)]/64`. Queries are '
             '`[13,29,41]/64`, the origin and point 17 itself. Both storage '
             'rearrangement modes are tested with sorted results. Each query '
             'requests its 1, 5 and all 48 nearest neighbors, and squared '
             'radii 0, 0.125 and 4: 36 search calls in total.', '',
             'Independent real64 scalar sums evaluate all squared distances '
             'from the actual input coordinates. An independent insertion '
             'sort supplies the nearest-distance references; tied indexes '
             'may appear in either order. Result indexes must be valid and '
             'unique, their distances finite and within `1e-6` of their '
             'references, and nearest distances must match the sorted prefix. '
             'Radius counts, every index, squared distance and the complete '
             'returned membership set are checked against exhaustive search. '
             'Zero radius checks exact self-membership; radius 4 includes '
             'all points in these fixtures.', '',
             'The archived single-precision setting is retained. These dyadic '
             'fixtures and real64 references make its precision explicit. '
             'The tree is destroyed after each storage mode. Global library '
             'search state is not thread-safe; concurrent searches, arbitrary '
             'dimensions, insufficient result capacity and large-data '
             'performance are not verified. This N5 driver does not '
             'separately verify the package\'s broader P mapping.', '',
             '## Three-dimensional scattered interpolation: DelaunaySparse (E2)', '',
             'Ten irregular points comprise four bounding tetrahedron vertices '
             'and six interior convex combinations. Six further convex '
             'combinations supply strictly interior query points. Three fields '
             'are supplied together: constant 1, affine '
             '`2*x-3*y+0.5*z+1`, and squared radius `x^2+y^2+z^2`. '
             'The serial routine must return status zero, finite weights '
             'and finite field values.', '',
             'Each returned tetrahedron must have four distinct valid vertex '
             'indexes and absolute edge determinant at least `1e-10`. '
             'Weights must be nonnegative within tolerance and sum to one. '
             'Scalar weighted sums of preserved original vertices must '
             'reconstruct the original query, and weighted vertex fields '
             'must match all three interpolated channels, within `1e-10` '
             'absolute error. The constant and affine fields must also '
             'agree with their direct analytic values at the query. '
             'The squared-radius channel is checked as piecewise-linear '
             'interpolation, not exact nonlinear-function recovery.', '',
             'The routine rescales coordinates in place, so references use '
             'saved inputs. This uses the existing MIT-licensed version-1 '
             'package and serial entry point. It does not verify the '
             'empty-circumsphere property, convex-hull extrapolation, '
             'all degenerate configurations or the parallel variant.', '',
             '## Nonuniform Fourier sums: NUFFT1D (J1)', '',
             'Eighty nodes `0.95*(pi*sin(0.37*j)+0.01*cos(0.11*j))` lie '
             'strictly inside `[-pi,pi]`. Mode counts 15, 16, 31 and 32 '
             'exercise odd/even ranges `-ms/2:(ms-1)/2`. Three strength '
             'patterns are a single complex source, all ones, and mixed '
             'dyadic complex values. Both exponent signs give 24 calls '
             'and 564 checked complex coefficients.', '',
             'The type-1 reference is '
             '`F_k=sum_j c_j*exp(sign*i*k*x_j)/nj`, evaluated independently '
             'by scalar real and imaginary trigonometric sums. All statuses '
             'must be zero and all outputs finite. The maximum complex '
             'coefficient error divided by `max(1,sum(abs(c))/nj)` must '
             'be at most `1e-8`, with requested library accuracy `1e-10`. '
             'The zero mode is separately compared with `sum(c)/nj`. '
             'These tolerances check usage and normalization, not a rigorous '
             'error guarantee for arbitrary signals.', '',
             'The cached package retains its existing checksum-guarded legacy '
             'FFT dummy-array declaration fixes and package-specific '
             '`-fallow-argument-mismatch` option. No transform formulas, '
             'library patches or build settings were changed for this driver. '
             'Types 2/3, the static F77 entry point, other dimensions and '
             'performance are not verified. J1 remains the broader '
             'recorded classification for this nonuniform configuration.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice. '
             'Author examples were reviewed for usage; upstream package '
             'licenses remain separate. Loading a link selects source '
             'without submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def pde_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-pde-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked GAMS partial differential equation drivers', '',
             'These I2 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, using existing precompiled libraries. Only '
             'their main programs and executables were compiled. The '
             '[verification report](gams-pde-validation.json) records source '
             'hashes, package pins and actual output. These examples do not '
             'exhaust PDE methods or the GAMS categories.', '',
             'Both drivers separate solver error against an exact discrete '
             'solution from error against the continuous PDE. The latter '
             'includes spatial discretization error and should not be '
             'interpreted as failure of the linear solver. The domains, '
             'boundary conditions and methods differ, so these runs are '
             'not a performance comparison.', '',
             '## Nonzero Dirichlet Poisson/Helmholtz: fishpack', '',
             'On `[0,2] x [-1,1]`, the continuous solution is '
             '`u=1+x/2-y/4+sin(pi*x/2)*sin(pi*(y+1))`. The driver supplies '
             'the nonzero affine boundary values and sampled forcing '
             'for `Laplacian(u)+lambda*u=f`, with `lambda=0` and `-0.75`. '
             'Three rectangular meshes have 16-by-12, 32-by-24 and '
             '64-by-48 intervals, for six solves.', '',
             'Let `w` denote the sine product, `a=1+x/2-y/4`, '
             '`mu_c=-(pi/2)^2-pi^2`, and '
             '`mu_h=-4*sin(pi/(2*m))^2/hx^2-4*sin(pi/n)^2/hy^2`. '
             'The forcing is `lambda*a+(mu_c+lambda)*w`. Because the affine '
             'part has zero discrete Laplacian and the sine product is a '
             'five-point eigenvector, the exact discrete solution is '
             '`a+((mu_c+lambda)/(mu_h+lambda))*w`.', '',
             'Solver status must be zero; the solution and forcing '
             'perturbation must be finite. Perturbation and boundary errors '
             'must be at most `1e-12`. Maximum error against the exact '
             'discrete solution must be at most `1e-11`. Scalar five-point '
             'residuals are independently evaluated on the preserved forcing; '
             'the maximum residual divided by `max(1,max(abs(f_interior)))` '
             'must be at most `1e-11`.', '',
             'These grids contain sine-product extrema, so the maximum '
             'continuous error must agree with '
             '`abs((mu_c+lambda)/(mu_h+lambda)-1)` within `1e-11`. '
             'Halving both spacings must reduce continuous error by a '
             'factor between 3.8 and 4.2. Positive Helmholtz shifts, '
             'Neumann/periodic boundary modes, singular compatibility '
             'corrections and general nonsmooth forcing are not verified.', '',
             '## Periodic spectral and finite-difference Poisson: PoisFFT', '',
             'On a periodic interval of length `2*pi`, the continuous '
             'solution is `u=sin(x)+cos(3*x)/4` and forcing '
             '`f=-sin(x)-9*cos(3*x)/4`. Grid sizes 16, 32 and 64 sample '
             'the interval without duplicating its endpoint. Only '
             'roundoff-level mean forcing is removed for compatibility.', '',
             'The double-precision serial solver is tested with spectral '
             'approximation and with the documented `approximation=2` '
             'second-order centered operator. For each mode k, the '
             'spectral eigenvalue is `-k^2`; the finite-difference '
             'eigenvalue is `mu_k=-4*sin(k*pi/n)^2/h^2`. The exact '
             'discrete reference is `-sin(x)/mu_1-9*cos(3*x)/(4*mu_3)`. '
             'The spectral reference therefore equals the continuous solution.', '',
             'All computed values must be finite, the maximum error against '
             'the exact discrete solution at most `1e-11`, and the solution '
             'mean at most `1e-11` in magnitude. Spectral continuous error '
             'must also be at most `1e-11`. Finite-difference solutions '
             'additionally pass an independent periodic three-point '
             'residual check with wraparound indexes, scaled by '
             '`max(1,max(abs(f)))` and bounded by `1e-11`. Their continuous '
             'error reduction factors must lie between 3.5 and 4.5 on '
             'successive doubled grids.', '',
             'Each of the six solver objects uses FFTW estimate planning '
             'and is reused for a second solve with zero forcing, which '
             'must return a finite zero solution within `1e-11`. Each '
             'object is finalized afterwards: twelve solves in total. '
             'The invoked API has no returned numerical status, so independent '
             'answer checks determine acceptance. Other boundary conditions, '
             'incompatible nonzero-mean forcing, higher dimensions, single '
             'precision and MPI/PFFT variants are not verified. Existing '
             'package build wrappers and FFTW links were unchanged.', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own MIT '
             'notice. Pinned author examples were reviewed for calling '
             'conventions; upstream package terms remain separate. Loading '
             'a link selects source without submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def data_kinds_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-data-kinds-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked numeric parsing, FIFO storage and machine-kind drivers', '',
             'These N3, N4 and R1 examples passed the restricted GNU Fortran '
             '16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. '
             'Only their main programs and executables were compiled. The '
             '[verification report](gams-data-kinds-validation.json) records '
             'source hashes, pinned revisions and actual output. GAMS '
             'categories are not exhausted.', '',
             '## Numeric text parsing: fortran-fast-float (N3)', '',
             'The driver checks 129 decimal strings representing `i/8`, '
             '`i=-64..64`, written with three fractional digits. Every expected '
             'value is exactly representable in binary64. Eight decimal int64 '
             'values and seven int32 values include signed minima, maxima, '
             'negative values and zero. References use native integer values; '
             'the signed minimum is formed without an out-of-range positive literal.', '',
             'Further successful calls check binary `11111111=255`, '
             'hexadecimal `7FFFFFFF=huge(int32)`, Fortran `1.25D-1=0.125`, '
             'and the halfway decimal `9007199254740993`, which must round '
             'to even binary64 value `9007199254740992`. Every successful '
             'call must return OK and its exact reference value; the 129 '
             'dyadic floating results must also be finite.', '',
             'Two invalid prefixes must return INVALID_INPUT. Exponent '
             'overflow `1e999`, positive and negative int64 overflow, and '
             'positive int32 overflow must return OUT_OF_RANGE. There are '
             '148 successful calls and six invalid/overflow calls: 154 '
             'in total. Correct rounding for every decimal, underflow, '
             'NaN/Inf conventions, complete-token consumption, alternate '
             'decimal separators and parser speed are not certified. '
             'Existing package manifest adaptations and compiler settings '
             'were unchanged.', '',
             '## Copied-record FIFO model: for_fifo_queue (N4)', '',
             'Each C-interoperable payload contains two int64 fields: serial '
             'number `j` and checksum `j*j-7*j`. An independent array model '
             'tracks enqueue/dequeue order. Three cycles each push 40 records, '
             'pop 17, push 13, then drain the queue: 159 primary records. '
             'Every push overwrites the caller\'s original storage afterwards, '
             'so later retrieval also checks byte-copy semantics. Counts '
             'and empty state are compared with the model after every operation.', '',
             'A second queue holds a sentinel record throughout the three '
             'cycles, then returns it unchanged, giving 160 checked records '
             'in total. Empty pops must return false and a null pointer. '
             'All popped C allocations are released with C `free`, and both '
             'fully drained queues are destroyed. The 16-byte payload '
             'keeps the library\'s following pointer header aligned in '
             'this sandbox. Pointer-owning values, arbitrary payload '
             'alignment, out-of-memory behavior, concurrency and leak-sanitizer '
             'coverage are outside this example.', '',
             '## Portable kinds and machine inquiries: PENF (R1)', '',
             'The driver checks I1P/I2P/I4P/I8P against ISO int8/int16/int32/int64 '
             'and R4P/R8P against ISO real32/real64 in this GNU environment. '
             'Public bit/byte constants and `byte_size` must report the '
             'corresponding widths. Integer and real maxima are checked '
             'against native inquiry values; smallR4P/smallR8P must equal '
             'the least positive **normal** values from TINY, not subnormal minima.', '',
             'The bytes of int32 pattern `0x01020304` independently determine '
             'the observed little/big endian code. Repeated `penf_init` must '
             'preserve that code and report initialization complete. A runtime '
             'experiment repeatedly halves a perturbation until adding half '
             'of it to one becomes indistinguishable from one. Volatile real32 '
             'and real64 variables keep the arithmetic observable. Measured '
             'perturbations must equal EPSILON and iteration counts plus one '
             'must equal DIGITS, giving 24 and 53 significand bits here.', '',
             'Compiler inquiries check the public environment on this '
             'sandbox; cross-platform portability and other rounding modes '
             'are not established. Quadruple precision, signed-minimum '
             'constants, ZeroR constants, character kinds, format strings '
             'and numeric/string conversions are outside this driver. '
             'In particular this R1 evidence does not verify PENF\'s '
             'separate N3 mapping.', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own '
             'MIT notice. Author examples were reviewed for usage; '
             'upstream package licenses remain separate. Loading a link '
             'selects source without submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def products_status_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-products-status-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked scalar-product, assertion and error-status drivers', '',
             'These D1, S3 and R3 drivers passed the restricted GNU Fortran '
             '16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. '
             'Only their mains and executables were compiled. The '
             '[verification report](gams-products-status-validation.json) records '
             'source hashes, pins and actual output. GAMS categories are not exhausted.', '',
             '## Exact scalar products: fordot (D1)', '',
             'Lengths 1, 7, 8, 17 and 64 cover singleton, odd and even arrays. '
             'Three integer numerator patterns produce mixed signed, cancelling '
             'and zero products. Inputs are `u_i=a_i/8`, `v_i=b_i/4`; an '
             'independent int64 scalar sum supplies `sum(a_i*b_i)/32`. '
             'All products and partial sums are small exactly representable '
             'dyadic values, so finite **exact equality** is required.', '',
             'For every dataset, the default call and all four methods '
             'm1..m4 are tested. Each method also uses valid distinct '
             'block counts from `[1,3,n]`, covering uneven partitions and '
             'single-element blocks. There are 231 calls. Empty inputs, '
             'invalid block counts, noncontiguous arrays, severe floating '
             'roundoff, coarray mode and performance are not verified.', '',
             '## Captured comparison outcomes: fassert (S3)', '',
             'Three positive assertions exercise integer arithmetic, '
             'integer arrays and an approximate real64 numerical result. '
             'Thirteen captured comparisons check matching/mismatching '
             'integer scalars and vectors; seven scalar real64 offsets '
             '`[-0.75,-0.5,-0.25,0,0.25,0.5,0.75]` with absolute tolerance '
             '0.5; and two vector comparisons at and outside tolerance 0.25.', '',
             'Native logical expressions independently determine the expected '
             'outcome. Both exact scalar tolerance boundaries must pass. '
             'Captured diagnostics must contain the supplied case label '
             'and the matching PASSED/FAILED prefix. Expected failures are '
             'returned to the caller and verified without terminating '
             'the program. Shape mismatches, NaN comparison semantics, '
             'negative tolerances, custom comparators, other ranks/types '
             'and framework integrations are outside this example. This '
             'S3 driver does not verify the separate R2 mapping.', '',
             '## Recovery and copied error objects: errstat (R3)', '',
             'An independently written `safe_ratio_root(a,b,status)` '
             'returns `sqrt(a/b)` for valid inputs, or zero plus a '
             'user-defined status/message for invalid inputs. Nine calls '
             'alternate successful results with positive/negative zero '
             'denominator errors (101), a negative radicand (102), '
             'and a quiet-NaN numerator (103). Exact arithmetic results, '
             'codes, flags and messages must match the specified cases. '
             'Every successful call must replace the previous error '
             'with status zero and message `ok`.', '',
             'A further error with code 701 and message `original` is '
             'copied to a second status object. Appending context must '
             'produce `original - context` only in the first object. '
             'Explicit success with message `recovered` must leave the '
             'copy unchanged. Initialization must reset the first object '
             'to success with an empty message. The arithmetic function '
             'and error codes belong to the driver; errstat supplies '
             'the status-handling API. Arbitrary arithmetic overflow, '
             'omitted status arguments, message repositories, additional-task '
             'callbacks and thread safety are not verified.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice. '
             'Author examples/tests were reviewed for usage; upstream '
             'package licenses remain separate. Loading a link selects '
             'source without submitting a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def kriging_network_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-kriging-network-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked kriging and neural-network drivers', '',
             'These L13 and K drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
             'reusing existing package libraries. Only their mains and executables were compiled. '
             'The [verification report](gams-kriging-network-validation.json) records pins, source hashes '
             'and actual output. GAMS categories are not exhausted.', '',
             '## Ordinary kriging: GSLIB (L13)', '',
             'Two observations at x=0 and x=2 have values 1 and 3. Seven query positions '
             '`[-1,0,0.5,1,1.5,2,3]` exercise interpolation and extrapolation with three covariance '
             'models: spherical, exponential and Gaussian. Nugget is zero, sill is one and the '
             'model parameter is 3. For separation h, the independent references are '
             '`max(0,1-1.5*t+0.5*t**3)` with t=h/3 (zero for t>=1), `exp(-h)` and '
             '`exp(-h*h/3)`. These formulas follow the implemented parameter convention, '
             'rather than assuming a common practical-range definition.', '',
             'The covariance routine cova3 uses **real32**, while ksol solves the packed symmetric '
             'system in **real64**. Six standalone distances per model and all query covariances '
             'must agree with analytic formulas within 2e-7. For r=C(2), c1=C(abs(x)) and '
             'c2=C(abs(x-2)), the independent solution is '
             '`w1=(1+(c1-c2)/(1-r))/2`, `w2=1-w1`, `mu=c1-w1-r*w2`. '
             'All 21 solves must agree with these weights for rounded covariances and have '
             'an independently accumulated system residual within 1e-11.', '',
             'Against fully analytic covariances, weight errors must stay within 5e-7 and '
             'prediction/variance errors within 1e-6. Predictions are `w1+3*w2`; '
             'variances are `1-w1*c1-w2*c2-mu`. Finite results, nonnegative variances '
             '(tolerance 1e-11), unit weight sums, constant-field reproduction, endpoint '
             'interpolation and midpoint/reflection symmetry are required. This is an '
             'independent API consumer; no matching author driver is recorded. GSLIB source-evidence '
             'hashes use UTF-8/LF normalization. Anisotropy, nugget effects, nested structures, '
             'large/singular systems and robust pivoting are not verified. This L13 example '
             'does not verify the separate E2 mapping.', '',
             '## Known dense-network evaluation: FKB (K)', '',
             'An independently specified 2-input, 3-hidden-unit, 2-output network uses ReLU '
             'hidden activation and linear outputs. Fixed small dyadic weights and biases '
             'make independent scalar forward calculations straightforward. The full integer '
             'input grid [-2,2] squared supplies 25 cases, including negative, positive and '
             'exactly zero hidden preactivations.', '',
             'The driver loads its model, saves it and reloads a second network. Both versions '
             'must report the expected dimensions and match independent scalar calculations '
             'with finite outputs within 1e-12: 50 predictions and 100 scalar outputs. '
             'The two temporary model files are removed on success. Author loading/saving '
             'tests were reviewed for the file format. This broad K demonstration verifies '
             'forward evaluation and serialization, not training or approximation quality. '
             'Gradients, dropout, batch normalization, Keras conversion and parallel performance '
             'are outside its verified scope.', '',
             '## Checked links and actual output', '',
             'These independently written drivers have their own MIT notice; upstream package '
             'licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def lookup_fastmath_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-lookup-fastmath-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked lookup services and approximate elementary functions', '',
             'These E3, C4b and C2 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-lookup-fastmath-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Lookup location and column services (E3)', '',
             'A nine-point linear grid spans [-2,2] in steps of 0.5. The first column '
             'contains 2*x+1. The second resamples five irregular source points '
             '`[-2,-1.25,0.25,1,2]`, with values `(x+1)**2`, onto that grid. '
             'Adding a third constant column (7) exercises column reallocation. An independent '
             'scalar interval scan and endpoint-clamped linear formula construct the expected '
             'stored grid values; the lookup routines do not supply their own references.', '',
             'After making an independent table copy, additive updates shift the first column '
             'by 3 and the second by -0.5. Both tables are queried at 49 points from -3 to 3 '
             'in steps of 0.125, totaling 98 queries. Four routes must agree with the independent '
             'two-stage reference within 2e-12: scalar and all-column lookups, each directly '
             'and through a reusable location object. This checks source resampling followed '
             'by table interpolation; off-grid values are not assumed equal to the original quadratic.', '',
             'Location indices and fractions must stay in bounds, and reconstruct the clamped '
             'query coordinate within 1e-12. Grid creation, endpoint and internal knots, clamping '
             'on both sides, column addition, additive updates and independence of the old copy '
             'are covered. Only linear grid spacing is verified. Quadratic/cubic spacing, '
             'extrapolation mode, 2D tables, persistence, invalid inputs and performance '
             'are outside this driver. Its E3 service checks do not independently verify '
             'the separate E1a mapping.', '',
             '## Approximate exponential and logarithm (C4b)', '',
             'For 641 values x=-80..80 in steps of 0.25, fexp(x) is compared with intrinsic '
             'exp(x), and flog_quintic(exp(x)) with the known x. Relative exponential error '
             'must be at most 1e-4; absolute logarithm error at most 1e-3. The approximate '
             'composition fexp(flog_quintic(exp(x))) must recover exp(x) with relative error '
             'at most 1.2e-3. Finite outputs, positive exponentials, strict monotonicity '
             'on this grid and scalar/array consistency are also required.', '',
             'These are accuracy checks of approximate functions, not replacements promising '
             'intrinsic precision. The saved run reports observed errors, separately from the '
             'acceptance tolerances. Overflow/underflow boundaries, subnormal and exceptional '
             'arguments, other polynomial/spline variants and speed are not verified.', '',
             '## Approximate reciprocal square root (C2)', '',
             'Exactly representable dyadic roots `r=(m/8)*2**k`, m=8..15 and '
             'k=-250..250 in steps of 25, supply 168 normal finite squares x=r*r. '
             'The independent reference is 1/r, without evaluating sqrt. Relative error '
             'in frsqrt(x) must be at most 2e-3, and the normalized equation residual '
             '`abs(x*y*y-1)` at most 4e-3. Results must be finite and positive, with '
             'scalar/array agreement. The fixture spans many exponents and eight mantissas; '
             'it does not establish a universal error bound. Zero, negative, subnormal, '
             'infinity/NaN inputs, wrapper variants and performance are not verified.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice. Author examples/tests '
             'were reviewed for usage; upstream package licenses remain separate. '
             'Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def circuits_beta_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-circuits-beta-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked complex circuits, elementary functions and beta identities', '',
             'These A4, C4 and C7 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-circuits-beta-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Complex RLC impedance: ECX (A4)', '',
             'The public z API computes resistor, capacitor and inductor impedances for '
             '12 parameter sets: R in [1,10,100] ohms, C in [0.001,0.01] farads and '
             'L in [0.01,0.1] henries. Each set uses 17 angular frequencies 2**k, '
             'k=-8..8, plus its resonance frequency 1/sqrt(L*C). All 36 array calls '
             'must return status zero and the success message. The API requires three '
             'parameter entries even for these one-parameter elements; unused entries are zero.', '',
             'All 648 element impedances must be finite and agree with independent real/imaginary '
             'formulas: R, -i/(omega*C) and i*omega*L. At each of the 216 frequency cases '
             'the driver also constructs series RLC and parallel RC combinations. Series '
             'impedance is checked against `R+i*(omega*L-1/(omega*C))`. Parallel RC is '
             'checked against `R/(1+t*t)-i*R*t/(1+t*t)`, t=omega*R*C. '
             'Complex error divided by max(1,abs(reference)) must be at most 2e-13.', '',
             'At resonance, the series imaginary part must vanish and magnitude equal R '
             'within 1e-12*max(1,R). Circuit composition is supplied by the driver; '
             'these checks do not establish a general package circuit solver. A4 describes '
             'the complex arithmetic interface, not an electrochemistry-specific taxonomy class. '
             'Nonideal elements, nonlinear kinetics, parameter estimation and exceptional '
             'inputs are outside this example.', '',
             '## Real sinc and sech: RPN calculator library (C4)', '',
             'There are 129 equally spaced arguments -8..8 in steps of 0.125, plus '
             '+/-1e-10 and +/-1e-6: 133 real arguments. The sinc reference is the '
             'independently accumulated 64-term series `sum((-x*x)**k/(2*k+1)!,k=0..63)`, '
             'evaluated by term recurrence without calling sin. Absolute error must '
             'stay within 5e-13. For sech, the reference is `2*a/(1+a*a)`, '
             'a=exp(-abs(x)), avoiding the package cosh implementation; absolute error '
             'must stay within 5e-14.', '',
             'Finite outputs, exact unit values at zero, even symmetry, the sech range '
             '(0,1] and scalar/array consistency are required. Available author tests '
             'were reviewed for public-module usage; they are not matching sinc/sech drivers. '
             'This real C4 driver does not verify the separate C2 cube-root mapping, '
             'complex overloads, extreme inputs or the interactive calculator.', '',
             '## Real beta: RPN calculator library (C7)', '',
             'The 128 positive argument pairs comprise all integers x,y=1..8 and '
             'all half-integers x,y=0.5..7.5. Integer references are '
             '`B(i,j)=(i-1)!*(j-1)!/(i+j-1)!`. Half-integer references use '
             '`B(n+1/2,m+1/2)=pi*(2*n)!*(2*m)!/(4**(n+m)*n!*m!*(n+m)!)` '
             'for n,m=0..7. Factorials through 15! are formed exactly in int64 '
             'and converted before products; the references do not call gamma or beta.', '',
             'For each pair, B(x,y), B(y,x), B(x+1,y) and B(x,y+1) are checked '
             'against the closed form and the two identities '
             '`B(x+1,y)=x/(x+y)*B(x,y)` and `B(x,y+1)=y/(x+y)*B(x,y)`, '
             'using the independent reference on the right. All 512 evaluations must '
             'be finite, positive and within relative error 2e-13. No matching author '
             'beta driver is recorded. The separate C10 Bessel mapping, complex beta, '
             'poles, large arguments and gamma-product overflow are not verified.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def inverse_tvd_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-inverse-tvd-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked matrix inversion and TVD ODE integration', '',
             'These D2 and I1 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-inverse-tvd-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Known-factor inverses and determinants: linalg_fortran (D2)', '',
             'Matrices have dimensions 1,2,3,4,5,8 and are constructed as `A=s*L*D*U`. '
             'L and U are unit bidiagonal matrices with subdiagonal ell in [-0.5,0.25] '
             'and superdiagonal up in [-0.25,0.5]. Diagonal entries are '
             '`d(k)=(-1)**(k+1)*(k+1)`, with s in [0.5,1,8]. Scalar loops form A. '
             'These 72 base matrices and 60 first/last-row swaps give 132 nonsingular cases.', '',
             'The independent inverse follows from the finite triangular factors: '
             '`Ainv(i,j)=sum((-up)**(k-i)*(-ell)**(k-j)/(s*d(k)),k=max(i,j)..n)`. '
             'The determinant is `s**n*product(d)`. A row swap negates the determinant '
             'and swaps the corresponding inverse columns. No package linear algebra '
             'supplies the references. Dimensions 2,3,4 exercise specialized determinant '
             'formulas, while 1,5,8 exercise its general LU branch.', '',
             'The package inverts a working copy in place and must return true. Finite '
             'inverse entries must agree within normalized max-norm error 2e-12. '
             'Independent scalar loops check both A*Ainv and Ainv*A against the identity '
             'with maximum entrywise residual 5e-12. Finite determinants must match '
             'the factor/permutation reference with relative error at most 2e-12. '
             'Two exactly rank-deficient matrices, a 2x2 proportional-row matrix and '
             'a 3x3 diagonal matrix with a zero entry, must return zero determinant '
             'and false inverse status. These two examples do not establish general '
             'near-singularity detection. Ill-conditioned, nonsquare, empty, complex '
             'and real32 inputs are outside this driver.', '',
             '## TVD Runge-Kutta ODE integration: HR-WENO (I1)', '',
             'The driver solves three equations from t=0 to 1: '
             '`u1\'= -u1`, `u2\'= -2*u2`, `u3\'=2*t`, with initial values [1,2,0]. '
             'Exact continuous solutions are exp(-t), 2*exp(-2*t) and t*t. '
             'Orders p=1,2,3 each use N=8,16,32,64 dyadic steps: 12 independent runs.', '',
             'For the two decay components, an independent discrete reference is '
             '`u_j(1)=j*P_p(-j/N)**N`, with stability polynomial '
             '`P_p(z)=sum(z**k/k!,k=0..p)`. The nonautonomous component must equal '
             '1-1/N for Euler and 1 for orders 2 and 3, checking stage-time usage. '
             'All three values must match the discrete references within 2e-12. '
             'Every single-step return time is checked within 1e-14; final state '
             'must be 2 and the function-evaluation count p*N.', '',
             'Errors of the decay components against the continuous exponential '
             'solutions must decrease with each step halving. Coarse/fine error ratios '
             'must lie between 0.7*2**p and 1.5*2**p. On N=64 the maximum errors '
             'must be below 0.01, 0.0001 and 0.000001 for orders 1,2,3, respectively. '
             'Actual errors are included below.', '',
             'This driver explicitly uses documented single-step mode, itask=2, to '
             'reach the prescribed dyadic times. The pinned source has a TODO about '
             'adjusting the final step in ordinary interval mode; that mode is not '
             'verified here. No matching standalone author ODE driver is recorded. '
             'Spatial WENO reconstruction, the separate multistep integrator, stiffness, '
             'backward integration, TVD behavior for shocks and performance are outside '
             'this example.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def roots_splines_quadrature_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-roots-splines-quadrature-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked quadratic roots, spline derivatives and quadrature', '',
             'These F1, E1 and H2 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-roots-splines-quadrature-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Known quadratic roots: fortranlib (F1)', '',
             'All 21 distinct pairs from [-4,-2,-0.5,0,0.5,2,4] are used to form '
             '`a*(x-r1)*(x-r2)`, with a in [-8,-0.5,0.5,8]: 84 calls. '
             'Coefficients and roots are dyadic, so this moderate fixture avoids '
             'coefficient-rounding ambiguity. Returned roots are sorted by the caller '
             'and must match the known pair within absolute error 2e-12. Root sums '
             'and products are also checked within 2e-12.', '',
             'Each root must have polynomial residual, divided by '
             '`max(1,abs(a*x*x)+abs(b*x)+abs(c))`, at most 2e-12. '
             'The ordinary real64 quadratic API is checked. No matching author driver '
             'is recorded. Repeated or complex roots, zero leading coefficient, '
             'Pascal/reduced variants, real32, severe cancellation and extreme scaling '
             'are outside this example. This F1 mapping describes a quadratic solver; '
             'it does not claim a general iterative root finder or verify the separate '
             'E1 interpolation and H2 integration mappings.', '',
             '## Cubic-spline values and derivatives: fortran-utils (E1)', '',
             'Four polynomials, degrees 0,1,2,3, are sampled on uniform grids of '
             '5,9,17 points and a nine-point nonuniform grid, all spanning [-1,1]. '
             'There are 16 polynomial/grid fixtures. The polynomials are '
             '`1`, `2*x-1`, `3*x*x-2*x+0.5` and `x**3-0.5*x*x+2*x-1`. '
             'Known formulas supply values and both derivatives at 65 queries '
             'from -1 to 1 in steps of 1/32: 3120 independent scalar references.', '',
             'The consistent-cubic endpoint conditions selected by spline3ders '
             'should reproduce these polynomials. Every component must be finite '
             'and within absolute error 5e-10. Three additional calls per fixture '
             'request only the first derivative, only the second derivative, and '
             'only values with reversed query order; they must agree with the full '
             'call within 5e-12. In total, 64 spline calls check endpoints, knots, '
             'interior values, optional outputs and decreasing query order. The '
             'author spline tests were reviewed for usage. Extrapolation, '
             'nonpolynomial convergence, other endpoint conditions, invalid grids '
             'and the separate N6 sorting mapping are not verified.', '',
             '## Sampled and adaptive integration: SciFortran (H2)', '',
             'On intervals [-1,1], [0,1] and [-0.5,1.5], sample counts '
             '[5,8,9,16,17] exercise even and odd panel counts. Powers x**p, '
             'p=0..3, give 60 fixtures. Simpson and trapezoidal calls use both '
             'endpoint and step-size overloads: 240 sampled-rule calls. Simpson '
             'must reproduce the polynomial antiderivative. The independent '
             'trapezoidal reference adds `(b-a)*h*h/6` for x*x and '
             '`(b*b-a*a)*h*h/4` for x**3 to the exact integral; for degrees '
             '0 and 1 it is exact. This checks the expected discrete rule, '
             'rather than treating trapezoidal discretization error as solver failure. '
             'Normalized errors must be at most 2e-12.', '',
             'Adaptive integration checks powers 0..7 on the same three intervals '
             'with the default wrapper and all six Gauss-Kronrod keys: 168 calls. '
             'Six exponential tails have rates [0.5,1,2], lower endpoints [0,1] '
             'and reference exp(-rate*a)/rate. Whole-line Gaussian and Cauchy '
             'integrals have references sqrt(pi) and pi. Endpoint-singular mode '
             'integrates sqrt(x) and 1/sqrt(x) on [0,1], with references 2/3 '
             'and 2. These total 178 adaptive calls. Requested absolute/relative '
             'tolerances are 1e-11, with normalized closed-form error at most 5e-11. '
             'All results must be finite; normalization is max(1,abs(reference)).', '',
             'Module callbacks follow the working upstream usage. This uses the '
             'existing selected SciFortran integration subset and coefficient-precision '
             'repairs; no library rebuild or new source patch is introduced. '
             'Weighted/pole integrals, complex and nonuniform sampled rules, all '
             'QUADPACK error paths and performance are outside this example.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def io_bounds_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-io-bounds-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked numeric file I/O and bounds validation', '',
             'These N1 and R2 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-io-bounds-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Independent numeric-file fixtures: IO-Fortran-Library (N1)', '',
             'Real64 matrices with shapes 1x1, 2x3, 4x2 and 3x4 are written with '
             'comma and semicolon delimiters, giving eight file fixtures. Values '
             'are `(10*i-7*j)/8`, with the first entry replaced by zero. '
             'The library writes exponential-format data. An independent native '
             'Fortran reader checks the exact row count, delimiter count per row, '
             'column order and values. Separators are replaced with spaces before '
             'native list-directed numeric parsing.', '',
             'The library then reads each file and must reproduce the original '
             'shape and values. To check its reader without relying on its own '
             'writer, the driver also creates a four-row, three-column CSV from '
             'literal text using native Fortran and checks the result against '
             'an explicit matrix. All loaded values must be finite, with '
             'elementwise error divided by max(1,abs(reference)) at most 5e-14. '
             'These references can detect compensating reader/writer layout errors '
             'that a library-only round trip might miss.', '',
             'Every successful library operation must return status zero. A file '
             'not created in the fresh sandbox must return nonzero status and a '
             'nonempty diagnostic. Temporary files are deleted after their checks. '
             'The author file tests were reviewed for API usage; all fixture data '
             'are independently specified. Headers, locale options, complex/integer '
             'arrays, other ranks, nonfinite values and output modes beyond '
             'exponential formatting are outside this example.', '',
             '## Inclusive typed bounds: fortran-error-handler (R2)', '',
             'Integer values -4..4 and real32/real64 values -3..3 test the '
             'inclusive interval [-2,2], lower-only and upper-only bounds. '
             'For each real kind, NEAREST supplies the immediately adjacent '
             'representable values inside and outside both endpoints. '
             'A further three values per type test equal lower/upper bounds '
             '[0,0], using +/-epsilon for reals. There are 102 calls in total.', '',
             'Independent native comparisons determine acceptance. Each accepted '
             'value must yield isError() false and code zero. All 30 expected '
             'rejections must yield isError() true, code 105, a message beginning '
             'with the supplied text and exactly one supplied application trace '
             'entry. Interleaved successes and failures ensure that each returned '
             'object reflects the current input. No errors are triggered or '
             'suppressed to allow continuation; the API returns diagnostics for '
             'the caller to inspect.', '',
             'The author validation example and criteria implementations were '
             'reviewed for usage. This checks limit(), including exact endpoint '
             'inclusion, rather than the other criteria or their tolerance '
             'settings. Reversed bounds, omitted bounds, NaNs, critical-error '
             'termination and the separate R3 error-handling mapping are not verified.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def optimization_spacing_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-optimization-spacing-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked derivative-free optimization and deterministic spacing', '',
             'These G1b and R drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-optimization-spacing-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Known unconstrained minima: ForTimize Nelder-Mead (G1b)', '',
             'Three coupled positive-definite quadratic problems use dimensions 2,3,5. '
             'For errors e=x-center, the objective is `sum(i*mixed(i)**2)`, '
             'where mixed(i)=e(i)+0.25*e(i+1), except for the final component e(n). '
             'The upper-bidiagonal transformation is invertible, so the unique minimizer '
             'is the specified center and the objective there is zero. Alternating '
             'signed half-integer centers and three displaced starting points per '
             'dimension give nine solves.', '',
             'Three further solves minimize `(1-x1)**2+100*(x2-x1*x1)**2`, '
             'starting at [-1.2,1], [0,0] and [2,2]. Its unique zero is [1,1]. '
             'All twelve results must be finite, within coordinate error 2e-4 of '
             'the known minimizer, and have objective in [0,1e-8]. A scalar '
             'recomputation of the objective must agree with the returned value '
             'within 1e-12. The callback rejects any derivative request, verifying '
             'that this configuration is derivative-free.', '',
             'The initial simplex step is 0.4, convergence_tolerance is 1e-20, '
             'konvge is 20 and the actual function-evaluation limit kcount is '
             '50000. The pinned wrapper does not expose its underlying termination '
             'status and does not use max_iters to bound this Nelder-Mead call; '
             'acceptance therefore depends on the independently checked result, '
             'not a success flag. The author example was reviewed for API usage; '
             'the driver and objectives are independently written. Upstream '
             'licensing remains separate from the driver notice.', '',
             'Other optimizer methods, nonsmooth/global problems, scaling extremes, '
             'all failure paths and performance are not verified. The implementation '
             'uses module-level callback/data pointers, so this serial driver does '
             'not verify concurrent independent optimizations. Its success does not '
             'verify the separate GradientDescent procedure record.', '',
             '## Arithmetic and geometric grids: pointsets (R)', '',
             'Array lengths [2,3,5,9,17] and endpoint pairs [0,1], [-2,3], '
             '[3,-2] and [1,1] give 20 arithmetic grids. Geometric spacing '
             'uses the same fixtures with ratios [0.5,0.75,1.25,2], giving '
             '80 further grids. Closed-form real64 references are '
             '`a+(b-a)*i/(n-1)` and '
             '`a+(b-a)*(q**i-1)/(q**(n-1)-1)`, i=0..n-1. '
             'These do not repeat the package accumulation algorithm.', '',
             'The pinned package selects wp=real32. Reference inputs are promoted '
             'from that working kind, and maximum coordinate error divided by '
             'max(1,abs(a),abs(b)) must stay within 32 working-kind epsilons. '
             'Both endpoints are checked separately. Increasing/decreasing grids '
             'must be strictly ordered; equal endpoints must produce a constant '
             'array. The reported maximum error retains the precision distinction.', '',
             'Seven guarded calls verify unchanged-array behavior: empty and '
             'singleton arrays for each routine, and geometric ratios -1,0,1 '
             'on a five-element sentinel array. In particular, ratio 1 does '
             'not fill a uniform grid at this pin; use arithmetic_spacing '
             'for that purpose. The author pointset tests were reviewed for '
             'usage. Random point generators, large arrays, extreme ratios, '
             'ratios approaching one and other pointset routines are outside '
             'this deterministic service example.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def raster_distributions_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-raster-distributions-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked software raster graphics and seeded distributions', '',
             'These Q and L6 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-raster-distributions-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Exact raster pixels and PNG round trip: fortran-sdl2 (Q)', '',
             'An 85x65, 32-bit software surface uses explicit RGB masks and a known '
             'background color. Four rectangles overlap and extend beyond the upper-left '
             'and lower-right edges. A native loop applies independent half-open '
             'coordinate tests in drawing order and forms the expected packed pixels '
             'with integer shifts and masks, without calling SDL color mapping. '
             'All 5525 RGB pixels must agree exactly, including backgrounds, edges, '
             'clipping and overwritten regions.', '',
             'The surface is exported as PNG, loaded through IMG_Load and converted '
             'to the original pixel format. Every pixel is checked again: 11050 '
             'exact comparisons in total. A native stream read independently verifies '
             'the PNG signature, IHDR chunk tag and big-endian dimensions. The '
             'generated PNG was returned as a browser artifact and visually reviewed:', '',
             '![Verified overlapping and clipped rectangles](gams-raster-distributions.png)', '',
             'The pinned bindings omit IMG_SavePNG; the driver supplies only its '
             'standard C declaration. SDL2_image performs the encoding. No display '
             'server, window, event loop or video initialization is used. The author '
             'surface/pixel examples were reviewed for interfaces; this drawing and '
             'its reference fixture are independently specified. Only RGB content '
             'is checked. Alpha blending, hardware rendering, interactive graphics, '
             'other codecs and the remaining SDL subsystems are outside this driver.', '',
             '## Fixed-seed distribution checks: rng-fortran (L6)', '',
             'Three fixed nonzero seeds use freshly allocated generator/replay '
             'objects. Each normal and Poisson call must replay exactly with the '
             'same seed and call sequence. There are 20000 samples per seed, '
             'or 60000 normal and 60000 Poisson samples, excluding replay calls. '
             'The normal mean must be within 0.04 of zero, and its second moment '
             'within 0.08 of one. Poisson rates 0.5,2,8 use analytic mean lambda, '
             'centered second moment lambda and zero probability exp(-lambda). '
             'Their respective absolute tolerances are 0.04*max(1,lambda), '
             '0.12*max(1,lambda) and 0.02. Normal outputs must be finite and '
             'Poisson counts nonnegative.', '',
             'For radii 0.25,1,3, a further 1000 circle and 1000 sphere samples '
             'per fixture must replay exactly and have normalized squared norm '
             'within 2e-12 of one. Normalized coordinate means must be within '
             '0.15 of zero; second moments must be within 0.12 of 1/2 for '
             'the circle and 1/3 for the sphere. The analytic moments are '
             'independent references, but these deliberately broad, fixed-seed '
             'smoke checks do not certify statistical quality or cryptographic '
             'safety. They are not a general hypothesis-testing suite.', '',
             'Fresh allocations avoid the known source behavior where set_seed '
             'does not clear a cached second normal after an odd normal() call. '
             'That issue remains unresolved; this driver does not verify such '
             'reseeding. All tested Poisson rates use the small-rate branch; '
             'rates >=10 and its rejection sampler are not verified. Parallel '
             'use, jump independence, extreme rates, all-zero seeds and other '
             'distribution routines are also outside this example. The author '
             'example was reviewed for API usage; no upstream sampling code is copied.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'If the graphics fixture changes, refresh its saved PNG preview from the successful '
              'sandbox artifact. No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def quantities_spherical_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-quantities-spherical-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked physical quantities and zonal spherical harmonics', '',
             'These A and J drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-quantities-spherical-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Typed quantity arithmetic: quaff (A)', '',
             'Six signed/zero length values [-8,-0.125,0,0.25,3,1000] test '
             'meters, centimeters, millimeters, feet and inches. Independent '
             'scalar references use 100 cm/m, 1000 mm/m, 0.3048 m/ft and '
             '0.0254 m/in, including the 12 inches/foot relationship. Both '
             'construction from non-SI units and conversion from meters are checked.', '',
             'Addition, subtraction, unary negation, scalar multiplication/division, '
             'division of two lengths, absolute value and sums of quantity arrays '
             'are compared with direct scalar formulas. For positive durations '
             '[0.25,1,10] seconds, typed length/time produces a speed checked '
             'in m/s and ft/s; multiplying the speed by time must recover the '
             'original signed length. Seconds/minutes/hours conversions use '
             'independent factors 60 and 3600. There are 180 numeric references.', '',
             'All results must be finite and have error divided by '
             'max(1,abs(reference)) at most 2e-12. These are numerical checks of '
             'valid typed expressions. The driver does not attempt invalid '
             'dimensional expressions, test their compiler diagnostics, or verify '
             'all quantity types. Parsing, string formatting, overflow and '
             'extreme conversion scales are outside this example. The author '
             'length tests were reviewed for usage; these fixtures are independently '
             'specified. The broad A assignment describes arithmetic with physical '
             'quantities rather than a narrower numerical algorithm.', '',
             '## Independent zonal analysis and synthesis: Spherepack (J)', '',
             'Gaussian grids have latitude/longitude sizes [9,16], [13,24] '
             'and [17,32]. For each grid, the five zonal fields P0..P4 and '
             'a mixture with amplitudes [1,-2,0.5,0.25,-0.75] give six '
             'fixtures, or 18 in total. For z equal to the radial unit-vector '
             'z coordinate, the independent Legendre formulas are '
             '`1`, `z`, `(3*z*z-1)/2`, `(5*z**3-3*z)/2` and '
             '`(35*z**4-30*z*z+3)/8`.', '',
             'Spherepack uses normalized associated Legendre functions and '
             'a half-weight for m=0. Thus a zonal field with amplitude c_l '
             'has real coefficient `a(1,l+1)=2*sqrt(2/(2*l+1))*c_l`. '
             'Every tested valid coefficient must agree with this reference: '
             'all other real coefficients and all imaginary coefficients vanish. '
             'The checks exclude the longitude Nyquist order and invalid '
             'triangular storage. Absolute coefficient error must be at most 2e-11.', '',
             'Synthesis is first checked after analysis, then the analyzed '
             'coefficients are erased and replaced with the independent exact '
             'amplitudes. This second synthesis must reproduce the polynomial '
             'field independently of the analysis output, so a compensating '
             'normalization error cannot pass solely through a round trip. '
             'All synthesized fields must be finite with absolute error at '
             'most 2e-11. There are 18 analyses and 36 syntheses, exercising '
             'repeated workspace use and three grid sizes.', '',
             'The author spherical Helmholtz example was reviewed for object '
             'construction and coordinates; this is an independently written '
             'transform driver, not a reuse of that PDE example. Nonzero '
             'nonzonal modes, vector transforms, Nyquist behavior, PDE/Helmholtz '
             'routines, unresolved-grid aliasing and performance are not '
             'verified. The separate I2 solver mapping remains source-supported '
             'by this dedicated-driver evidence.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def delay_embedding_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-delay-embedding-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked delay equations and numerical Lua embedding', '',
             'These I and S drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-delay-embedding-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Analytic delayed solutions: dde_solver (I)', '',
             'Twelve problems solve `y\'(t)=r*y(t-tau)` with constant history H '
             'through t=4*tau. Delays tau=[0.25,1,2], rates r=[0.5,1] and '
             'histories H=[1,-2] cover all combinations. The independent '
             'method-of-steps reference on this interval is:', '',
             '```text',
             'y(t) = H * (1 + r*t + r**2*max(0,t-tau)**2/2',
             '                 + r**3*max(0,t-2*tau)**3/6',
             '                 + r**4*max(0,t-3*tau)**4/24)', '```', '',
             'Differentiating each interval verifies the delayed equation; '
             'higher terms vanish on the tested interval. Three further '
             'oscillators solve `y\'(t)=-w*y(t-tau)` with history sin(w*t) '
             'and tau=pi/(2*w), for w=[0.5,1,2]. The exact solution remains '
             'sin(w*t), because the delayed sine is -cos(w*t). Each run '
             'samples 65 times from 0 to 4*tau, including all delay knots '
             'and interior points: 975 dense-output references in total.', '',
             'Every solve must return flag zero. Dense output must have '
             'shape [65,1], be finite and agree within error divided by '
             'max(1,abs(reference)) at most 2e-7. Requested relative/absolute '
             'solver tolerances are 1e-10 and 1e-12. Solver and interpolation '
             'arrays are released between runs. Module callbacks and independently '
             'written fixtures follow the interfaces reviewed in the author '
             'delay-oscillator example. No upstream implementation or test code '
             'is copied.', '',
             'Only scalar retarded equations with one constant positive delay '
             'are checked. State-dependent, neutral or multiple delays, events, '
             'derivative interpolation, stiffness and every error path are '
             'outside this example. The broad I mapping is intentional; '
             'ordinary ODE subclasses do not fully describe delayed problems.', '',
             '## Numeric results and state recovery: fortran-lua54 (S)', '',
             'An in-memory Lua script independently defines factorial, sum of '
             'squares, a signed quadratic and a two-argument Euclidean norm. '
             'Fortran checks factorials 0!..20!, sums of squares for n=0..64 '
             'against n*(n+1)*(2*n+1)/6, and `(n-3)*(n+2)` for n=-20..20. '
             'All returned values must have the Lua integer type and agree '
             'exactly with native integer references.', '',
             'Five real calls check known Pythagorean triples, including a '
             'negative argument and the zero vector. Returned values must '
             'be numeric and finite, with absolute error at most 1e-12. '
             'Every function lookup, protected call, result count and stack '
             'cleanup is checked. A negative factorial input must produce '
             'LUA_ERRRUN and its supplied diagnostic. A malformed definition '
             'must produce LUA_ERRSYNTAX and a nonempty diagnostic. Clearing '
             'those error objects must leave the existing functions usable: '
             'a subsequent factorial(6) must return 720. This yields 128 '
             'successful integer calls and five real calls, plus two '
             'expected error paths. The state is closed after all checks.', '',
             'The author in-memory example was reviewed for API usage; '
             'the script and reference fixtures are independently written. '
             'No external scripts are needed. This S driver checks the '
             'numeric language boundary and recovery, not all Lua semantics '
             'or bindings. Arbitrary modules, userdata, callbacks from Lua '
             'to Fortran, concurrent states and a separate Lua 5.3 package '
             'are not verified.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def matrix_roots_box_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-matrix-roots-box-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked matrix square roots and box-constrained quadratics', '',
             'These D and G2 drivers passed the restricted GNU Fortran 16.2.0 sandbox '
             'with FPM 0.12.0, reusing existing package libraries. Only their mains and '
             'executables were compiled. The [verification report](gams-matrix-roots-box-validation.json) '
             'records pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Principal matrix functions: NTPoly (D)', '',
             'Four positive square-root eigenvalue pairs [1,2], [1,3], [0.5,2] '
             'and [2,4] combine with three orthogonal factors: identity, a '
             'rotation with cosine/sine [0.6,0.8], and a 45-degree rotation. '
             'Both dimensions 2 and 3 are checked; the third dimension adds '
             'a decoupled root eigenvalue equal to the pair average. There '
             'are 24 symmetric positive-definite matrices and 48 function calls.', '',
             'Independent scalar sums construct A=Q*diag(r*r)*transpose(Q), '
             'its principal root Q*diag(r)*transpose(Q), and its inverse root '
             'Q*diag(1/r)*transpose(Q). The package must reproduce both '
             'reference matrices with max-entry error divided by '
             'max(1,maxabs(reference)) at most 2e-8. Symmetry error must '
             'be at most 2e-9. Scalar loops independently check root*root=A, '
             'inverse_root*A*inverse_root=I and root*inverse_root=I. '
             'Maximum residual must be at most 5e-8; the first identity is '
             'normalized by max(1,maxabs(A)). All entries must be finite.', '',
             'Exactly one MPI process with serialized thread support and '
             'a 1x1x1 process grid is used. Solver settings request '
             'converge_diff=1e-12, threshold=1e-14 and at most 200 iterations. '
             'The cached native MPI/OpenBLAS setup is reused. The author '
             'matrix example was reviewed for API usage; these fixtures '
             'are independently specified. Distributed scaling, large '
             'sparse behavior, complex/indefinite/singular matrices and '
             'the separate Invert/D2 API are not verified.', '',
             '## Known interior box minima: serial QNSTOP (G2)', '',
             'Four diagonal quadratics have positive weights and known '
             'minimizers inside [-2,2] in every coordinate. Three '
             'two-variable runs use center [0.25,-0.5] from distinct '
             'starts; a three-variable run uses [-0.5,0,0.75]. '
             'The objective is sum(weights*(x-center)**2), so the '
             'unique minimum is zero at the specified center. Each '
             'run seeds the pinned GNU intrinsic generator with its '
             'recorded fixed seed.', '',
             'Mode G uses a 32-point sample design, at most 500 iterations, '
             'tau=1 and gain=10. Normal stopping status 1..3, positive '
             'evaluation count, finite results and strict box feasibility '
             'are required. Coordinates must be within 0.03 of the known '
             'minimizer, and the interior objective at most 1e-3. The '
             'returned objective must match an independent scalar sum '
             'within 1e-10*max(1,reference). These are fixed-seed '
             'accuracy smoke checks, not a global-optimum guarantee '
             'or a cross-compiler random-sequence guarantee.', '',
             'Active-bound accuracy is not verified. A separate '
             'face-minimum probe returned normal iteration-limit status '
             'but missed the 0.03 coordinate tolerance, with error about '
             '0.17212 at both 500 and 2000 iterations. Its sources and '
             'actual failed results are retained in the '
             '[candidate notes](gams-candidates/qnstop/README.md). '
             'The corner fixture in those probes was not reached. '
             'The public driver retains its original accuracy thresholds '
             'and separately verifies only the four interior fixtures. '
             'Noisy objectives, parallel QNSTOPP, active boundaries, '
             'all stopping/input modes and performance remain outside '
             'the checked scope. The author serial example was reviewed '
             'for interfaces; no upstream implementation or test code '
             'is copied.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream '
             'package licenses remain separate. Loading a link does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def dispersion_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-dispersion-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked oscillator eigenvalues and molecular dispersion',
            '',
            'These D4 and Z drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-dispersion-validation.json) records pins, source hashes and actual output. GAMS categories '
            'are not exhausted.',
            '',
            '## Bare coupled oscillators: libmbd (D4)',
            '',
            'Two oscillators have frequency pairs [1,1] or [0.5,1.5], polarizabilities [0.5,1] or [1,2], separation '
            '2, 3 or 4 bohr, and three unit orientations: [0,0,1], [0.6,0.8,0], [1,2,2]/3. Each of 36 nonperiodic '
            'fixtures is translated by [1,-2,0.5] and run both with and without eigenvectors, giving 72 Hamiltonian '
            'calls. Bare dipole coupling is used; no atom-specific screening or damping is involved.',
            '',
            'In principal coordinates the real 6x6 Hamiltonian splits into three symmetric 2x2 blocks. Their '
            'diagonals are a=omega1**2 and b=omega2**2; off-diagonals are c,c,-2*c where '
            'c=omega1*omega2*sqrt(alpha1*alpha2)/r**3. Each block has eigenvalues (a+b +/- '
            'sqrt((a-b)**2+4*coupling**2))/2. All six sorted eigenvalues are independently computed from these scalar '
            'formulas. Maximum error divided by max(1,maxabs(reference)) must be at most 1e-12. The zero-point energy '
            '0.5*sum(sqrt(eigenvalues))-1.5*sum(omega) must agree within absolute 1e-12.',
            '',
            'Scalar loops independently assemble the full oriented Hamiltonian and check H*v-lambda*v and eigenvector '
            'orthogonality within absolute 1e-12; no signs or basis choices are imposed in degenerate eigenspaces. '
            'All outputs must be finite, and library exceptions fail the driver. This checks the internal real '
            'Hamiltonian diagonalization, not a general-purpose eigensolver API. Screened/damped physical models, '
            'periodic/complex/distributed modes, unstable Hamiltonians and gradients are not verified. The driver is '
            'independently written under MIT; the package retains MPL-2.0 terms.',
            '',
            '## PBE-D4 two-body dispersion: DFT-D4 (Z)',
            '',
            'The author test_pbed4_mb01 supplies the PBE-D4 two-body damping parameters and energy reference '
            '-0.018578752883363366 Hartree. Its 16-atom MB16-43/01 geometry is reproduced unchanged from mstore '
            'v0.4.0; all 48 coordinate literals were checked against that release. The driver expands the existing '
            'catalog consumer with independent finite-difference and rigid-transformation checks. The adapted '
            'consumer retains LGPL-3.0-or-later and Apache-2.0 licenses and a geometry attribution notice.',
            '',
            'The energy must match within absolute 1e-10 Hartree. All 48 Cartesian gradient components are checked '
            'using central differences at step 1e-5 bohr, tolerance 1e-6 Hartree/bohr. Net gradient must vanish '
            'within 1e-9. Translation by [1.25,1.25,1.25] bohr and an orthogonal xy rotation with cosine/sine '
            '[0.6,0.8] must preserve energy within 1e-11 and transform gradients within 1e-9. Energy and every '
            'gradient must be finite; initialization errors fail the driver. There are 99 evaluations: base, 96 '
            'displaced, one rotation and one translation.',
            '',
            'Z marks a domain-specific molecular dispersion model. This does not verify a generic differentiation '
            'API, the physical model against experiment, other molecules, periodic systems, D4S, three-body '
            'corrections or Hessians. The published energy is an upstream regression reference, while finite '
            'differences and rigid transformations independently check gradient consistency and covariance.',
            '',
            '## Checked links and actual output',
            '',
            'Loading a link does not submit a job. License texts and attribution accompany the driver sources.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def rules_differences_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-rules-differences-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked quadrature rules and periodic finite differences',
            '',
            'These H2c and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-rules-differences-validation.json) records pins, source hashes and actual output. GAMS '
            'categories are not exhausted.',
            '',
            '## Exact polynomial moments: Kronrod (H2c)',
            '',
            'The unchanged original internal procedures are exposed through the checksum-guarded playground_kronrod '
            'catalog module. The driver independently requests Gauss orders 2,3,4,5,6,7,10 and their 2*n+1-node '
            'symmetric Kronrod extensions. The package returns the nonnegative half in descending order. Every '
            'Kronrod weight must be positive, every embedded Gauss weight nonnegative, nodes strictly ordered in '
            '[0,1), and the central node zero within 1e-50. Counting reflected nonzero Gauss weights must give '
            'exactly n nodes.',
            '',
            'Using MPFUN arithmetic, the driver checks 64 Kronrod even moments through the even portion of degree '
            '3*n+1+mod(n,2), and 37 embedded Gauss even moments through degree 2*n-2. Exact references are 2/(p+1) '
            'for integral x**p on [-1,1]. Odd moments on the symmetric interval cancel by construction and are not '
            'counted as independent checks. An additional 54 moments on [1,3] use explicitly reflected nodes 2+x and '
            '2-x; powers 0 through min(2*n-1,8), including odd powers, must match (3**(p+1)-1)/(p+1). The total is '
            '155 exact polynomial moments. Node iteration requests 1e-50; every moment error divided by '
            'max(1,abs(reference)) must be at most 1e-40. The package is configured for at least 1000 decimal digits. '
            'This does not independently validate MPFUN arithmetic, all orders, error estimators or adaptive '
            'integration.',
            '',
            'Gauss order 1 is not verified. A separate three-node probe failed even the constant integral: its '
            'weights summed to about 1.156959262120 instead of 2. Its source and actual failed result are retained in '
            'the [candidate notes](gams-candidates/kronrod/README.md). Later cases in that probe were not reached. '
            'The seven public orders were separately run and passed without relaxing the original moment tolerance. '
            'The author main normally demonstrates orders 7 through 87; the cause of the small-order failure is not '
            'established.',
            '',
            '## Fourier modes and convergence: Tsunami Chapter 4 (H1)',
            '',
            'The original serial mod_diff module returns raw differences without division by physical grid spacing. '
            'This independent consumer explicitly divides by h=2*pi/n on periodic grids of 16,32,64,128,256 cells. '
            'Ninety fixtures combine sine/cosine, wavenumbers 1,2,3 and phases 0,0.37,1.1. Grid samples are rounded '
            'to REAL32, matching the API; reference formulas and RMS error accumulation use REAL64.',
            '',
            'For a sine mode with theta=k*x+phase and q=k*h, the exact discrete centered derivative is '
            'sin(q)*cos(theta)/h and the upwind derivative is ((1-cos(q))*sin(theta)+sin(q)*cos(theta))/h. The cosine '
            'counterparts are -sin(q)*sin(theta)/h and ((1-cos(q))*cos(theta)-sin(q)*sin(theta))/h. All results must '
            'be finite. Maximum absolute discrepancy from these formulas must be at most 8*epsilon(REAL32)/h, '
            'explicitly allowing input/stencil roundoff amplification by grid spacing.',
            '',
            'Five additional nonsmooth, exactly representable dyadic fixtures check every output against '
            'independently indexed left/right neighbors, including both wraparound boundaries, and require exact '
            'telescoping sums of zero. Five constant fixtures require exact zero derivatives. Continuous '
            'sine-derivative RMS errors on successive grids must decrease with ratios in [3.8,4.2] for the centered '
            'stencil and [1.9,2.1] for the upwind stencil. This checks second-order and first-order convergence over '
            'the recorded grids; it does not promise continued refinement below REAL32 roundoff.',
            '',
            'This H1 driver does not verify PDE evolution, other chapters, coarrays, parallel scaling or nonperiodic '
            'boundaries. The ordinary package demo still illustrates wave evolution, but it is not promoted to a '
            'class-specific PDE driver by these differentiation checks.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a '
            'link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def qr_autodiff_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-qr-autodiff-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked real QR factorization and automatic differentiation',
            '',
            'These D5 and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-qr-autodiff-validation.json) records pins, source hashes and actual output. GAMS categories '
            'are not exhausted.',
            '',
            '## Rectangular real QR: linalg (D5)',
            '',
            'Row counts [1,2,4,6], column counts [1,2,3,5], four matrix patterns and scales [-4,0.5,2] give 192 '
            'matrix fixtures. The deterministic base entries are small dyadic fractions with a diagonal shift. Other '
            'patterns repeat the first column as the last when possible, set the first column to zero, or set the '
            'whole matrix to zero. Thus the fixtures include square, tall and wide matrices and rank-deficient cases; '
            'no full-rank assumption or rank estimate is made.',
            '',
            'Each fixture is factored without pivoting, with free column pivoting, and with the first input column '
            'locked: 576 QR calls. Pivot indices must form a valid permutation; the locked column must remain first. '
            'The returned permutation matrix is checked entry by entry against those indices, and the input must '
            'remain unchanged. Returned full Q and trapezoidal R must have shapes [m,m] and [m,n] and finite values.',
            '',
            'Independent scalar loops check Q*R against A(:,pivot) with maximum absolute error divided by '
            'max(1,maxabs(A)) at most 2e-12. They also check every entry of transpose(Q)*Q-I within 5e-12, and '
            'entries of R below the diagonal within normalized 1e-12. The driver does not prescribe factor signs or a '
            'particular valid ordering of free pivots. These checks verify real factorization and output invariants; '
            'they do not verify complex QR, solves, numerical rank estimation, rank-one updates or '
            'malformed-dimension behavior. The author QR example was reviewed for registration and pivot conventions; '
            'no example code is copied.',
            '',
            '## Analytical scalar derivatives, gradients and Jacobians: differentia (H1)',
            '',
            'Thirty-three scalar inputs t=i/8 for i=-16..16 exercise three functions: t**5-3*t**3+2*t-7; '
            'exp(t)*sin(t)+cos(2*t); and log(t+3)+sqrt(t+3)+1/(t+3). Hand-derived derivatives are 5*t**4-9*t**2+2; '
            'exp(t)*(sin(t)+cos(t))-2*sin(2*t); and 1/z+0.5/sqrt(z)-1/z**2 with z=t+3. Both function values and '
            'derivatives are checked, giving 99 scalar calls. All logarithm/square-root arguments are positive and '
            'bounded away from zero.',
            '',
            'At 33 three-variable inputs the coupled scalar x1**2*x2+sin(x3)+exp(x1-x2) is checked against gradient '
            '[2*x1*x2+e,x1**2-e,cos(x3)], where e=exp(x1-x2). This adds 33 gradient calls. The input vectors are '
            '[i/8,(modulo(i,7)-3)/4,(modulo(i,5)-2)/3].',
            '',
            'The vector map [x1*x2+sin(x3),exp(x1)+x2**2-x3,x1/(x3+4)+cos(x2)] has analytical Jacobian rows '
            '[x2,x1,cos(x3)], [exp(x1),2*x2,-1], [1/(x3+4),-sin(x2),-x1/(x3+4)**2]. Every vector value and all nine '
            'entries are checked first with a temporary workspace and again with one reused dense workspace, giving '
            '66 Jacobian calls. All results must be finite, with error divided by max(1,abs(reference)) at most '
            '2e-12. These are automatic derivatives of dual-number callbacks, not finite differences.',
            '',
            'Before the valid evaluations, a length-two gradient output for three inputs and a length-two vector '
            'output for the square three-input Jacobian must each return an allocated error. Workspace construction '
            'and subsequent valid calls must clear those errors and succeed. Module callbacks avoid nested callback '
            'state. Sparse Jacobians, all intrinsic overloads, nonsmooth points, higher derivatives and every failure '
            'mode remain unverified. The separate forwarddiff catalog alias and each linalg sibling algorithm require '
            'their own matching driver; the QR and AD drivers do not supply execution evidence for them.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a '
            'link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def dense_spectra_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-dense-spectra-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked dense real eigenproblems and singular-value decompositions',
            '',
            'These D4a1 and D6 linalg drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
            'reusing existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-dense-spectra-validation.json) records pins, source hashes and actual output. GAMS '
            'categories are not exhausted.',
            '',
            '## Known real symmetric eigenvalues: linalg (D4a1)',
            '',
            'Ninety-six fixtures combine dimensions 1,2,3,5; four prescribed spectra; signed scales [-4,0.5,2]; and '
            'identity or Householder mixing. The unscaled spectra are 2*i-n-1, constant 2, i-1, and all zero. A '
            'Householder factor Q=I-2*v*transpose(v)/dot(v,v), with v=[1,2,...,n], supplies an independently known '
            'orthogonal basis. Scalar loops construct A=Q*diag(d)*transpose(Q), so the sorted prescribed d are the '
            'exact mathematical eigenvalues of each fixture. Repeated eigenvalues, singular matrices, indefinite '
            'matrices and zero matrices are included.',
            '',
            'Each fixture is evaluated with eigenvalues only and with eigenvectors: 192 calls. The API uses the lower '
            'triangle. To check this contract, every unused upper-triangle entry is replaced with a large, finite, '
            'asymmetric sentinel before the call; residual references retain the full symmetric A. Both calls must '
            'preserve that input, return correctly shaped finite outputs, and match sorted prescribed eigenvalues '
            'with maximum error divided by max(1,maxabs(d)) at most 2e-12. Scalar loops check A*v-lambda*v within '
            'normalized 5e-12 and transpose(V)*V-I within absolute 5e-12. No signs or particular bases are prescribed '
            'in repeated eigenspaces.',
            '',
            'This verifies the real symmetric standard eigenproblem. Generalized, nonsymmetric, complex and sparse '
            'overloads, malformed inputs, large matrices, difficult conditioning and performance are not verified. '
            'The API has no returned status in this invocation; acceptance is based on answers, shapes, preservation '
            'and finite-value checks.',
            '',
            '## Known rectangular singular values: linalg (D6)',
            '',
            'Six shapes [1,1], [2,3], [3,2], [3,3], [4,2], [2,5] combine with four prescribed spectra, signed scales '
            '[-4,0.5,2], and identity/Householder factors: 144 fixtures. For k=min(m,n), spectra are k-i+1, constant '
            '2, [3,0,...,0], and all zero. Independent scalar loops construct A=L(:,1:k)*diag(d)*transpose(R(:,1:k)) '
            'using known orthogonal factors; its prescribed singular values are abs(d), already in descending order.',
            '',
            'Each matrix is evaluated in full-factor, values-only, U-only and VT-only modes: 576 calls. The driver '
            'checks output shapes, finite values, unchanged input, descending nonnegative singular values and error '
            'divided by max(1,maxabs(d)) at most 2e-12. When both factors are returned, scalar sums reconstruct every '
            'entry of U*diag(s)*VT within normalized 5e-12. Every returned U column and VT row must be orthonormal '
            'within 5e-12.',
            '',
            'Independent scalar products additionally check (A*transpose(A))*u=s**2*u and (transpose(A)*A)*v=s**2*v '
            'for every returned vector, including one-sided modes and full-storage null vectors with zero reference '
            'eigenvalue. Maximum residual divided by max(1,maxabs(d))**2 must be at most 1e-11. These checks avoid '
            'arbitrary vector signs and basis choices for repeated or zero singular values. Complex decompositions, '
            'invalid inputs, large/ill-conditioned cases and performance are outside the verified scope.',
            '',
            '## Reproduced fortran-lapack link-size limit',
            '',
            'Initial high-level fortran-lapack eigh and svd consumers compiled their mains but failed during linking '
            'with process signal 25 and "File size limit exceeded". This reproduces the [previously documented '
            'high-level link limit](gams-linear-algebra.md#observed-high-level-link-limit); it is not a numerical '
            'result. The new sources and actual failures are saved in the [candidate '
            'notes](gams-candidates/fortran-lapack/README.md). Neither probe ran, and neither high-level procedure '
            'receives a checked-driver designation. Existing lower-level fortran-lapack syev/gesvd demonstrations and '
            'their independent evidence remain separate. No sandbox limit, backend or package recipe was changed. The '
            'public linalg drivers above are separate consumers with successful execution evidence.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a '
            'link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def least_interpolation_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-least-interpolation-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked full-rank least squares and one-dimensional interpolation',
            '',
            'These D9a1 and E1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-least-interpolation-validation.json) records pins, source hashes and actual output. GAMS '
            'categories are not exhausted.',
            '',
            '## Prescribed least-squares solutions and residuals: linalg (D9a1)',
            '',
            'Seventy-two fixtures combine shapes [1,1], [2,1], [3,2], [5,3], [2,3], [3,5]; signed scales [-4,0.5,2]; '
            'identity/Householder factors; and two residual settings. Let k=min(m,n). Scalar sums construct '
            'A=L(:,1:k)*diag(d)*transpose(R(:,1:k)), with d(i)=i*scale and known orthogonal L/R. For each of three '
            'right-hand sides c, z(i)=(2*i-c)/4 and x_star=R(:,1:k)*z. The right-hand side is b=A*x_star+noise. Noise '
            'is zero for the first residual setting and for square/underdetermined systems; in the second '
            'overdetermined setting it is 0.25*c*L(:,n+1). Thus 18 fixtures have prescribed nonzero residuals. '
            'Settings coincide when a nonzero orthogonal residual is unavailable; the count describes evaluations, '
            'not 72 distinct matrices.',
            '',
            "All matrices have full rank. For tall systems the noise is orthogonal to A's columns, so x_star is the "
            'unique least-squares minimizer and the exact residual is -noise. For wide systems b is consistent and '
            "x_star lies in A's row space, so it is the unique minimum-norm solution. Each three-column matrix solve "
            'is checked alongside three separate vector solves: 288 solver calls. The author API is source-reviewed; '
            'no matching author example is recorded for this procedure, so these fixtures and references are '
            'independently constructed.',
            '',
            'Every solution must have the expected shape and finite values, and must match x_star within '
            'maximum-entry error divided by max(1,maxabs(x_star)) of 3e-12. Inputs must remain unchanged. Scalar '
            'products independently reconstruct A*x-b; it must equal -noise within max-entry error divided by '
            'max(1,maxabs(b)) of 5e-12. Squared residual norms must match (rho*c)**2 with absolute error divided by '
            'max(1,(rho*c)**2) at most 1e-11. Normal-equation products transpose(A)*(A*x-b) must be at most 1e-11 '
            'after division by max(1,maxabs(b))*max(1,maxabs(A)). Both exact-fit and nonzero-residual cases are '
            'checked. Rank-deficient, complex, malformed-input and large/ill-conditioned systems, alternative '
            'least-squares APIs and performance remain unverified.',
            '',
            '## Affine exactness and shape-preserving cubics: interpolation (E1a)',
            '',
            'Two five-knot grids are [-2,-1,0,1,2] and [-2,-1.5,-0.25,0.5,2]. For each grid, methods linear, pchip '
            'and its cubic alias interpolate three affine components with slopes [2,-0.75,0] and offsets [1,2,-3] at '
            '41 queries on [-2,2]. All four combinations of scalar/vector tabulated quantities and scalar/vector '
            'queries are checked. Explicit extrapolation at -3 and 3 must reproduce those affine functions; the '
            'default behavior at the same outside points must instead return NaN. There are 2,988 exact affine '
            'references and 36 explicit NaN checks.',
            '',
            'PCHIP is then sampled at 129 queries on each grid for the plateau profile [0,1,1,2,3], the turning '
            'profile [0,2,-1,3,1], and their negatives. Every sample must be finite and lie between its independently '
            'identified bracketing data values, within 2e-12. Both signs of the plateau profile must remain monotone. '
            'These give 1,032 interval-bound checks and 512 adjacent monotonicity checks; all five knots for each of '
            'eight profiles add 40 exact references.',
            '',
            'An explicit nonlinear reference uses [0,1,0] at [0,1,2]. This package uses endpoint secant slopes and a '
            'zero slope at the middle peak. On [0,1], the Hermite constraints give f(t)=-t**3+t**2+t; on [1,2] the '
            'function is its reflection f(2-t). Both pchip and cubic must reproduce that polynomial at 129 points, '
            "adding 258 exact references. The endpoint convention is part of this pinned package's checked behavior; "
            'no equivalence to every other PCHIP implementation is claimed.',
            '',
            'In total 3,286 exact values must be finite and agree within error divided by max(1,abs(reference)) of '
            '2e-12. The fixture does not independently certify error bounds for arbitrary smooth functions, nonlinear '
            'extrapolation, malformed or unsorted input, the interpolator class interface or every possible shape. '
            'Author tests were reviewed for public API and boundary behavior; no upstream code is copied.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Loading a '
            'link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def rkf_qags_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-rkf-qags-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked RKF45 initial-value integration and adaptive quadrature',
            '',
            'These I1a1a and H2a1a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-rkf-qags-validation.json) records pins, source hashes and actual output. GAMS categories '
            'are not exhausted.',
            '',
            '## Forward and backward analytical IVPs: RKF45 (I1a1a)',
            '',
            'Twenty-four two-variable runs combine three nonstiff problem families, rates a=0.25 or 1, two initial '
            'states, and both time directions. Frequencies w=1 or 3 accompany the two rates. Each run integrates from '
            '-0.5 to 1.5 or from 1.5 to -0.5, with 16 equally spaced requested targets and continued solver state: '
            '384 calls. Every run resets the work arrays, initial flag and callback counter. The pinned package must '
            'provide at least 15 decimal digits of real precision.',
            '',
            "Family 1 is damped rotation: y1'=-a*y1-w*y2, y2'=w*y1-a*y2. Its exact solution is exp(-a*(t-t0)) times "
            'rotation by w*(t-t0) of the initial vector [1,-0.5] or [-0.25,2]. Its squared norm must also follow the '
            'independently known decay law norm(y0)**2*exp(-2*a*(t-t0)).',
            '',
            "Family 2 is a manufactured nonautonomous tracking system y'=-a*(y-g(t))+g'(t), with "
            'g=[sin(w*t)+t*t,cos(w*t)+t]. Its exact solution is g(t)+exp(-a*(t-t0))*offset, for offsets [0.25,-0.5] '
            'or [-0.75,0.125]. The implemented right-hand side explicitly differentiates g; the solution reference '
            'uses the separate exponential correction.',
            '',
            'Family 3 contains two independent logistic equations with rates a and a/2, starting at [0.25,0.75] or '
            '[0.1,0.6]. The exact component is p/(p+(1-p)*exp(-rate*(t-t0))). Both components must remain strictly '
            'between zero and one throughout forward and backward runs.',
            '',
            'Every requested target must return normal flag 2, finite states and time within '
            '16*epsilon(t)*max(1,abs(target)). Relative and absolute tolerance requests are 1e-10 and 1e-12. Maximum '
            'state error divided by max(1,maxabs(exact_state)) must be at most 5e-8; the normalized damped-rotation '
            'norm error must be at most 1e-7. The callback must actually be evaluated in every run. These are answer '
            'checks, not a claim that every returned global error obeys the local tolerance request. Stiff equations, '
            'single-step mode, warning recovery, all tolerance regimes, long trajectories and performance remain '
            'unverified.',
            '',
            '## Analytical finite-interval QAGS integrals: FGSL (H2a1a1)',
            '',
            'Twenty integrals are each evaluated at two absolute/relative tolerance pairs, both 1e-7 and both 1e-10: '
            '40 calls. The five families are:',
            '',
            '- x**p on [0,1], for p=-0.5,-0.25,0.5,2,5, with integral 1/(p+1).',
            '- x**p*log(x) on [0,1] for the same p, with integral -1/(p+1)**2. The negative powers and logarithm '
            'exercise integrable endpoint singularities.',
            '- 1/(1+(p*x)**2) on [-2,3], for p=0.5,1,2, with integral (atan(3*p)-atan(-2*p))/p.',
            '- exp(p*x) on [-1,2], for p=-1,0.5,2, with integral (exp(2*p)-exp(-p))/p.',
            '- sin(p*x) on [0,pi], for p=1,3,5,16, with integral (1-cos(p*pi))/p; the last case checks a '
            'cancellation-dominated zero integral.',
            '',
            'One 1000-subinterval workspace and one C-interoperable callback handle are reused across all cases. A '
            'BIND(C) settings object passes the changing family and parameter through C_LOC/C_F_POINTER; its target '
            'remains alive until the handle is freed. Both the function handle and workspace are released after all '
            "calls. The package's pinned GNU/Linux LP64 configuration and C support are reused.",
            '',
            'Every call requires success status and at least one callback evaluation. Value and estimated absolute '
            'error must be finite. Error divided by max(1,abs(exact_integral)) must be at most 5 times the requested '
            'tolerance. The reported estimate must be nonnegative and no larger than max(epsabs,epsrel*abs(value)), '
            "allowing additive roundoff of 32*epsilon(value)*max(1,abs(value)). This verifies the estimate's "
            'consistency with the requested stopping budget; it does not establish a rigorous upper bound on actual '
            'error. Arbitrary singularities, infinite intervals, invalid-input recovery, every GSL integration '
            'strategy, other FGSL interfaces and performance are outside the checked scope.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading '
            'a link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def jacobian_roots_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-jacobian-roots-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked Jacobian-based nonlinear least squares and scalar Newton methods',
            '',
            'These G1b1b and F1b drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing '
            'existing package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-jacobian-roots-validation.json) records pins, source hashes and actual output. GAMS '
            'categories are not exhausted.',
            '',
            '## User-Jacobian nonlinear fits: MINPACK lmder1 (G1b1b)',
            '',
            'Twenty-four exact-data fits use five residuals f_i(a,b)=a*exp(b*t_i)-a0*exp(b0*t_i), with '
            't=[-1,-0.5,0,0.5,1]. Known amplitudes a0=0.5 or 2, exponents b0=-1,0.25,1 and four starting combinations '
            'a/a0=0.5 or 1.5, b-b0=-0.5 or 0.5 give the 24 cases. The supplied residual-Jacobian columns are '
            'exp(b*t_i) and a*t_i*exp(b*t_i). The unique exact solution is [a0,b0]; it yields zero residual and hence '
            'a global least-squares minimum.',
            '',
            'Sixteen nonzero-residual fits use f_i(a,b)=exp(a)-2+t_i*(b**3-1)+rho*q_i, with t=[-2,-1,0,1,2] and '
            'q=[1,-2,2,-2,1]. The q vector is orthogonal to both the constant and t vectors, whose squared norms are '
            '5 and 10; norm(q)**2=14. Consequently the exact squared objective is '
            '5*(exp(a)-2)**2+10*(b**3-1)**2+14*rho**2. Its unique global minimizer is [log(2),1], with minimum '
            '14*rho**2. Four rho values [-0.5,-0.125,0.125,0.5] and starts a=log(2)+/-0.7, b=0.5 or 1.5 give 16 fits. '
            'Starting at the flat b=0 stationary point is outside this checked scope.',
            '',
            'Before each fit, both analytical Jacobian columns are checked by central differences with step '
            '1e-5*max(1,abs(start_parameter)). Maximum entry discrepancy in a column divided by '
            'max(1,maxabs(analytical_column)) must be at most 2e-7: 400 entries across 40 starting points. This '
            'independently checks the user-supplied derivatives before testing lmder1. The solver receives tolerance '
            '1e-12 and correctly sized real/integer work arrays; both residual iflag=1 and Jacobian iflag=2 callbacks '
            'must actually be used.',
            '',
            'Acceptance requires normal stopping info in 1..4, finite parameters and residuals, and maximum parameter '
            'error divided by max(1,maxabs(expected_parameters)) at most 2e-7. Recomputed and returned residuals must '
            'agree within 1e-11. Squared residual norm must equal the known minimum with error divided by '
            'max(1,minimum) at most 1e-10. Maximum absolute component of transpose(J)*f must be at most 1e-6. '
            'Exact-data fits must additionally have maximum absolute residual at most 1e-8. G1b1b here describes '
            'nonlinear least squares with user residual Jacobians; the interface does not accept a general '
            'scalar-objective gradient. These fixtures establish successful solutions at the recorded starts, not a '
            'global convergence guarantee. Rank deficiency, arbitrary data noise, malformed inputs, every stopping '
            'mode and performance remain unverified.',
            '',
            '## Three Newton configurations with prescribed roots: forsolver (F1b)',
            '',
            'Ninety-six fixtures combine three functions of u=x-center, four prescribed roots center=[-2,0,0.5,3], '
            'scales [0.5,2] and starting offsets [-2,-0.5,0.5,2]. The functions are scale*(u+u**3), scale*(exp(u)-1), '
            'and scale*(u+0.25*sin(u)). Each has exactly one real root, u=0: its derivative is strictly positive '
            'everywhere. Analytic derivatives are scale*(1+3*u*u), scale*exp(u), and scale*(1+0.25*cos(u)). Real and '
            'complex callbacks implement the same analytic expressions.',
            '',
            'Each fixture is solved using analytic-derivative Newton, central-finite-difference Newton with step '
            'setting 1e-6, and complex-step Newton with setting 1e-20: 288 solves. All use maxit=100, TolFun=1e-12 '
            'and verbosity=0. Callback counters must show the required real/derivative or complex evaluation '
            'occurred. The complex root must have finite real and imaginary parts and imaginary magnitude at most '
            '1e-12.',
            '',
            'Every real root must be finite and agree with the prescribed center within error divided by '
            'max(1,abs(center)) of 1e-9. Its residual divided by max(1,abs(scale)) must be at most 1e-10. The three '
            'methods must agree within normalized spread 1e-9. Agreement alone is insufficient: all methods '
            'independently face the known-root and residual tests. The invoked API has no returned convergence-status '
            'value, so these are answer-based checks. Vector systems, arbitrary complex roots, derivative '
            'singularities, failure recovery, global convergence and performance remain outside the verified scope.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading '
            'a link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)



def higher_ad_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-higher-ad-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked higher-order complex derivatives and polynomial Hessians',
            '',
            'These H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing '
            'package libraries. Only their mains and executables were compiled. The [verification '
            'report](gams-higher-ad-validation.json) records pins, source hashes and actual output. GAMS categories '
            'are not exhausted.',
            '',
            '## Complex univariate derivatives through order five: DNAOAD-FPM',
            '',
            'Fifteen sample points combine real parts [-1,-0.25,0,0.5,1] and imaginary parts [-0.5,0,0.25]. At every '
            'point, requested derivative order ranges from zero through five. Each dual variable is initialized with '
            'the sample as its value, unit first derivative when present, and zero higher seed derivatives. The '
            'pinned configuration supports at least order five and at least 15 decimal digits of real precision. All '
            'resulting expressions must retain the requested order.',
            '',
            'Three scaled transcendental cases use exp(a*z)+sin(b*z), with (a,b)=[(0.5,-2),(1,0.5),(2,1)]. The k-th '
            'exact derivative is a**k*exp(a*z) plus b**k times the sine/cosine cycle sin(b*z), cos(b*z), -sin(b*z), '
            '-cos(b*z). This yields 945 derivative references across all sample points and requested orders, '
            "including each expression's value.",
            '',
            'The composed expression exp(z*z+z) tests nonlinear chain rules. Let u=2*z+1. Its k-th derivative is '
            'exp(z*z+z) times the finite polynomial sum over j=0..floor(k/2) of k!/(j!*(k-2*j)!)*u**(k-2*j). These '
            'independently computed factors give another 315 references. The degree-five polynomial z**5-2*z**3+3*z+1 '
            'is evaluated through repeated dual multiplications; exact derivatives use scalar coefficients and '
            'falling factorials, adding 315 references. Zero input values and derivatives above the degree of '
            'individual terms are included.',
            '',
            'There are 450 dual expressions and 1,575 exact complex references. Every actual real and imaginary '
            'component must be finite. Complex absolute error divided by max(1,abs(reference)) must be at most 2e-11. '
            'This verifies complex analytic univariate derivatives at the recorded points and requested orders, '
            'including product/chain rules. It does not verify orders beyond five, multivariate derivatives, '
            'nonanalytic operations, singular branches, malformed input or performance.',
            '',
            '## Forward/reverse gradients and Hessians: diffstruc',
            '',
            'The independent three-variable polynomial is f(x)=x1**3+x1*x2+x2*x3**2+x3**2. Its gradient is '
            '[3*x1**2+x2,x1+x3**2,2*(x2+1)*x3]. The symmetric Hessian has rows [6*x1,1,0], [1,0,2*x3], '
            '[0,2*x3,2*(x2+1)]. Five exactly representable dyadic points are [0.5,-1,2], [-0.75,0.5,1.25], [0,0,0], '
            '[2,-0.5,-1], [1,2,-2]. The fixtures exercise repeated appearances of inputs, mixed terms, vanishing '
            'derivatives and nonzero off-diagonal Hessian entries.',
            '',
            'At each point six forward passes use the three coordinate basis directions, [1,-2,0.5], [-0.5,0,2], and '
            '[0,0,0]. Every directional derivative must equal the independent gradient dot direction. The full '
            '[1,1,1] direction mask is restored before reverse accumulation. One reverse pass checks the gradient of '
            'f, and three reverse passes through the coordinate forward-derivative graphs check every Hessian entry. '
            'Gradient buffers are reset for every reverse pass, and Hessian symmetry is checked separately.',
            '',
            'There are 30 forward calls, 20 reverse calls and 95 exact scalar references: five values, 30 directional '
            'derivatives, 15 reverse-gradient components and 45 Hessian entries. Expression, derivative and gradient '
            'pointers must be associated before access, and actual values must be finite. Scalar errors divided by '
            "max(1,abs(reference)) must be at most 1e-5 at the package's REAL32 precision; absolute Hessian symmetry "
            'error must also be at most 1e-5. The references are hand-derived formulas, so agreement between AD modes '
            'alone cannot pass the driver.',
            '',
            'All graphs are retained for the lifetime of this short standalone process. Graph disposal, long-lived '
            'graph reuse, memory scaling, arbitrary expressions/intrinsics, nonsmooth functions and performance are '
            'not verified. The example demonstrates the recorded forward/reverse calls and Hessian calculation, not a '
            'general graph-lifecycle prescription.',
            '',
            '## Checked links and actual output',
            '',
            'These independent API consumers have their own MIT notice; upstream terms remain separate. Author '
            'sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading '
            'a link does not submit a job.',
            '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        links = (f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                 f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]})')
        if d['author_example']:
            links += f' / [Author example/test]({base}{d["author_example"]})'
        lines += ['### '+d['id'], '', links, '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def moments_nufft2d_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-moments-nufft2d-validation.json']
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    records = {p['id']: p for p in data['procedure_mappings']}
    lines = ['# Checked quadrature moments and two-dimensional Fourier sums', '',
             'These H2c and J1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, '
             'reusing existing package libraries. Only their mains and executables were compiled. The '
             '[verification report](gams-moments-nufft2d-validation.json) records pins, source hashes and '
             'actual output. GAMS categories are not exhausted.', '',
             '## Exact moments: QDUtilLib (H2c)', '',
             'Orders 1,2,3,4,6,8,12 for LegendreP and HO give 14 rules. Initialization must succeed and '
             'return finite nodes/weights of shape [1,n] and [n], with positive weights. Legendre nodes '
             'must be strictly inside [-1,1]. Copied node/weight pairs are sorted before checking symmetry; '
             'native ordering is not prescribed. Paired node sums must be at most '
             '1e-11*max(1,maxabs(nodes)); paired effective-weight differences must be at most '
             '1e-11*max(1,maxabs(weights)).', '',
             'Legendre moments through degree 2*n-1 have exact references zero for odd powers and 2/(p+1) '
             'for even powers. HO stores full-function weights: the consumer explicitly includes '
             'exp(-x*x) to obtain Gaussian polynomial moments on the real line. Odd Gaussian moments '
             'vanish; even references start at M0=sqrt(pi), with Mp=(p-1)*M(p-2)/2. These analytical '
             'recurrences are independent of the generated rule.', '',
             'There are 144 Legendre/Gaussian moments. Another 47 shifted Legendre moments use '
             '(x+2)**p for p=0..min(2*n-1,8), with exact integral (3**(p+1)-1)/(p+1). All 191 sums '
             'must be finite and satisfy abs(actual-reference)/max(1,abs(reference),sum(abs(weighted_terms))) '
             '<=5e-11. Scaling by absolute contributions accounts for cancellation of large odd Gaussian '
             'terms. After every rule, deallocation must release the public node/weight arrays. Other '
             'rule families, arbitrary weighted integrals, adaptive integration, invalid inputs and '
             'performance are not verified.', '',
             '## Direct nonuniform Fourier sums: NUFFT2D (J1)', '',
             'Source counts [8,31,64], mode grids [8,10], [9,11], [16,18], four point/strength patterns, '
             'both exponent signs and tolerance requests 1e-7/1e-10 give 144 transforms. Integer mode '
             'ranges are -ms/2..(ms-1)/2 and -mt/2..(mt-1)/2. All 22,416 coefficients are checked.', '',
             'Scattered points use x_j=pi*sin(0.71*j), y_j=pi*cos(0.43*j), with strengths '
             'cos(0.13*j)+i*sin(0.17*j). Coincident points are all at the origin. A repeated near-boundary '
             'pattern uses x=+/-(pi-1e-6) and y cycling through -pi/2,0,pi/2. A fourth pattern uses '
             'scattered points with zero strengths. Exact +/-pi endpoints are not included.', '',
             'Independent scalar loops form F(k,l)=sum_j c_j*(cos(phase)+i*sin(phase))/nj before calling '
             'the library, with phase=sign*(k*x_j+l*y_j). The 1/nj normalization is checked separately '
             'at the DC mode. Each call requires success, finite complex coefficients and unchanged '
             'coordinates/strengths. Maximum complex error divided by max(1,maxabs(direct_reference)) '
             'must be at most 50 times the requested tolerance. Zero strengths must give exactly zero '
             'coefficients.', '',
             'The existing checksum-guarded legacy extent-one FFT dummy-array adapter is reused unchanged. '
             'No formulas, local arrays or library build settings change. Type-2/type-3 transforms, '
             'the static Fortran 77 interface, every FFT path, exact periodic endpoints, large grids '
             'and performance remain unverified. Direct-sum agreement does not establish a speed ranking.', '',
             '## Checked links and actual output', '',
             'These independent API consumers have their own MIT notice; upstream terms remain separate. '
             'Author sources were reviewed for interfaces; no upstream code is copied. Loading a link '
             'does not submit a job.', '']
    for d in drivers:
        evidence = records[d['procedure_id']]['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author example/test]({base}{d["author_example"]})', '']
        report = json.loads((root/driver_validation_path(d)).read_text(encoding='utf-8'))
        result = next(r for r in report['drivers'] if r['driver_id'] == d['id'])
        output = next(s['stdout'] for s in result['stages'] if s['name'] == 'Run')
        lines += ['```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def iterative_ls_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-iterative-ls-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-iterative-ls-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked iterative least squares: LSQR and LSMR', '',
             'Both D9a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
             'Existing package libraries were reused; only mains and executables were compiled. '
             'The [verification report](gams-iterative-ls-validation.json) retains source hashes, '
             'immutable revisions and actual output. GAMS categories are not exhausted.', '',
             '## Shared mathematical fixtures', '',
             'Each driver makes 216 vector solves across 72 fixtures. Matrix shapes are '
             '[1,1], [2,1], [3,2], [5,3], [2,3], [3,5]. Signed scales are -4, 0.5, 2; '
             'left/right orthogonal factors are identity or Householder reflections '
             'Q=I-2*v*vT/(vT*v), with v=[1,...,dimension]. Two residual settings and three '
             'right-hand sides are used. Some settings coincide for square/wide matrices; '
             '72 counts fixtures, not distinct matrices.', '',
             'With k=min(m,n), construct A=L(:,1:k)*diag(scale*[1,...,k])*R(:,1:k)T. '
             'For right-hand side c=1,2,3, set z_i=(2*i-c)/4 and '
             'x_reference=R(:,1:k)*z. Then b=A*x_reference+noise. Noise is zero except for '
             '18 tall fixtures, where noise_c=0.25*c*L(:,n+1). Orthogonality makes the '
             'reference the unique tall least-squares solution and the wide minimum-norm solution. '
             'It also gives residual A*x-b=-noise and squared residual norm (0.25*c)**2 '
             'in those tall fixtures. References are constructed before invoking either solver, '
             'rather than obtained from another numerical solver. These are also the fixtures used '
             'in the [linalg least-squares review](gams-least-interpolation.md).', '',
             '## Checks and interfaces', '',
             'Every solution must be finite. Maximum coordinate error divided by '
             'max(1,maxabs(x_reference)) must be <=3e-12. Prescribed residual error is scaled '
             'by max(1,maxabs(b)) and must be <=5e-12. The normal-equation residual A^T*(A*x-b), '
             'scaled by max(1,maxabs(b))*max(1,maxabs(A)), must be <=1e-11. The known squared '
             'residual norm has normalized tolerance 1e-11. Matrices and right-hand sides must '
             'remain unchanged. Accepted stop codes are 0,1,2, alongside all accuracy checks; '
             'zero solutions occur explicitly. Iterations must be between 0 and 100.', '',
             'LSQR uses lsqr_solver_ez with column-major coordinate triples, reinitializing '
             'the object for each solve. LSMR uses separate forward/transpose additive '
             'matrix-product callbacks and no local reorthogonalization. Both use zero damping, '
             'atol=btol=1e-12, conlim=1e8 and iteration limit 100. No library edits are made.', '',
             'These small, full-rank fixtures check answers, not speed or large sparse scalability. '
             'Rank deficiency, severe ill conditioning, damping/regularization, error estimates, '
             'invalid inputs and performance remain unverified. Sibling procedures require their '
             'own class-specific evidence.', '',
             '## Checked links and actual output', '',
             'The independently written API consumers have their own MIT notice. Upstream '
             'terms remain separate. Pinned procedures and author tests were reviewed for the '
             'interfaces; no upstream code was copied. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author test]({base}{d["author_example"]})', '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def spectral_wrappers_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-spectral-wrappers-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-spectral-wrappers-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked real spectra: forsvd and foreig', '',
             'These D6 and D4a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
             'Existing package libraries were reused; only mains and executables were compiled. '
             'The [verification report](gams-spectral-wrappers-validation.json) retains pins, source '
             'hashes and actual output. GAMS categories are not exhausted.', '',
             '## forsvd: reduced real SVD (D6)', '',
             'The shapes [1,1], [2,3], [3,2], [3,3], [4,2], [2,5], four spectra, signed scales '
             '-4, 0.5, 2 and identity/Householder factors give 144 matrix fixtures. Each is solved '
             'using the default method, explicit gesvd and explicit gesdd: 432 decompositions. '
             'Some degenerate settings coincide; the count is fixtures, not distinct matrices.', '',
             'Let k=min(m,n). Before calling the library, construct '
             'A=L(:,1:k)*diag(d)*R(:,1:k)T. L and R are identity or '
             'Q=I-2*v*vT/(vT*v), v=[1,...,dimension]. Before signed scaling, spectra are '
             '[k,...,1], all twos, rank one [3,0,...,0], and all zeros. Exact singular values '
             'are abs(scale) times these descending nonnegative values. These are the same '
             'matrix fixtures as the [linalg SVD review](gams-dense-spectra.md).', '',
             'Caller storage is U(m,m), VT(n,n), S(k), matching the pinned author test and wrapper '
             'leading dimensions. Only the returned reduced factors U(:,1:k), VT(1:k,:) are '
             'checked. Extra rows/columns are not claimed to be full null-space bases. Finite '
             'singular values must be nonnegative, descending and within normalized error 2e-12 '
             'of the prescribed spectrum. Independent scalar loops check A=U*diag(S)*VT '
             '(normalized tolerance 5e-12), reduced column/row orthogonality (absolute 5e-12), '
             'and A*A^T*u=s**2*u / A^T*A*v=s**2*v (normalized 1e-11). Value and reconstruction '
             'errors use max(1,maxabs(d)); squared-operator residuals use its square.', '',
             'The driver passes a fresh input copy for every call: the pinned wrapper declares '
             'INTENT(IN) but passes the array directly to destructive LAPACK routines. Input '
             'preservation is therefore not claimed. This consumer workaround does not correct '
             'the upstream declaration. Default and explicit GESVD calls intentionally exercise '
             'both dispatch paths; agreement between methods is not used as the reference.', '',
             '## foreig: real symmetric eigenproblem (D4a1)', '',
             'Sizes 1,2,3,5, four spectra, signed scales -4, 0.5, 2 and identity/Householder '
             'factors give 96 fixtures and 96 explicit method=syev calls. Before scaling, '
             'diagonal spectra are d_i=2*i-n-1, all twos, d_i=i-1, and all zeros. Construct '
             'A=Q*diag(d)*Q^T and independently sort d for exact ascending eigenvalues. '
             'The eigenvalue normalization is max(1,maxabs(d)). Repeated spectra, negative '
             'eigenvalues and zero matrices allow arbitrary valid eigenspace bases.', '',
             'Finite poison 1000+17*i+31*j replaces every lower-triangle entry of the input. '
             'The symmetric reference remains separate; this checks that SYEV uses the upper '
             'triangle. The input including poison must remain unchanged. Returned values and '
             'vectors must have the expected shape and be finite. Maximum normalized eigenvalue '
             'error must be <=2e-12; independent scalar A*v-lambda*v residuals must be <=5e-12 '
             'after normalization. Orthonormality uses absolute tolerance 5e-12. These use the '
             'same spectral fixtures as linalg, with the opposite unused triangle poisoned.', '',
             '## Scope', '',
             'Neither wrapper exposes LAPACK INFO; no status-code check is possible. Independent '
             'answer/factor identities determine success. Workspace-query internals, malformed '
             'inputs, complex overloads, severe ill conditioning, full SVD null spaces, low-rank '
             'image compression, nonsymmetric/generalized eigenproblems and performance are '
             'not verified. No backend changes or library patches were made.', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own MIT notice; upstream '
             'terms remain separate. Pinned sources and author tests were reviewed for interfaces, '
             'without copying upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / '
                  f'[Author test]({base}{d["author_example"]})', '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def regrid_rk45_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-regrid-rk45-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-regrid-rk45-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked regridding and adaptive RK45', '',
             'These E1a and I1a1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-regrid-rk45-validation.json) retains '
             'pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## REGRIDPACK: one-dimensional linear/cubic interpolation (E1a)', '',
             'Grid sizes 4,7,12 use x_i=-2+5*t_i or -2+5*t_i**2, '
             't_i=(i-1)/(n-1). Each target grid includes original nodes, quarter/half/three-quarter '
             'points of every interval and a repeated final endpoint: 4*n-2 targets. '
             'Signed function scales are -2, 0.5, 3.', '',
             'Linear interpolation checks monomials of degrees 0..1; cubic interpolation checks '
             'degrees 0..3, directly against scale*target**degree. These give 108 calls. Another '
             '18 linear calls use quadratic source values and independent interval-location loops '
             'with (1-f)*y_i+f*y_(i+1) as the reference. This separately checks piecewise-linear '
             'behavior on nonaffine data. Every successful result must be finite, return status zero '
             'and preserve source coordinates, source values and target coordinates. Maximum value '
             'error divided by max(1,maxabs(reference)) must be <=2e-12.', '',
             'Eight deliberately rejected requests check size mismatch (10), unsupported interpolation '
             'mode (6), insufficient source nodes for linear/cubic methods (2), targets below/above '
             'the source interval (3), repeated source coordinates (4) and descending targets (4). '
             'Failed output arrays are not inspected. A final cubic affine recovery call checks '
             'two known values within absolute error 1e-12. In total there are 127 successful calls '
             'and 3,614 analytical value checks, plus eight rejected requests. Multidimensional '
             'overloads, low-level caller workspaces, arbitrary-function accuracy, unsorted-target '
             'support and extrapolation are not verified; extrapolation is deliberately rejected.', '',
             '## diffeq: Dormand-Prince RK45 (I1a1a)', '',
             'Three two-component analytical IVPs, rates r=0.5,2, forward/backward integration '
             'over [0,2], and absolute/relative tolerance pairs 1e-8 and 1e-10 give 24 runs. '
             'Each requests 17 equally spaced times, giving 408 checked solution points. '
             'With s=r*t, exact solutions are:', '',
             '- Exponentials: y=[exp(s),2*exp(-s)], with RHS r*[y1,-y2].',
             '- Polynomial: y=[1+s+s**2,2-s+0.5*s**3], with RHS r*[1+2*s,-1+1.5*s**2].',
             '- Oscillator: y=[cos(s)+0.25*sin(s),-sin(s)+0.25*cos(s)], with RHS r*[y2,-y1].', '',
             'Every run starts from the analytical value at its first time. The same solver object '
             'is reused with explicit clear_buffer calls. Maximum step size is 0.3. Callback '
             'parameters carry family/rate and an evaluation counter through the polymorphic '
             'args interface; callbacks must occur without changing family/rate. Input times '
             'and initial conditions must remain unchanged. Output shape must be [17,3], all '
             'entries finite, and returned times must match every requested time within 1e-13.', '',
             'At each requested time, maximum component error divided by '
             'max(1,maxabs(exact_solution)) must be <=50*requested_tolerance. For the oscillator, '
             'absolute error in y1**2+y2**2=1.0625 must be <=100*requested_tolerance. These '
             'checks use analytical answers, not agreement between time directions or tolerance '
             'settings. The tolerances are acceptance limits, not rigorous global error bounds.', '',
             'Stiff problems, event detection, continuation without resetting the buffer, all '
             'interpolant queries, malformed inputs and performance remain unverified. '
             'The upstream plotted Duffing example was reviewed for interface usage; this '
             'independent driver uses analytical models and has no plotting dependency.', '',
             '## Checked links and actual output', '',
             'The independently written API consumers have their own MIT notice. Upstream terms '
             'remain separate; no upstream code was copied. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def fitpack_polynomials_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fitpack-polynomials-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-fitpack-polynomials-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked FITPACK polynomial values and derivatives', '',
             'These E1a and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-fitpack-polynomials-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Common fixtures', '',
             'Each independent driver constructs 144 interpolating fits. Source sizes 8 and 13 '
             'use uniform ascending coordinates x=-0.5+2*t, t=(i-1)/(n-1), or nonuniform '
             'coordinates x=-0.5+2*(t+0.2*t*(1-t)) supplied in reverse order. '
             'Spline degrees k=1,3,5 use every monomial x**p for p=0..k with scales -2,0.5,3. '
             'All fits explicitly request smoothing=0. Some constant fixtures coincide; 144 '
             'counts fits, not distinct data sets.', '',
             'The same curve object is reused through new_fit, including changes in data size '
             'and spline degree. Original coordinates and values must remain unchanged. Fitting '
             'and every evaluation must return a successful FITPACK status. All outputs must '
             'be finite. Final destroy must reset m and release public x, y and knot arrays. '
             'This checks the observed public state, not all internal memory management.', '',
             '## Values and interpolation (E1a)', '',
             'At 33 uniformly spaced targets on [-0.5,1.5], including both endpoints, '
             'the scalar and vector eval overloads are each compared directly to scale*x**p. '
             'These give 9,504 checks. Vector evaluation at the original source nodes adds '
             '1,512 checks, for 11,016 total value references. Reversed source data are sorted '
             'before use as vector evaluation targets, independently of FITPACK source sorting.', '',
             'Maximum value error divided by max(1,maxabs(reference)) must be <=5e-12. '
             'Node errors use the analogous normalization from source values. Scalar and vector '
             'agreement is not the reference: both must independently reproduce the polynomial.', '',
             '## Derivatives of the stored spline (H1)', '',
             'Every fit is checked at the same 33 targets using both scalar and vector dfdx '
             'overloads for orders r=0..k. Independent analytical references are zero for r>p '
             'and scale*p!/(p-r)!*x**(p-r) otherwise. Falling factorials are formed with small '
             'integer-factor products. There are 34,848 positive-order derivative checks and '
             '9,504 zeroth-order value checks, totaling 44,352 references. Quintic fits exercise '
             'derivative orders through five, including derivatives of lower-degree polynomials '
             'that should vanish.', '',
             'Maximum error for each derivative-order/fixture pair is divided by '
             'max(1,maxabs(analytical_derivative)) and must be <=1e-8. This looser threshold '
             'than the value threshold accounts for amplification of coefficient roundoff in '
             'higher spline derivatives. It is an explicit acceptance criterion, not an error '
             'bound promised by the package. No finite-difference approximation or second '
             'numerical library supplies reference derivatives.', '',
             '## Scope', '',
             'The H1 link differentiates a fitted spline representation, not an arbitrary '
             'callback. These drivers check polynomial reproduction and supported interfaces. '
             'Positive smoothing, noisy-data approximation, periodic curves, roots/integrals, '
             'extrapolation, malformed inputs, arbitrary nonlinear accuracy and performance '
             'remain outside these drivers. The separate stored-spline integration driver retains '
             'its own [H2a2b2 evidence](gams-sparse-integral.md).', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own MIT notice; upstream '
             'terms remain separate. Pinned sources and author tests/examples were reviewed for '
             'interfaces, without copying upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def diagonal_response_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-diagonal-response-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-diagonal-response-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked diagonal solves and uncoupled harmonic responses', '',
             'These D2 and I1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-diagonal-response-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## SpecialMatrices: nonsingular real diagonal systems (D2)', '',
             'Sizes 1,2,7,32, three diagonal patterns and scales -4,0.125,8 give 36 fixtures. '
             'Before scaling the diagonals are d_i=i, d_i=(-1)**i*(1+mod(i,3)), or '
             'd_i=2**(mod(i,7)-3). All entries are nonzero. Four known solution columns use '
             'x_i,c=(2*i-3*c)/8 for c=1,2,3, and zero for c=4. Construct b_i,c=d_i*x_i,c '
             'before calling the library.', '',
             'Each fixture calls solve once with the four-column matrix and four times with '
             'individual vectors: 180 solves and 3,024 solution-coordinate comparisons. '
             'Returned shapes and finite values are required. Maximum coordinate error divided '
             'by max(1,maxabs(reference_column)) must be <=2e-13. Scalar residuals '
             'abs(d_i*x_i-b_i)/max(1,abs(b_i),abs(d_i*reference_i)) must also be <=2e-13 '
             'for both overloads. The right-hand sides, constructor diagonal and dense views '
             'of the structured matrix must remain unchanged.', '',
             'The D2 assignment is deliberately broad; this driver verifies only real diagonal '
             'solve overloads. Other matrix structures, singular diagonals, invalid sizes, '
             'complex arithmetic and performance are not verified.', '',
             '## dynamics: unit-mass, diagonal-stiffness response (I1)', '',
             'This is a steady-state harmonic response of second-order ODEs, not an initial-value '
             'integration. Sizes n=1,2,3 use M=I and K=diag(1**2,...,n**2). Damping is '
             'C=alpha*M+beta*K, alpha=0.1,0.4 and beta=0,0.05. Two complex force patterns '
             'give 24 fixtures, each at angular frequencies [0,0.5,1,1.5,2,2.5,3,4] rad/s. '
             'There are 384 complex-coordinate comparisons, including damped resonances and '
             'static frequency zero.', '',
             'For physical coordinate i and force pattern p=1,2, '
             'F_i(w)=i*(1+0.1*w)+imaginary_unit*p*(0.25*i-0.2*w). The closed-form reference is '
             'X_i=F_i/(i**2-w**2+imaginary_unit*w*(alpha+beta*i**2)). Both real and imaginary '
             'parts contribute to the complex absolute error. At each frequency, maximum '
             'coordinate error divided by max(1,maxabs(reference_response)) must be <=1e-10. '
             'Responses must have shape [8,n], be finite and return unchanged frequency values. '
             'Optional natural frequencies must match [1,...,n] within 1e-12. The polymorphic '
             'force callback must be invoked exactly eight times without changing its pattern.', '',
             '## Failed broader response probes', '',
             '**Non-unit mass and coupled systems are not verified.** Both probes built '
             'successfully but disagreed with independent static solutions at the pinned revision. '
             'The failed sources, hashes, package revision and complete build/run results are '
             'retained in [the candidate directory](gams-candidates/dynamics/README.md). '
             'The successful driver keeps the original 1e-10 threshold; it narrows the matrices '
             'rather than relaxing accuracy.', '',
             '- With n=1, M=2, K=2, alpha=0.1, beta=0 and force pattern 1, frequency zero '
             'gave normalized response error 0.5153882032 against X=F/K.',
             '- With n=2, M=I, Q=I-2*v*vT/(vT*v), v=[1,2], and '
             'K=Q*diag(1,4)*Q^T, the corresponding static error was 0.5625.', '',
             'These are response failures, not compiler failures. No library fix is included. '
             'The published I1 driver demonstrates only the explicitly uncoupled unit-mass '
             'configuration; sparse/modal-truncated methods, arbitrary mass normalization, '
             'coupling, transient integration, invalid inputs and performance remain unverified.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and the dynamics author example were reviewed without '
             'copying upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def ranking_magic_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-ranking-magic-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-ranking-magic-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked sorting indices and magic-square construction', '',
             'These N6 and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-ranking-magic-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## ORDERPACK rank: indices that sort data (N6)', '',
             'Every permutation of lengths 1..7 gives 5,913 exhaustive fixtures. Another '
             '84 fixtures use six patterns at sizes [0,1,2,3,4,7,8,15,16,31,32,63,64,127]: '
             'ascending signed values, descending values, a constant, three repeated keys, '
             'alternating signed magnitudes and mod(37*i+11,17)-8. Each fixture exercises '
             'integer32, real32, real64 and character overloads, giving 5,997 fixtures and '
             '23,988 rank calls. Some degenerate patterns coincide; fixture counts are not '
             'counts of distinct data arrays.', '',
             'Real keys are integer values divided by eight, exactly representable in both '
             'floating-point kinds. Character keys are four-digit, zero-padded decimal strings '
             'of integer_value+512, so their lexical ordering agrees with integer ordering. '
             'This is a controlled character fixture, not a test of language-specific collation.', '',
             'Independent insertion-sort loops compute expected sorted integer values before '
             'calling ORDERPACK. Each returned index must be in range and each original index '
             'must occur exactly once. Original values indexed by the result must match the '
             'reference sequence exactly. This checks all four overloads against the independent '
             'reference, not against each other. All four source arrays must remain unchanged. '
             'Empty arrays are exercised without reading undefined output elements.', '',
             'Tied keys may have any valid index order; stable tie ordering is not required or '
             'claimed. NaNs, infinities, signed-zero conventions, arbitrary character encodings, '
             'mismatched output lengths, other ORDERPACK procedures and performance remain '
             'unverified. This N6 mapping concerns sorting indices, not statistical rank inference.', '',
             '## M_LA mat_magic: normal magic squares (D1)', '',
             'Orders 1 and 3..32 include 16 odd, eight doubly-even and seven singly-even orders. '
             'Order two is excluded because no normal magic square of that order exists. '
             'Each order is constructed twice with compact leading dimension n and twice '
             'with padded leading dimension n+3: 124 calls. Storage is reset to a finite '
             'sentinel before each call; padded rows must remain untouched.', '',
             'All outputs must be finite. Active entries must be exactly integer-valued '
             'and form a permutation of 1..n**2. Exact int64 scalar sums verify every row, '
             'column and both principal diagonals against n*(n**2+1)/2. These checks do not '
             'depend on the constructor algorithm or a preferred square arrangement. '
             'Across all calls there are 45,744 entry checks and 4,456 exact line-sum checks. '
             'Repeated construction checks valid results after storage reuse without imposing '
             'a particular arrangement on valid squares.', '',
             'The D1 mapping covers this matrix constructor only. Other M_LA utilities, '
             'unsupported orders, invalid leading dimensions and performance remain unverified.', '',
             '## Checked links and actual output', '',
             'These independently written API consumers have their own MIT notice; upstream '
             'terms remain separate. Pinned sources and the ORDERPACK author example were '
             'reviewed without copying upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def geodesy_forlab_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-geodesy-forlab-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-geodesy-forlab-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked WGS84 coordinates and overdetermined least squares', '',
             'These P and D9a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-geodesy-forlab-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## maptran3d: WGS84 forward/inverse coordinates (P)', '',
             'The reference ellipsoid uses a=6378137 meters and flattening f=1/298.257223563. '
             'Let e2=f*(2-f), b=a*(1-f) and N=a/sqrt(1-e2*sin(latitude)**2). '
             'Independent Cartesian references are X=(N+h)*cos(latitude)*cos(longitude), '
             'Y=(N+h)*cos(latitude)*sin(longitude), Z=(N*(1-e2)+h)*sin(latitude). '
             'These are ellipsoid geometry formulas, not another call to the conversion library.', '',
             'Seven latitudes [-89,-60,-30,0,30,60,89] degrees, six longitudes '
             '[-180,-90,-23,0,74,180] degrees and heights [-100,0,1000,100000] meters '
             'give 168 points. Both explicit degree and radian interfaces give 336 cases. '
             'Each forward result must be finite, preserve its geodetic inputs and agree '
             'with the reference within 5e-6 meters in every Cartesian component.', '',
             'The inverse receives the independently constructed Cartesian reference, rather '
             'than the library forward result. Returned coordinates must be finite. Angular '
             'error must be <=2e-7 degrees and height error <=5e-3 meters. Longitude differences '
             'are wrapped with atan2(sin(delta),cos(delta)), so -180 and +180 are equivalent. '
             'Another eight forward calls check both exact poles at heights 0 and 1000 meters '
             'in both angle units against [0,0,+/-(b+h)]. There are 680 conversion calls in total.', '',
             'Inverse conversion at the poles, where longitude is not unique, is not verified. '
             'The origin, custom ellipsoids, extreme heights, invalid coordinates and performance '
             'are also outside this scope. The broad P classification is retained; no detailed '
             'astronomy or geodesy class is invented.', '',
             '## forlab: tall real single-precision least squares (D9a1)', '',
             'The catalog uses forlab RPRE with 32-bit real storage. Shapes [2,1], [3,2], '
             '[5,3], signed scales -4,0.5,2, identity/Householder factors and two residual '
             'settings give 36 full-column-rank fixtures. Three vector right-hand sides each '
             'give 108 solver calls. Eighteen fixtures have prescribed nonzero residuals. '
             'These are the tall subset of the [shared least-squares fixtures](gams-least-interpolation.md).', '',
             'Construct A=L(:,1:n)*diag(scale*[1,...,n])*R^T, where orthogonal factors are '
             'identity or Q=I-2*v*vT/(vT*v), v=[1,...,dimension]. For right-hand side c=1,2,3, '
             'set z_i=(2*i-c)/4 and x_reference=R*z. Construct b=A*x_reference+noise with '
             'noise zero or 0.25*c*L(:,n+1). Orthogonality gives the unique least-squares '
             'solution, residual -noise and its exact squared norm independently of forlab.', '',
             'Solutions must have the expected shape and be finite. Maximum coordinate error '
             'scaled by max(1,maxabs(reference_solution)) must be <=3e-5. Prescribed residual '
             'error scaled by max(1,maxabs(b)) must be <=5e-5. The normal-equation residual '
             'A^T*(A*x-b), scaled by max(1,maxabs(b))*max(1,maxabs(A)), must be <=1e-4. '
             'The prescribed squared residual norm has normalized tolerance 2e-4. Source '
             'matrices and right-hand sides must remain unchanged. These explicit tolerances '
             'match the native single-precision configuration; no double-precision library '
             'build is substituted. The existing unrelated checksum-guarded optional-norm '
             'argument fix is reused unchanged.', '',
             '## Failed underdetermined probe', '',
             '**Wide systems are not verified.** The full-row-rank matrix '
             'A=[[-4,0,0],[0,-8,0]] and b=[-1,-6] have exact minimum-norm solution '
             '[0.25,0.75,0], but the pinned solver returned nonfinite values. The build '
             'passed. The [candidate source, hash and full result](gams-candidates/forlab/README.md) '
             'are retained. The published driver keeps its original accuracy thresholds and '
             'narrows the shapes; it does not fix the library or promote this failed configuration. '
             'Square-system LU, rank deficiency, matrix right-hand sides, invalid inputs and '
             'performance remain unverified.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and maptran3d author tests were reviewed without copying '
             'upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def jacobian_transforms_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-jacobian-transforms-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-jacobian-transforms-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked user-Jacobian exact fits and rigid transforms', '',
             'These G1b1b and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-jacobian-transforms-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## nonlin: exact nonlinear least squares with user Jacobian (G1b1b)', '',
             'Five observations at t=[-1,-0.5,0,0.5,1] follow y=A*exp(B*t). '
             'Amplitudes A=0.5,2 and exponents B=-1,0.25,1 use four starts each: '
             'amplitude 0.5*A or 1.5*A, exponent B-0.5 or B+0.5. There are 24 fits. '
             'Residuals are x1*exp(x2*t)-A*exp(B*t), with user Jacobian columns '
             'exp(x2*t) and x1*t*exp(x2*t). These are the exact-fit subset of the '
             '[MINPACK lmder1 fixtures](gams-jacobian-roots.md), with known parameters '
             '[A,B] and minimum sum of squared residuals zero.', '',
             'The helper is explicitly configured with both residual and Jacobian callbacks. '
             'All 240 starting Jacobian entries are checked against central differences using '
             'h=1e-5*max(1,abs(x_j)); maximum entry error divided by '
             'max(1,maxabs(analytical_column)) must be <=2e-7. Both callbacks must actually be '
             'used during every solve. The solver uses initial step bound factor 1, maximum '
             '2,000 function evaluations, and function/variable/gradient tolerances 1e-12.', '',
             'At least one normal convergence flag is required, but is not sufficient. '
             'Returned parameters/residuals must be finite; residuals must agree with an '
             'independent final evaluation within 1e-11. Maximum parameter error divided by '
             'max(1,maxabs(exact_parameters)) must be <=2e-7. Sum of squared residuals must '
             'be <=1e-10, each residual <=1e-8, and maxabs(J^T*r) <=1e-6. '
             'This verifies user-Jacobian mode only: the sibling G1b1a finite-difference '
             'configuration and bound-constrained solver type are not promoted.', '',
             '## Failed broader least-squares probes', '',
             'The [candidate directory](gams-candidates/nonlin-least-squares/README.md) '
             'retains two failed probe sources, normalized hashes and complete results:', '',
             '- Default step bound factor 100: the exact fit A=0.5, B=1 from [0.25,0.5] '
             'returns unchanged parameters with converge_on_chng true; normalized parameter '
             'error is 0.5.',
             '- Step bound factor 1: all 24 exact fits complete, but the first nonzero-residual '
             'fixture returns unchanged starting parameters with the same convergence flag. '
             'Its known minimizer is [log(2),1]; normalized parameter error is 0.7.', '',
             'No library fix or relaxed answer tolerance is included. The public driver '
             'specifies step factor 1 and verifies only the exact exponential family. '
             'Nonzero-residual minima, the default step setting, arbitrary starts, finite-difference '
             'mode and global convergence remain unverified.', '',
             '## fglm: components and homogeneous transforms (D1)', '',
             'Twenty-four deterministic pairs of vec3d objects give 48 double-precision '
             'vector additions/component products and 144 coordinate references. '
             'With i=1..24, a=[i/8,(i-12)/4,(-1)**i/2] and '
             'b=[(25-i)/4,-i/8,mod(i,5)-2]. Outputs must be finite, agree with scalar '
             'component formulas within absolute 1e-13, and preserve both inputs. '
             'Multiplication here is componentwise, not a dot product.', '',
             'Single-precision mat4f transformations use nine angles '
             '[-2*pi,-pi,-pi/2,-pi/3,0,pi/6,pi/2,pi,2*pi], four translations '
             '[0,0,0], [1,-2,0.5], [-4,0,2], [0.25,0.5,-0.75], and both call orders. '
             'Every matrix starts from explicit identity. Translate then rotate produces T*R; '
             'rotate then translate produces R*T. There are 72 matrices and 216 transformed '
             'homogeneous vectors: points [1,2,3,1], [-2,0.5,0,1], and direction [1,-1,2,0]. '
             'The zero homogeneous coordinate independently checks translation invariance '
             'of directions. All 864 output coordinates are compared to direct formulas.', '',
             'Reference sine/cosine values are computed in double precision from the actual '
             'single-precision input angle. Coordinates use Rz(x,y)=[cos*x-sin*y,sin*x+cos*y] '
             'and the appropriate translation order. Maximum coordinate error divided by '
             'max(1,maxabs(reference_vector)) must be <=2e-6. Every matrix/output must be '
             'finite. Scalar checks of R^T*R=I give 648 orthogonality entries, and 72 '
             'determinants must equal one; both use absolute tolerance 2e-6. '
             'Arbitrary 3D rotation axes, other vector overloads, projection matrices and '
             'performance remain unverified.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and the nonlin author example were reviewed without '
             'copying upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', output.rstrip(), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def expression_evaluation_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-expression-evaluation-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-expression-evaluation-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked numeric expression evaluation and recovery', '',
             'These N3 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-expression-evaluation-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## Common mathematical references', '',
             'Each engine checks 14 formulas at all 20 pairs from '
             'x=[-2,-0.5,0,0.75,2], y=[-1.5,0,0.5,1.25]: 280 ordinary references. '
             'The engines use the same expression strings with variables pgx and pgy. '
             'Both use double precision in the checked catalog configuration. '
             'All results must be finite and satisfy '
             'abs(result-reference)/max(1,abs(reference)) <=2e-12. '
             'References use Fortran arithmetic and elementary identities, not agreement '
             'between the two libraries.', '',
             '| Expression (x/y denote pgx/pgy) | Independent reference |',
             '| --- | --- |',
             '| x+2*y | x+2*y |',
             '| (x+2)*(y-3) | (x+2)*(y-3) |',
             '| x**2+3*x*y+y**2 | x*x+3*x*y+y*y |',
             '| sin(x)**2+cos(x)**2 | 1 |',
             '| exp(log(x+4)) | x+4 |',
             '| sqrt((x+4)**2) | x+4, positive on this input grid |',
             '| abs(x-y) | absolute difference |',
             '| sin(x+y)-sin(x)*cos(y)-cos(x)*sin(y) | 0 |',
             '| (x-y)/(x+4) | direct quotient, nonzero denominator |',
             '| x**3-3*x**2*y+3*x*y**2-y**3 | (x-y)**3 |',
             '| log(exp(y/4)) | y/4 |',
             '| 2+3*4 | 14 |',
             '| (2+3)*4 | 20 |',
             '| -(x+y) | -x-y |', '',
             'The fixtures cover precedence, parentheses, unary negation, powers, changing '
             'variables, cancellation and common elementary functions. They do not establish '
             'correctness for every accepted expression or extreme numerical range.', '',
             '## Fortran Function Parser', '',
             'Each ordinary expression is parsed once and evaluated at all input pairs. '
             'Parsing and evaluation must report no error, and supplied variable arrays '
             'must remain unchanged. The same parser object is reused with explicit error '
             'clearing and destruction between expressions.', '',
             'Three malformed expressions `pgx+`, `(pgx` and `unknown(pgx)` must set a parse error. '
             'Three separately parsed expressions, sqrt(pgx), log(pgx), 1/(pgx-pgx), '
             'must set an evaluation error when pgx=-1. Outputs from rejected requests are '
             'not used as numeric answers. After each of these six errors, clear/destroy, '
             'parse pgx+pgy and evaluate [0.25,-0.5] against -0.25. This gives 286 successful '
             'value references, six expected rejected requests and six successful recoveries.', '',
             '## M_calculator dnum0', '',
             'Every ordinary evaluation first assigns pgx and pgy through decimal strings '
             'formatted with 17 fractional digits in scientific notation. All 560 assignments '
             'must return status zero, finite values and absolute assignment error <=1e-14. '
             'Every expression evaluation must return status zero. Reassignment on each input '
             'pair checks that prior variable values are replaced.', '',
             'Malformed expressions `(1+2`, `1+@` and `1+*2` must return nonzero status. '
             'After each error, pgx+pgy must still evaluate successfully to the last assigned '
             'sum, 3.25. This checks recovery and retained variable state without assuming a '
             'particular diagnostic message. There are 283 successful value references, '
             'three expected rejected requests and three recoveries, plus the 560 assignment '
             'checks. Domain-error handling in this engine is not verified by these probes.', '',
             '## Scope', '',
             'N3 records numeric expression parsing/evaluation, not symbolic algebra or '
             'nonlinear solving. Missing-variable conventions, general grammar completeness, '
             'case folding, user-defined functions, all domain errors, NaN/infinity behavior, '
             'state isolation between clients and performance remain unverified. '
             'Recovery calls intentionally follow the documented explicit reset steps for '
             'the parser; no cross-engine error-code equivalence is assumed.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and author examples/tests were reviewed without copying '
             'upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def conversion_triangulation_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-conversion-triangulation-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-conversion-triangulation-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked decimal conversion and planar Delaunay meshes', '',
             'These A6 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-conversion-triangulation-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## fortran-string-to-real str2real (A6)', '',
             'Eight mantissas (0, 1, 25, 12345, 9876543, .125, 12.5, 0.000125) use both signs. '
             'Each is tested without an exponent and with E/e and explicit signed exponents '
             '[-100,-12,-1,0,1,12,100]. These give 240 strings. Four additional long-mantissa '
             'cases include a positive 16-digit integer, a negative 15-digit integer and '
             'positive/negative 24-fractional-digit decimals: 244 conversions in total. '
             'Every tested string is at most 28 characters.', '',
             'Each conversion has two independent references: the numeric mantissa multiplied '
             'by 10**integer_exponent, and compiler formatted READ of the same string. '
             'Long decimal reference literals are rounded by the compiler independently of '
             'str2real. Results and READ references must be finite. Nonzero values must satisfy '
             'relative error <=5e-14 against both references, including small normal values '
             'near 1e-104. Zero inputs must return exactly zero; a signed-zero convention is '
             'not required. Unlike normalization by max(1,abs(reference)), this relative '
             'criterion does not make the small-number checks trivial.', '',
             'The library does not validate malformed strings. These valid-input checks do '
             'not establish malformed-input handling, every length/digit boundary, D exponents, '
             'whitespace conventions, overflow, underflow/subnormals, correctly rounded conversion '
             'or performance. Numerical agreement within tolerance is not a bitwise-rounding claim.', '',
             '## GEOMPACK r8tris2: rectangle with interior points (P)', '',
             'Three layouts have 5,9,13 points: square corners (-1,-1), (1,-1), (1,1), (-1,1) '
             'and the first 1,5,9 points from the fixed interior list:', '',
             '```text',
             '(0,0), (-0.7,-0.2), (0.2,-0.6), (0.65,0.1), (-0.1,0.7),',
             '(-0.45,0.45), (0.45,0.55), (-0.55,-0.65), (0.55,-0.45)',
             '```', '',
             'Positive scales 0.5,2,8, translations (0,0) and (-3,5), and original/reversed '
             'input order give 36 triangulations. The known hull always has four vertices, '
             'so Euler references are T=2*n-6 triangles and E=3*n-7 distinct edges. '
             'Every input vertex must be used. Triangle vertices must be in range and distinct '
             'triangles must not repeat the same vertex set. Input coordinates must be finite '
             'and restored exactly after the routine returns.', '',
             'All 432 triangles must be counterclockwise with twice-area >1e-14*scale**2. '
             'Their summed area must match 4*scale**2 with normalized error <=5e-12, '
             'using max(1,4*scale**2) as denominator. Undirected edges must have incidence '
             'one or two, exactly four edges must be boundary edges, and distinct edge count '
             'must equal the Euler reference. Every positive neighbor must refer to a different '
             'in-range triangle sharing the reversed edge, with a reciprocal neighbor link. '
             'Negative boundary links must form one closed four-edge cycle without repetition.', '',
             'For every triangle and nonincident point p, independently form a=v1-p, b=v2-p, '
             'c=v3-p and the incircle determinant '
             'D=dot(a,a)*cross(b,c)-dot(b,b)*cross(a,c)+dot(c,c)*cross(a,b). '
             'Counterclockwise orientation makes D positive for an interior circumcircle point. '
             'All 3,360 tests require D/max(1,scale**4) <=1e-10. This checks the Delaunay '
             'empty-circumcircle condition without using another triangulation library.', '',
             'No particular triangle sequence or diagonal choice is required. Cocircular '
             'ambiguities can have multiple valid solutions. Duplicate points, entirely '
             'collinear or nearly coincident sets, arbitrary hulls, extreme coordinate scales, '
             'three-dimensional meshes and performance remain unverified.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and author tests were reviewed without copying upstream '
             'code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def graph_sorting_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-graph-sorting-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-graph-sorting-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked dependency ordering and numeric sorting', '',
             'These P and N6 drivers passed the restricted GNU Fortran 16.2.0 sandbox with '
             'FPM 0.12.0. Existing package libraries were reused; only mains and executables '
             'were compiled. The [verification report](gams-graph-sorting-validation.json) '
             'retains pins, source hashes and actual output. GAMS categories are not exhausted.', '',
             '## DAGLIB topological ordering (P)', '',
             'Five vertices have ten possible dependency edges under a fixed topological '
             'order. All 1,024 edge subsets are tested under labels [1,2,3,4,5] and '
             '[5,4,3,2,1], giving 2,048 acyclic graph fixtures. This is exhaustive for '
             'these two fixed orders, not every labeled five-vertex DAG. Some fixtures '
             'coincide. Edgeless graphs, disconnected components and isolated vertices are '
             'included. Each graph is sorted twice without rebuilding between sorts.', '',
             'Every successful sort must return status zero and an allocated permutation '
             'of the complete vertex set. A separately built dependency matrix supplies '
             'the reference: every prerequisite must precede its dependent vertex. '
             'No particular order of unrelated vertices is required. Graph destruction '
             'must reset its reported vertex count.', '',
             'Self-loops, two-vertex cycles and three-vertex cycles are each sorted twice. '
             'All six calls must return status -1 and leave the output unallocated. '
             'After each cyclic graph, the same object is explicitly rebuilt as the '
             'chain 1 -> 2 -> 3 and sorted twice. Totals are 2,051 acyclic fixtures, '
             '4,102 successful sorts, 20,492 independent dependency-precedence checks '
             'and six expected cyclic rejections. Recovery uses explicit set_vertices '
             'rebuilding; arbitrary edge mutation is not verified.', '',
             'Zero-vertex graphs, invalid vertex indices, every labeled DAG, large recursion '
             'depths, metadata/Graphviz export, other traversal methods and performance '
             'remain unverified. The existing broad P graph-algorithm assignment is retained.', '',
             '## coretran in-place numeric sorting (N6)', '',
             'The public driver explicitly requests stable=.true. for every sort. '
             'All permutations through length seven give 5,913 fixtures. Another 84 use '
             'six patterns at lengths [0,1,2,3,4,7,8,15,16,31,32,63,64,127]: ascending, '
             'descending, constant, three repeated keys, alternating signed magnitudes '
             'and a repeated modular pattern. Total: 5,997 fixtures and 23,988 typed calls.', '',
             'Each fixture is independently insertion-sorted before invoking the library. '
             'Integer32 values are used directly; integer64 keys are integer_value*10**10+3 '
             'to include magnitudes beyond integer32. Real32/real64 keys divide the integer '
             'values by eight, giving exactly representable inputs. All four returned '
             'arrays must exactly equal the corresponding independently sorted values. '
             'The fixtures match the [ORDERPACK ranking reference](gams-ranking-magic.md), '
             'but this driver exercises in-place sorting rather than sorting indices.', '',
             'Equal numeric keys carry no auxiliary record labels, so the checks do not '
             'establish stability of equal-key records despite the requested stable mode. '
             'Default/unstable sorting, NaNs, indirect sorting, every coretran utility '
             'and performance remain unverified. The existing OpenMP build is reused '
             'unchanged; the execution sandbox uses one thread.', '',
             '## Failed coretran probes', '',
             'Both failures built successfully and retain their exact sources, normalized '
             'hashes, pinned revision and full results:', '',
             '- [Nearest-neighbor probe](gams-candidates/coretran-nearest/README.md): '
             'a valid two-dimensional 31-point query returned squared distance '
             '0.07390715705352345 instead of the direct minimum 0.048195228517966246. '
             'No nearest-neighbor GAMS driver is published.',
             '- [Mixed sorting settings](gams-candidates/coretran-sort/README.md): '
             'explicit stable=.false. on 16 equal integer32 values (all 7) accesses '
             'element 17 beyond bound 16 in sm_partition.f90. Default and stable=true '
             'settings had reached this fixture successfully before the unstable call '
             'failed. The full mixed-mode suite did not complete; this does not establish '
             'a default-mode failure.', '',
             'The checked sorting driver narrows the algorithm setting, keeping the full '
             'input suite and exact value checks. No source patch, relaxed comparison '
             'or disabled bounds checking is used. The sorting proof does not verify '
             'the separately mapped nearest-neighbor capability.', '',
             '## Checked links and actual output', '',
             'Independent API consumers have their own MIT notice; upstream terms remain '
             'separate. Pinned sources and author tests were reviewed without copying '
             'upstream code. Loading a link does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def neighbors_sparse_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-neighbors-sparse-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-neighbors-sparse-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked nearest-neighbor searches and sparse products',
     '',
     'These N5 and D1b4 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing '
     'libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-neighbors-sparse-validation.json) retains pins, source hashes and complete actual '
     'output. GAMS categories are not exhausted.',
     '',
     '## fortran-flann exact k-nearest neighbors (N5)',
     '',
     'The driver constructs 60 single KD-tree indexes: point counts [1,2,8,31,64], dimensions two and '
     'three, three data patterns, and original/reversed point order. Patterns are deterministic modular '
     'coordinates, collinear points, and duplicate coordinate pairs. For each tree there are 20 off-data '
     'queries followed by every source point as a self-query, giving 2,472 query points. The modular '
     'two-dimensional family includes the 31-point query that failed the separate coretran probe; this '
     'verifies FLANN, not coretran.',
     '',
     'Each query batch is searched three times, with k=1, min(3,n), and n, including repeated k settings '
     'for the smallest sets. There are 180 batched calls and 96,072 returned neighbors. Euclidean search '
     'explicitly requests checks=-1 (unlimited/exact search). Source and query arrays are single precision. '
     'The independent oracle converts those already-rounded input values to real64, directly calculates '
     'every squared Euclidean distance, and insertion-sorts those distances.',
     '',
     'For every returned neighbor, the zero-based index must be in range, distinct within the returned '
     'list, and consistent with its reported squared distance. The indexed direct distance must equal the '
     'corresponding kth sorted reference within 32*epsilon(float32)*max(1,reference_distance). This '
     'accounts for native single-precision distance accumulation; it is not an approximate-search accuracy '
     'claim. Tied points may have any index order. Status must be zero; distances must be finite and both '
     'source and query arrays unchanged. The native index is finalized while its target array still exists.',
     '',
     'Other metrics, approximate searches, radius queries, empty data, malformed requests, high dimensions '
     'and performance remain unverified. The pinned wrapper prints diagnostic lines on each search; the '
     'short transcript below shows only the final five summary lines. Complete diagnostics remain in the '
     'verification report.',
     '',
     '## sparse_fortran COO/CSR products (D1b4)',
     '',
     'Five row counts crossed with five column counts, each from [1,2,3,8,17], provide square, tall and '
     'wide matrices. Five patterns are used: all zero, diagonal, tridiagonal, modular sparse with an '
     'explicitly empty row/column, and dense. Both API orders are initialized from the same dense matrix. '
     'That gives 250 matrix/order fixtures and 500 independently initialized sparse objects. The pinned '
     '[CSR product '
     'source](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/src/sparse_csr_fortran.f90#L173) '
     'supplements the COO procedure evidence.',
     '',
     'This API gives order a computational meaning: C computes A*x, while non-C order (F here) computes '
     'transpose(A)*x. The author example also demonstrates the latter convention. Three right-hand sides '
     'are used: ones, alternating signed i/8, and i*(n_input+1-i)/4. Each format is checked separately '
     'against scalar loops over the original dense matrix, rather than merely agreeing with the other '
     'format. Totals are 1,500 products and 9,300 checked result entries.',
     '',
     'All nonzero fixture entries are small binary fractions, at least 1/8 in magnitude. Products and sums '
     'are exactly representable at these sizes, so returned values must equal the scalar references '
     'exactly. Output sizes and finiteness and dense-input preservation are checked. Zero matrices and '
     'empty rows/columns exercise empty storage segments. A fresh object is used for each initialization.',
     '',
     'Zero dimensions, near-zero entry dropping (the initializer uses a 1e-15 threshold), coordinate-list '
     'initialization, repeated initialization of an existing object, incremental insertion/deletion, '
     'invalid shapes and performance remain unverified. Storage conversion is outside this multiplication '
     'proof.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources '
     'and author examples were reviewed without copying upstream code. Loading a link does not submit a '
     'job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        if d['id'] == 'flann-knn-reference':
            output = '\n'.join(output.splitlines()[-5:])
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def adaptive_ad_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-adaptive-ad-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-adaptive-ad-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked automatic differentiation and adaptive IVPs',
     '',
     'These H1 and I1a1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-adaptive-ad-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## forwarddiff analytic scalar derivatives (H1)',
     '',
     'The differentia derivative entry point seeds one dual-number direction and returns both the '
     'function value and its first derivative. The driver compares those outputs with elementary '
     'analytic formulas, without finite differences or another differentiation package. A lifted '
     'constant 0*x+3 and monomials x**p for p=1..8 are checked at 65 points x=i/16, i=-32..32. This '
     'gives 585 calls and includes zero and negative inputs. The constant is explicitly lifted into '
     'the seeded dual space rather than assigning a real to an uninitialized dual.',
     '',
     'Twelve smooth functions are each checked at 97 points x=i/32, i=-48..48: 1/(1+x*x), exp(sin(x)), '
     'log(2+x), sqrt(2+x), sin(2*x)*cos(x), atan(x), tan(x/2), (2+x)**1.5, 2**x, (2+x)**(1+x/4), '
     'asin(x/2), and acos(x/2). These exercise chain, product and quotient rules, integer/real/dual '
     'exponents, and several elementary intrinsic overloads. Logarithms, roots and variable powers '
     'stay strictly inside their real domains; inverse trigonometric endpoints and tangent poles are '
     'avoided.',
     '',
     'Total: 1,749 derivative calls and 3,498 analytic value/slope comparisons. Both results must be '
     'finite and abs(result-reference)/(1+abs(reference)) must not exceed 2e-12. The saved maximum '
     'normalized error is 1.6666e-16. This is a first scalar derivative check, not a gradient, '
     'Jacobian, higher-order AD, nonsmooth-function, exceptional-input or performance verification.',
     '',
     '## FLINT explicit adaptive integration and dense output (I1a1a)',
     '',
     'All four exposed methods are exercised: DOP853, DOP54, VERNER98R and VERNER65E. Three analytic '
     'three-state systems provide independent endpoint and dense-output references:',
     '',
     '```text\n'
     'Diagonal exponentials:\n'
     '  y = [1,-2,1/2] * exp(a*[-1/2,1/4,-3/2]*t)\n'
     "  y' = a*[-1/2,1/4,-3/2]*y\n"
     'Oscillator plus nonautonomous polynomial:\n'
     '  y = [cos(a*t)+sin(a*t)/4, -sin(a*t)+cos(a*t)/4, t**3-2*t+1]\n'
     "  y' = [a*y2,-a*y1,3*t*t-2]\n"
     'Coupled triangular system:\n'
     '  y = [1,t,t*t]*exp(-a*t)\n'
     "  y' = [-a*y1,y1-a*y2,2*y2-a*y3]\n"
     '```',
     '',
     'The cross product is four methods, three systems, parameters a=1/2 or 3/2, starting times -1/2 '
     'or 3/4, and forward/backward intervals of length 5/4: 96 integrations. Each fixture starts with '
     'its exact state at the specified nonzero initial time and creates a fresh equation/solver '
     'object. The initial step is selected automatically (StepSz=0); no constant-step mode is used.',
     '',
     'For a=1/2 the requested scalar tolerances are ATol=1e-12 and RTol=1e-11. For a=3/2 they are '
     'componentwise [1,2,4]*1e-12 and [1,2,4]*1e-11. Initialization and integration must report '
     'FLINT_SUCCESS, the reached time must be finite and agree with the requested endpoint within '
     '32*epsilon*max(1,abs(endpoint)), and the initial state must remain unchanged. The returned '
     'endpoint state is compared with the closed form, giving 288 endpoint reference entries.',
     '',
     'Each stored dense solution is sampled at 17 equally spaced times including both endpoints, '
     'ordered in the integration direction. It is sampled twice: the first call retains coefficients '
     'with SaveInterpCoeffs=true, and the second releases them with SaveInterpCoeffs=false. Both calls '
     'must report success; every state entry is checked against the closed form, and the repeated '
     'output must be identical. There are 9,792 dense-output reference entries, including the repeated '
     'calls.',
     '',
     'All returned states must be finite. Endpoint and dense errors use '
     'abs(result-reference)/(1+abs(reference)) <= 5e-9. The saved maximum across these checks is '
     '1.6699e-9. Requested local error tolerances and independently checked solution errors have '
     'different meanings. These examples do not rank methods by speed or accuracy. Stiff equations, '
     'event detection, step-advance/constant-step modes, invalid requests and failure diagnostics '
     'remain unverified.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned '
     'sources, implementations and author examples were reviewed without copying upstream code. '
     'Loading a link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def lu_orbits_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-lu-orbits-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-lu-orbits-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked LU solves and orbital state conversions',
     '',
     'These D2a1 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-lu-orbits-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## linalg dense real LU (D2a1)',
     '',
     'The driver makes 96 nonsingular square factorizations: sizes [1,2,3,5,8,13], four matrix '
     'families, scales 1e-6 and 1e6, and original/reversed row order. The families are nonsymmetric '
     'strictly row-diagonally-dominant, upper triangular, lower triangular, and a cyclic permutation '
     'with nonzero weights. Reversing rows and the permutation fixtures exercise row pivoting; 48 '
     'factorizations actually perform swaps. These are modest manufactured systems, not an '
     'ill-conditioned accuracy benchmark.',
     '',
     'Three exact solution vectors are supplied independently: ones, alternating signed i/8, and '
     'i*(n+1-i)/4. Right-hand sides are built with scalar loops over the original dense matrix. Each '
     'is solved with the vector overload; all three are also solved together with the matrix overload. '
     'There are 384 solve calls and 3,072 known solution entries. Agreement between overloads alone is '
     'insufficient: both must match the manufactured solutions and satisfy independently recomputed '
     'scalar residuals.',
     '',
     'Packed factors, extracted L/U, and P are requested simultaneously. Pivots must have the '
     'sequential LAPACK range i..n. The driver independently applies those row swaps to an index '
     'vector and requires the returned P to encode exactly that permutation. It checks unit '
     'lower-triangular L, upper-triangular U, and each scalar entry of P*A=L*U. The dense input, '
     'right-hand sides and packed factors must remain unchanged by the applicable factor/solve calls. '
     'The packed factor, pivot and solution arrays must have expected shapes; all successful '
     'numerical outputs must be finite.',
     '',
     'Acceptance bounds are 2e-12 for all three measures: max abs(x-x_exact)/(1+abs(x_exact)); max '
     'absolute factorization discrepancy divided by max abs(A); and max '
     'abs(A*x-b)/(norm_inf(A)*norm_inf(x)+norm_inf(b)). The printed maxima are 4.0219e-16, 2.8115e-16 '
     'and 2.3570e-16 respectively. No solver-to-solver reference is used.',
     '',
     'Eight additional singular factorizations use sizes [1,2,5,8] with all-zero matrices and identity '
     'matrices whose last row duplicates the first. At size one, both patterns necessarily use zero. '
     'The documented diagnostic is NaN in every returned factor/permutation entry and zero in every '
     'pivot entry, rather than a status argument. All eight diagnostics are checked; no solve is '
     'attempted with these invalid factors. Complex/sparse/transpose solves, malformed dimensions, '
     'ill-conditioned error bounds and performance remain unverified.',
     '',
     '## Fortran Astrodynamics Toolkit orbital elements to state (P)',
     '',
     'The driver makes 864 conversions. Eccentricities [0,0.2,0.7,1,1.5] cover circular, elliptic, '
     'parabolic and hyperbolic conics. Inclinations are [0,0.3,pi/2,pi-0.4,pi], including equatorial, '
     'polar and retrograde configurations. Node angles are [0,1.2] and periapsis angles [0,0.7], '
     'except that undefined nodes at inclination 0/pi and undefined periapses for circles use only '
     'canonical zero. The routine singularity convention is therefore respected without claiming a '
     'test of its near-singular thresholds.',
     '',
     'True anomalies [-1.2,0,0.8,2] are used at three (mu,p) scale pairs: (1,2), (398600.4418,7000), '
     'and (1e6,2e5), in consistent units. Every fixture requires 1+e*cos(nu)>0; hyperbolic points stay '
     'inside the physical branch. Inertial position and velocity are checked against independently '
     'implemented geometric rotations: start with the planar conic state, then apply z(periapsis), '
     'x(inclination), and z(node) separately to each vector. The library uses a combined rotation '
     'matrix; this driver does not call its rotation or inverse-conversion utilities. There are 5,184 '
     'Cartesian component references.',
     '',
     'The following physical relations supply another 6,912 scalar invariant/direction checks (eight '
     'per state):',
     '',
     '```text\n'
     'radius = p/(1+e*cos(nu))\n'
     'h = cross(r,v),       |h|**2 = mu*p\n'
     'e_vector = cross(v,h)/mu - r/|r|,       |e_vector| = e\n'
     'energy = |v|**2/2 - mu/|r| = mu*(e**2-1)/(2*p)\n'
     'radial_speed = dot(r,v)/|r| = sqrt(mu/p)*e*sin(nu)\n'
     'h/sqrt(mu*p) = [sin(node)*sin(inc), -cos(node)*sin(inc), cos(inc)]\n'
     '```',
     '',
     'All returned components must be finite. Component differences are scaled by p for position and '
     'sqrt(mu/p) for velocity. Radius error is scaled by p, eccentricity error by 1+e, energy error by '
     'mu/p, and radial speed error by sqrt(mu/p); the angular-momentum relations are dimensionless as '
     'written. Each maximum must be at most 5e-12. Saved maxima are 1.1102e-15 for components and '
     '1.9984e-15 for invariants. The checks include parabolic zero energy and both prograde and '
     'retrograde angular-momentum direction.',
     '',
     'This is not merely a forward/inverse round trip. It verifies the named elements-to-state '
     'procedure, rather than orbit propagation, inverse elements, near-singular angle conventions, '
     'invalid conics, asymptotic hyperbolic anomalies or every toolkit method. The broad P '
     'classification is retained; no astronomy-specific GAMS subclass is invented.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned '
     'sources and author examples were reviewed without copying upstream code. Loading a link does not '
     'submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def dae_fft_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-dae-fft-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-dae-fft-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked differential-algebraic IVPs and complex FFT plans',
     '',
     'These I1a2 and J1a2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-dae-fft-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## DASKR index-one DAEs (I1a2)',
     '',
     'Two three-state differential-algebraic systems have independent closed-form states and '
     'derivatives. With tau=t-t0, the first combines triangular exponential dynamics and a nonlinear '
     'algebraic constraint:',
     '',
     '```text\n'
     'u = A*exp(-a*tau)\n'
     'v = B*exp(-b*tau) + c*A*(exp(-a*tau)-exp(-b*tau))/(b-a)\n'
     'w = u+v*v\n'
     'G = [u_prime+a*u, v_prime+b*v-c*u, w-u-v*v] = 0\n'
     '```',
     '',
     'The rate pairs (a,b) are (0.5,20) and (1,100), with c=0.75. Initial differential states (A,B) '
     'are (1,0.25) and (-0.5,2). Both rates are positive and unequal. This family is integrated '
     'forward only; reverse stiff exponential growth is outside the checked scope. The second, '
     'nonautonomous family is:',
     '',
     '```text\n'
     'u = tau*tau+C\n'
     'v = tau**3/3+C*tau+D\n'
     'w = sin(tau)+u*v\n'
     'G = [u_prime-2*tau, v_prime-u, w-sin(tau)-u*v] = 0\n'
     '```',
     '',
     'For parameter p=1 or 2, C=A*p and D=B/p use the same two initial-state pairs above. This '
     'polynomial family is integrated in both time directions. Both families use t0=-0.5 or 0.75, so '
     'residuals must honor a nonzero time origin. Consistent initial states and derivatives are '
     'supplied from the closed forms; automatic correction of inconsistent initial data is not tested.',
     '',
     'Each configuration is run with a numerical Jacobian and with a supplied dense Jacobian, '
     'independently checked against the closed form. The user callback supplies dG/dy+cj*dG/dy_prime, '
     'including algebraic rows. Its actual invocation is counted and required in user-Jacobian mode; '
     'it must not run in numerical-Jacobian mode. Only the dense direct linear-solver path is used. '
     'INFO(5) selects the Jacobian mode, while INFO(2) selects scalar or vector tolerances. Scalar '
     'RTol=1e-10 and ATol=1e-12 become componentwise [1,2,4] times those values in vector mode.',
     '',
     'There are 32 exponential and 64 polynomial trajectories, 96 total. The BDF history is retained '
     'between eight requested relative times: [0.01,0.02,0.04,0.08,0.16,0.32,0.64,1], negated for '
     'backward polynomial runs. This gives 768 checkpoints and 4,608 analytic state/derivative '
     'entries. Forty-eight trajectories actually use the supplied Jacobian. Every output must have '
     'IDID 2 or 3, finite time/state/derivative values, and a reached time agreeing with the requested '
     'checkpoint within 32*epsilon*max(1,abs(tout)); an arbitrary positive return is insufficient.',
     '',
     'State and derivative errors use abs(result-reference)/(1+abs(reference)), bounded by 5e-7 and '
     '5e-6 respectively. The algebraic constraint uses the absolute residual divided by one plus the '
     'magnitudes of its state/product terms, bounded by 5e-9. The complete DAE residual is recomputed '
     'at every checkpoint, with each row scaled by one plus the magnitudes of its contributing terms, '
     'bounded by 2e-6. Saved maxima are 4.6001e-10 for state, 1.6290e-7 for derivative, 6.9436e-11 for '
     'constraint and 1.0779e-8 for residual. These global solution checks have a different meaning '
     'from requested local tolerances.',
     '',
     'Krylov solves and preconditioners, banded storage, roots/events, inconsistent-data '
     'initialization, higher-index DAEs, invalid requests and performance remain unverified. Neither '
     'another solver nor mere agreement between Jacobian modes serves as the oracle.',
     '',
     '## NAFPack single-precision radix-two FFT plans (J1a2)',
     '',
     'Lengths [2,4,8,16,32,64,128], explicit RADIX2_DIT and RADIX2_DIF algorithms, four input patterns '
     'and scales [1/16,1,16] give 168 plan fixtures. Patterns are a shifted complex impulse, complex '
     'DC, a two-tone complex signal, and deterministic modular real/imaginary components. At the '
     'smallest lengths the tones alias naturally; the direct reference uses the actual discrete '
     'samples.',
     '',
     'Each plan is executed with both ITERATIVE and recursive implementations, using explicit classic '
     'loops. Each implementation is called twice on the same unchanged input and must reproduce '
     'exactly its previous output. The plan is destroyed before the shared transform object creates '
     'its next plan. Totals are 672 calls and 24,384 coefficient comparisons, including repetitions.',
     '',
     'The independent oracle converts the already-rounded single-precision input samples to real64 and '
     'computes all bins with scalar complex sums:',
     '',
     '```text\nF(k) = sum(j=0..n-1) x(j)*exp(-2*pi*i*k*j/n), k=0..n-1\n```',
     '',
     'Every returned real and imaginary component must be finite, and both input arrays must remain '
     'unchanged. The maximum coefficient discrepancy divided by sum(abs(input)) must be no greater '
     'than 64*epsilon(float32). Parseval independently requires abs(sum(abs(F)**2)/n - '
     'sum(abs(x)**2))/sum(abs(x)**2) <= 128*epsilon(float32). These L1/energy scales remain meaningful '
     'at bins whose exact Fourier amplitude is zero. Saved maxima are 5.1072e-7 for the L1-scaled '
     'coefficient discrepancy and 1.0004e-7 for relative Parseval error.',
     '',
     'This checks the forward sign, frequency ordering, amplitude normalization, direct coefficient '
     'values and repeated plan usage without depending on an inverse transform to undo matching '
     'errors. Other radices, mixed/split transforms, automatic algorithm choice, inverse transforms, '
     'other precisions, multidimensional APIs, parallel loop methods and performance remain '
     'unverified.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned '
     'sources and author examples were reviewed without copying upstream code. Loading a link does not '
     'submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def propack_fmm_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-propack-fmm-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-propack-fmm-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked partial SVD and Laplace kernel applications',
     '',
     'These D6 and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-propack-fmm-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## Historical PROPACK leading singular triplets (D6)',
     '',
     "This uses the catalog's explicitly labeled historical SciPy PROPACK 2.1 snapshot, not a claim to "
     'test the current maintained PROPACK release. Its native serial double-precision DLANSVD and '
     'existing LP64 BLAS/LAPACK recipe are reused unchanged. Pinned DLANSVD/DLANBPRO sources and API '
     'documentation were reviewed directly; the procedure record has no pinned author example.',
     '',
     'The driver constructs matrices with known distinct nonzero singular values s*[r,r-1,...,1], '
     'r=min(m,n). Column counts are [8,12,20], row counts are n-3, n, and n+3, and scales s are '
     '[1/8,1,8]. Each rectangular diagonal core is used directly or transformed by chained '
     'adjacent-plane rotations of its rows and columns. Orthogonal rotations preserve the prescribed '
     'spectrum and make the rotated operator dense. All matrices have full rank min(m,n); wide/tall '
     'null spaces do not establish rank-deficient-SVD behavior.',
     '',
     'For each matrix the leading one and three singular triplets are requested separately. This gives '
     '108 calls and 216 checked leading triplets. KMAX=r, TOLIN=1e-12, and the exact operator norm s*r '
     'is supplied as the norm estimate. A writable K is checked after return, along with INFO=0. The '
     'initial left vector is A times a vector of ones, giving a deterministic nonzero start inside the '
     'column space; the default random-start path is not tested.',
     '',
     'The callback implements both A*x and transpose(A)*x with scalar loops, counts both directions, '
     'and must leave the stored matrix unchanged. Both directions must actually be invoked by the '
     'solver. Residuals are subsequently recomputed with separate loops over a saved copy rather than '
     'calling the operator callback as the oracle. Every returned leading singular value must match '
     'its known descending reference. Both A*v-sigma*u and transpose(A)*u-sigma*v residual norms must '
     'be small, and all returned left/right vector pairs must have identity Gram matrices. Signs of '
     'singular vectors are unrestricted.',
     '',
     'Singular values and vectors must be finite, and returned bound estimates must be finite and '
     'nonnegative. Singular-value discrepancies and two-sided Euclidean residual norms are divided by '
     'the known operator norm; their maxima must not exceed 2e-9. Every Gram entry error must also be '
     'at most 2e-9. Saved maxima are 1.8808e-15 for singular values, 3.4320e-14 for triplet residuals '
     'and 1.2801e-13 for orthogonality.',
     '',
     'The checks do not establish sharpness of the reported error bounds, restarted DLANSVD variants, '
     'repeated/zero singular values, arbitrary sparse-matrix adapters, other precisions, malformed '
     'requests or performance. No comparison with another SVD solver is used as the reference.',
     '',
     '## FMM2D real Laplace target potentials (D1)',
     '',
     'The named procedure applies the structured kernel matrix K(i,j)=log(norm(target_i-source_j)) to '
     'a real charge vector. This driver verifies that matrix application under D1. Although the '
     'procedure also has a source-supported I2 relationship to Green functions/PDEs, it does not solve '
     'a boundary-value problem; the D1 driver must not promote I2 to a checked PDE-solver claim.',
     '',
     'Source counts [1,7,64,257,1024], two geometries, three charge patterns, requested precisions '
     '[1e-6,1e-10], and original/reversed source order give 120 calls. Each call has 24 separate '
     'targets, giving 2,880 direct target references. Source/target coincidence is explicitly rejected '
     'in fixture construction.',
     '',
     'One geometry uses deterministic modular points in the unit square. The second concentrates the '
     'same points into two small clusters near (0,0) and (0.75,0.75). Targets include points within '
     'the broad source region, near the small cluster, and farther away. Charge patterns are positive, '
     'alternating signed weights, and a centered neutral distribution. The singleton neutral case has '
     'exactly zero charge. Reversing sources also reverses charges so the physical field is preserved; '
     'both orders are independently checked against direct sums.',
     '',
     'For each target, independent scalar loops compute sum_j q(j)*log(distance), and a '
     'cancellation-aware scale sum_j abs(q(j)*log(distance)). The maximum absolute discrepancy divided '
     'by max(1e-12,that scale) must be at most 2e-5 for eps=1e-6 and 2e-8 for eps=1e-10. The floor '
     'handles the zero-charge fixture. Scaling by unsigned contributions avoids a meaningless relative '
     'error when the total potential nearly cancels. Every potential must be finite, IER must be zero, '
     'and source coordinates, charges and targets must remain unchanged.',
     '',
     'Saved maximum cancellation-scaled errors are 5.6386e-12 and 2.8739e-13 respectively. This does '
     'not promise those errors on arbitrary inputs or prove that a particular multipole interaction '
     'path was selected: small fixtures may use direct interactions internally. These are correctness '
     'examples, not a large-scale speedup benchmark.',
     '',
     'The precompiled native Fortran recipe retains its existing checksum-guarded '
     'array/empty-interaction compatibility edits, OpenMP build and one-thread sandbox execution. No '
     'kernel formulas, bounds checking, sandbox limits or library artifacts were changed for this '
     'batch. Source self-potentials, dipoles, gradients/Hessians, other kernels, vector interfaces, '
     'complete PDE solves and parallel performance remain unverified by this driver.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Loading a '
     'link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def gmres_inverse_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-gmres-inverse-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-gmres-inverse-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked GMRES systems and SPD matrix inverses',
     '',
     'These D2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing '
     'libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-gmres-inverse-validation.json) retains pins, source hashes, actual output and '
     'native diagnostics. GAMS categories are not exhausted.',
     '',
     '## LightKrylov real GMRES (D2)',
     '',
     'The driver uses the real double-precision dense operator/vector implementation. Sizes [2,5,8,13] '
     'are combined with three matrix families: nonsymmetric strictly row-diagonally-dominant matrices, '
     'a nonsymmetric tridiagonal with upper entry 0.5 and lower entry -0.125, and the symmetric '
     'tridiagonal Poisson matrix with diagonal 2 and adjacent entries -1. These modest full-rank '
     'systems do not establish behavior on arbitrary matrix-free or sparse adapters.',
     '',
     'Three exact solution vectors are ones, alternating signed i/8, and i*(n+1-i)/4. Scalar loops '
     'generate the right-hand side for either A*x or transpose(A)*x. Each system is solved from zero '
     'and from a deliberately incorrect constant -0.25 initial guess. Both a full n-vector Krylov '
     'dimension and a min(3,n)-vector dimension are selected with gmres_dp_opts; maxiter is set to '
     '500. Requested RTol=1e-10 and ATol=1e-12 are identical across these configurations.',
     '',
     'The cross product gives 288 solves and 2,016 known solution entries. Convergence metadata must '
     'be true and the information flag nonnegative; returned states must be allocated, correctly sized '
     'and finite. A negative iteration-count flag is rejected. There must actually be at least one '
     'solve with more than one outer cycle; the saved run contains 100 such solves. Exact initial '
     'guesses and zero right-hand sides are outside the verified scope.',
     '',
     'The maximum abs(x-x_exact)/(1+abs(x_exact)) must not exceed 5e-8. Independently recomputed '
     'scalar true residuals must satisfy '
     'norm_inf(A_effective*x-b)/(norm_inf(A_effective)*norm_inf(x)+norm_inf(b)) <= 2e-10, where '
     'A_effective is A or its transpose. This uses the true matrix product rather than only the '
     'internal residual estimate or solver-to-solver agreement. Original operator data and right-hand '
     'sides must remain unchanged. Saved maxima are 5.3793e-9 for normalized solution error and '
     '9.2868e-11 for scaled true residual.',
     '',
     'Logging is reduced through the public logger_setup API, preserving solver error checks. The '
     'saved run still has two initialization messages and a Fortran runtime warning that an array '
     'temporary was created for DTRTRS. That warning did not prevent the run from returning zero and '
     'passing every answer check; bounds checks and native library code were unchanged. '
     'Preconditioners, custom matrix-free operators, complex/single precision, exact-start/zero-RHS '
     'behavior, singular systems, parallel operation and performance remain unverified.',
     '',
     '## NTPoly Hotelling inversion with one MPI process (D2)',
     '',
     'The driver uses InverseSolversModule:Invert, separate from the previously checked '
     'SquareRoot/InverseSquareRoot APIs. It initializes MPI with serialized thread support, requires '
     'MPI_SUCCESS and exactly one process, and uses the existing one-process process-grid and '
     'shared-memory/self-transport recipe. It does not test distributed scaling or multi-process '
     'correctness.',
     '',
     'Sizes [2,3,5,8], prescribed spectral condition numbers [2,10,50], scales [1/4,4], and '
     'diagonal/rotated eigenbases give 48 real SPD inversions and 1,224 analytic inverse entries. The '
     'eigenvalues are scale*(1+(condition-1)*(i-1)/(n-1)). An identity eigenbasis is used directly or '
     'transformed by chained adjacent-plane rotations. Scalar sums form A=Q*diag(lambda)*transpose(Q), '
     'with independently known inverse Q*diag(1/lambda)*transpose(Q). No other inversion solver is '
     'used as the oracle.',
     '',
     'Input matrices are filled through triplet lists; inverse and original matrices are gathered '
     'through separate lists, checking every returned index and rejecting nonfinite entries. Solver '
     'parameters are converge_diff=1e-12, threshold=1e-14, max_iterations=200 and be_verbose=false. '
     'Invert has no returned convergence-status argument here: the independent mathematical checks '
     'determine acceptance.',
     '',
     'Each inverse entry must agree with its analytic value within '
     'abs(result-reference)/(1+abs(reference)) <= 5e-9. Separate scalar loops check every entry of '
     'A*inverse and inverse*A against identity, each with maximum absolute residual <= 5e-9. '
     'Normalized symmetry error must also be <= 5e-9. Gathering the original matrix after inversion '
     'must preserve it within 2e-12 relative maximum-entry error. Saved maxima are 3.4957e-14 for '
     'inverse entries, 1.7244e-14 for A*inverse, 9.7700e-15 for inverse*A and 3.3869e-15 for '
     'normalized symmetry.',
     '',
     'The saved output includes a UCX discovery diagnostic: scandir(/sys/class/net) failed because the '
     'path is absent in the sandbox. MPI initialization/finalization nevertheless returned MPI_SUCCESS '
     'and the one-process run returned zero with all mathematical checks passing. This proof concerns '
     'that one-process configuration; the diagnostic is retained rather than hidden. '
     'Nonsymmetric/indefinite/singular matrices, complex inverses, load balancing, multi-process '
     'execution and performance remain unverified.',
     '',
     '## Checked links and actual output',
     '',
     'Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned '
     'sources and author examples were reviewed without copying upstream code. Loading a link does not '
     'submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def periodic_calculus_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-periodic-calculus-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-periodic-calculus-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked polynomial calculus and orthogonal periodic distances',
     '',
     'These H1 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-periodic-calculus-validation.json) retains pins, source hashes and actual output. '
     'GAMS categories are not exhausted.',
     '',
     '## Formal polynomial gradient, divergence and conservation (H1)',
     '',
     "This independent API consumer uses the library's default real precision (real32 in this build) "
     'and a single coarray image. It constructs scalar f=xi**p and vector v=xi**q, '
     'xi=(x-origin)/length, for p,q=0,1,2. Orders 2 and 4, cell counts [32,64,128], and '
     '(origin,length) pairs [(-1.5,1),(0,0.5),(0.75,2)] give 162 field pairs. These translated/scaled '
     'intervals exercise the physical derivative factor 1/length rather than just unit-interval '
     'formulas.',
     '',
     'Every gradient value on the face grid is compared with p*xi**(p-1)/length, and every divergence '
     'value on the cell-center grid with q*xi**(q-1)/length. Degree-zero reference derivatives are '
     'explicitly zero. Values must be finite and have the expected grid shape; each '
     'abs(result-reference)/(1+abs(reference)) must be <= 5e-4. There are 24,354 pointwise derivative '
     'references. The saved maximum normalized error is 6.1035e-5.',
     '',
     'The same fields check weighted volume integrals of v*grad(f) and f*div(v), and the signed '
     'boundary flux f*v. For p+q>0, their analytic values are p/(p+q), q/(p+q), and 1; when both '
     'degrees are zero, all three are zero. There are 486 analytic integral references. The maximum '
     'absolute discrepancy must be <= 2e-4 for order 4, or <= 2e-4+2/n**2 for order 2. The additional '
     'second-order term allows discretization error in the polynomial product quadrature instead of '
     'pretending that every cubic integrand is integrated exactly.',
     '',
     'The extended Gauss identity requires abs(volume_gradient+volume_divergence-boundary_flux) <= '
     '5e-4 for every pair. The saved maximum integral error is 4.6539e-4 across the mixed order/grid '
     'suite, and the maximum conservation residual is 1.0316e-5. Requested order settings are '
     'exercised, but convergence order for nonpolynomial fields is not established by these checks. '
     'Laplacians, higher dimensions, PDE time integration, and multi-image execution remain '
     'unverified.',
     '',
     '## RAFFLE periodic distances in orthogonal cells (P)',
     '',
     'This uses the pinned RAFFLE v1.0.0 snapshot. Three orthogonal edge-length sets [1,1,1], [1,2,3], '
     'and [0.5,1.5,2] are each used directly and after two rigid Cartesian rotations, giving six cell '
     'geometries (orthogonal to real32 working precision). Two species contain five fixed fractional '
     'atom positions. Each cell has 15 modular query points plus the five exact atom positions; each '
     'query is also shifted by fractional integer vectors [0,0,0], [2,-3,1] and [-2,1,3]. Total: 360 '
     'queries.',
     '',
     'For every query, all five specified-atom distances and the nearest-atom vector lengths from real '
     'and fractional outputs are checked: 2,520 distance references. Near-atom exclusion is explicitly '
     'disabled so an exact atom query has zero nearest distance. Fractional outputs are independently '
     'converted to Cartesian coordinates with scalar sums before their norms are checked. No '
     'particular nearest-atom identity is required in a tie; this verifies lengths, rather than all '
     'returned-vector direction semantics.',
     '',
     'The independent oracle converts the actual rounded real32 inputs to real64, wraps the query into '
     'a reference cell with floor, and enumerates all 729 integer image offsets in [-4,4]**3 for each '
     "atom. It does not use the library's componentwise nearest-integer wrapping formula. For these "
     'orthogonal length ratios, a nearest image lies in this box; omitted images have a larger lower '
     'distance bound than a componentwise-near image, with ample margin for the small '
     'rotation-rounding errors.',
     '',
     'Each distance must be finite and abs(result-reference)/max_cell_edge <= 128*epsilon(float32). '
     'This scale accounts for input translation/rounding and real32 Cartesian arithmetic without '
     'dividing by a zero self-distance. The saved maximum is 1.3591e-7. Directional options, ignore '
     'lists, near-atom exclusion, highly skew lattices, structure generation and performance remain '
     'unverified.',
     '',
     '## Preserved skew-cell failure',
     '',
     'A separate valid skew-cell probe built successfully but returned distance 0.92970967292785645 '
     'where an independent image search found 0.31679647220910667. Its lattice rows are [1,0,0], '
     '[0.8,0.6,0], [0,0,1], with one atom at the origin and query [0.49,0.49,0]. A periodic image '
     'displaced by [-1,0,0] is closer than the componentwise-wrapped image.',
     '',
     'The [reproducer](gams-candidates/raffle-skew/README.md) retains the exact source, pin, '
     'normalized hash and complete failed result. It tests the specified-atom API; general skew-cell '
     'behavior is not promoted by the successful orthogonal driver. The failed probe is not registered '
     'as a checked driver. No source patch, relaxed comparison or disabled bounds check was '
     'introduced.',
     '',
     '## Sources, licenses and actual output',
     '',
     "Independent drivers have their own MIT notice; upstream terms remain separate. Formal's original "
     'Berkeley Lab terms, including its enhancements clause, remain in the [retained '
     'license](fpm-candidates/formal/licenses/LICENSE.txt); the library is not relabeled plain '
     'BSD-3-Clause. RAFFLE retains its GPL-3.0 terms. These are independent API consumers, not copies '
     'of upstream example bodies. Loading a link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def expressions_sky_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-expressions-sky-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-expressions-sky-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked expressions and sky-coordinate rotations',
     '',
     'These N3 and P drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing package libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-expressions-sky-validation.json) retains pins, source hashes, stdout and stderr. GAMS '
     'categories are not exhausted.',
     '',
     '## FEQParse multivariable expression evaluation (N3)',
     '',
     'Twelve valid real64 expressions cover arithmetic, parentheses, powers, pi, trigonometric functions, '
     'exp, log, sqrt, abs and compositions. Each is evaluated on a 7 by 7 by 7 grid: x,y,z range from -1.5 '
     'to 1.5 in steps of 0.5. These 343 tuples stay inside the real domains of every expression.',
     '',
     'There are 24 parser objects: one with declarations [x,y,z] and one with [z,y,x] for each expression. '
     'Scalar and batch evaluations use correspondingly reordered inputs; reversed declarations are also '
     'evaluated in reverse scalar traversal. All 16,464 outputs are checked against direct native Fortran '
     'formulas, rather than merely against another parser call. Quartics use explicit products; the real '
     'power 2**(x/2) uses exp(log(2)*x/2) as its reference. Inputs must remain unchanged.',
     '',
     'Every output must be finite and abs(result-reference)/(1+abs(reference)) <= 2e-12. The maximum saved '
     'error is 9.1974e-17. The run retains array-temporary warnings for noncontiguous row sections passed '
     'to scalar evaluation; bounds checking was not disabled. This verifies selected valid real64 '
     'expressions and variable binding, not complete grammar coverage, malformed-input recovery, custom '
     'functions, other precisions/ranks or symbolic algebra.',
     '',
     '## astro-fortran Galactic/ICRS directions (P)',
     '',
     'The independent reference applies three elementary passive rotations sequentially, using the defining '
     'pole right ascension 192.85948 degrees, pole declination 27.12825 degrees and node longitude 32.93192 '
     'degrees. It does not copy the library matrix or author test body. For ICRS to Galactic it applies '
     'z(pi/2+pole_ra), x(pi/2-pole_dec), z(-node); the opposite direction uses the inverse sequence. A '
     'passive z rotation maps (x,y) to (cos(a)*x+sin(a)*y,-sin(a)*x+cos(a)*y), with the analogous y,z rule '
     'for x rotations.',
     '',
     'There are 24 longitude samples, nine latitudes [-90,-75,-45,-10,0,10,45,75,90] degrees, and three '
     'longitude shifts [-4*pi,0,6*pi] in each starting frame. The 1,296 direction fixtures exercise 2,592 '
     'forward/inverse calls. Every forward output is compared with an independently rotated Cartesian unit '
     'vector, and every round trip with its original input vector. Longitude equality at a pole is '
     'deliberately not required.',
     '',
     'Direct and roundtrip vector discrepancies and unit-norm errors must each be <= 2e-12. Saved maxima '
     'are 8.9509e-16, 9.4857e-16 and 2.2204e-16 respectively. Output angles must be finite and within the '
     'canonical intervals with an absolute endpoint allowance of 64 real64 machine epsilons. An initial '
     'strict [0,2*pi) assertion encountered exactly 2*pi from wrapping a tiny negative angle; the roundoff '
     'allowance addresses that equivalent direction without changing vector accuracy checks. No assertion '
     'about precession, proper motion, astrometric corrections, unrelated coordinate APIs or physical '
     'accuracy of the frame definition follows.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned implementations and author tests were reviewed before writing these independent API consumers. '
     "The drivers have their own MIT notice. Upstream package terms, including astro-fortran's retained "
     'SOFA-derived notices, remain separate; the package sources and author test bodies are not relabeled '
     'or copied. Loading a driver link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def unsigned_bitsets_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-unsigned-bitsets-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-unsigned-bitsets-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked unsigned arithmetic and operable bitsets',
     '',
     'These A1 and N2 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-unsigned-bitsets-validation.json) retains exact source hashes, pins, build logs and '
     'program output. GAMS categories are not exhausted.',
     '',
     '## uint-fortran fixed-width integers (A1)',
     '',
     'The independent driver checks uint8, uint16 and uint32 against ordinary integer(int64) formulas. Each '
     'width uses 24 operand fixtures, including zero, one, powers-of-two boundaries, the signed midpoint '
     'and neighbors, the unsigned maximum and neighbors, and fractions of the modulus. Some small-width '
     'fixtures coincide; these are 1,728 operand pairs across the three widths, not a claim of distinct '
     'values in every fixture.',
     '',
     'Each pair checks addition and subtraction modulo 2**width, division when the divisor is nonzero, all '
     'six relational operators, and preservation of both operands. Conversions are checked for every '
     'outer-loop fixture. Nine negative int64 assignments per width include -1, -128, -256, -257, -65536 '
     'and -4294967295; their references use the nonnegative Fortran MODULO result. In total, 17,307 exact '
     'checks passed. The int64 oracle safely contains all tested sums, differences and quotients.',
     '',
     'The checks exercise carry, borrow, unsigned ordering above the signed boundary, truncating '
     'nonnegative integer division and assignment conversion. Multiplication, powers, mixed-kind operators, '
     'uint64 and C interoperability remain unverified. This is fixed-width arithmetic, not '
     'arbitrary-precision integer validation. The driver does not change library source or compiler '
     'overflow settings.',
     '',
     '## ORBS bitset operators (N2)',
     '',
     'Eleven widths [1,4,8,31,32,63,64,65,127,128,129] cross storage-word boundaries. Each width uses 16 '
     'deterministic patterns: zero, all ones, low/high endpoint bits and modularly generated binary '
     'strings. Patterns can coincide at small widths. Every ordered pair is tested, giving 2,816 operand '
     'pairs.',
     '',
     'AND, OR, XOR and ANDNOT references are built one character at a time from logical truth tables. '
     'Addition and subtraction use independent base-two schoolbook carry/borrow arithmetic, discarding the '
     'final carry/borrow to model fixed width. These references call neither ORBS nor its stdlib/bstrith '
     'dependencies. Every input pattern also checks NOT and every shift from 1-width through width-1, '
     'including zero. Shift references relocate individual characters and fill vacated positions with '
     'zeros; undefined shifts outside the documented range are not attempted.',
     '',
     'All 37,760 binary-string references must match exactly and retain their expected width. Pair '
     'operations must preserve both operands. Multiword carry/borrow and shifts are exercised, including '
     '65-, 127-, 128- and 129-bit values. Mixed widths, zero-length sets, mutation methods, sorting, '
     'formatted I/O and malformed-input handling remain unverified. This driver supports the N2 mapping; it '
     'does not automatically promote the sibling A1 mapping for the same procedure record.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned operator/conversion implementations and available author tests were reviewed. The '
     'independently written API consumers have their own MIT notice; upstream terms remain separate. No '
     'upstream test bodies are copied. The ORBS record has no pinned author example recorded, so its API '
     'source was reviewed directly. Loading a driver does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def sparse_advection_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-sparse-advection-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-sparse-advection-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked sparse systems and periodic advection',
     '',
     'These D2 and I2 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-sparse-advection-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## HeatFlow sparse BiCG systems (D2)',
     '',
     'Four matrix sizes [5,9,17,33], three banded families and three scales [0.125,1,8] give 36 matrices. '
     'All are strictly row-diagonally dominant with positive diagonals: the first family is symmetric '
     'tridiagonal, the second changes the upper band to make it nonsymmetric, and the third adds unequal '
     'second bands. Sparse storage must retain exactly the nonzero count of the original dense matrix.',
     '',
     'Each matrix is solved for three manufactured solutions (constant, alternating with varying magnitude, '
     'and a shifted sine), using zero and nonzero initial guesses. All 216 solves check 3,456 known '
     'solution entries. Right-hand sides and true residuals are formed with independent scalar dense sums, '
     'not the library multiply routine. Right-hand sides must remain unchanged. The sparse allocation is '
     'released between matrices.',
     '',
     'The requested relative L2 tolerance is 1e-11 with stopping mode 1 and a 500-iteration cap. Returned '
     'values and solver error must be finite, iterations must lie in [1,500], and the reported error must '
     'be <= 1.01e-11. Independently, max(abs(x-x_exact))/(1+max(abs(x_exact))) must be <= 2e-9 and '
     'max(abs(A*x-b))/(1+max(abs(b))) <= 2e-10. Saved maxima are 2.5522e-11 and 2.3739e-11 respectively. '
     'These modest, well-conditioned systems do not verify singular/indefinite behavior, other stopping '
     'modes, parallel execution or the full HeatFlow evolution/Cattaneo application.',
     '',
     '## HR-WENO periodic finite-volume advection (I2)',
     '',
     'The independent consumer solves u_t+c*u_x=0 on a unit periodic interval using WENO k=3 reconstruction '
     'and third-order TVD Runge-Kutta. It supplies three ghost cells on each side and selects right states '
     'for positive velocity or left states for negative velocity. The two endpoint fluxes are identical, '
     'making the semidiscrete flux sum telescope. This exercises spatial reconstruction in a PDE, rather '
     'than only the package time integrator.',
     '',
     'Three grids [64,128,256], modes [0,1,2], velocities [-1.5,0.75], phase origins [0,0.37], and '
     '(mean,amplitude) pairs [(1.25,0.2),(-0.5,-0.3)] give 72 problems. Mode zero supplies constant-state '
     'tests. Initial data are exact cell averages: '
     'mean+amplitude*sin(pi*m*dx)/(pi*m*dx)*sin(2*pi*m*(x-origin)), with the zero-mode factor defined as '
     'one. The step is 0.2*dx/abs(c). Two continued calls request travel distances 0.0625 and 0.125, '
     'producing 144 checkpoints and 21,504 analytic cell-average references.',
     '',
     'This fixed-step API returns the first time beyond the requested time rather than interpolating to it. '
     'The harness initially assumed exact output times; source review corrected that assumption. Returned '
     'time must be finite and between the requested time and one step beyond it, with a 1e-12 roundoff '
     'allowance. The analytic reference shifts the wave by c times the actual returned time.',
     '',
     'Every cell must be finite. Constant-state maximum error must be <= 5e-12. For nonzero mode m, the '
     'maximum absolute error bound is 5e-12+0.002*abs(amplitude)*(m*64/n)**2. This is an explicit '
     'resolution/frequency-dependent acceptance bound, not a claim of a measured convergence order. Every '
     'normalized mass error abs(sum(u)*dx-mean)/(1+abs(mean)) must be <= 5e-12. The saved maximum '
     'amplitude-scaled cell error is 8.0028e-5, the largest error divided by its fixture bound is '
     '1.0004e-2, and the maximum normalized mass error is 6.9081e-16. Nonuniform grids, shocks, nonlinear '
     'fluxes, multidimensional equations and formal convergence rates remain unverified.',
     '',
     '## Preserved k=2 accuracy-threshold result',
     '',
     'A k=2 probe built but exceeded the proposed accuracy bound: the first failing 64-cell mode-one '
     'negative-velocity fixture had maximum cell error 1.4202932710161154e-3 versus bound '
     '4.0000000500000000e-4. This is not an established algorithm defect. Spatial/time discretization error '
     'requires a convergence study before judging that configuration; the k=3 suite alone does not verify '
     'k=2.',
     '',
     'The [preserved probe](gams-candidates/hrweno-k2-accuracy/README.md) retains its exact source, pin, '
     'normalized hash and complete result. It is not registered as a checked driver. The successful suite '
     'keeps the same reference and bounds, restricted to k=3; no comparison was relaxed and no library '
     'source or bounds checking was changed.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned implementations and the HR-WENO author conservation-law example were reviewed before writing '
     'these independent API consumers. The drivers and preserved probe have their own MIT notice. HeatFlow '
     'retains its GPL-3.0 terms, and HR-WENO its MIT terms; upstream test and implementation bodies are not '
     'copied or relabeled. The HeatFlow record has no pinned author example, so its source was reviewed '
     'directly. Loading a link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def products_partitions_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-products-partitions-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-products-partitions-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked matrix products and graph partition objectives',
     '',
     'These D1 and P drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-products-partitions-validation.json) retains source hashes, pins and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## ForMatmul matrix products (D1)',
     '',
     'Six (rows,inner,columns) shapes [(1,1,1),(1,3,2),(2,1,4),(2,3,5),(5,4,3),(7,5,9)] include rectangular '
     'and unit dimensions. Three deterministic input families exercise a zero left matrix, signed dyadic '
     'fractions and non-dyadic sine/cosine values with offsets. Scalar triple loops form every reference '
     'entry and its sum of absolute products; the oracle calls neither package nor intrinsic MATMUL.',
     '',
     'Methods m1 through m4 each test default matrix multiplication and all four explicit paired transpose '
     'combinations. Transposed storage represents the same logical matrices, so the reference is identical '
     'across those variants. Matrix-vector products use a column of the right-hand matrix, with absent, '
     'false and true transpose settings. This gives 360 matrix-matrix calls and 216 matrix-vector calls, '
     'checking 6,588 scalar entries.',
     '',
     'Output shape and finite values are required. Every abs(result-reference)/(1+sum(abs(a_i*b_i))) must '
     'be <= 128*epsilon(rk)*inner_dimension. The saved maximum scaled error is 1.6933e-16. Zero and dyadic '
     'fixtures must additionally agree exactly; all products and sums in these small fixtures are '
     'representable in the working binary precision. Both input matrices must remain unchanged.',
     '',
     'The existing single-false-transpose-flag failures at this pin remain in [the retained '
     'probes](fpm-candidates/formatmul/false-transpose-checks.json), with '
     '[transA=false](fpm-candidates/formatmul/transa-false.f90) and '
     '[transB=false](fpm-candidates/formatmul/transb-false.f90) sources. The checked matrix-matrix calls '
     'always supply both transpose flags whenever either is present. The single matrix-vector flag uses its '
     'separate API and is checked independently. No library patch or disabled bounds checking is '
     'introduced. Methods beyond m4, complex inputs, multiple images, distributed execution and performance '
     'remain unverified.',
     '',
     '## METIS k-way graph partitions (P)',
     '',
     'Three sizes [12,24,48], three connected graph families (cycles, four-column rectangular grids, and '
     'three linked cliques), and unit/unequal positive edge weights give 18 graphs. Each graph is '
     'partitioned into two and three parts using seeds [1,42,93], for 108 METIS_PartGraphKway calls and '
     '3,024 assigned vertices. Adjacency is symmetric and uses zero-based C numbering.',
     '',
     'Every call must return METIS_OK, label every vertex in [0,nparts-1], populate every requested part '
     'and keep each part no larger than 1.5*n/nparts. This is a coarse population check, not a proof that '
     'every requested imbalance bound is met. The weighted edge-cut objective is independently recomputed '
     'once per undirected edge from the original dense upper triangle, rather than the CSR passed to METIS. '
     'Each of the 108 exact objectives must equal the returned edgecut. CSR offsets, neighbors and edge '
     'weights must remain unchanged. The observed part populations range from 4 to 26 across the suite.',
     '',
     'No expected label sequence is imposed: swapping part numbers leaves a valid partition unchanged. The '
     'driver does not prove global optimality, heuristic reproducibility, mesh partitioning, nested '
     'dissection, vertex-weight constraints, communication-volume objectives or invalid-input handling.',
     '',
     '## Preserved METIS option-index failure',
     '',
     'The pinned Fortran interface declares UFACTOR at index 18 and NUMBERING at index 19, while the '
     'bundled C enum uses 17 and 18. SEED is index 9 in both. A valid cycle-graph probe using the named '
     'Fortran NUMBERING=0 and UFACTOR=100 settings builds but prints Input Error: Incorrect numflag. The C '
     'code reads 100 as the numbering flag and rejects it.',
     '',
     'The [preserved probe](gams-candidates/metis-option-indices/README.md) includes exact source, pin, '
     'normalized hash, C-header hash and full result. The successful driver leaves numbering at its default '
     'zero, uses the matching SEED constant and passes imbalance through the typed ubvec=[1.1_real_t] '
     'argument. It does not hard-code replacement option indices or change library source, CSR checks or '
     'objective comparisons. Other option constants are not verified by this workaround.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned implementations, C declarations and available author tests were reviewed before writing these '
     'independent consumers. Their own MIT notice covers the drivers and preserved variants. ForMatmul '
     'retains BSD-3-Clause terms; metis-fpm retains its MIT wrapper and Apache-2.0 METIS/GKlib terms. No '
     'upstream implementation or test body is copied or relabeled. The METIS record has no pinned author '
     'example, so its interface and bundled C source were reviewed directly. Loading a link does not submit '
     'a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def multidimensional_fft_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-multidimensional-fft-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-multidimensional-fft-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked multidimensional complex Fourier transforms',
     '',
     'These J1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing '
     'libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-multidimensional-fft-validation.json) retains pins, source hashes and complete output. '
     'GAMS categories are not exhausted.',
     '',
     '## Independent Fourier references',
     '',
     'Each shape uses eight deterministic complex fixtures: zero, a nonzero complex constant, an origin '
     'impulse, an off-origin complex impulse, two axis-dependent plane waves with different '
     'positive/negative frequencies, mixed signed dyadic data and a general nonperiodic sine/cosine '
     'mixture. Off-origin impulses and axis-dependent waves test phase and axis order, which an origin '
     'impulse alone cannot distinguish.',
     '',
     'For every forward coefficient, independent nested scalar loops sum '
     'data(i,j,k)*exp(-2*pi*imaginary_unit*(a*i/nx+b*j/ny+c*k/nz)), with zero-based spatial and frequency '
     'indices. The exponential is formed from native sine/cosine values. The 2-D driver uses nz=1. The '
     'oracle calls neither FFT library nor another FFT implementation.',
     '',
     'Each fixture then tests the inverse using the independently calculated coefficients divided by the '
     'total number of points N. The expected inverse is the original complex data. A separate third call '
     'applies the inverse to the saved library-forward output divided by N, checking a round trip as '
     'additional evidence. The independent inverse input prevents matching forward/inverse errors from '
     'being the only test.',
     '',
     'All complex results must have finite real and imaginary components. Maximum forward coefficient error '
     'divided by 1+sum(abs(original)) must be <= 2e-12. Maximum independent-inverse and roundtrip errors '
     'divided by 1+max(abs(original)) must each be <= 2e-12. Parseval checks '
     'abs(sum(abs(forward)**2)-N*sum(abs(original)**2))/(1+N*sum(abs(original)**2)) <= 2e-12. Small zero '
     'inputs remain well-defined under these scalings.',
     '',
     '## dtFFT 2-D CPU/FFTW plans (J1)',
     '',
     'Shapes [4,6], [5,7] and [8,8] include unequal axes, prime lengths and a square grid. There are 24 '
     'fixtures and 72 execute calls: 984 forward coefficients, 984 independent inverse entries and 984 '
     'roundtrip entries, totaling 2,952 complex references. Three estimate-mode plans use the FFTW3 '
     'executor on exactly one MPI process. Every exposed MPI/dtFFT status is checked.',
     '',
     'The physical input uses Fortran shape [nx,ny], but the Fourier output is a Y-aligned pencil with '
     'Fortran shape [ny,nx]. Local starts must be zero and local counts must match these layouts. The '
     'harness initially assumed equal physical/spectral shapes; source review and the rectangular-grid '
     'counts corrected that assumption. It explicitly transposes the output back to logical x/y order for '
     'comparison and transposes independent Fourier input into Y-pencil order for the inverse. Square-grid '
     'fixtures retain this same mapping.',
     '',
     'Saved maximum normalized forward, independent-inverse, roundtrip and Parseval errors are 1.7516e-15, '
     '5.0619e-15, 2.0015e-16 and 3.8611e-16. A fresh block-scoped plan object is used for each shape; all '
     'eight fixtures repeatedly execute that live plan before explicit buffer release and destruction. '
     'Recreating a destroyed plan object is not verified by this successful driver.',
     '',
     '## 2DECOMP&FFT 3-D generic CPU transforms (J1)',
     '',
     'Shapes [4,3,2], [5,4,3] and [6,5,4] exercise unequal axes and mixed factorization sizes with the '
     'built-in generic CPU backend. There are 24 fixtures and 72 transform calls: 1,632 forward '
     'coefficients, 1,632 independent inverse entries and 1,632 roundtrip entries, totaling 4,896 complex '
     'references.',
     '',
     'Exactly one MPI process uses a 1-by-1 process grid, physical-X input and spectral-Z output. Both '
     'arrays have full logical x/y/z indexing in this one-process configuration, and their shapes are '
     'checked. Buffers, FFT state and the decomposition are finalized between shapes. Saved maximum '
     'normalized forward, independent-inverse, roundtrip and Parseval errors are 1.6165e-14, 2.0123e-14, '
     '9.0006e-15 and 3.6096e-15.',
     '',
     '## Preserved dtFFT plan-recreation failure',
     '',
     'A probe that creates, executes and destroys one plan, then creates another shape in that same object, '
     'fails with an already-allocated-component runtime error. At the pinned source, destroy releases '
     'self%fft but leaves self%fft_mapping allocated; the next create tries to allocate it again. The '
     '[retained reproducer](gams-candidates/dtfft-plan-recreate/README.md) includes exact source, pin, '
     'normalized hash and full build/run result.',
     '',
     'The checked driver keeps the same numeric comparisons and uses fresh plan objects rather than '
     'patching private library components or disabling runtime checks. Its block exit releases remaining '
     'allocatable components. Repeated execution is verified; general cleanup correctness, destroyed-object '
     'recreation and long-running memory behavior are not. No comparison was relaxed.',
     '',
     '## Scope, native diagnostics and licenses',
     '',
     'Both successful results retain a UCX diagnostic about scandir(/sys/class/net) in stdout. MPI '
     'initialization/finalization statuses and the numerical checks nevertheless passed. The complete '
     'diagnostic is preserved in the verification report; these runs do not establish distributed '
     'communication behavior.',
     '',
     'These are one-process, double-precision complex transforms. Multiple MPI processes, distributed '
     'scaling, real transforms, GPU execution, other executors, large-size accuracy and performance remain '
     'unverified. Pinned implementations and author examples were reviewed without copying their bodies. '
     'The independent drivers and preserved probe have their own MIT notice; dtFFT retains GPL-3.0-or-later '
     'and 2DECOMP&FFT BSD-3-Clause terms. Loading a driver does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def sparse_spectra_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-sparse-spectra-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-sparse-spectra-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked sparse column updates and symmetric spectra',
     '',
     'These D2a4 and D4a1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted '
     'sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-sparse-spectra-validation.json) retains pins, source hashes and complete output. GAMS '
     'categories are not exhausted.',
     '',
     '## LUSOL factorization, single update and transpose solves (D2a4)',
     '',
     'Sizes [2,3,5,8], two nonsymmetric banded families, scales [0.25,2], and '
     'original/first-last-row-swapped matrices give 32 sparse LU factorizations. The base diagonal is '
     '4+i/n, with lower/upper bands -0.5 and -1; the second family adds bands 0.25 and -0.125. Row swaps '
     'exercise pivot permutations without changing the system condition.',
     '',
     'Each factorization is used before and after one replacement of column one. The new unpermuted column '
     'has off-diagonal entries 0.125*sin(i+2) and diagonal 6+1/8, then receives the same scale and row '
     'permutation. The consumer uses the public 64-bit index kind and the parameter defaults documented by '
     'the EZ wrapper. Workspace capacity is 10,000 entries. These small fixtures do not test workspace '
     'exhaustion.',
     '',
     'Three exact solution patterns (constant, alternating with varying magnitude, and a shifted sine) each '
     'supply a normal and transpose system at both states. All 384 solves check 1,728 known solution '
     'entries. Scalar dense loops form right-hand sides and true residuals, calling no package matrix '
     'multiply. Solve modes 5 and 6 use their documented, different output arrays. Factorization, update '
     'and solve statuses must all be zero; solutions and update diagnostics must be finite.',
     '',
     'Both max(abs(x-x_exact))/(1+max(abs(x_exact))) and max(abs(A*x-b))/(1+max(abs(b))) must be <= 5e-12, '
     'with A transposed for mode 6. Saved maxima are 2.2204e-16 and 5.1194e-16. Singular/rectangular '
     'systems, rank-changing updates, other pivot policies and multiple replacements on one factorization '
     'remain unverified.',
     '',
     '## Preserved repeated-update accuracy probe',
     '',
     'A two-update probe exceeded the same 5e-12 bounds after replacing columns one and eight in an 8-by-8 '
     'fixture: normalized solution error 1.0743406164692715e-11 and true residual 8.7795268635037098e-12. '
     'Successful statuses alone therefore do not establish the requested accuracy. The [retained '
     'probe](gams-candidates/lusol-drop-tolerance/README.md) includes exact source, pin, normalized hash '
     'and full result. This is not an established algorithm defect or diagnosis of a drop-tolerance '
     'problem.',
     '',
     'The successful driver restricts its scope to one replacement and keeps the original solver settings '
     'and comparison bounds. It does not claim repeated-update accuracy. No library patch, relaxed '
     'comparison or disabled bounds checking was introduced.',
     '',
     '## ScaLAPACKFX prescribed symmetric spectra (D4a1)',
     '',
     'Exactly one MPI process uses a 1-by-1 BLACS grid. Sizes [2,3,5,8], three prescribed spectra, '
     'diagonal/Givens-rotated bases, scales [0.125,4], shifts [-2,0.75], lower/upper storage and block '
     'sizes [1,2] give 384 eigensystems and 1,728 eigenvalue references. Both input and eigenvector local '
     'shapes must be n-by-n.',
     '',
     'The three base spectra are i-(n+1)/2, 1+i*i/n, and floor((i-1)/2)-1, with indices i=1..n. The third '
     'includes repeated eigenvalues; combinations of scale and shift include positive, negative and mixed '
     'spectra. Two sweeps of elementary adjacent-column Givens rotations build the nontrivial orthogonal '
     'basis Q. Scalar sums construct A=Q*diag(lambda)*transpose(Q); sorted eigenvalues are known from the '
     'scaled/shifted input spectrum.',
     '',
     'The unused half of A is filled with quiet NaNs before scalafx_psyev(jobz=V,uplo=L/U), checking that '
     'each triangle-storage choice uses the intended entries. Descriptor and eigensolver statuses must be '
     'zero, and all returned eigenvalues/eigenvectors finite. The maximum eigenvalue error divided by '
     '1+max(abs(expected)) must be <= 5e-12. Scalar loops check every eigenpair residual divided by '
     '1+norm_infinity(A), and every entry of transpose(V)*V-I, each within 5e-12. Eigenvector signs and '
     'bases inside repeated-eigenvalue subspaces are deliberately not prescribed.',
     '',
     'Saved maximum normalized eigenvalue, eigenpair and orthogonality errors are 1.0151e-15, 6.4223e-16 '
     'and 2.2204e-15. Matrices/descriptors are recreated for every storage/block choice. Generalized or '
     'complex eigensystems, multiple MPI processes, distributed scaling, large/ill-conditioned matrices and '
     'performance remain unverified.',
     '',
     '## Sources, diagnostics and licenses',
     '',
     'Pinned implementations and author tests were reviewed before writing these independent API consumers. '
     'The drivers and preserved probe have their own MIT notice; upstream LUSOL and ScaLAPACKFX terms '
     'remain separate. No upstream implementation or test bodies are copied or relabeled. The successful '
     'ScaLAPACKFX run retains a native UCX scandir(/sys/class/net) diagnostic in stdout; BLACS setup, '
     'solver statuses and numeric checks passed, without establishing distributed communication behavior. '
     'Loading a link does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def projection_lbfgs_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-projection-lbfgs-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-projection-lbfgs-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked constrained projections and L-BFGS quadratics',
     '',
     'These G2h3b1b and G1b1b drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted '
     'sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-projection-lbfgs-validation.json) retains pins, source hashes and actual output. GAMS '
     'categories are not exhausted.',
     '',
     '## PSQP ball-and-plane projection (G2h3b1b)',
     '',
     'The consumer minimizes f(y)=0.5*sum((y-t)**2), y=x-center, subject to y(1)=h and sum(y**2)<=R**2. '
     'Analytic objective gradients and the full constraint Jacobian are supplied through callbacks; their '
     'call counts must be positive. This exercises a nonlinear inequality and an equality, with simple '
     'variable bounds disabled. The feasible set is convex and the quadratic objective strictly convex, so '
     'the analytic projection is the unique global minimizer for these fixtures.',
     '',
     'Dimensions [2,3,5], radii [0.5,2], zero/translated centers, two signed target directions and '
     'feasible/infeasible ball starts give 48 problems and 160 optimizer-coordinate references. The plane '
     'height is h=R/4. Targets have t(1)=0.7*R and norm(t(2:))=2*R. Starts satisfy the plane and set the '
     'free coordinates to 0.25 or 1.25 times the target coordinates, putting them inside or outside the '
     'ball.',
     '',
     'Let r=sqrt(R**2-h**2). The exact solution has y_star(1)=h and y_star(2:)=r*t(2:)/norm(t(2:)). '
     'Independent multipliers are mu=(norm(t(2:))/r-1)/2 and nu=t(1)-(1+2*mu)*h, with mu positive. They '
     'satisfy stationarity (1+2*mu)*y_star-t+nu*e1=0 for L=f-mu*(R**2-sum(y**2))+nu*(y(1)-h). The reference '
     'objective is evaluated directly at y_star.',
     '',
     'Only convergence statuses 1 through 4 are accepted; iteration/evaluation limits and negative statuses '
     'fail. The callback and returned objective/gradient/constraint summaries must be finite. Coordinate '
     'error normalized by 1+max(abs(y_star)) must be <= 2e-5, objective error normalized by 1+f_star <= '
     '5e-8, and the maximum normalized plane/ball violation <= 2e-7. The residual using the independent '
     'analytic multipliers, divided by 1+norm(t), must be <= 5e-5. Returned f must also agree with direct '
     'evaluation within normalized error 5e-8. Solver-reported residuals alone are not the acceptance test.',
     '',
     'Saved maximum coordinate, objective, feasibility and stationarity errors are 5.7909e-12, 9.9295e-12, '
     '1.3172e-11 and 6.7059e-12 respectively. These checks do not verify active variable bounds, nonconvex '
     'constraints, arbitrary equality manifolds or general global optimization.',
     '',
     '## SEISCOPE L-BFGS SPD quadratics (G1b1b)',
     '',
     'Dimensions [2,3,5], condition ratios [1,5,25], diagonal/rotated Hessians, scales [0.25,2] and three '
     'starts give 108 minimizations and 360 known minimizer entries. Diagonal cases are centered at zero; '
     'rotated cases use quarter-integer centers. Elementary adjacent-column rotations construct Q, and '
     'scalar sums form H=scale*Q*diag(lambda)*transpose(Q), with linearly spaced positive eigenvalues from '
     '1 to the requested condition ratio.',
     '',
     'The Hessian is rounded to the library callback precision and explicitly symmetrized there. With these '
     'small, well-conditioned matrices, rounding is far smaller than the smallest positive eigenvalue. The '
     'objective is 0.5*(x-center)^T*H*(x-center), with analytic gradient H*(x-center). Its unique minimizer '
     'is center, with zero objective and gradient. Default real is real32 in this GNU 16 image. Native '
     'callbacks use scalar loops; a separate real64 audit uses the actual rounded matrix coefficients and '
     'returned coordinates.',
     '',
     'The optimizer uses memory length 10, iteration limit 1,000 and relative cost tolerance 1e-12. '
     'Reverse-communication requests are capped at 20,000 and only flags 1 through 4 are allowed; '
     'termination must be convergence flag 2, not line-search failure flag 4. Flag 1 recomputes the '
     'objective and gradient, while flag 3 continues with the accepted step. Every native callback result '
     'must be finite.',
     '',
     'Independent endpoint checks require max(abs(x-center))/(1+max(abs(center))) <= 2e-3, absolute real64 '
     'objective divided by 1+initial_cost <= 2e-7, and maximum absolute real64 gradient divided by '
     '1+norm_infinity(H) <= 2e-4. The normalized native-versus-real64 objective/gradient discrepancy must '
     'be <= 64*epsilon(real32). Saved maxima are 1.0656e-5 for coordinates, 9.1633e-13 for objective, '
     '1.7733e-6 for gradient and 3.2135e-12 for the callback discrepancy.',
     '',
     'The cached package already contains the guarded catalog edit replacing an uninitialized '
     'workspace-length argument l with optim%l in descent_LBFGS. This driver reuses that existing build and '
     'does not introduce another library patch. The exact edit and original source hash remain in [the '
     'package manifest](../fpm_catalog.json) under catalog_patches. Its upstream source link therefore '
     'documents the original revision, while the effective build includes the disclosed edit.',
     '',
     'Nonquadratic or nonconvex objectives, constrained L-BFGS operation, other precisions, other SEISCOPE '
     'optimizer methods and performance remain unverified. A successful quadratic suite does not establish '
     'their convergence behavior.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned APIs/implementations and author tests were reviewed before writing these independent API '
     'consumers. The drivers have their own MIT notice; upstream PSQP and SEISCOPE license terms remain '
     'separate. No upstream test or implementation bodies are copied or relabeled. Loading a driver does '
     'not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def gradient_swarm_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-gradient-swarm-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-gradient-swarm-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked fixed gradient steps and seeded particle swarms',
     '',
     'These G1b and G2i drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-gradient-swarm-validation.json) retains pins, source hashes and complete output. GAMS '
     'categories are not exhausted.',
     '',
     '## ForTimize fixed-step gradient descent (G1b)',
     '',
     'The independent consumer minimizes SPD quadratics f(x)=0.5*(x-center)^T*H*(x-center). Dimensions '
     '[2,3,5], condition ratios [1,5], diagonal/rotated Hessians, step settings [0.5,1.5]/lambda_max, '
     'iteration counts [1,2,5,25,100] and two starts give 240 runs and 800 coordinate references. Centers '
     'are quarter-integers; starts have positive or alternating displacements. Elementary adjacent-column '
     'rotations construct Q and scalar sums form H=Q*diag(lambda)*transpose(Q), with explicit '
     'symmetrization in working precision.',
     '',
     'An independent spectral reference computes '
     'x_N=center+Q*diag((1-step*lambda)**N)*transpose(Q)*(x_0-center), and the analogous previous point and '
     'objective. Steps remain strictly inside the SPD stability interval; the larger setting exercises '
     'sign-alternating contraction in the highest mode. The gradient callback must be requested exactly N '
     'times. The implementation uses max_iters as a fixed count and does not use convergence_tolerance for '
     'early termination.',
     '',
     'Every returned point and objective must be finite. Coordinate discrepancies, scaled by '
     '1+max(abs(x_0-center)), must be <= 2e-12. Objectives are compared with the spectral sums using scale '
     '1+f_0 and the same 2e-12 bound. Recomputed endpoint cost must not exceed initial cost beyond '
     'roundoff, and f_100/f_0 must be <= 1e-8. Saved maximum point, returned-cost and endpoint-cost '
     'discrepancies are 1.8504e-16, 1.7504e-16 and 1.2643e-16. The largest f_100/f_0 is 4.6923e-10.',
     '',
     '## Verified returned-objective caveat',
     '',
     'At this pinned [gradient-descent '
     'implementation](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/with_derivatives/gradient_descent.f90#L23), '
     'the callback evaluates F before each update and the routine does not refresh F after the final '
     'update. Returned X is x_N, but returned F is f(x_(N-1)). The driver explicitly checks the '
     'preceding-iterate reference, then recomputes the objective at returned X. It does not present the '
     'stale value as the endpoint objective.',
     '',
     'The first one-step fixture returns 0.625 while the endpoint objective is 0.15625. This discrepancy is '
     'printed in the successful proof and is visible when the example is run. No library source patch or '
     'relaxed numeric comparison was introduced. The dedicated test establishes fixed-step behavior on '
     'these quadratics, not adaptive stopping, a reliable final-objective API, arbitrary step choices or '
     'nonquadratic convergence.',
     '',
     '## Opti seeded shifted Rastrigin search (G2i)',
     '',
     'Two and three dimensions, amplitudes A=[1,10] and seeds [314159,271828,161803] give 12 bounded '
     'stochastic searches and 30 known minimizer entries. Centers have coordinates (i-2)/4, and each '
     'coordinate is bounded by center plus/minus 3. The objective is sum(d**2+A*(1-cos(2*pi*d))), '
     'd=x-center. Every term is nonnegative; zero is attained uniquely at center, providing an analytic '
     'global reference for these nonconvex multimodal benchmarks.',
     '',
     'Each call uses 80 particles, a 1,200-generation cap, desired_error=1e-10 and adaptive topology 2. The '
     'GNU random-seed array is initialized with seed(i)=base_seed+37*i after querying its required size. '
     'The resulting positions must be finite and inside their boxes. Callback counts must be positive and '
     'within the conservative 2*80*(1200+2) bound; the successful run used 644,800 optimizer callback '
     'evaluations overall.',
     '',
     'An independent identity evaluates the returned objective as sum(d**2+2*A*sin(pi*d)**2), avoiding '
     'subtraction of nearly equal cosine values near a minimum. It must agree with the callback formula '
     'within 2e-12*(1+reference). The independent objective must be <= 1e-5 and maximum coordinate distance '
     'from center <= 1e-3. Saved maxima are 9.8261e-11 and 1.6632e-6 respectively.',
     '',
     'These are recorded successful seeds and work budgets, not a global-convergence guarantee or a '
     'measured success probability. The RNG sequence is not claimed portable across compilers or versions. '
     'The API exposes no termination status, so the driver checks results independently instead of '
     'interpreting an unavailable success flag. Other topologies, dimensions, bound-active optima, '
     'arbitrary multimodal landscapes and performance remain unverified. The package prints progress during '
     'each call; this review shows its final verification summary, while the complete progress output '
     'remains in the saved report.',
     '',
     '## Sources, licenses and actual output',
     '',
     'Pinned implementations and author API examples were reviewed before writing these independent '
     'consumers. Their own MIT notice covers only these drivers. ForTimize upstream licensing remains '
     'unspecified; the driver notice does not relicense the package, and no upstream example body is '
     'copied. Opti retains its GPL-2.0-or-later terms. Loading a driver does not submit a job.',
     '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        if d['id'] == 'opti-rastrigin-reference':
            output = output[output.index('Swarm verification summary:'):]
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def projection_training_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-projection-training-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-projection-training-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked halfspace projections and affine-network training',
 '',
 'These G2h3b1b and G1b drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted '
 'sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-projection-training-validation.json) retains pins, source hashes and complete output. '
 'GAMS categories are not exhausted.',
 '',
 '## Optgra weighted halfspace projections (G2h3b1b)',
 '',
 'The independent consumer minimizes f(x)=0.5*sum(h_i*(x_i-c_i)**2) subject to a dot (x-c)>=b. Every '
 'h_i is positive and b>0. The unconstrained minimizer c is infeasible; the unique constrained '
 'minimizer is x_star=c+lambda*a/h, with lambda=b/sum(a_i**2/h_i)>0 and '
 'f_star=b**2/(2*sum(a_i**2/h_i)). These formulas follow directly from the single active constraint and '
 'stationarity h*(x-c)-lambda*a=0. The driver checks them independently of the optimizer.',
 '',
 'Dimensions [2,3,5], diagonal condition ratios [1,5], heights [0.5,2], zero/quarter-integer centers '
 'and feasible/infeasible starts give 48 projections and 160 optimizer-coordinate references. Diagonal '
 'entries are linearly spaced from 1 to the condition ratio, and a_i=(-1)**i*(1+i/4). Starts are c and '
 'c+2*(x_star-c). The supplied callbacks return the objective gradient and full affine-constraint '
 'Jacobian; analytic mode Varder=1 must actually call the derivative callback. There were 240 '
 'derivative calls.',
 '',
 'Optgra must return status 1 (feasible optimum) with finite coordinates and returned values. The '
 'method is spectral conjugate gradients (Optmet=2), with a 300-iteration limit and '
 'constraint/objective Consca thresholds 1e-9/1e-11. Consca contains convergence thresholds, not scale '
 'factors. Coordinate error normalized by 1+max(abs(x_star)) must be <=2e-4, objective error divided by '
 '1+f_star <=1e-7, inequality violation divided by 1+b <=2e-7, and stationarity residual divided by '
 '1+max(abs(lambda*a)) <=2e-4. Returned objective/constraint values must also agree with direct '
 'evaluation within normalized error 1e-8.',
 '',
 'Saved maximum point, objective, feasibility, stationarity and returned-value discrepancies were '
 '1.34283e-6, 4.12945e-12, 1.25825e-15, 2.16013e-6 and 4.11316e-17. This driver checks only one affine '
 'inequality with strictly convex quadratic objectives. It does not verify nonlinear constraints, '
 'equality constraints, multiple active constraints, nonconvex objectives or general solver robustness.',
 '',
 '## neural-fortran affine-network training (G1b)',
 '',
 'The independent consumer calls network%train directly, rather than implementing its own training '
 'loop. A single dense layer with linear activation learns two-output affine maps from one or two input '
 'coordinates. For map index m=1 or 2, weight rows are m*[0.75,-0.5] and [-0.25,1]/m, and bias is '
 'm*[0.5,-0.75]; the second weight column is omitted for one input. These dyadic coefficients have '
 'exact representations in the default real32 precision used by this cached build.',
 '',
 'The Cartesian training grid is {-1,0,1} in each input dimension, with three or nine observations and '
 'two output channels. Its augmented design matrix has full column rank. A linear dense layer can '
 'represent the map exactly, so the known global minimum training loss is zero; this is a convex '
 'least-squares fixture, not a nonlinear neural-network convergence claim.',
 '',
 'Two dimensions, two affine maps, seeds [42,1729,314159] and two batch settings give 24 training runs. '
 'Each GNU random seed array contains seed+37*i. Stochastic batches have size 1; full batches use every '
 'observation. network%train runs 400 epochs with SGD learning rate 0.1 and its default quadratic loss. '
 'At this pin stochastic training draws random contiguous batches with replacement, so an epoch need '
 'not visit every observation. Full batches include the complete grid. Only one coarray image is used.',
 '',
 'A separate real64 scalar affine formula checks predictions on 11-point Cartesian grids from -1 to 1 '
 'in steps of 0.2, including points absent from training. The 3,168 output entries must be finite and '
 'have maximum absolute error divided by 1+max(abs(expected)) <=2e-4. Training MSE is independently '
 'recomputed in real64 against the affine formula, averaged across observations and output channels; it '
 'must be <=1e-8 and <=1e-5 of its initial value. This is not a check of a library-reported loss.',
 '',
 'Saved maximum normalized prediction error, final training MSE and final/initial MSE ratio were '
 '8.84756e-7, 4.52182e-13 and 5.87537e-13. Nonlinear activations, hidden layers, noisy data, other '
 'optimizers, parallel training and cross-compiler RNG reproducibility remain unverified. The G1b '
 'mapping is network-specific internal-backpropagation optimization; it is not a general '
 'scalar-objective callback solver.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned implementations/interfaces and author API examples were reviewed before writing these '
 'independent consumers. No upstream implementation or test bodies are copied. The drivers have their '
 'own MIT notice; Optgra and neural-fortran retain their respective upstream license terms. Loading a '
 'driver does not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def directions_fitting_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-directions-fitting-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-directions-fitting-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked feasible directions and annealing; a failed friction fit',
 '',
 'The G2h3b1b and G2i drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted '
 'sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-directions-fitting-validation.json) retains pins, source hashes and complete output. '
 'GAMS categories are not exhausted.',
 '',
 '## CONMIN nonlinear ball projections (G2h3b1b)',
 '',
 'The independent driver minimizes f(x)=0.5*norm(x-target)**2 subject to '
 'g(x)=norm(x-center)**2-R**2<=0. The target is center+2*R*d for a unit direction d; the exact solution '
 'is center+R*d, with objective R**2/2 and multiplier 1/2 for the constraint g<=0. Strict convexity '
 'gives a unique global minimizer on this convex ball. Independent endpoint checks use these formulas, '
 'including the stationarity residual (x-target)+(x-center).',
 '',
 'Dimensions [2,3,5], radii [0.5,2], zero/quarter-integer centers, two signed target directions and '
 'feasible/infeasible noncollinear starts give 48 problems and 160 coordinate references. Direction d '
 'normalizes entries (-1)**(direction*i)*i. A perpendicular unit vector q is obtained by normalizing '
 'e1-d(1)*d. Starts are center+R*(0.25*d+0.1*q) and center+R*(1.25*d+0.1*q), so the optimizer must '
 'correct a tangential error as well as the radial error.',
 '',
 'NFDG=1 supplies both objective and constraint derivatives. Reverse communication services INFO=1 with '
 'values and INFO=2 with the objective gradient and active constraint Jacobian, stored by columns. The '
 'active set is provided through NAC/IC when g>=CT; the sphere is marked nonlinear. There were 426 '
 'user-gradient requests. Variable bounds and automatic scaling are disabled. The nonlinear constraint '
 'thickness starts at -0.01*R**2 and its minimum magnitude is 1e-9*R**2. Objective relative and '
 'absolute change settings are 1e-12.',
 '',
 'The driver caps solver iterations at 300 and reverse-communication requests at 10,000. IGOTO=0 is '
 'required, with the iteration cap not reached, finite values and positive gradient-request counts. '
 'CONMIN exposes no separate success code here, so return alone is not an accuracy certificate. '
 'Independent normalized coordinate error must be <=2e-4, objective error <=2e-7, positive ball '
 'violation <=2e-7, stationarity residual <=2e-4 and returned/direct objective discrepancy <=1e-8. '
 'Normalizers are respectively 1+max(abs(x_star)), 1+R**2/2, 1+R**2, 1+2*R and 1+actual_f.',
 '',
 'Saved maxima were 5.98188e-5, 1.16625e-8, 1.77636e-16, 7.41370e-5 and zero. Multiple simultaneous '
 'constraints, equality constraints, active variable bounds, nonconvex feasible sets and general '
 'optimizer robustness remain unverified.',
 '',
 '## Simulated annealing shifted Rastrigin (G2i)',
 '',
 'The driver searches R(x)=sum(z_i**2+A*(1-cos(2*pi*z_i))), with z=x-center, center=[-0.25,0] and '
 'bounds center +/- 3. Every summand is nonnegative, and only z=0 makes all quadratic terms zero; the '
 'unique global minimizer is center with objective zero. An independent sin-squared identity '
 'sum(z_i**2+2*A*sin(pi*z_i)**2) checks the returned value.',
 '',
 'Two amplitudes [1,10] and seed pairs [(1,2),(1234,5678),(91,2718)] give six two-dimensional searches '
 'and 12 known minimizer coordinates. Seeds use the library generator, not Fortran random_seed. The '
 'start is center+[-2.5,2.5], initial steps are 1, temperature is 20 and the cooling factor is 0.9. '
 'Settings are ns=20, nt=10, neps=4, eps=1e-9, adaptive step mode 1, and n_resets=1. At this pin '
 'n_resets counts complete main-loop runs, not additional restarts. Known-minimum early stopping is '
 'disabled, so the reference answer does not steer termination.',
 '',
 'Termination must return status 0; finite callback and final points must remain inside bounds. Each '
 'reported evaluation count must equal the independent callback count and be <=600,000. Independent '
 'objective must be <=1e-5, maximum coordinate error <=1e-3, and normalized returned-value discrepancy '
 '<=2e-12. Saved maxima were 2.80888e-12, 3.61574e-7 and 8.16990e-16; the six runs used 271,406 '
 'callbacks. These are fixture results, not a performance comparison.',
 '',
 'A valid three-dimensional amplitude-10 search with seed (1,2) returned status 0 at objective '
 'approximately 0.994959, both with cooling factors 0.85 and 0.9. The [finite-schedule '
 'probes](gams-candidates/annealing-finite-budget/README.md) retain exact sources and results. That is '
 'a nonglobal finite-budget outcome, not evidence of a certified global solution or necessarily a '
 'library defect. The published driver covers only two dimensions and keeps all three original seed '
 'pairs and its original answer tolerances.',
 '',
 'A separate [two-loop probe](gams-candidates/annealing-reset-objective/README.md) failed objective '
 'identity checks, consistent with repeated conversion of the internally negated minimization value. '
 'The checked driver uses one main-loop run; multi-loop correctness remains unverified. An earlier '
 '[zero-loop consumer](gams-candidates/annealing-loop-count/README.md) used an invalid configuration '
 'and is documented as a consumer error. No general global-convergence, success-probability or '
 'cross-compiler RNG guarantee follows from the six successes.',
 '',
 '## Friction fitting remains unverified (L8)',
 '',
 'The independent Coulomb probe generated exact signed-force data for coefficient 0.375 and varied '
 'positive normal loads. The identifiable scalar least-squares answer is sum(a_i*F_i)/sum(a_i**2), '
 'where a_i=sign(v_i)*N_i, giving exactly 0.375. The cached library instead fitted 0.7499999991182843 '
 'and reported residual convergence; independently recomputed force discrepancy reached '
 '1.499999996473137. The unchanged 1e-7 coefficient comparison rejected it.',
 '',
 'Source review finds fit_fcn subtracts observed force before returning callback values, while fmdl_fit '
 'also supplies observed force as the least-squares dependent data. The pinned fstats dependency '
 'expects model predictions, so this explains the observed doubling. The [preserved '
 'probe](gams-candidates/friction-double-subtraction/README.md) records the complete cached GNU 16 '
 'result, source hash, pins and source-based diagnosis. The L8 record has no checked driver, and no '
 'library patch or upstream-confirmed fix is claimed. Ordinary algebraic force evaluation remains '
 'separately demonstrated; dynamic internal-state fitting is not verified.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned APIs, implementations and author tests were reviewed before writing these independent '
 'consumers. No implementation or test bodies are copied. Drivers/probes have their own MIT notice; '
 'upstream CONMIN, simulated-annealing and friction licenses remain separate. Loading a driver does not '
 'submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def random_references_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-random-references-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-random-references-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked KISS streams and normalized random spacing',
 '',
 'These L6a21 and L6 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted '
 'sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-random-references-validation.json) retains pins, source hashes and complete output. GAMS '
 'categories are not exhausted. These are sequence/construction checks and selected-seed law smoke '
 'checks, not statistical-quality certification.',
 '',
 '## rndgen-fortran KISS streams (L6a21)',
 '',
 'Seven interleaved generators use seeds [0,1,-1,12345,-67890,294727492,2147483646]. Each yields 4,096 '
 'draws, for 28,672 outputs. Every draw must be finite in [0,1), lie exactly on the 31-bit grid '
 'k/2**31, and reproduce on reset. The first eight decoded integers per stream, 56 entries, must match '
 'independent constants exactly. A rolling modular checksum over every stream must also match its '
 'independent reference. Checksums compactly check the long streams; they are not a collision-free '
 'comparison of every entry to a stored reference.',
 '',
 'The [reference generator](../fpm_catalog/gams-drivers/references/kiss_vectors.py) uses unbounded '
 'Python integers and explicit modulo-2**32 arithmetic, rather than Fortran signed overflow. The seed '
 'shuffle interprets its modular product as signed int32 before taking its absolute value and clamping '
 'it to [1,2147483646]. Four Park-Miller seed steps use direct multiplication modulo 2**31-1 rather '
 'than the library Schrage decomposition; one initial KISS draw is discarded. The reference implements '
 'the reviewed mathematical KISS convention, not an independent statistical randomness oracle. No '
 'upstream implementation or test bodies were copied.',
 '',
 'The KISS state combines a linear-congruential component, a three-shift xor component and two '
 'multiply-with-carry components. Explicitly wrapping the combined sum to 32 bits and discarding its '
 'low bit produces k. For each 4,096-entry stream, checksum starts at zero and updates as '
 '(65599*checksum+k) modulo 2147483647; its int64 products fit safely. Stored '
 '[vectors](../fpm_catalog/gams-drivers/references/kiss-vectors.json) and embedded Fortran constants '
 'are checked by running the generator without --write. The Fortran consumer requires no Python '
 'installation.',
 '',
 'The consumer additionally saves an opaque in-memory state after each reset replay, generates 257 more '
 'values, restores the state and checks all of them exactly: 1,799 continuation entries. Interleaving '
 'checks these objects do not contaminate one another, not that streams are statistically independent. '
 'Positive and negative seeds with equal absolute value intentionally share a stream. All 56 prefixes, '
 'seven long-stream checksums, 28,672 reset replay entries and 1,799 continuation entries passed.',
 '',
 'The upstream implementation relies on signed int32 overflow in several updates. This result checks '
 'the cached GNU 16 wraparound behavior; it does not establish standard-conforming integer overflow, '
 'other-compiler behavior, generator period, statistical quality or cryptographic suitability. The '
 'minimum int32 seed, file serialization and integer/ranged-real convenience APIs remain unverified.',
 '',
 '## Pointsets normalized random increments (L6)',
 '',
 'The pinned random_spacing routine draws n intrinsic uniform values, discards the first, accumulates '
 'the remaining positive increments, and rescales the cumulative sequence to the requested interval. '
 'For n>=2 its mathematical construction is x_i=a+(b-a)*sum(U_2,...,U_i)/sum(U_2,...,U_n), with x_1=a '
 'and x_n=b. It does not sort uniform points or use exponential spacings. The former L6a21 procedure '
 'mapping has been broadened to L6 random-number generation: the returned coordinates are not uniform '
 'draws or uniform order statistics.',
 '',
 'Seven sizes [0,1,2,3,9,33,129], intervals [0,1], [-3.5,2.25], [0.25,0.25] and seeds [42,1729,314159] '
 'give 63 fixtures. GNU random seed arrays contain seed+37*i. A separately seeded intrinsic draw '
 'supplies the same raw inputs to a real64 sum-and-ratio oracle, while the cached package works in '
 'real32. This isolates the construction from the intrinsic generator: it does not independently verify '
 'the generator itself.',
 '',
 'For the 45 nontrivial-size fixtures, all 1,584 coordinates are checked against the oracle within '
 'normalized tolerance 8*n*epsilon(real32), using normalizer 1+max(abs(a),abs(b)). Finite values, '
 'nondecreasing order and endpoints are checked. All 18 empty/singleton fixtures must leave their input '
 'unchanged, including the singleton sentinel -99. They consume no random draws; larger arrays consume '
 'exactly n. The next intrinsic random value and exact full-result seeded replay verify this behavior. '
 'The maximum normalized coordinate error was 2.84632e-7.',
 '',
 'With three points on [0,1], the only interior coordinate is R=U/(U+V) for independent uniform '
 'increments U,V. For 0<=r<=1/2, P(R<=r)=r/(2*(1-r)); for 1/2<=r<=1 it is 1-(1-r)/(2*r). The two '
 'expressions follow from integrating the area U<=r*V/(1-r) in the unit square. Consequently the CDF '
 'values at 1/4 and 3/4 are 1/6 and 5/6, and symmetry gives mean 1/2. A single uniform interior point '
 'would instead have CDF 1/4 and 3/4 there.',
 '',
 'Each of the three seeds supplies 20,000 three-point sets, for 60,000 law samples. The empirical CDFs '
 'must be within 0.015 of 1/6 and 5/6, the empirical mean within 0.015 of 1/2, and the quarter-point '
 'CDF must differ from 1/4 by at least 0.04. Observed quarter-point CDFs were 0.16425, 0.16510 and '
 '0.16585; the largest CDF discrepancy was 0.00271667. These fixed-seed smoke checks distinguish this '
 'construction from uniform order statistics without certifying the full distribution or statistical '
 'quality of an RNG.',
 '',
 'Reversed intervals, rare all-zero increment sums, other precisions, other pointsets generators and '
 'cross-compiler intrinsic RNG sequences remain unverified. No library patch, backend redeployment or '
 'cached package rebuild is required by either driver.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned APIs/implementations and author examples were reviewed before writing the independent '
 'consumers and reference arithmetic. Drivers and reference generator have their own MIT notice; '
 'upstream rndgen-fortran and pointsets license terms remain separate. Loading a driver does not submit '
 'a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def tangents_blocks_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-tangents-blocks-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-tangents-blocks-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked tangent flows and block-sparse products',
 '',
 'These I1 and D1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
 'Existing libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-tangents-blocks-validation.json) retains pins, source hashes and complete output. GAMS '
 'categories are not exhausted.',
 '',
 '## FATODE coupled decay and full tangent derivatives (I1)',
 '',
 'The independent consumer integrates y1_prime=-k*y1+c*y2, y2_prime=-k*y2, k_prime=0, c_prime=0. The '
 'last two constant states expose derivatives with respect to rate k and coupling c through the same '
 'tangent-linear interface as initial-condition derivatives. Four identity columns initialize the '
 'tangent matrix. The supplied analytical Jacobian is explicitly selected and tangent variables '
 'participate in adaptive error control. This verifies the explicit ERK/TLM implementation compiled by '
 'the existing wrapper; no bundled binary or changed numerical library is used.',
 '',
 'For elapsed time tau and initial physical states a,b, let E=exp(-k*tau). The exact final state is '
 '[E*(a+c*b*tau), E*b, k, c]. The exact flow-derivative rows, with columns for initial a,b,k,c, are '
 '[E,c*tau*E,-tau*y1,b*tau*E], [0,E,-tau*y2,0], [0,0,1,0] and [0,0,0,1]. These elementary formulas give '
 'independent endpoint references without finite differencing or another ODE solver.',
 '',
 'Methods 4 (Dopri5) and 6 (Dopri853), rates [0.25,2,8], couplings [-1.5,0,2], durations '
 '[-1,-0.125,0.125,1,2], initial physical states [(1,0.5),(-0.75,1.25),(0,0)] and time origins [0,0.75] '
 'give 540 integrations. This includes forward/backward evolution, coupled and uncoupled states, signed '
 'and zero initial states, and translation of the time origin. All 2,160 state entries and 8,640 '
 'tangent entries are checked, including the constant-state derivative rows.',
 '',
 'Absolute/relative tolerances are 1e-12/1e-10 for both state and tangent arrays, with a 10,000-step '
 'cap. Return status must be exactly 1, callbacks and accepted steps must be present, and all output '
 'values must be finite. Exit time must agree with the requested endpoint within '
 '64*epsilon(real64)*max(1,abs(endpoint)). Constant k,c states must be unchanged exactly. Each '
 'state/tangent entry error divided by 1+abs(analytic_entry) must be <=2e-7.',
 '',
 'The saved maximum state and tangent discrepancies were 4.43326e-10 and 7.23387e-10. Each callback '
 'type was actually invoked 535,978 times. These counts describe this suite and are not a performance '
 'comparison. Finite-difference Jacobians, the other ERK methods, implicit/stiff integrators, adjoints, '
 'sparse variants and arbitrary nonlinear systems remain unverified. I1 is the maintained broad ODE '
 'mapping; these checks do not establish a narrower stiff-solver class.',
 '',
 '## DBCSR irregular block products and accumulation (D1)',
 '',
 'The independent serial real64 consumer checks C_out=alpha*op(A)*op(B)+beta*C_in, comparing every '
 'entry against scalar loops. No MATMUL, BLAS call or other sparse library supplies the reference. '
 'Operator dimensions (m,k,n) are (4,3,4) and (3,6,5). Their block partitions are respectively '
 'm=[1,2,1], k=[2,1], n=[1,3] and m=[2,1], k=[1,3,2], n=[2,1,2], exercising unequal block sizes and '
 'rectangular operands/results. Stored arrays/partitions are transposed when a T operand is requested.',
 '',
 'Each layout uses four data patterns: full dyadic values, block-sparse dyadic values, full non-dyadic '
 'values, and a structurally empty A. Entry formulas before applying block masks are '
 'A_ij=(2*i-3*j+1)/dA, B_ij=(3*i+j-2)/dB and C_ij=(i-2*j+3)/dC. Dyadic denominators are all 8; '
 'non-dyadic denominators are 7,11,13. In the sparse pattern, A keeps blocks with even row+column block '
 'index, while B removes blocks for which 2*row_block+column_block is divisible by 3. C_in contains its '
 'full formula. Zero blocks are not inserted.',
 '',
 'Both layouts, four patterns and every NN/NT/TN/TT pair give 32 products and 496 scalar reference '
 'entries. The six alpha/beta pairs [(1,0),(-1.25,0.5),(0,-1),(2,0),(0,0),(0.5,1)] cycle through those '
 'fixtures in order. They are not an extra Cartesian dimension, so not every scalar pair is tested with '
 'every matrix. This covers overwriting C, scaling an existing C, negative accumulation, zero '
 'multipliers and structurally empty input.',
 '',
 'Filtering is explicitly set to zero. The consumer reconstructs stored C blocks, treating missing '
 'blocks as zeros and honoring returned block-transposition flags. Every entry must be finite. Absolute '
 'discrepancy divided by 1+abs(beta*C_in_ij)+sum_h(abs(alpha*A_ih*B_hj)) must be '
 '<=128*epsilon(real64)*(k+2). The maximum normalized discrepancy was 1.91702e-16. Serial nonsymmetric '
 'real64 CPU operation is verified here; MPI, OpenMP, GPU, accelerators, symmetry storage, complex '
 'arithmetic and general sparse-pattern behavior remain unverified.',
 '',
 'The [288-case Cartesian draft](gams-candidates/dbcsr-output-limit/README.md) compiled but was stopped '
 'by the 200,000-byte output limit because the checked library build repeatedly reported array '
 'temporaries. It is not counted as numerical verification. The successful selected driver supplies '
 'contiguous copied blocks and preserves its remaining native diagnostics in the proof (about 105 KB of '
 'run stderr). No diagnostics are suppressed and no backend limit or library source is changed. An '
 'earlier [read-only unpacking handle](gams-candidates/dbcsr-consumer-intent/README.md) was a consumer '
 'interface error, corrected to intent(inout) without changing the reference or tolerance.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned APIs, implementations and author examples were reviewed before writing the independent '
 'consumers. No upstream implementation or example bodies are copied. The drivers have their own MIT '
 'notice; upstream FATODE and DBCSR license terms remain separate. Loading a driver does not submit a '
 'job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def radial_dense_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-radial-dense-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-radial-dense-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked radial eigenstates and dense-layer inference',
 '',
 'These I1 and K drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
 'Existing libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-radial-dense-validation.json) retains pins, source hashes and complete output. GAMS '
 'categories are not exhausted.',
 '',
 '## dftatom nonrelativistic Coulomb eigenstates (I1)',
 '',
 'The independent consumer solves the radial eigenproblem for V(r)=-Z/r with nuclear charges Z=[1,2,4]. '
 'All six (n,l) states through n=3 are tested on meshes with 3,000 and 4,500 intervals, giving 36 '
 'eigenproblems. The library exponential mesh runs from 1e-8/Z to 100/Z with a largest/smallest '
 'interval ratio of 1e6. Initial energy is -0.4*Z**2/n**2, bracket [-Z**2,0], energy tolerance '
 '1e-11*Z**2 and iteration limit 100. The nonrelativistic mode is selected and Coulomb-tail '
 'perturbation corrections are enabled.',
 '',
 'The exact energy is -Z**2/(2*n**2) Hartree. See the [MIT hydrogen '
 'lecture](https://ocw.mit.edu/courses/5-61-physical-chemistry-fall-2007/c2078ff25c61c136e67ceb6fd8eb9b34_lecture21to22.pdf) '
 'for Coulomb energies and radial eigenstates. The wavefunction normalization convention used here is '
 'the generalized-Laguerre form in [Gonzalez et al., equations '
 '(1.2)-(1.4)](https://arxiv.org/html/1505.06274v3). In atomic units, rho=2*Z*r/n and '
 'P=r*R_nl=C*r*exp(-rho/2)*rho**l*L_(n-l-1)^(2*l+1)(rho), with '
 'C=sqrt((2*Z/n)**3*(n-l-1)!/(2*n*(n+l)!)). The reference Q is the direct derivative dP/dr.',
 '',
 'Only polynomial degrees 0,1,2 are needed. The driver evaluates their elementary formulas and '
 'derivatives directly; the convention is documented by [NIST DLMF '
 '18.5.12](https://dlmf.nist.gov/18.5.E12). No special-function library or numerical differencing '
 'supplies the reference. One common sign aligns P and Q with the analytic state, since an '
 'eigenfunction phase is arbitrary. Every one of the 135,036 P entries and 135,036 Q entries is '
 'compared, including zeros and tails.',
 '',
 'The driver independently integrates P**2, r*P**2 and P**2/r with scalar trapezoidal sums on the '
 'physical nonuniform mesh. It checks normalization one, mean radius (3*n**2-l*(l+1))/(2*Z), and mean '
 'inverse radius Z/n**2. Moments are divided by the independently computed norm; the norm is also '
 'checked separately. These moment formulas also follow by integrating the explicit degree-at-most-two '
 'polynomials. The library normalization quadrature is not reused.',
 '',
 'Solver status must be zero, and energy/P/Q must be finite. Absolute energy discrepancy divided by '
 'Z**2 must be <=1e-7. Maximum P discrepancy divided by sqrt(Z) must be <=2e-5; maximum Q discrepancy '
 'divided by Z**1.5 must be <=5e-5. Trapezoidal norm discrepancy must be <=2e-5. Radius discrepancy '
 'times Z/(1+n**2) and inverse-radius discrepancy divided by Z must each be <=2e-5. Finite-domain tails '
 'and quadrature discretization are part of this acceptance test; it is not a rigorous continuous error '
 'bound.',
 '',
 'Saved maxima for energy, P, Q, norm, radius and inverse-radius checks were 4.76529e-11, 9.19163e-10, '
 '1.20398e-5, 3.53696e-6, 2.11486e-9 and 9.09494e-11. The trapezoidal norm discrepancy decreases from '
 'about 3.537e-6 on the 3,000-interval mesh to 1.572e-6 on the finer mesh; it should not be read as an '
 'error in the library normalization routine. Q errors are larger than P errors and remain subject to '
 'their separately stated bound. Dirac eigenstates, general potentials, higher states, Poisson and '
 'self-consistent density-functional calculations remain unverified. The maintained I1 mapping is '
 'broad, not a claim to verify every radial solver mode.',
 '',
 '## Athena fixed dense-layer forward evaluation (K)',
 '',
 'The independent consumer creates 192 fixed layers: input widths [1,2,3,5], output widths [1,2,4], '
 'activations [none,relu,tanh,sigmoid], bias on/off and two parameter patterns. With one-based indices, '
 'weights W_ij=(2*i-3*j+1)/8 and biases b_i=(2*i-3)/8 in the dyadic pattern; denominators are 7 and 9 '
 'in the non-dyadic pattern. Values are first rounded to the cached library real32 precision; the '
 'oracle uses these actual stored coefficients widened to real64. Randomly initialized weights are '
 'overwritten completely.',
 '',
 'Each layer evaluates 11 inputs: zero, every coordinate basis vector, then deterministic mixed signed '
 'dyadic vectors. Zero/basis inputs expose bias handling and individual weight columns. The mixed '
 'vectors use x_j=(modulo(sample*(2*j+1),17)-8)/8. A scalar real64 loop forms z_i=b_i+sum_j(W_ij*x_j), '
 'omitting bias when disabled. Reference activations are z, max(0,z), 2/(1+exp(-2*z))-1 and a '
 'sign-stable sigmoid expression. No MATMUL or another network package supplies the oracle.',
 '',
 'There are 4,928 independent output entries. Every output must have the requested dimension and be '
 'finite, with error divided by 1+abs(reference) <=2e-6. After the other inputs, the initial zero '
 'feature is evaluated again and all 448 output entries must match their original values exactly, '
 'giving 2,304 total forward calls. The maximum normalized real64-oracle discrepancy was 5.77239e-8. '
 'This verifies forward evaluation of known functions, not how well a trained network approximates an '
 'external dataset. K remains the broad approximation class.',
 '',
 'The input array is deliberately persistent and marked is_temporary=.false. after allocation. An '
 '[earlier draft](gams-candidates/athena-temporary-input/README.md) left the default temporary '
 'ownership flag in place and aborted during repeated forward calls. Its exact source, dependency pins '
 'and failed result are retained. Correcting the consumer flag preserved all weights, fixtures and '
 'tolerances; no library source was patched. Training, automatic derivatives, batch inference, graph '
 'networks, serialization and general memory safety remain unverified.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned APIs, implementations and author tests were reviewed before writing the independent consumers. '
 'No upstream implementation or test bodies are copied. The drivers have their own MIT notice; upstream '
 'dftatom and Athena license terms remain separate. Loading a driver does not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def inference_pairs_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-inference-pairs-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-inference-pairs-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked Fiats and ennuf fixed-network inference',
 '',
 'Both K drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing '
 'libraries were reused; only mains and executables were compiled. The [verification '
 'report](gams-inference-pairs-validation.json) retains pins, source hashes and complete output. GAMS '
 'categories are not exhausted. K is the maintained broad function-approximation class; these examples '
 'verify fixed network evaluation, not training or approximation quality on a scientific dataset.',
 '',
 '## Fiats irregular multilayer networks (K)',
 '',
 'The independent consumer constructs four architectures [1,2,1], [2,3,2], [3,2,1] and [2,4,3,2]. These '
 'have one or two hidden layers and changing widths, so active input/output slices differ between '
 'layers. Combining them with ReLU, sigmoid and swish activations, two parameter patterns and '
 'zero/nonzero biases gives 48 fixed networks. The pinned Fiats 0.12.0 package and its compatible '
 'Julienne/Assert dependencies are reused; this driver does not change the historical version offered.',
 '',
 'At connection l, W_ij=(2*i-3*j+l)/8 and b_i=(i-2*l)/8 in the dyadic pattern, while denominators are 7 '
 'and 9 in the non-dyadic pattern. The zero-bias setting zeroes active biases. Native coefficients have '
 'decimal precision 6 (real32 in this image); the oracle widens the actual stored coefficients to '
 'real64. Padded matrix/bias slots are filled with sentinel 17 and must not affect the result. Tensor '
 'input/output ranges are left at their default [0,1] maps, which act as identity maps here, including '
 'the selected inputs outside that interval.',
 '',
 'Each network evaluates 11 inputs: zero, every coordinate basis vector, then deterministic mixed '
 'signed dyadic vectors x_j=(modulo(sample*(2*j+1),17)-8)/8. A scalar real64 oracle propagates the '
 'active widths connection by connection, evaluating ReLU as max(0,z), sigmoid with a sign-stable '
 'exponential formula, and swish as z*sigmoid(z). The activation is applied at the output layer too, as '
 'required by this pinned API; a linear output is not assumed. No MATMUL or another network '
 'implementation supplies the reference.',
 '',
 'All 792 output entries must be finite with the requested output width and absolute discrepancy '
 'divided by 1+abs(reference) <=5e-6. After the other inputs, each network receives zero again and all '
 '72 replay entries must match the first result exactly. There are 576 total inference calls; the '
 'largest normalized oracle discrepancy was 3.46692e-8. Nonidentity range maps, model-file round trips, '
 'the other Fiats activations, training, derivatives, parallel scaling and dataset approximation '
 'quality remain unverified.',
 '',
 '## ennuf generic dense/activation pipelines (K)',
 '',
 'The independent consumer directly calls the cached Fortran neural_net_mod dense and '
 'activation_function routines. The same four width architectures are composed with ReLU, leaky ReLU '
 '(alpha=0.125), sigmoid, tanh and softmax. Optional biases are present or absent, parameter patterns '
 'are dyadic or non-dyadic, and channel counts are [1,2,5]. Channel rows are independent feature '
 'vectors transformed by shared weights, rather than summed together. The routines execute in Fortran; '
 'no Python inference or external model conversion runs in the sandbox.',
 '',
 'Weight and bias formulas match the Fiats suite, rounded first to native real32. Each configuration '
 'has 11 inputs: zero, coordinate bases scaled in channel c by c/(channels+1), then mixed inputs '
 'x_cj=(modulo(sample*(2*j+1)+3*c,17)-8)/8. There are 2,640 pipeline batches, each with two or three '
 'dense/activation stages, giving 5,940 calls to each primitive. Unlike many network conventions, the '
 'selected activation also follows the final dense stage in these explicit consumer pipelines.',
 '',
 'A real64 scalar oracle evaluates each channel and layer from the actual stored coefficients. It uses '
 'elementary pointwise activation formulas; its tanh uses the logistic identity, and its softmax '
 'subtracts the row maximum before exponentiation. This stabilization is in the reference, not a patch '
 'to the library implementation, which uses unshifted exponentials. Selected logits are moderate; '
 'extreme-logit stability is not checked. The reference retains real64 intermediates across layers so '
 'that native real32 rounding differences accumulate in the comparison.',
 '',
 'All 35,200 layer-output entries, including 10,560 final-layer entries, must be finite and agree '
 'within normalized discrepancy 5e-6. Softmax outputs must be positive and each channel row must sum to '
 'one within 2e-6. The largest normalized scalar-reference discrepancy was 5.25551e-8 and the largest '
 'softmax sum error 1.19209e-7. Channel mixing, wrong optional-bias handling or width ordering would '
 'change these explicit per-channel references.',
 '',
 '## ennuf cached generated model',
 '',
 'The consumer also calls the existing ennuf_example_mod model, whose audited [generated '
 'asset](../fpm_catalog/generated/ennuf-2555a7f1560ef3cb7cf707221fa5bb1b5334ee6f.json) is already part '
 'of the package build. Its closed-form scalar function is '
 'y=2*max(x1+2*x2+0.5,0)-3*max(-x1+0.5*x2-0.25,0)+1. Hidden units are ReLU, and the final output is '
 'linear. This is a fixed illustrative model, not a trained scientific surrogate.',
 '',
 'Both coordinates independently range over [-2,-1,-0.5,-0.25,0,0.25,0.5,1,2], giving 81 generated '
 'model evaluations. The grid includes positive/negative inputs, exact hidden-unit threshold values and '
 'all four combinations of active/inactive ReLU units. Region counts are [21,29,14,17] in order neither '
 'active, first only, second only, both active; exact-zero preactivations count as inactive. Each '
 'finite output is checked against the closed form using the same normalized 5e-6 tolerance. The '
 'observed discrepancy was zero for this dyadic grid.',
 '',
 'The generated asset hash remains 6f7fc6b3b9943943fd294017179004dfc37567dfdd637aabed2d0908dbdb9a7b, '
 'matching the package recipe. No new model generation or library rebuild is required. External '
 'TensorFlow/PyTorch conversion, arbitrary generated models, convolution/pooling/skip layers, extreme '
 'softmax logits, training and dataset approximation quality remain unverified.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned APIs, implementations and author examples were reviewed before writing these independent API '
 'consumers. No upstream implementation or example bodies are copied. The drivers have their own MIT '
 'notice; the Berkeley Lab Fiats terms and ennuf BSD/Crown notices remain separate and unchanged. '
 'Loading a driver does not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def helmholtz_streams_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-helmholtz-streams-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-helmholtz-streams-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked spherical Helmholtz inversion and xoroshiro streams',
 '',
 'Both independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
 'The existing package libraries were reused; only driver mains and executables compiled. The '
 '[verification report](gams-helmholtz-streams-validation.json) preserves package pins, source hashes, '
 'commands and output. GAMS categories are not exhausted.',
 '',
 '## Spherepack Helmholtz and Poisson equations (I2)',
 '',
 'The driver solves (Delta_S - lambda) u = f on the unit sphere with the public Sphere%invert_helmholtz '
 'API. Ten exact real spherical harmonics are supplied as Cartesian fields: 1; x, y, z; xy, xz, yz, '
 '(3*z*z-1)/2, x*x-y*y; and (5*z**3-3*z)/2. Their degrees are 0, 1, 1, 1, 2, 2, 2, 2, 2 and 3. For each '
 'mode the surface Laplacian eigenvalue is -l*(l+1), giving the right-hand side directly without finite '
 'differences or another solver. A mixed field uses amplitudes '
 '[1,-0.5,0.25,0.75,-1,0.5,-0.25,0.125,0.625,-0.375].',
 '',
 'Both GaussianSphere and RegularSphere use grids [9,16], [13,24] and [17,32] in latitude/longitude '
 'counts. Shifts lambda=[0,0.25,1,3.5] exercise the Poisson branch and three invertible Helmholtz '
 'operators. At lambda=0 the constant-only fixture is skipped and the mixed field loses its constant '
 'component: the compatible solution has a zero-constant gauge. No arbitrary constant offset is removed '
 'after solving, so the returned gauge is checked too.',
 '',
 'There are 258 solves and 86,000 grid-point references. Every returned value must be finite and '
 'max(abs(solution-exact))/(1+max(abs(exact))) must be <=2e-11. The largest observed discrepancy was '
 '3.11709e-15. Nonzero nonzonal modes are now checked for this PDE interface, separately from the older '
 'zonal scalar-transform driver. The test uses the existing catalog recipe with its previously '
 'documented vector-workspace rank fixes; it adds no library patch. Resonant negative shifts, '
 'inhomogeneous geometry, variable coefficients, vector PDEs and convergence outside these band-limited '
 'fields remain unverified.',
 '',
 '## rng_fortran uniform bitstream and seed/jump API (L6a21)',
 '',
 'The pinned generator is xoroshiro128+(24,16,37). Five nonzero 128-bit seed pairs cover small integers, '
 'all-one/signed-boundary words, the package default words and mixed hexadecimal patterns. Each is '
 'tested without jumping, with set_seed default jumping, and with two explicit jump calls after '
 'do_jump=.false. Fifteen integer states and fifteen matching uniform states are interleaved for 4,096 '
 'outputs each. The test makes 61,440 calls to each output API, checks 120 exact integer prefix words, '
 'and checks all uniform values are finite, in [0,1), and exactly the upper 52 bits of their '
 'corresponding integer output divided by 2**52.',
 '',
 'The [Python oracle](../fpm_catalog/gams-drivers/references/xoroshiro_vectors.py) uses unbounded '
 'nonnegative integers with explicit 64-bit masking and produces [saved '
 'vectors](../fpm_catalog/gams-drivers/references/xoroshiro-vectors.json). For jump references it '
 'constructs the 128-column GF(2) transition map and squares it 64 times to obtain T**(2**64). It does '
 'not import the package, use its jump-polynomial constants, or iterate 2**64 times. Two applications '
 'supply the double-jump fixture. The small-power transition-matrix checks in the test suite compare '
 'this machinery with direct repeated transitions.',
 '',
 'Thirty independent rolling hashes cover all integer and 52-bit uniform streams, with multiplier 65599 '
 'modulo 2**31-1. Fortran signed words are interpreted as unsigned by accounting for 2**64 modulo that '
 'prime (=4); rolling arithmetic itself cannot overflow int64. Each stream is restarted and its '
 'eight-word prefix is checked again (120 entries). Reference source/data hashes are recorded with the '
 'driver. The cached package keeps its existing -fwrapv setting for intentional signed integer '
 'wraparound; this is evidence for the GNU 16 build, not a cross-compiler portability guarantee.',
 '',
 'Exact bitstream and algebraic jump agreement do not certify statistical quality, cryptographic '
 'suitability or independence under thread scheduling. Parallel collection APIs and every possible seed '
 'are unverified. The all-zero absorbing state is deliberately excluded. The known cached-normal '
 'reseeding defect remains unresolved; this driver calls no normal sampler and does not claim to fix it.',
 '',
 '## Sources, licenses and output',
 '',
 'Pinned implementations, interfaces and author examples were reviewed. These are independently written '
 'API consumers; upstream implementation and example bodies are not copied. The new consumers and Python '
 'oracle have their own MIT notice; upstream Spherepack UCAR/MIT and rng_fortran GPL terms remain '
 'separate. Loading an example does not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def friction_torch_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-friction-torch-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-friction-torch-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked LuGre state integration and FTorch tensor inference',
 '',
 'Both independent consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox, '
 'reusing the existing package libraries and compiling only mains and executables. The [verification '
 'report](gams-friction-torch-validation.json) retains pins, source hashes and full output. GAMS '
 'categories are not exhausted.',
 '',
 '## LuGre internal-state histories (I1)',
 '',
 'This driver uses the public lugre_model%state and evaluate APIs and the cached diffeq runge_kutta_23 '
 'integrator. A new procedure record, friction-lugre-state, distinguishes them from the private '
 'friction_core internal_state_odes/internal_var_fit_fcn fitting callbacks. Those private callbacks and '
 'parameter fitting remain unverified; the separate Coulomb-fit failure is not fixed or hidden.',
 '',
 'For fixed velocity v and normal load N, the model is z_prime=v-a*z, where a=abs(v)/g(v), and '
 'g(v)=N/stiffness*(mu_c+(mu_s-mu_c)/(1+(abs(v)/v_s)**shape)). The exact segment solution is '
 'z(t)=v/a+(z0-v/a)*exp(-a*t) when a>0. At rest, a=v=0 and z remains constant. The force reference is '
 'stiffness*z+damping*z_prime+viscous_damping*v. These closed-form expressions provide the state, '
 'derivative and force references without a second numerical integrator.',
 '',
 'Four parameter sets indexed by p=1..4 use mu_s=0.5+p/16, mu_c=0.25+p/32, v_s=0.125, stiffness=8+p, '
 'damping=p/8, viscous_damping=p/16 and shape=p. Base loads are [2,5,11], initial bristle states '
 '[-1/16,0,1/16], and both velocity orientations are tested. Every history has velocities '
 '[0.125,-0.25,0,0.0625] (or their negatives), durations [0.25,0.125,0.375,0.5] and segment load '
 'multipliers [1,1.25,1.5,1.75]. States are continuous at segment boundaries, while velocities and loads '
 'change.',
 '',
 'There are 72 histories, 288 integrated segments and 1,440 requested output times. Every numerical '
 'endpoint continues into the next segment, but the closed-form reference propagates its own exact '
 'endpoint, so numerical state errors are not reset by the oracle. At each output the driver checks the '
 'state, evaluates the model derivative at the exact reference state, and compares the force at the '
 'numerical state with the analytical force. Derivative checks are algebraic API checks; integration '
 'accuracy is established separately by the state histories.',
 '',
 'The integrator uses relative/absolute tolerances 1e-11 and maximum step duration/8, with five '
 'requested times per segment. Returned times, dimensions, finiteness, callback use and initial-state '
 'immutability are checked. Normalized tolerances are 2e-8 for state, 2e-13 for derivative and 2e-7 for '
 'force. Observed maxima were 1.18833e-11, 4.33973e-17 and 1.13208e-10, respectively, with 80,598 '
 'integration callback evaluations. The force denominator is 1+abs(numerical force); state/derivative '
 'denominators use 1+abs(reference).',
 '',
 'This is a prescribed-velocity, positive-load constitutive test, not a coupled mass/spring/contact '
 'simulation. Continuously varying velocity/load, zero normal force, model fitting and private '
 'fitting/interpolation callbacks remain unverified. The author LuGre example was reviewed for public '
 'API usage; its plotting and coupled-mechanics application are not copied.',
 '',
 '## FTorch affine model and tensor layouts (K)',
 '',
 'The consumer reuses the existing playground-owned 1,766-byte embedded TorchScript fixture as data. It '
 'computes the fixed elementwise function y=2*x+1. The model archive SHA256 is '
 '13b09124005d3c931b04a5da83624973b3f78b231a579217932469ab8179077c, identical to the ordinary FTorch '
 'demo. It is written to a local sandbox file and loaded once; no download, Python inference, model '
 'conversion or new generation occurs during a run. The separate FTorch/LibTorch system-library '
 'footprint is unchanged.',
 '',
 'Ten configurations cover REAL32 and REAL64 at rank 1 ([7]), rank 2 ([2,3]) and rank 3 ([2,3,4]). Rank '
 '2 also uses permute_dims=[2,1] with a [3,2] output; rank 3 uses [2,3,1] with a [3,4,2] output. '
 'Permutations apply only to input tensors, so expected output indices are explicitly '
 'transposed/permuted rather than using two compensating layout changes. The driver checks input tensor '
 'rank, shape, stride and dtype against the requested Fortran layout.',
 '',
 'Each configuration constructs input/output tensors once, updates the same Fortran input buffer in '
 'place for 12 batches and repeats the first batch as a thirteenth call. Signed input values are '
 '(modulo(sample*index_code,37)-18)/8, where index_code is i, i+7*j or i+7*j+11*k. Distinct axis weights '
 'make permutations observable. Output buffers are overwritten with a sentinel before every call, and '
 'input buffers must remain unchanged. All predictions must be finite and exactly match the independent '
 'scalar dyadic function; first/replay outputs must also match exactly.',
 '',
 'All 130 forward calls and 1,742 scalar output references passed with zero discrepancy. This checks a '
 'fixed affine model, CPU tensor aliasing/layout and repeated inference. It does not verify a trained '
 'scientific model, nonlinear layers, gradients, training, GPU execution, arbitrary external archives or '
 'all supported ranks/dtypes. These limits are explicit even though the model is classified under broad '
 'K.',
 '',
 '## Sources, licenses and output',
 '',
 'Pinned interfaces, implementations and author examples were reviewed. The consumers are independently '
 'written and have their own MIT notice; the existing tiny model is reused as data, and upstream package '
 'notices remain unchanged. No upstream example or implementation body is copied. Loading a driver does '
 'not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def pareto_diis_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-pareto-diis-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-pareto-diis-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Checked Pareto-segment searches and Jacobi/DIIS systems',
 '',
 'Both independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
 'Existing package libraries were reused; only mains and executables compiled. The [verification '
 'report](gams-pareto-diis-validation.json) retains pins, source hashes, build commands and actual '
 'output. GAMS categories are not exhausted. Two failed initial probes are preserved with exact sources '
 'and full service results; neither failure is described as fixed.',
 '',
 '## ddPCM Jacobi/DIIS linear systems (D2)',
 '',
 'The consumer calls the cached external jacobi_diis routine directly, separately from the ordinary '
 'formaldehyde solvation demonstration. It manufactures strictly row-diagonally-dominant systems of '
 'sizes 3, 7 and 13. The symmetric pattern has off-diagonal a_ij=(modulo(i+j,5)-2)/16; the nonsymmetric '
 'pattern uses (modulo(3*i-2*j,7)-3)/16. Both use a_ii=2+i/4+2*sum_j(abs(offdiag_ij)), so the diagonal '
 'is positive and dominates the off-diagonal row sum.',
 '',
 'Two prescribed solutions are x_i=(modulo(3*i,11)-5)/4 and x_i=1/(i+1). A separate scalar loop forms '
 'b=A*x_exact. Initial guesses are zero or the repeating pattern modulo(i,3)-1. Every combination runs '
 'in all four library convergence modes, both as plain Jacobi (history 0) and DIIS with the package '
 'default history 25. This gives 192 solves and 1,472 scalar solution references; 48 runs exercise the '
 'custom maximum-norm callback.',
 '',
 'The matvec callback must supply only the off-diagonal matrix, because the implementation subtracts it '
 'from b before applying the inverse diagonal. The public comments call it a matrix-vector product, but '
 'supplying the entire A would implement the wrong splitting. Both callbacks must run; the custom norm '
 'must run only in mode 4. Convergence, iteration limit and finite solutions are checked. Every result '
 'must match x_exact within normalized error 2e-9 and satisfy an independently formed full-matrix '
 'residual within 2e-10. The solver uses tolerance 1e-11; this is an increment criterion, so the true '
 'residual is checked separately. Observed maxima were 2.29881e-11 and 6.57610e-11.',
 '',
 'The first probe used history 4 and hit a GNU bounds error at makeb with index -5. Source review finds '
 'that diis removes ten entries whenever nmat reaches ndiis, so a small history makes nmat negative. The '
 '[retained probe](gams-candidates/ddpcm-diis-history/README.md) includes the exact main, normalized '
 'hash, package pin and full result. The published consumer uses the existing default history 25; it '
 'does not patch the library or claim to repair small histories. Arbitrary matrix conditioning, '
 'nonconvergence behavior, every history/eviction path, molecular coupling and forces remain outside '
 'this direct-solver check.',
 '',
 '## VTMOP quadratic Pareto segment (G2)',
 '',
 'The driver minimizes f1(x)=sum((x-a)**2) and f2(x)=sum((x-b)**2) on [0,1]^n. For n=2 and n=3, '
 'a_i=(i+1)/10 and b_i=1-a_i. The exact Pareto set is the segment p(t)=a+t*(b-a), 0<=t<=1. Orthogonal '
 'projection onto that segment cannot increase either objective. If the unclamped projection lies inside '
 'the segment, both objective improvements equal the squared distance from x to its projection. These '
 'formulas provide independent geometric references without another optimizer.',
 '',
 'Two intrinsic RANDOM_SEED settings (1729 and 2903) are applied for each dimension. All four runs use '
 'the existing serial VTMOP/GPS/LSHEP setup, a 200-evaluation black-box budget, 40 maximum iterations, '
 'search budget 6, initial search budget 10 and local optimization budget 200. Both seed settings '
 'produced identical observed archives for each dimension. These are seeded repeats of two problem '
 'configurations, not four demonstrably independent stochastic searches or a reproducibility guarantee '
 'across compilers.',
 '',
 'Every archive point must be finite and feasible, its two objectives must match independent scalar '
 'recomputation within 1e-12, and no other returned point may dominate it. The projection dominance and '
 'interior orthogonal-distance identities are checked within 1e-12. Distances to the exact Pareto '
 'segment are divided by its length. Each run must have at least five returned points within relative '
 'distance 0.05, and those near-front points must span at least 0.25 in clamped segment coordinate t. '
 'Best and worst full-archive distances are reported rather than hiding distant points.',
 '',
 'There were 800 objective evaluations and 108 returned points. The two 2-D archives each had 32 points, '
 '28 near-front points, maximum relative distance 0.128205 and near-front span 0.978158. The two 3-D '
 'archives each had 22 points, five near-front points, maximum relative distance 0.181848 and near-front '
 'span 0.970018. Thus 66 points met the near-front threshold, all four best distances were zero at '
 'printed precision, and the largest projection identity error was 3.03702e-16. This is a modest '
 'finite-budget approximation check, not a tight solution-accuracy or global convergence guarantee.',
 '',
 'The first consumer required all archive points to have relative distance <=0.15. It passed both 2-D '
 'runs but failed on the first 3-D run. The [retained exact '
 'probe](gams-candidates/vtmop-archive-distance/README.md) documents that unsupported stronger '
 'assertion. The revised driver verifies a useful near-front subset and reports the full-archive '
 'maximum; it does not claim the failed all-point accuracy bound. Other objective families, dimensions, '
 'surrogate choices, parallel evaluation, checkpoint recovery and comparative performance remain '
 'unverified.',
 '',
 '## Sources, licenses and actual output',
 '',
 'Pinned solver interfaces, implementations and author examples were reviewed. The drivers are '
 'independently written MIT API consumers; upstream ddPCM LGPL and VTMOP MIT terms remain separate and '
 'unchanged. No upstream implementation or example bodies are copied. Loading a driver does not submit a '
 'job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def data_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-data-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-data-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked data-handling drivers',
 '',
 'Ten independently written API consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted '
 'hosted sandbox. All reused existing package libraries and compiled only their mains and executables. '
 'The [verification report](gams-data-ten-validation.json) retains pins, normalized source hashes, '
 'compiler/build details and complete output. These extend GAMS N data-handling coverage. Numerical '
 'records with known failures are not relabeled as verified. GAMS categories are not exhausted.',
 '',
 '## Editable integer vectors (fortran_vector, N4)',
 '',
 'Twelve traces begin with capacities 1..5 and append 96 scalar values modulo 19, then six four-element '
 'batches modulo 23. A separate plain-array state model checks every active value after each append, '
 'removal of the fixed value zero, twelve positional deletions, cut, pop-to-empty and '
 'clear/reinitialize. There are 2,622 checked operations and 143,017 element references. Removal '
 'arguments do not alias the container storage. Unique, sorting, invalid indices and self-aliased remove '
 'arguments remain unverified.',
 '',
 '## Integer sets (integer_set, N4)',
 '',
 'Eight traces apply 240 deterministic edits to paired 32-bit and 64-bit sets. Keys lie in [-50,50]; '
 '64-bit payloads add 5,000,000,000. A Boolean membership array independently tracks duplicate insertion '
 'and present/absent removal. Every check rejects duplicate elements and compares complete membership. '
 'The 32-bit set is also sorted and must be strictly ascending. Clear/reuse precedes explicit '
 'destruction. There are 1,944 paired membership checks and 218,354 stored-value references. 64-bit '
 'sorting, integer extrema and reuse after destroy remain unverified.',
 '',
 '## Heterogeneous linked lists (slinked-list, N4)',
 '',
 'Twenty cycles use lengths 1+modulo(17*cycle,61) and rotate integer, default-real and fixed-width '
 'character values. An independent formula checks all 601 elements, dynamic types and insertion order. '
 'Emptying retains capacity; later appends replace values/types in existing nodes. Maximum previous '
 'length supplies the capacity reference. Iterator exhaustion and explicit finalization are checked. '
 'Empty-list iterators, mutation during iteration, arbitrary pointer lifetimes and memory-leak behavior '
 'remain unverified.',
 '',
 '## Scanner cursor semantics (scanner, N3)',
 '',
 'Sixty-four generated printable-ASCII strings of lengths 1..64 are compared with direct string '
 'indexing. The consumer checks 3,232 cursor positions through forward/backward traversal, immutable '
 'peek/peek_back, remaining count, failed end advances, oversized clamped moves and forward jump_to '
 'searches. The jump reference starts after the current position. Empty input, Unicode semantics, '
 'reverse jumps and negative movement counts remain unverified.',
 '',
 '## Token fields and callbacks (fortran-tokenizer, N3)',
 '',
 'Sixty-four constructed records contain named fields separated by space, comma, semicolon, tab and '
 'newline. Separators repeat and occur at both ends; fields starting with ! are ignored. The expected '
 '423 retained strings are saved while constructing the input, rather than parsed by a second tokenizer. '
 'Stored procedure-pointer callbacks and optional callback arguments alternate across records. Empty '
 'input and clearing every returned list are checked. Default validator, quoting/escaping and Unicode '
 'lexical rules remain unverified.',
 '',
 '## Delimiter enclosure (enclose, N3)',
 '',
 'All 820 strings through width three over ()[]{}<>x are checked with a separate SELECT CASE '
 'bracket-pair involution. The reverse closing sequence must match get_closing_brackets. Three trimmed '
 'ASCII payloads give 2,460 fixtures for automatic enclosure, literal repeated delimiters and explicit '
 'END closures. Empty delimiters and payloads are included. Arbitrary trailing-blank preservation and '
 'UTF-8 delimiter semantics remain unverified.',
 '',
 '## Growable matrices (rearrayfx, N4)',
 '',
 'Sixteen traces combine row counts [1,2,3,4] and overprovision factors [1,1.5,2,3]. The column schedule '
 '[1,3,2,7,4,12,1,5] gives 128 explicit allocations through spare capacity and new backing storage. The '
 'active prefix shared with the preceding view must survive before new values are assigned. Explicit '
 'dyadic values and a final shape-changing 2-by-3 array assignment supply 2,096 scalar references. '
 'Inactive capacity, zero sizes, container-object copying, row-changing preservation and memory-leak '
 'behavior remain unverified. Library allocation debug messages are retained in the saved output.',
 '',
 '## UTF-8 code points (string-utf-8, N3)',
 '',
 'Thirty-three fixtures of lengths 0..32 use integer code points [65,233,8364,119070,769,32] and an '
 'independent arithmetic UTF-8 encoder. They cover one-to-four-byte encodings, a combining mark and '
 'space. Direct construction supplies byte references for round trips, positive substrings of up to '
 'three code points, first single-code-point searches, expanding replacement of U+00E9 by U+20AC plus x, '
 'and deletion. There are 825 exact checks across 528 original code points. Malformed encoding, '
 'normalization, grapheme clusters, negative substring semantics and multi-code-point search remain '
 'unverified.',
 '',
 '## C++ sorting and binary search (flibcpp, N6)',
 '',
 'The 780 original-pattern arrays combine lengths 0..64, four patterns and INT32/INT64/REAL64 wrappers. '
 'Patterns are ascending, descending, duplicated modular values and alternating signs. Scalar insertion '
 'sort gives the independent reference. INT64 values add 5,000,000,000 and REAL64 values are exact '
 'eighths. All 24,960 sorted entries and 31,980 queries over keys -20..20 are checked. Duplicate hits '
 'require a valid matching index; absence requires zero. First-occurrence semantics, NaNs, custom '
 'comparators, strided arrays, ordering stability and large-size index limits remain unverified. This is '
 'class-specific N6 evidence and does not automatically verify every N5 capability.',
 '',
 '## Modbus register encoding (fortran-modbus, N2)',
 '',
 'The consumer checks 264 finite binary32 patterns in ABCD, BADC, CDAB and DCBA order. Eight explicit '
 'IEEE patterns include signed zeros, normal/subnormal minima, a largest finite value and an asymmetric '
 'pattern; 256 further signed patterns vary exponents and mantissas. Expected register words come '
 'directly from bit positions and a permutation table, with explicit signed Fortran 16-bit carrier '
 'conversion.',
 '',
 'There are 1,056 independent setter and 1,056 independent getter comparisons. Setters must produce '
 'reference words; getters receive independently assembled words and must reproduce exact bits. This '
 'prevents compensating encoder/decoder errors from passing a paired round trip. The [libmodbus 3.1.11 '
 'source contract](https://raw.githubusercontent.com/stephane/libmodbus/v3.1.11/src/modbus-data.c) was '
 'reviewed alongside the pinned Fortran binding; the existing cached system package is libmodbus-dev '
 '3.1.11-2. NaN payloads, infinities, network I/O, physical devices and other floating formats remain '
 'unverified.',
 '',
 '## Provenance, licenses and actual output',
 '',
 'Pinned public APIs, implementations and available author examples were reviewed. These are '
 'independently written MIT API consumers; no upstream implementation or example bodies are copied. '
 'Upstream package/system-library terms remain separate and unchanged. Loading a driver does not submit '
 'a job. No failed probes occurred in this ten-driver batch.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def state_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-state-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-state-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked configuration, state and reference drivers',
 '',
 'Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. '
 'All reused existing package libraries and compiled only mains and executables. The [verification '
 'report](gams-state-ten-validation.json) preserves pins, source hashes and complete output. The '
 '[retained probes](gams-candidates/state-ten-first-probes/README.md) distinguish consumer/API '
 'corrections from unsupported package behavior. GAMS categories are not exhausted.',
 '',
 '## Array bounds (array_range, R)',
 '',
 'The driver checks 784 nonempty rank-2 arrays: both lower origins range from -3 to 3 and both extents '
 'from 1 to 4. The descriptor constructor receives actual intrinsic bounds, but exact expected endpoints '
 'come independently from the allocation parameters. All 3,136 bound entries and 4,900 visited elements '
 'are checked; traversal sums use closed-form arithmetic-progression formulas rather than another '
 'traversal. Zero extents, malformed bound arrays and scalar/vector/tensor aggregate constructors remain '
 'unverified.',
 '',
 '## Typed values and owned arrays (any, N4)',
 '',
 'Thirty-two fresh groups contain an INT32 scalar, dyadic REAL64 scalar, logical, nonempty character '
 'string, integer vector and REAL64 matrix. Vectors have lengths 1..32 and matrices shape [2,length]. '
 'Original input arrays are overwritten after wrapping; extraction must recover the earlier exact values '
 'and shape, establishing owned copies for these cases. All 1,712 scalar/array references pass. '
 'Type-bound assignment is used; the initial attempted module-level assignment import was a consumer '
 'error.',
 '',
 'Empty values are deliberately outside the successful scope. After fixing the import, the empty-string '
 'fixture segfaulted; a second probe with nonempty strings and empty arrays segfaulted at array '
 'extraction. Exact mains/results are retained. The published driver uses nonempty inputs and does not '
 'fix these GNU 16 compiler/library interactions. Reassigning populated buffers, type mismatches, '
 'container copying and all ranks/kinds remain unverified.',
 '',
 '## Format descriptors (fed, N1)',
 '',
 'There are 550 exact full-record comparisons against independently constructed native Fortran format '
 'strings. Integer widths 1..12 combine minimum digits 0..min(width,6) and five signed/zero/large '
 'values. Fixed-point widths 4..18 in steps of two combine decimal places 0..4 and five exact binary '
 'values. Five concatenated integer/character/real formats are also checked. Overflow fields and '
 'trailing output blanks remain part of the comparison.',
 '',
 'The oracle follows reviewed FED normalization: a zero minimum omits .m (it is not native Iw.0 zero '
 'suppression), and real width is raised to at least d+2. The first incorrect native-format assumptions '
 'are retained as consumer reference errors, not package defects. Exponential, complex, user-defined, '
 'locale and cross-compiler rounding behavior remain unverified.',
 '',
 '## INI scalar/default values (io_utilities, N1)',
 '',
 'Thirty-six self-contained INI files check 180 exact references for signed integers, dyadic reals, '
 'text, absent-key defaults and all six reviewed true spellings. They contain a section header and '
 'inline comments, but descriptors use wildcard sections. Expected values come from the file-generation '
 'parameters. Files are deleted inside the sandbox. False spellings, section-specific matching, '
 'malformed input and CLI filename overrides remain unverified.',
 '',
 '## Nested configuration and dynamic arrays (config-fortran, N1)',
 '',
 'Twenty-four fresh configurations/files check integer, REAL64, logical and text values, solver%dt '
 'nested keys, a retained default and dynamic arrays of lengths 1..8. Exact expected eighths are written '
 'and independently compared after reading; CFG_get_size must match the requested length. There are 228 '
 'scalar/array references. Each object is explicitly cleared. Repeated reads into the same '
 'configuration, malformed files, unknown keys and CLI inputs remain unverified.',
 '',
 '## Mixed dictionaries and deletion (fdict, N4)',
 '',
 'Eight 49-key dictionaries store integer, dyadic REAL64, text and three-element integer-array values. '
 'Reverse-order lookups must match independent formulas; source arrays are overwritten after insertion '
 'to check ownership. Every even key is then deleted, and selected odd survivors plus the base key are '
 'checked before explicit destruction. There are 488 typed lookups. The character assign overload has no '
 'success keyword; correcting that consumer error preserves the numeric/array status checks. '
 'Missing/type-mismatched lookups, duplicate-key policy, dictionary copying and every hash collision '
 'remain unverified.',
 '',
 '## C-backed vector and map state (qcontainers, N4)',
 '',
 'Eight traces perform 96 vector appends each, periodic indexed replacements, FIFO removal to empty, and '
 'hash-map insertion/replacement across 17 keys. A plain array and indexed membership/value tables '
 'supply 51,080 exact value/presence references. Absent map keys, vector clear, map clear/reuse and '
 'scope finalization are checked.',
 '',
 'Appending to the cleared vector is excluded: the retained probe reports success but returns an '
 'incorrect payload, and source review shows qvector_clear resets the C element size to zero. The '
 'successful driver does not append afterward or patch the library. Map clear/reuse still passes. '
 'Payloads are integers; iterators, object copying, all ownership paths, memory leaks and thread safety '
 'remain unverified.',
 '',
 '## SQLite transactions and queries (sqliteff, N1)',
 '',
 'An in-memory database receives 64 prepared/bound inserts for keys -32..31 and values key/8. Each '
 'insertion checks SQLITE_DONE and statement reset. After commit, an update and sentinel-row insertion '
 'are rolled back. Five exact aggregate references (count, sum, average, minimum and maximum) verify '
 'restoration. Deleting keys divisible by three leaves 43 rows; ordered key/value pairs must match an '
 'independent integer loop, followed by SQLITE_DONE. All statements are finalized and the database '
 'closed. Disk persistence, concurrent transactions, text/NULL, error recovery and general N5 searching '
 'are outside this N1 driver.',
 '',
 '## Integer expression parsing (shunting-yard-fortran, N3)',
 '',
 'The driver supplies independently written integer operand/binary callbacks and checks 437 valid '
 'bounded expressions against direct arithmetic. Seventy-two combinations of a=1..6, b=1..4, c=1..3 each '
 'generate six precedence/parenthesis/subtraction/division templates. Five fixed cases check '
 'right-associative powers, grouped powers, mixed precedence, binary negation as 0-x and ignored spaces. '
 'All expected division results are exact integers and powers stay safely bounded.',
 '',
 'Unary registration is intentionally absent. The retained registered-unary-minus probe evaluates 1-1-1 '
 'as 1 instead of -1: register_unary adds the minus token to a shared right-associative list that is '
 'also consulted for binary operators. The binary-only consumer passes without a library change. '
 'Unary/real-function behavior, malformed syntax, overflow, registration isolation and arbitrary '
 'callback types remain unverified.',
 '',
 '## Exact SI constants and photon energies (fundamental_constants, R)',
 '',
 'The selected Planck constant, speed of light and elementary charge match the defining decimal values '
 'in the [NIST 2022 CODATA listing](https://physics.nist.gov/cuu/Constants/Table/allascii.txt). The '
 'independent [Python Fraction oracle](../fpm_catalog/gams-drivers/references/photon_vectors.py) uses '
 'exact rational arithmetic to generate [saved energy '
 'vectors](../fpm_catalog/gams-drivers/references/photon-vectors.json); no package imports supply the '
 'reference. Source/data hashes are recorded with the driver.',
 '',
 'Twelve integer wavelengths [1,2,10,121,250,400,500,656,800,1064,10000,1000000] nm give 24 '
 'joule/electron-volt energy references. The native REAL64 computation must agree within relative '
 'tolerance 2e-15; its observed maximum was 2.22045e-16. This checks three exact constant values and '
 'their use in unit conversion, not the entire collection or the accuracy of constants with experimental '
 'uncertainty.',
 '',
 '## Provenance and actual output',
 '',
 'Pinned APIs, implementations and available author examples were reviewed. These are independent MIT '
 'consumers; upstream implementation/example bodies are not copied and upstream licenses remain '
 'separate. Exact failed sources/results are retained with hashes and pins. No unsupported probe is '
 'promoted to successful verification, and loading an example does not submit a job.',
 '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def interop_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-interop-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-interop-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked structured-data and interoperability drivers', '',
             'Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted '
             'hosted sandbox. Every run reused the existing package library and compiled only the '
             'main and executable. The [verification report](gams-interop-ten-validation.json) '
             'preserves pins, normalized source hashes, timings and complete output. '
             'GAMS categories are not exhausted.', '',
             '## Independent references and limits', '',
             'JSON and YAML values are compared with the parameters used to generate their inputs; '
             'the JSON values must match both before and after serialization. The NPY consumer '
             'uses native stream I/O rather than a package reader, checking header shape/type/order '
             'and every payload value. Native stream integer/REAL64 representation is scoped to '
             'the little-endian GNU/Linux sandbox.', '',
             'Container states are compared with plain indexed arrays after every operation. '
             'Error lists are checked against independently numbered diagnostics and parity '
             'categories, including snapshots from before each append. File drivers compare '
             'expected byte lengths and content through the native runtime and test disappearance '
             'after deletion. These are Linux filesystem checks, not portability claims.', '',
             'Lua integer polynomials, dyadic affine arithmetic and finite sums use direct closed-form '
             'Fortran references; the low-level binding also checks stack depth and one syntax error. '
             'Embedded NumPy reductions use scalar-loop sum/max/sum-of-squares references. '
             'Sum/max are exact for the selected dyadic inputs and Frobenius norms allow relative '
             'error 1e-13. Scalar reductions do not establish array-axis or memory-layout correctness.', '',
             'The [two retained initial probes](gams-candidates/interop-ten-first-probes/README.md) '
             'are consumer corrections: erloff category tags require message_type_t, and valid '
             'NPY shape tuples permit a trailing comma. Exact failed sources, hashes, pins and '
             'full service results remain available; neither is classified as an upstream defect.', '']
    for d in drivers:
        lines += ['### '+d['package_id']+' ('+d['gams_code']+')', '',
                  d['modifications'], '']
    lines += ['## Provenance and actual output', '',
              'Pinned APIs, implementations and available author examples were reviewed. These '
              'are independent MIT consumers; upstream implementation/example bodies were not '
              'copied and upstream licenses remain separate. A checked driver demonstrates only '
              'its recorded class and scope; it does not verify other package classifications. '
              'Loading an example does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def storage_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-storage-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-storage-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked storage, configuration and binding drivers', '',
             'Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted '
             'hosted sandbox. Each reused the existing package library and compiled only the main '
             'and executable. The [verification report](gams-storage-ten-validation.json) preserves '
             'pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.', '',
             '## Independent references and limits', '',
             'Dense undirected graph adjacency indices, vertex features and degrees are compared with '
             'plain-array oracles. The smart-pointer consumer owns integer arrays and checks nested '
             'alias counts, shared mutation, cleanup counts and a closed-form cleanup checksum. '
             'The gFTL vector/map traces check every prefix in reverse against integer/dyadic formulas.', '',
             'The regex consumer enumerates every nonempty string of length at most four over 01a. '
             'and checks two pattern languages with an independently written character-state grammar. '
             'This is bounded coverage of these patterns, not a general regex conformance suite. '
             'Offline URL components and path updates are checked against generated exact strings; '
             'no network request is made.', '',
             'LMDB transactions are compared with 64 formula-generated key/value states after '
             'commit, rollback, and committed replacements/deletions. Lua configuration values '
             'are checked against closed forms, including missing-key defaults and status flags. '
             'Logging must produce exactly the expected ordered warning/error text while filtering '
             'debug/info records.', '',
             'NetCDF4 wrapper files are cross-read with native NetCDF C indexed calls and checked '
             'against explicit axis-dependent formulas, reversed C axis order, zero-based indices '
             'and metadata. The [Unidata variable API](https://docs.unidata.ucar.edu/netcdf-c/current/group__variables.html) '
             'and [dimension API](https://docs.unidata.ucar.edu/netcdf-c/current/group__dimensions.html) '
             'document the C signatures. Classic NetCDF additionally '
             'checks CDF-1 magic and full/indexed reads after one-cell updates. These APIs share '
             'the native NetCDF library, so this does not establish independent file-format '
             'implementation compatibility. Checks are for the pinned GNU/Linux builds.', '',
             'The [retained native-module probe](gams-candidates/storage-ten-native-module/README.md) '
             'failed during FPM dependency discovery because the external netcdf Fortran module '
             'was not exposed by this consumer setup. It never compiled or ran and is not an '
             'upstream I/O defect. The successful C API consumer needs no manifest or library changes.', '']
    for d in drivers:
        lines += ['### '+d['package_id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '',
              'Pinned APIs, implementations and available author examples were reviewed. These '
              'independent MIT consumers do not copy upstream implementation/example bodies; '
              'upstream license terms remain separate. Only each recorded class and tested scope '
              'is verified. Loading an example does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def workflows_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-workflows-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-workflows-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked command-line, testing and workflow drivers', '',
             'Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted '
             'hosted sandbox on their first verification runs. Every run reused the existing package '
             'library and compiled only the main and executable. The '
             '[verification report](gams-workflows-ten-validation.json) preserves pins, normalized '
             'source hashes, timings and complete output. GAMS categories are not exhausted.', '',
             '## Independent references and limits', '',
             'The argparse consumer relaunches its own executable twelve times with generated options. '
             'Parsed integers, exact binary reals, quoted labels, absent defaults and present/absent '
             'flags are compared with the generating parameters. M_CLI converts 32 generated '
             'prototypes into native NAMELIST text; the native reader must recover all 224 values. '
             'These are bounded parser examples, not all-syntax or invalid-input conformance suites.', '',
             'Veggies equality result flags follow a 17-by-17 integer truth table, and combined '
             'objects must report exact assertion/failure counts. Its test runner executes two passing '
             'specifications. Julienne independently checks 289 integer comparisons and 765 dyadic '
             'absolute-tolerance outcomes against integer inequalities, including inclusive boundaries. '
             'Intentionally failed result objects are inspected successfully rather than ignored. '
             'Arithmetic inside these consumers belongs to the examples, not the testing libraries.', '',
             'Tcl finite sums are checked against n*(n+1)*(2*n+1)/6 for n=0..64; a malformed expression '
             'must fail and the interpreter must subsequently recover. Four fixed local printf pipes '
             'are checked for all 170 ordered records, end of output and close status. The Linux '
             'filesystem example checks 65 binary file lifecycles and directory/file classification. '
             'No network or host-system access is added.', '',
             'The gFTL consumer checks 55,872 integer prefix values and 1,152 closed-form prefix sums. '
             'FyCollections integer list edits follow plain-array oracles; integer/string contents, '
             'exact search indices and missing searches are checked after every step. These exercise '
             'the existing audited template instantiations, not arbitrary generated types.', '',
             'The history consumer records twelve commands, edits each via a scratch directive unit, '
             'then recalls each original to establish that substitutions did not overwrite history. '
             'It uses the supported 1024-character buffers and executes no recorded text as shell code. '
             'All successful sources were saved directly; this batch produced no failed service probes.', '']
    for d in drivers:
        lines += ['### '+d['package_id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '',
              'Pinned APIs, implementations and available author examples were reviewed. These '
              'independent MIT consumers do not copy upstream implementation/example bodies; '
              'upstream license terms remain separate. Only each recorded class and tested scope '
              'is verified. Loading an example does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def statistics_services_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-statistics-services-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-statistics-services-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked statistical, matrix, quadrature and service drivers', '',
             'Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted '
             'hosted sandbox. Seven newly reviewed stdlib procedures and three existing service '
             'records have dedicated drivers. Every successful run reused the existing package '
             'library and compiled only the main and executable. The '
             '[verification report](gams-statistics-services-ten-validation.json) preserves pins, '
             'source hashes, timings and full output. GAMS categories are not exhausted.', '',
             '## Independent numerical references', '',
             'Median references come from nine-bin integer histogram ordering, not another sorting '
             'or selection routine. Covariance references use pairwise differences: the sum over '
             'k<l of (x[k,i]-x[l,i])*(x[k,j]-x[l,j]), divided by n*(n-c), where c is 1 for sample '
             'or 0 for population covariance. Correlations normalize these pairwise sums. Both '
             'axis conventions are checked without using package mean, variance or covariance '
             'routines to produce the references.', '',
             'Third/fourth moment references use exact INT64 arithmetic. With x[i]=q[i]/8 and '
             'S=sum(q), the central moment numerator is sum((n*q[i]-S)**p), with denominator '
             'n**(p+1)*8**p. Explicit zero-center references instead use sum(q[i]**p)/(n*8**p). '
             'All integer operations stay within INT64 range; final rational conversion is REAL64.', '',
             'Determinants of 96 nonsingular 3x3 matrices are checked with the independent six-term '
             'polynomial. Inverses of 128 nonsymmetric matrices A=D*(I+u*v**T)*E are compared with '
             'E**(-1)*(I-u*v**T/(1+v**T*u))*D**(-1), plus left/right identity residuals. '
             'Default calls must preserve input matrices. These are bounded matrix families, '
             'not a certification for arbitrary conditioning, sizes or singular cases.', '',
             'Trapezoidal integration checks 864 affine antiderivatives over nonuniform, reversed '
             'and constant-spacing grids. Selected inputs/results are exact binary values; no '
             'reference is produced by summing another trapezoidal rule. Nonlinear integration '
             'errors and adaptivity remain outside this driver.', '',
             '## Service references and scope', '',
             'Timer results, multiplied by nloops, must lie between independently sampled inner '
             'and outer native clock intervals. Four SYSTEM_CLOCK ticks and 2 microseconds CPU '
             'resolution slack are allowed. Sixteen reused timer pairs also check exact work '
             'sums. No performance or minimum-duration claim is made.', '',
             'Assertions are tested through 65 passing pure-contract calls and one deliberately '
             'false assertion in a self-invoked child. The parent requires nonzero exit and the '
             'specified diagnostic; the expected failure is checked rather than ignored. '
             'MPI wrappers run on exactly one process and check 1,408 identity values/statuses '
             'across 64 traces. This does not verify communication between processes or speedup.', '',
             '## Retained random-array bounds failure', '',
             'The [requested-bounds probe](gams-candidates/test-helper-bounds/README.md) for '
             'fortran_test_helper compiles with cached-library reuse but returns a maximum '
             '1.944083652 for requested [0,1] bounds. The public source transforms intrinsic draws '
             'with 0.99*(low+(high+1-low)*draw), explaining the excess. Its exact source, normalized '
             'hash, package pin and full failed result are retained. That record receives no '
             'checked driver and no source patch.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies explicit '
             'parents for covariance/correlation (L1c1b), shape moments (L1a1c), real general '
             'determinants (D3a1) and nonautomatic sampled-grid quadrature (H2a1b2). '
             'Only these reviewed scopes are promoted; adjacent statistical/solver capabilities '
             'and the retained bounds failure remain separate.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '',
              'Pinned APIs, implementations and available author examples were reviewed. These '
              'independent MIT consumers do not copy upstream implementation/example bodies; '
              'upstream license terms remain separate, including the custom assertion-library '
              'terms. Only each recorded class and tested scope is verified. Loading an example '
              'does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def factorization_rules_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-factorization-rules-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-factorization-rules-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib factorization, matrix and quadrature drivers', '',
             'Ten newly reviewed stdlib procedures passed GNU Fortran 16.2.0 with FPM 0.12.0 in '
             'the restricted hosted sandbox on their first verification runs. Existing compiled '
             'stdlib libraries were reused; only mains and executables were compiled. The '
             '[verification report](gams-factorization-rules-ten-validation.json) records package '
             'pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.', '',
             '## Factorizations and spectral references', '',
             'For 64 real 5x3 inputs, full and reduced QR must reconstruct the input, have '
             'orthonormal Q columns and triangular R. These defining equations avoid assuming a '
             'particular choice of factor signs. For 56 SPD matrices, the independent reference '
             'is the positive-diagonal dyadic lower factor used to form A=L*L**T. Both Cholesky '
             'triangle choices are compared directly, including unused-half zeroing.', '',
             'Symmetric eigenproblems use A=shift*I+rho*u*u**T. Its spectrum has n-1 copies of '
             'shift and one value shift+rho*(u**T*u). Upper/lower triangle selections, eigenpair '
             'residuals and orthonormality are checked for 96 eigensystems. No arbitrary basis '
             'is prescribed for the repeated eigenspaces.', '',
             'The SVD inputs are real 4x3 matrices constructed from orthonormal factors and '
             'prescribed singular values, with ranks one through three. Forty-eight decompositions '
             'check all 144 singular values, both singular-vector equations, reconstruction and '
             'thin-factor orthogonality. Singular-vector signs and nullspace bases are not unique. '
             'The pseudoinverse reference for A=u*v**T is v*u**T/((u**T*u)*(v**T*v)); 80 rectangular '
             'cases check 1,120 entries and all four Moore-Penrose identities with explicit rtol=1e-10.', '',
             '## Norms and matrix exponentials', '',
             'Independent scalar loops compute maximum absolute column/row sums and the square root '
             'of the sum of squares. These supply 525 1/infinity/Frobenius norm references, including '
             '35 zero matrices. This does not test the spectral 2-norm or higher-rank reduction APIs.', '',
             'For a strictly upper-triangular 3x3 N, N**3=0, so exp(shift*I+N) equals '
             'exp(shift)*(I+N+N**2/2). A second family is the 2x2 plane-rotation generator, whose '
             'exponential has analytic sine/cosine entries. Default and order-12 Pade calls '
             'supply 858 entry references across 132 calls. These bounded families do not certify '
             'accuracy for general stiff or badly scaled matrices.', '',
             '## Quadrature references', '',
             'Simpson integration checks analytic cubic antiderivatives on uniform odd grids and '
             'quadratic antiderivatives on nonuniform odd grids: 432 references over lengths 3..33. '
             'No second numerical quadrature routine supplies the expected integral. Even-grid '
             'policies, adaptivity and arbitrary-integrand errors remain unverified.', '',
             'Gauss-Legendre and Lobatto node/weight routines each generate 33 rules, orders 2..12, '
             'on [-1,1], [0,1] and [-0.5,1.5]. With z=(2*x-a-b)/(b-a), the exact integral of z**p '
             'is zero for odd p and (b-a)/(p+1) for even p. Gauss rules check 462 moments through '
             'degree 2*n-1; Lobatto rules check 396 through degree 2*n-3 and require interval endpoints. '
             'Both check positive weights, ordered nodes and symmetry. Moment tolerance is '
             '5e-12 times interval width; high-order or reversed-interval behavior is not claimed.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies matrix norm '
             'class D1b2; QR, real SPD factorization, symmetric eigenproblems, SVD and generalized '
             'inverses use D5, D2b1b, D4a1, D6 and D9c. Simpson is nonautomatic sampled-grid '
             'quadrature H2a1b2; node/weight generation uses H2c. Matrix exponentials retain broad '
             'linear algebra D: a matrix-polynomial classification would not describe the general '
             'exponential procedure. Verification belongs only to these recorded stdlib APIs '
             'and configurations; no other package is promoted by these results.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '',
              'Pinned public APIs, implementations and author tests were reviewed. These are '
              'independent MIT consumers; upstream implementation/test bodies were not copied '
              'and upstream license terms remain separate. Input preservation and finite outputs '
              'are checked where specified. Loading an example does not submit a job.', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def special_functions_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-special-functions-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-special-functions-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib special-function drivers', '',
             'Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the '
             'restricted hosted sandbox. Existing stdlib libraries were reused; only mains '
             'and executables were compiled. The [verification report]'
             '(gams-special-functions-ten-validation.json) retains normalized source hashes, '
             'package pins, timings and full output. GAMS categories are not exhausted.', '',
             '## Independent references and limits', '',
             'Legendre values and their first derivatives use the explicit Rodrigues '
             'polynomial coefficients, differentiated term by term. This differs from the '
             'upstream three-term recurrence. Degrees 0..10 at 33 dyadic points in [-1,1] '
             'give 363 value references and 363 derivative references, including endpoints. '
             'The scaled absolute tolerance is 2e-11. This is polynomial class C3a2, without '
             'a claim about associated or noninteger Legendre functions.', '',
             'Complex gamma and log-gamma each have 24 independent reference constants from '
             'mpmath 1.3.0 at 80 decimal digits, confirmed at 120 digits to better than 1e-70. '
             'The [reference table](gams-special-functions-ten-references.json) records exact '
             'dyadic arguments and 26-digit component values. Gamma includes negative real '
             'parts away from poles; log-gamma uses positive real parts and the analytic '
             'branch real on the positive real axis. Both use scaled complex absolute '
             'tolerance 2e-11. This does not certify the full complex plane or branch cuts.', '',
             'Log-factorial checks INT64 arguments 0..200 against a REAL64 running sum of '
             'log(k). The pinned API returns REAL32 for every integer kind. Converting that '
             'result to REAL64 does not add precision, so the scaled tolerance is 2e-6; '
             'a double-precision accuracy claim would be incorrect.', '',
             'Lower, upper and regularized incomplete gamma use 264 shape/argument pairs '
             'each: integer-valued REAL64 shapes n=1..8 and x=0..8 in steps of 0.25. The '
             'independent oracle is Q(n,x)=exp(-x)*sum(x**k/k!,k=0..n-1), P=1-Q. Multiply '
             'by (n-1)! for unregularized integrals. The regularized driver checks both P '
             'and Q and their sum. Endpoints, x=n and both continuation branches are '
             'covered; noninteger shapes and integer overloads are not. Absolute/scaled '
             'tolerance 3e-12 does not promise relative accuracy in tiny tails.', '',
             'Beta and log-beta each check 144 integer-valued REAL64 shape pairs 1..12, '
             'in both argument orders. The reference uses B(a,1)=1/a followed by finite '
             'products B(a,b+1)=b*B(a,b)/(a+b), with a logarithm for log-beta. There are '
             '288 references per driver, scaled absolute tolerance 3e-12.', '',
             'Despite its name, incomplete_beta returns the regularized I_x(a,b), not '
             'the unnormalized integral. For integer shapes, an independent binomial '
             'tail sum from j=a to a+b-1 gives I_x. Shapes a,b=1..8 at 33 dyadic x in '
             '[0,1] give 2,112 references, including both endpoints and both symmetry '
             'branches, with scaled absolute tolerance 5e-12. No gamma, beta or numerical '
             'quadrature routine is used by this oracle.', '',
             'All floating results must be finite. Invalid inputs, extreme parameter '
             'scales, noninteger incomplete-integral shapes, other kinds and performance '
             'remain unverified. Passing these bounded examples does not establish '
             'accuracy for every argument supported by an API.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies '
             'C3a2 (Chebyshev, Legendre), C7a (gamma/log gamma), C7b (beta/log beta), '
             'C7e (incomplete gamma) and C7f (incomplete beta). Log-factorial uses C7a '
             'as log-gamma evaluated at n+1. '
             'These are independent MIT consumers; upstream implementation and test '
             'bodies were not copied. The pinned gamma-family author tests were '
             'reviewed; no direct Legendre example/test was found in those source trees. '
             'Loading a driver does not submit a job.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def systems_spectra_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-systems-spectra-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-systems-spectra-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib linear-system and spectral drivers', '',
             'Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the '
             'restricted hosted sandbox. Existing stdlib libraries were reused; only mains '
             'and executables were compiled. The [verification report]'
             '(gams-systems-spectra-ten-validation.json) saves normalized source hashes, '
             'package pins, timings and full output. GAMS categories are not exhausted.', '',
             '## Direct SPD solves (D2b1b)', '',
             'Two drivers construct 72 SPD matrices each, orders 2..10, from known dyadic '
             'positive-diagonal lower factors L. The matrices are A=L*transpose(L). Three '
             'prescribed solution vectors generate right-hand sides by scalar loops. Both '
             'triangle choices and vector/three-RHS matrix interfaces give 288 solve calls '
             'per driver. One driver calls solve_chol to factor and solve; the other calls '
             'solve_lower_chol/solve_upper_chol with independently constructed factors, '
             'without using a package factorization as its oracle. Both check finite '
             'solutions, prescribed values, original-matrix residuals, status and input '
             'preservation, with scaled tolerance 3e-12. Invalid SPD inputs, complex '
             'values, overwriting and general conditioning are not covered.', '',
             '## Equality-constrained and weighted least squares', '',
             'The D9b1 driver has 96 full-rank 6x3 fits with one equality constraint. '
             'Before a shear change of coordinates, the objective Hessian is diagonal H '
             'and the unconstrained minimizer is u. For constraint c*x=d, the independent '
             'answer is u-H**(-1)*c*lambda, with lambda=(c*u-d)/(c*H**(-1)*c). Applying '
             'the explicit inverse shear gives the reference in mixed coordinates. '
             'The residual is generally nonzero. The driver checks the solution, equality '
             'feasibility, Lagrange stationarity, status, finiteness and input preservation '
             'at scaled tolerance 5e-12. Multiple constraints and deficient ranks are not claimed.', '',
             'The D9a1 driver has 96 weighted line fits with 4..15 observations and '
             'nonuniform positive weights with ratio at most 16. Scalar sums sw, sx, sxx, '
             'sy and sxy give intercept/slope through an explicit two-by-two determinant. '
             'This independent formula and the weighted normal residuals are checked at '
             'tolerance 5e-12. Non-exact quadratic/noisy data prevent a merely interpolating '
             'fit. Zero/negative weights, rank deficiency and extreme weight ratios remain unverified.', '',
             '## Ordinary eigenproblems, Schur form and generalized eigenvalues', '',
             'Each spectral driver has 64 real 3x3 problems obtained by explicit shear '
             'similarities of a planar rotation block and a distinct real eigenvalue. '
             'The analytic spectrum has one conjugate pair alpha +/- i*beta and one real '
             'value r. Each driver matches all 192 eigenvalues without assuming output order '
             'at absolute tolerance 8e-12. Ordinary eig also checks both left/right '
             'eigenvector equations and Euclidean unit norms. Real schur checks '
             'orthogonal Z, reconstruction A=Z*T*transpose(Z) and nonoverlapping '
             'quasi-triangular blocks. Schur vectors are not individual eigenvectors.', '',
             'The generalized D4b2 driver forms B=S*diag(1,2,4)*inverse(S) and '
             'A=B*S*T*inverse(S), giving the same analytic eigenvalues for an invertible '
             'nonsymmetric B. Only the eigenvalue-only interface is verified. Singular '
             'pencils, defective/repeated spectra, complex input and other sizes remain unverified.', '',
             'The initial generalized-vector consumer incorrectly required Euclidean unit '
             'norms; GGEV uses max(abs(real(v))+abs(imag(v)))=1. Correcting that consumer '
             'exposed a second failure: complex eigenvalues were returned with real-only '
             'vectors and right residual about 0.322. The nearly conjugate scaled '
             'eigenvalues fail an exact equality comparison used by the pinned vector '
             'reconstruction routine. That is a likely cause, not a patched fix. '
             'The [exact sources and full failures](gams-candidates/stdlib-systems/README.md) '
             'are retained. The checked eigenvalue-only result does not promote returned '
             'generalized eigenvectors.', '',
             '## Iterative public kernels', '',
             'CG, Jacobi PCG and unpreconditioned BiCGSTAB each solve 102 manufactured '
             'dense systems, orders 2..18, with six solution families and nonzero initial '
             'guess 0.125. Matrix-vector products and preconditioners are ordinary module '
             'procedures; callers own and initialize the workspaces. Right-hand sides and '
             'final residuals are independently recomputed with scalar loops.', '',
             'CG uses symmetric strictly diagonally-dominant SPD matrices; PCG applies '
             'positive diagonal congruence factors spanning 0.1..10 and an explicit inverse '
             'diagonal preconditioner. Both request rtol=1e-12 and check solution/residual '
             'errors at 2e-9. BiCGSTAB uses nonsymmetric strictly diagonally-dominant '
             'matrices, requests rtol=1e-10 and checks errors at 5e-8. These bounded '
             'results do not certify all requested tolerances, breakdown recovery or '
             'arbitrary ill-conditioning. Sparse convenience interfaces, boundary masks, '
             'zero RHS and performance remain unverified.', '',
             'The dense convenience wrappers for all three methods compiled but segfaulted '
             'in this hosted configuration. Their exact probes are retained in the same '
             '[candidate notes](gams-candidates/stdlib-systems/README.md). The wrappers use '
             'internal procedure callbacks; the crash cause has not been established. '
             'Only the public kernels with module-level callbacks are demonstrated here; '
             'their success does not verify those failed wrappers. No upstream numerical '
             'source was patched.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies '
             'D2b1b (real SPD), D2a1 (general real nonsymmetric), D9a1 (unconstrained '
             'least squares), D9b1 (constrained least squares), D4a2 (ordinary real '
             'nonsymmetric eigenproblems) and D4b2 (real general pencils). The dense '
             'iterative examples do not claim sparse interfaces. These are independent '
             'MIT consumers. Pinned public APIs, implementations and author tests were '
             'reviewed; implementation/test bodies were not copied. Loading an example '
             'does not submit a job.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def distribution_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-distribution-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-distribution-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib probability-distribution drivers', '',
             'Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the '
             'restricted hosted sandbox. Existing stdlib libraries were reused; only mains '
             'and executables were compiled. The [verification report]'
             '(gams-distribution-ten-validation.json) saves normalized source hashes, '
             'package pins, timings and full output. GAMS categories are not exhausted.', '',
             'These examples demonstrate probability density functions (PDFs) and '
             'cumulative distribution functions (CDFs), not random-number generators. '
             'There are 16,669 reference comparisons altogether. Every result must be '
             'finite and nonnegative; CDFs must also stay at or below one and be '
             'nondecreasing on the ordered grids (monotonicity slack 3e-14).', '',
             '## Uniform: interval geometry (L5a1u)', '',
             'Each driver checks 1,625 inputs: five locations, five positive widths and '
             '65 dyadic relative positions from -0.5 to 1.5. The PDF reference is interval '
             'membership divided by width. The pinned API includes both endpoints in '
             'the density support; endpoint density values are an API convention. '
             'The CDF reference is the relative interval length clipped to [0,1]. '
             'Scaled absolute tolerance is 4e-15. Integer/complex overloads, invalid '
             'widths and other kinds are not covered.', '',
             '## Normal: high-precision references (L5a1n)', '',
             'Each driver checks 585 inputs: standardized z=-8..8 by 0.25 at three '
             'locations and standard deviations [0.25,1,4]. Independent standard '
             'normal PDF/CDF constants were computed with mpmath 1.3.0 at 80 decimal '
             'digits and confirmed at 120 digits to absolute difference below 1e-70. '
             'The [reference table](gams-distribution-ten-references.json) records '
             'arguments and 26-digit values. Density references transform by inverse '
             'standard deviation; CDF references remain unchanged. Scaled absolute '
             'tolerance is 3e-14. This does not certify relative accuracy in tiny tails, '
             'invalid scales, extreme arguments or complex overloads.', '',
             '## Exponential: scale and rate interfaces (L5a1e)', '',
             'Each driver makes 1,170 comparisons over 585 inputs: 65 standardized '
             'positions z=-0.5..7.5 by 0.125 and nine location/scale pairs. Both '
             'the location/scale interface and the shifted zero-location/rate '
             'interface are checked against independent 80/120-digit constants. '
             'Rate is the reciprocal of scale. The PDF reference is exp(-z)/scale '
             'on support; the CDF reference uses high-precision -expm1(-z). Negative '
             'support and the boundary are included, with scaled tolerance 3e-14. '
             'Invalid parameters, tiny relative tails and other kinds remain unverified.', '',
             '## Gamma: integer and noninteger shapes (L5a1g)', '',
             'The PDF driver has 486 references at shapes [1,1.5,2.5,3,5,8]. The '
             'CDF driver has 567 references and also includes shape 0.5. Each uses '
             'nine standardized positions [-0.25,0,0.125,0.25,0.5,1,2,4,8], three '
             'locations and three positive rates [0.25,1,4]. Inputs satisfy '
             'z=rate*(x-location); rate is not scale. The independent 80/120-digit '
             'unit-rate density/integral constants transform by rate for PDFs and '
             'remain unchanged for CDFs. The CDF is the lower incomplete gamma '
             'integral divided by gamma(shape). No second stdlib special-function '
             'call supplies the oracle.', '',
             'The shape-one endpoint density equals rate; for larger shapes it is '
             'zero. Singular density endpoints for shape below one are deliberately '
             'excluded, while the CDF checks shape 0.5 at its boundary. The scaled '
             'absolute tolerance is 3e-12, without a relative-tail accuracy claim. '
             'Only explicit-location, REAL64 interfaces and bounded parameter scales '
             'are verified; optional-default/error overloads and other kinds are not.', '',
             '## Beta: polynomial references (L5a1b)', '',
             'Each driver has 4,428 references: 36 integer shape pairs a,b=2..7, '
             'three locations and 41 relative positions from -0.125 to 1.125. '
             'For the PDF, a finite product supplies 1/B(a,b), multiplied by '
             'z**(a-1)*(1-z)**(b-1). For the CDF, an independent binomial tail '
             'sum from j=a to a+b-1 gives the regularized probability. These '
             'references call neither gamma/log-gamma nor beta/incomplete-beta '
             'routines. The shapes above one have continuous zero endpoint '
             'densities; outside-support densities vanish and CDFs saturate. '
             'Scaled tolerance is 3e-12. Shape-one/singular endpoint conventions, '
             'noninteger shapes, invalid parameters and other kinds remain unverified.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) places '
             'univariate PDFs/CDFs in L5a1, with leaves L5a1u (uniform), L5a1n '
             '(normal), L5a1e (exponential), L5a1g (gamma) and L5a1b (beta). '
             'Some leaf labels include other distributions; these drivers verify '
             'only the specifically named stdlib procedures. They do not establish '
             'random-sampling quality or performance.', '',
             'Pinned public APIs, implementations and author tests were reviewed. '
             'These independent MIT consumers do not copy upstream implementation '
             'or test bodies; upstream license terms remain separate. No numerical '
             'source was patched. Loading a driver does not submit a job.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def pca_ordering_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-pca-ordering-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-pca-ordering-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked ordering and array-algebra drivers; retained PCA probe', '',
             'Ten independent stdlib drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 '
             'in the restricted hosted sandbox. Existing libraries were reused; only '
             'mains and executables were compiled. The [verification report]'
             '(gams-pca-ordering-ten-validation.json) saves normalized source hashes, '
             'package pins, timings and complete output. GAMS categories are not exhausted.', '',
             '## Order statistics and associated sorting', '',
             'select and arg_select each make 2,976 calls: every rank in 186 arrays '
             'of lengths 1..31 across six deterministic dyadic families. Independent '
             'insertion sorting supplies expected order statistics. Ascending, '
             'descending, all-equal, signed, modular and repeated-block inputs '
             'exercise ties and pivots. select must preserve the full multiset and '
             'produce a valid partial partition. arg_select must preserve values '
             'and produce a valid index permutation and partition, including when '
             'initial indices are reversed. An arbitrary identity within ties is '
             'not prescribed. Empty/invalid ranks and bounded-search options are unverified.', '',
             'sort_index and sort_adjoint each make 780 calls on lengths 0..64, six '
             'families and both sort directions. A separate stable insertion sort '
             'supplies complete key order and original-position associations. '
             'sort_index actively sorts the keys and returns a permutation; it '
             'is not a passive-only argsort. sort_adjoint moves unique dyadic '
             'payloads alongside keys. Both check stable ordering within ties '
             'in ascending and descending mode, including empty/constant inputs. '
             'NaNs, infinities, workspace options and other index/payload kinds '
             'remain unverified.', '',
             'unique has 390 exact sorted-output comparisons, lengths 0..64. '
             'An independent bounded-bin membership scan supplies the sorted set '
             'without calling any sorting routine. Count, values, finiteness and '
             'input preservation are checked, including empty and all-equal '
             'inputs. Only sorted_output=true and tolerance=0 are verified; '
             'hash-based unsorted mode and approximate grouping are not.', '',
             '## Adjacent differences and vector products', '',
             'diff makes 325 comparisons on lengths 0..24 and orders 0..6, plain '
             'or with prepend/append arrays for positive orders. The independent '
             'reference is the explicit binomial stencil sum '
             'sum((-1)**(n-j)*choose(n,j)*x(i+j),j=0..n), rather than another '
             'sequence of adjacent differences. Order zero is the identity and '
             'inputs too short for a positive order give empty results. Exact '
             'bounded dyadic arithmetic, output length, finite values and input '
             'preservation are checked. This is an array difference operator, '
             'not a step-scaled numerical derivative. Rank-two/dimension options '
             'and negative-order policies remain unverified.', '',
             'cross_product checks 2,154 pairs: nine ordered basis pairs and '
             '2,145 bounded dyadic pairs, including zero and parallel vectors. '
             'A Levi-Civita determinant sum independently supplies all components. '
             'Antisymmetry and orthogonality to both inputs are also checked '
             'exactly. Arbitrary floating conditioning and scale extremes '
             'are not covered.', '',
             '## Outer products, tensor products and diagonals', '',
             'outer_product checks 224 rectangular rank-one matrices, rows 1..8 '
             'and columns 1..7, with four dyadic families including a zero factor. '
             'Every entry is checked, together with independent scalar-dot matrix '
             'action A*x=a*(b*x), zero adjacent two-by-two minors and '
             'sum(A*A)=sum(a*a)*sum(b*b). Complex conjugation semantics are not claimed.', '',
             'kronecker_product checks 432 products: 144 rectangular shape pairs '
             'and three sign/zero families. Independent flattened output indices '
             'supply every entry. A separate scalar contraction verifies '
             '(A tensor B)*vec(X)=vec(B*X*transpose(A)) using Fortran column-major '
             'ordering. This distinguishes block layout from an ordinary matrix '
             'product. The bounded dyadic cases use exact comparisons; empty '
             'inputs, other kinds and extreme scales remain unverified.', '',
             'diag makes 84 offset-diagonal constructions for vector lengths '
             '1..12 and offsets -3..3, checking the entire matrix including '
             'off-diagonal zeros. There are 168 extractions: embedded vectors '
             'and separately filled dense matrices with independent scalar '
             'index references. Shape, exact values and finiteness are checked. '
             'Rectangular extraction, empty vectors and out-of-range offsets '
             'are not covered.', '',
             '## PCA remains source-supported', '',
             'A separate analytic PCA consumer was prepared for 24 rotated '
             'full-rank datasets, both SVD and covariance methods, and known '
             'means, axes, singular values, variances and truncated projections. '
             'Its main source compiled, but linking failed with file-size limit '
             'signal 25 under the existing 16 MiB hosted limit. No program ran '
             'and no PCA numerical assertions were verified. This is a service '
             'limit, not evidence of incorrect numerical results.', '',
             'The [exact source, pin, hash and complete failure]'
             '(gams-candidates/stdlib-pca/README.md) are retained for local '
             'investigation. No checked PCA driver is published, and L13b '
             'remains source-supported. The separate retained forpca numerical '
             'failure is unchanged. No backend limit was relaxed or numerical '
             'source patched; outer_product is the tenth successful example.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) '
             'supplies broad searching N5 for order-statistic selection and '
             'sorting N6 for active/associated sorting and sorted unique sets. '
             'D1a11 covers other vector operations (array differences and cross '
             'products), D1b1 covers matrix initialization, D1b6 covers rank-one '
             'multiplication, and broad D1b covers tensor-product matrix operations. '
             'A finer passive-only sorting or numerical-derivative label would '
             'misdescribe these demonstrated interfaces.', '',
             'Pinned public APIs, implementations and author tests were reviewed. '
             'The checked drivers are independent MIT consumers; upstream '
             'implementation and test bodies were not copied, and upstream '
             'license terms remain separate. These are bounded correctness '
             'checks, not timing benchmarks. Loading a driver does not submit a job.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def activations_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-activations-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-activations-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib activation and normalization drivers', '',
             'Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 '
             'in the restricted hosted sandbox. Existing libraries were reused; '
             'only mains and executables were compiled. The [verification report]'
             '(gams-activations-ten-validation.json) saves normalized source '
             'hashes, pins, timings and complete output. GAMS categories are not exhausted.', '',
             '## Scalar values and independently differentiated references', '',
             'Nine drivers check Gaussian, ELU, ReLU, leaky ReLU, GELU, SELU, '
             'sigmoid, SiLU and softplus values on 97 exact dyadic points '
             'x=-6..6 by 0.125. ELU uses parameters [0.125,1,2]; leaky ReLU '
             'uses [0.125,0.5,1]. The other functions have no free parameter. '
             'The [reference table](gams-activations-ten-references.json) '
             'contains 1,261 value rows and independent derivative references, '
             'including those needed to reproduce the failed gradient probes.', '',
             'Definitions used by the independent mpmath 1.3.0 reference generator:', '',
             '```text\n'
             'Gaussian: exp(-x*x)\n'
             'ELU: x for x>=0, otherwise alpha*expm1(x)\n'
             'ReLU: max(x,0)\n'
             'leaky ReLU: x for x>=0, otherwise alpha*x\n'
             'GELU: x*Phi(x), with Phi the standard normal CDF\n'
             'SELU: scale*(x for x>0, otherwise alpha*expm1(x))\n'
             'sigmoid: 1/(1+exp(-x))\n'
             'SiLU: x/(1+exp(-x))\n'
             'softplus: log1p(exp(x))\n'
             '```', '',
             'mp.diff differentiates these definitions independently at 80 decimal '
             'digits. Values and derivatives are confirmed at 120 digits to '
             'absolute difference below 1e-65; 26-digit constants are stored in '
             'the table. SELU uses canonical decimal scale '
             '1.0507009873554804934193349852946 and alpha '
             '1.6732632423543772848170429916717. The Fortran comparisons use '
             'scaled absolute tolerance 2e-12, finite outputs and input preservation.', '',
             'Seven scalar drivers verify gradients as well as values. Derivative '
             'assertions at zero are omitted for ELU, ReLU, leaky ReLU and SELU, '
             'where piecewise definitions can have a kink. A chosen API branch '
             'value at such a point is not claimed as a unique mathematical derivative. '
             'GELU and SiLU gradients failed and are excluded from their published '
             'value-only drivers. Thus the successful scalar tests cover 1,261 '
             'values and 1,059 derivative values.', '',
             'All claims are limited to these bounded REAL64 grids. Large-input '
             'overflow/underflow behavior, relative accuracy of tiny outputs, '
             'other kinds and performance are unverified. In particular this is '
             'not a blanket stability claim for exp-based scalar activations. '
             'Approximate GELU and the fast approximate intrinsic APIs are not tested.', '',
             '## Softmax, log-softmax and diagonal derivatives', '',
             'The tenth driver normalizes 144 rank-one vectors of lengths 1..12 '
             'and 24 rank-two 3x4 arrays with explicit dim=1 and dim=2. Positive '
             'dyadic weights independently define probabilities w/sum(w), their '
             'logarithms and diagonal derivatives p*(1-p). Logits are log(w) '
             'plus a common shift from [-1000,0,1000]. These shifts test '
             'normalization without overflowing exp of the unshifted logits.', '',
             'Each of softmax, logsoftmax and softmax_grad has 1,224 entry '
             'references: 3,672 comparisons altogether. Finite values, '
             'normalization sums and unchanged inputs are checked at absolute '
             'tolerance 3e-12. Singleton and tied-logit cases are included. '
             'softmax_grad returns the Jacobian diagonal only; this driver '
             'does not claim a full Jacobian. Rank-three/four APIs, empty or '
             'nonfinite inputs, invalid dimensions, extreme dynamic ranges '
             'and performance remain unverified.', '',
             '## Retained gradient failures', '',
             'The exact [GELU and SiLU gradient probes and full results]'
             '(gams-candidates/stdlib-activations/README.md) are retained. '
             'Both compiled and ran against the pinned cached library, then '
             'failed comparison with independent derivatives at x=-6:', '',
             '| API | Actual | Independent derivative |',
             '| --- | ---: | ---: |',
             '| gelu_grad | -6.3628744084007051e-8 | -3.5468709453902015e-8 |',
             '| silu_grad | -1.2320303571493932e-2 | -1.2326432591525513e-2 |', '',
             'For GELU=x*Phi(x), the derivative is Phi(x)+x*phi(x). The '
             'pinned exponential term omits 1/sqrt(pi). For SiLU, the '
             'derivative is sigmoid(x)+x*sigmoid(x)*(1-sigmoid(x)); the '
             'pinned leading term uses exp(x) instead of sigmoid(x). '
             'The upstream SiLU gradient test repeats that implementation '
             'expression, illustrating why it is insufficient as an independent '
             'oracle. No upstream numerical source was patched.', '',
             'The failed gradient APIs have separate source-reviewed procedure '
             'records without checked drivers. Successful GELU/SiLU value '
             'checks do not promote their gradients, and neither failed '
             'gradient call appears in the published examples.', '',
             '## Classification and provenance', '',
             'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) '
             'supplies broad C19 (other special functions) for the scalar '
             'activation functions and D1a11 (other vector operations) for '
             'normalization. These records do not claim a fitting/training '
             'algorithm or an invented neural-network taxonomy leaf.', '',
             'Pinned public APIs, implementations and available author tests '
             'were reviewed. No direct softplus author consumer was found in '
             'the pinned test file; its public API and implementation were '
             'reviewed directly. These are independent MIT consumers; upstream '
             'implementation/test bodies were not copied and upstream license '
             'terms remain separate. Loading a driver does not submit a job.', '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def grids_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-grids-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-grids-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib grid and numerical utility drivers',
     '',
     'Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing stdlib libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-grids-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and '
     'complete output. GAMS categories are not exhausted.',
     '',
     '## Independent references and tested scope',
     '',
     'These drivers cover numerical setup and checking utilities, rather than ten new solvers. The [reference '
     'tables](gams-grids-ten-references.json) save logarithmic-grid values, an exact rational tolerance truth '
     'table and an independent pi constant. The reference generator uses mpmath 1.3.0 at 80 digits, confirmed at '
     '120 digits to absolute difference below 1e-65, for powers and pi. No upstream implementation or '
     'author-test body was copied; pinned public APIs, implementations and linked author examples were reviewed.',
     '',
     '- **Greatest common divisor (B):** all 6,561 signed INT64 pairs -40..40, with exhaustive common-divisor '
     'enumeration rather than Euclid, plus four large exact cases. The zero-zero convention is checked. The '
     'minimum representable integer and overflow are excluded.\n'
     '- **Linear grids (D1a11):** 2,916 REAL64 and 2,916 COMPLEX128 grids, with independent convex endpoint '
     'weights. Lengths -2..33 cover empty and singleton behavior; a singleton returns the end. Default length '
     '100 is also checked.\n'
     '- **Logarithmic grids (D1a11):** 60 grids with 372 high-precision references for positive bases 2, 4, 10 '
     'and 0.5, ascending/descending/constant exponents and lengths 1, 2, 3, 8 and 17. Empty/negative lengths and '
     'default base/length are checked separately. Complex and negative bases are excluded.\n'
     '- **Stepped ranges (D1a11):** 867 bounded REAL64 dyadic ranges checked by repeated addition, and 17 '
     'single-argument INT64 ranges. Endpoints are inclusive when reached; positive step magnitudes are directed '
     'toward descending endpoints as documented by this API. Explicit zero/negative steps are excluded.\n'
     '- **Cartesian grids (D1b1):** 42 rectangular sizes with both xy and ij layouts checked by coordinate '
     'lookup. Only the rank-two API is claimed.\n'
     '- **Clipping (A3a):** 1,935 value/bound combinations, scalar and elemental calls, plus five INT64 values '
     'at 10^12 scale. Bounds are ordered, including equal bounds. Nonfinite values and reversed bounds are '
     'excluded.\n'
     '- **Tolerance comparisons (R2):** 289 exact rational truth-table pairs with explicit relative tolerance '
     '1/8 and absolute tolerance 1/16; scalar/elemental symmetry, REAL64 and COMPLEX128 matrix all_close, and '
     'NaN policy. The complex policy is componentwise, not a complex-modulus tolerance. Default tolerances and '
     'infinities are excluded.\n'
     '- **Complex phase (C4a):** eight exact axis/diagonal directions at 25 powers-of-two scales, checked in '
     'radians, degrees and multiples of pi (600 references). Origin, signed-zero branch cuts and general '
     'off-diagonal angles are excluded.\n'
     '- **Angle units (R):** 145 degree/radian values from -1080 to 1080 degrees, checked independently in each '
     'direction; round trips are secondary. This is unit conversion, not huge-angle reduction or a trigonometric '
     'accuracy claim.\n'
     '- **Vector exchange (D1a5):** lengths 0..64 for REAL64, COMPLEX128 and INT64, checked after one and two '
     'swaps, plus disjoint strided slices and unchanged untouched elements. Aliasing and other overloads are '
     'excluded.',
     '',
     'All comparisons require finite real results where applicable. Real checks use scaled absolute tolerance '
     '3e-13; integer, truth-table and exchange checks are exact. These are bounded test sets, not blanket claims '
     'for all overloads, inputs or performance.',
     '',
     '## Classification and provenance',
     '',
     'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies B (number theory), A3a (standard '
     'precision arithmetic), C4a (trigonometric and inverse trigonometric functions), D1a5 (copy/exchange), '
     'D1a11 (other vector operations), D1b1 (matrix initialization), R2 (error checking) and broad R (service '
     'routines). Grid constructors do not claim interpolation or integration; the angle converter uses broad '
     'service classification. Loading any example does not submit a job.',
     '',
     'These are independent MIT consumers; upstream package license terms remain separate. No upstream numerical '
     'source was patched. The [coverage report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def complex_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-complex-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-complex-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked stdlib matrix and complex linear algebra drivers',
     '',
     'Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing stdlib libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-complex-ten-validation.json) saves normalized UTF-8/LF source hashes, package pins, timings '
     'and complete output. GAMS categories are not exhausted.',
     '',
     '## Independent references and scope',
     '',
     'The first five drivers check elementary matrix operations, predicates and vector norms. The next five '
     'exercise pivoted LU and complex Cholesky, Hermitian eigenpairs, thin SVD and least squares. The drivers '
     'are independent MIT consumers; pinned API declarations, implementations and linked author examples were '
     'reviewed. Upstream implementations and test bodies were not copied. No upstream numerical source was '
     'patched.',
     '',
     '- **Trace (D1b):** 90 rectangular shapes, including empty dimensions, for REAL64, COMPLEX128 and INT64. '
     'Closed-form diagonal sums follow from polynomial entry formulas; input preservation is checked. '
     'Rectangular trace means summing through min(m,n).\n'
     '- **Identity (D1b1):** 90 rectangular identities in three kinds and ten default square shapes, checked by '
     'entrywise Kronecker deltas, including empty shapes.\n'
     '- **Conjugate transpose (D1b3):** 90 real/complex rectangular shapes, including empty shapes. Independent '
     'coordinate formulas check transposition, conjugation and input preservation; involution is a secondary '
     'check.\n'
     '- **Structure predicates (R2):** 204 one-hot positions in sizes 1..8, zero matrices, positive real '
     'symmetric/skew pairs and genuinely complex Hermitian pairs. Seven APIs distinguish exact structural '
     'properties; both triangle orientations and 42 rectangular squareness checks are included. This is an '
     'exact-zero test, not approximate symmetry.\n'
     '- **Vector norms (D1a3):** the exact 3-4-12 Pythagorean triple plus zero gives L1=19, L2=13, Linf=12 and '
     'minimum magnitude 0. Seventeen dyadic scales, complex coordinate phases and rank-two dimension reductions '
     'use known column factors and independent square-root references. Only orders 1, 2, inf and -inf are '
     'claimed.\n'
     '- **Pivoted LU (D2a1):** 120 REAL64 calls for sizes 1..10, three scales, vector/multiple right-hand sides, '
     'preservation and overwrite modes. Row-reversed diagonally dominant matrices have known manufactured '
     'solutions; solution errors, residuals and pivot ranges are checked.\n'
     '- **Complex Cholesky (D2d1b):** 72 positive-definite matrices formed from explicit positive-diagonal lower '
     'factors, tested with 144 lower/upper calls. The unique factors, reconstruction, zero unused triangles and '
     'input preservation are checked.\n'
     '- **Complex Hermitian eigenpairs (D4a3):** 320 solves for sizes 2..9, four independently checked unitary '
     'patterns, five scales and both storage triangles. Prescribed distinct eigenvalues, eigenpair residuals, '
     'orthonormality, reconstruction and input preservation are checked. Eigenvector phases are unrestricted.\n'
     '- **Complex thin SVD (D6):** 150 cases covering 25 tall/square/wide shapes, full-rank and '
     'one-zero-singular-value spectra, and three scales. Known singular values, reconstruction and both '
     'singular-vector Gram matrices are checked, without fixing phases or null-space bases.\n'
     '- **Complex least squares (D9a1):** 45 full-column-rank overdetermined systems with known coefficients and '
     'a nonzero residual in an independently checked orthogonal complement. Coefficients, rank, residual, A^H*r '
     'stationarity and input preservation are checked. Rank-deficient and underdetermined minimum-norm problems '
     'remain outside this driver.',
     '',
     '## Manufacturing the complex problems',
     '',
     'Each unitary matrix is constructed locally as Q=I-2*v*v^H/(v^H*v), with integer real/imaginary entries of '
     'v and nonzero denominator. Q^H*Q is explicitly checked before Q is used. Eigenproblems use '
     'A=Q*diag(lambda)*Q^H with prescribed distinct integer eigenvalues at dyadic scales. SVD uses A=Q*Sigma*P^H '
     'with prescribed singular values. Least squares uses columns Q(:,j)*(j+1), a known coefficient vector and a '
     'nonzero multiple of Q(:,n+1) as residual. Cholesky uses a directly specified triangular factor with '
     'positive real diagonal. These constructions supply mathematical references independently of the package '
     'routines under test.',
     '',
     'Real and imaginary components must be finite and agree to scaled absolute tolerance '
     '2e-10*max(1,abs(reference component)); integer/predicate and input-preservation checks are exact. These '
     'are bounded, moderately conditioned examples, not a precision benchmark. Extreme scales, ill-conditioned '
     'systems, repeated eigenvalues, singular/error handling and other overloads need separate drivers. Full '
     'storage is populated even when selecting an upper/lower triangle; poisoned-unused-triangle behavior is not '
     'tested.',
     '',
     '## GAMS classifications',
     '',
     'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies elementary matrix operations (D1b), '
     'initialization (D1b1), transpose (D1b3), vector norms (D1a3), error checking (R2), general real systems '
     '(D2a1), positive-definite complex Hermitian systems/factorization (D2d1b), ordinary complex Hermitian '
     'eigenproblems (D4a3), SVD (D6) and linear least squares (D9a1). Predicates do not claim to solve the '
     'matrix problems they recognize. Loading a driver does not submit a job. The [coverage '
     'report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def complex_operators_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-complex-operators-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-complex-operators-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked complex matrix operator and fitting drivers',
     '',
     'Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing stdlib libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-complex-operators-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings '
     'and complete output. GAMS categories are not exhausted.',
     '',
     '## Independent references and scope',
     '',
     'All ten drivers exercise COMPLEX128 APIs. Independent mathematical constructions define expected answers, '
     'with residuals and structural identities as additional checks. The pinned public API declarations, '
     'implementations and linked author examples were reviewed. The examples are independent MIT consumers; '
     'upstream implementation and author-test bodies were not copied. No upstream numerical source was patched.',
     '',
     '- **Determinants (D3c1):** 72 matrices of sizes 1..8, three diagonal spectra and three dyadic scales. '
     'Unitary similarity preserves the known product of diagonal entries; a cyclic row permutation adds an '
     'independently known sign. This checks nonzero complex determinants and exact input preservation.\n'
     '- **Inverses (D2c1):** 72 matrices with independent reciprocal-diagonal inverses under checked unitary '
     'similarity. Both left and right identity residuals and input preservation are checked.\n'
     '- **Pseudoinverses (D9c):** 150 tall/square/wide cases from 25 shapes, full-rank and '
     'one-zero-singular-value patterns, and three scales. Reciprocal nonzero singular values supply the expected '
     'pseudoinverse. All four Moore-Penrose identities and input preservation are checked with explicit '
     'rtol=1e-12.\n'
     '- **QR (D5):** 150 full/reduced factorizations across 25 tall/square/wide shapes and three '
     'upper-trapezoidal templates. Reconstruction, orthonormal columns, upper-trapezoidal zeros and prescribed '
     'diagonal magnitudes are checked without imposing factor phases.\n'
     '- **Schur (D4a4):** 63 nonnormal matrices from known complex upper-triangular templates under unitary '
     'similarity. Eigenvalues are matched one-to-one without assuming order. Unitary Schur vectors, '
     'triangularity, reconstruction and preservation are checked.\n'
     '- **Matrix exponential (D):** 180 evaluations for sizes 2..7, three superdiagonal templates, five scales '
     'and default/order-12 Pade. For A=lambda*I+N with nilpotent N, the independent answer is exp(lambda) times '
     'the finite sum of N^j/j! for j=0..n-1. The next nilpotent term is explicitly checked as zero.\n'
     '- **General linear systems (D2c1):** 144 vector/multiple-RHS calls with known complex coefficients in '
     'row-reversed diagonally dominant matrices of sizes 1..8. Residuals and preservation are checked.\n'
     '- **Positive-definite systems (D2d1b):** 288 vector/multiple-RHS calls on 72 known-factor matrices with '
     'lower/upper factorizations. Coefficients, residuals and preservation are checked. Both triangles are '
     'populated.\n'
     '- **Weighted least squares (D9a1):** 45 overdetermined full-column-rank fits with weights 1, 4 and 16. '
     'Known coefficients and a nonzero weighted-orthogonal residual provide independent references; weighted '
     'stationarity, rank and preservation are checked.\n'
     '- **Equality-constrained least squares (D9b1):** 72 fits with one complex equality and a full-column-rank '
     'cost. A closed-form complex diagonal-Hessian KKT correction supplies the minimizer. Coefficients, equality '
     'feasibility, stationarity and preservation of A, b, C and d are checked.',
     '',
     '## Mathematical constructions',
     '',
     'The drivers construct Q=I-2*v*v^H/(v^H*v) locally and check Q^H*Q before using Q. Determinant/inverse '
     'examples use Q*diag(z)*Q^H with nonzero prescribed z. Pseudoinverses use A=Q*Sigma*P^H and '
     'A+=P*Sigma+*Q^H. QR uses Q times a known upper trapezoid; Schur uses Q*T*Q^H with known nonnormal '
     'triangular T. No library factorization is used to manufacture these references.',
     '',
     'For weighted fitting, sqrt(w) is an exact power of two. The columns of sqrt(W)*A are checked-unitary '
     'columns scaled by j+1, and sqrt(W)*r is a nonzero multiple of the next orthogonal column. For constrained '
     'fitting, write y=Q*x and H=diag(5*D^2). The unconstrained minimizer is u=(D*b1+2*D*b2)/diag(H). For the '
     'nonconjugated equality c*y=d, lambda=(c*u-d)/(c*H^-1*c^H), y=u-H^-1*c^H*lambda and x=Q^H*y. The '
     'stationarity assertion uses A^H*(A*x-b)+C^H*lambda=0. These formulas retain the conjugations required for '
     'genuinely complex constraints.',
     '',
     'All real/imaginary components must be finite and agree to scaled absolute tolerance '
     '2e-10*max(1,abs(reference component)); input-preservation assertions are exact. The tests are bounded, '
     'moderately conditioned examples, not a precision or performance benchmark. Singular square solves, '
     'ill-conditioned inverses, near-cutoff pseudoinverse decisions, zero matrices, extreme weights, deficient '
     'fitting ranks, inequalities, repeated/clustered Schur spectra, pivoted QR and poisoned unused triangles '
     'remain outside these drivers. The exponential driver covers bounded nonnormal Jordan-type matrices, not '
     'general matrix-function stability.',
     '',
     '## GAMS classification and provenance',
     '',
     'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies general complex non-Hermitian '
     'determinants (D3c1), systems/inversion (D2c1), positive-definite complex Hermitian systems (D2d1b), '
     'ordinary complex non-Hermitian spectra (D4a4), QR (D5), unconstrained least squares (D9a1), constrained '
     'least squares (D9b1) and generalized inverses (D9c). The matrix exponential retains broad D rather than '
     'inventing a matrix-function leaf. Loading an example does not submit a job. The [coverage '
     'report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def statistics_rank_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-statistics-rank-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-statistics-rank-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked complex statistics and rank-sensitive linear algebra drivers',
     '',
     'Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing stdlib libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-statistics-rank-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings '
     'and complete output. GAMS categories are not exhausted.',
     '',
     '## Complex statistics: exact references and conventions',
     '',
     'Five drivers use 32 bounded three-variable datasets: observation counts n=4..11 and patterns k=1..4, each '
     'with all observations and a shared row mask excluding mod(i+k,3)=0. This gives 64 selections, each '
     'retaining at least two observations and strictly positive component variances. For variable j=1..3, real '
     'parts are (mod(i*i+3*j*i+2*k*j,17)-8)/8 and imaginary parts are (mod(2*i*i+j*i+k*(j+1),19)-9)/8. These '
     'inputs are exactly representable dyadics. The [reference table](gams-statistics-rank-ten-references.json) '
     'records selected indices and exact rational real/imaginary components.',
     '',
     'Python Fraction arithmetic supplies exact means, pairwise-difference covariance and analytic central '
     'powers from a binomial expansion of raw powers. The population column-observation covariance is '
     'sum(conjg(z_i(a)-z_i(b))*(z_j(a)-z_j(b)))/(2*N*N), summed over ordered observation pairs a,b. Sample '
     'correction multiplies by N/(N-1). Correlation normalizers use mpmath 1.3.0 at 80 digits and are confirmed '
     'at 120 digits to absolute difference below 1e-65. Fortran constants retain 18 significant digits; the '
     'rational references remain available in full.',
     '',
     '- **Complex means (L1a1a):** masked scalar, rank-two whole-array and dim=1/2 reductions, plus unmasked '
     'dim=1 calls, against 192 exact complex component means.\n'
     '- **Complex variances (L1a1b):** 192 population references and sample correction, using rank-one and '
     'dim=1/2 masked reductions. The result is real E(abs(Z-mean)**2), not the analytic second central power.\n'
     '- **Complex covariance (L1c1b):** 576 complex population entries, population/sample corrections, shared '
     'masks and unmasked paths (384 calls). Column observations dim=1 conjugate the first variable. Row '
     'observations obtained by transposing the data and using dim=2 give the conjugate matrix; both documented '
     'source conventions are checked explicitly.\n'
     '- **Complex correlation (L1c1b):** 576 independently normalized complex entries, 192 masked/unmasked '
     'dim=1/2 calls, unit diagonal and Hermitian structure. The same orientation convention applies.\n'
     '- **Complex central powers (L1a1c):** 768 exact references of orders 2..5 from E((Z-mean)**p). Packed '
     'selected-vector calls and unmasked dim=1/2 reductions are checked. These complex powers differ from '
     'magnitude moments and do not estimate variance when p=2.',
     '',
     '## Pivoted QR, minimum norm and reused factors',
     '',
     '- **REAL64 pivoted QR (D5):** 180 full/reduced factorizations from 30 tall/square/wide shapes and three '
     'scaled triangular templates. Pivot indices must be a permutation; reconstruction uses A(:,pivots). '
     'Orthonormal columns, triangular zeros and preservation are checked. At least one nonidentity permutation '
     'must occur, without prescribing a pivot order or factor signs.\n'
     '- **COMPLEX128 pivoted QR (D5):** the same 180-case shape/mode coverage with genuinely complex entries, '
     'unitary Gram checks and unrestricted phases.\n'
     '- **Complex rank-deficient least squares (D9a1):** 45 overdetermined rank-(n-1) cases with a nonzero '
     'orthogonal residual. Checked unitary factors and prescribed singular values define the minimum-norm '
     'solution; returned rank, solution, stationarity and null-space orthogonality are checked with cond=1e-12.\n'
     '- **Complex underdetermined minimum norm via PINV (D9a1):** 45 full-row-rank consistent systems. A known '
     'solution in the row space supplies the independent oracle; PINV(A)*b must match it and remain orthogonal '
     'to every explicit null-space vector. rtol=1e-12. This does not verify the failing LSTSQ consumer described '
     'below.\n'
     '- **Complex factored positive-definite solves (D2d1b):** 288 vector/multiple-RHS lower/upper solves on 72 '
     'explicitly manufactured factors, with known solutions, residuals and exact factor/RHS preservation. The '
     'solve calls do not factorize the matrix.',
     '',
     'The linear algebra examples construct unitary matrices locally with Householder formulas and check the '
     'unitary Gram matrices before using them. Rank-sensitive references use prescribed nonzero singular values '
     'j+1 and exact zero singular values, so these are separated-rank examples. No claim is made for near-cutoff '
     'rank decisions or ill-conditioned problems.',
     '',
     '## Retained failed LSTSQ probe',
     '',
     'The complex underdetermined LSTSQ consumer compiled but returned an invalid-problem-size API error on its '
     'first 2x4 matrix. The exact [original/diagnostic sources and full '
     'results](gams-candidates/stdlib-underdetermined/README.md) are retained with pins and hashes. The '
     'diagnostic adds only shape and error-state printing. The pinned routine passes ldb=m to GELSD where LAPACK '
     'requires at least max(1,m,n), a source-level explanation consistent with the failure. No numerical answer '
     'was produced; this was not a sandbox time or executable-size limit. Successful PINV solves do not promote '
     'the separate source-supported LSTSQ procedure.',
     '',
     '## Limits, provenance and maintenance',
     '',
     'Real and imaginary components must be finite and agree to scaled absolute tolerance '
     '2e-10*max(1,abs(reference component)); integer/permutation and preservation checks are exact. Empty or '
     'all-false masks, singleton variance, nonfinite observations, variable-specific missingness, '
     'constant-variable correlation, user-supplied moment centers, approximate rank thresholds, invalid factors '
     'and poisoned unused triangles are outside these drivers. These bounded tests are not a precision or '
     'performance benchmark.',
     '',
     'Pinned public APIs, implementations and linked author examples were reviewed. These are independent MIT '
     'consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source '
     'was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the existing '
     'L1a1a/L1a1b/L1a1c/L1c1b statistics classes, D5 QR, D9a1 least squares and D2d1b positive-definite complex '
     'systems. The PINV application is classified by the demonstrated minimum-norm problem; it does not claim a '
     'different fitting algorithm. Loading an example does not submit a job. The [coverage '
     'report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def grids_spectra_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-grids-spectra-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-grids-spectra-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked grid weights, complex spectra and masked statistics drivers',
     '',
     'Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. '
     'Existing stdlib libraries were reused; only mains and executables were compiled. The [verification '
     'report](gams-grids-spectra-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and '
     'complete output. GAMS categories are not exhausted.',
     '',
     '## Reusable sampled-grid quadrature weights (H2a1b2)',
     '',
     'The two weight drivers use lengths n=0..16, three dyadic spacing patterns and ascending/descending grids. '
     'The first node is -3/4 and each subsequent increment is (1+mod(i*k,4))/8. Empty and singleton grids '
     'produce empty/zero weights. Python Fraction arithmetic integrates each local Lagrange basis polynomial '
     'exactly, by polynomial multiplication and analytic antiderivatives, rather than reproducing upstream '
     'spacing formulas. The [reference table](gams-grids-spectra-ten-references.json) saves every node and exact '
     'rational weight. The Fortran consumers compare individual weights, polynomial integrals and exact grid '
     'preservation.',
     '',
     '- **Trapezoidal weights:** 102 grid cases, piecewise linear interpolation, exact constant and linear '
     'integrals for n>=2.\n'
     '- **Simpson weights:** 306 grid/mode cases, with even=-1,0,1 and omitted-default equivalence. Two nodes '
     'use a linear panel, three nodes a quadratic panel, and four nodes a cubic panel. Larger odd grids use '
     'quadratic panels. Larger even grids place a cubic panel at the left/right end or average the two schemes. '
     'Constant, linear and (when n>=3) quadratic integrals are checked; arbitrary cubic exactness on nonuniform '
     'composite quadratic panels is not claimed.',
     '',
     '## Complex matrix norms and eigenvectors',
     '',
     '- **Matrix norms (D1b2):** 108 rectangular matrices of sizes 1..6 by 1..6, including zeros. Entries '
     '(3+4i)*t/8 have the exact modulus 5*abs(t)/8, which supplies independent one-, infinity- and '
     'Frobenius-norm references. Character/integer orders and rank-three batched infinity reductions with '
     'dim=[1,2] are checked. Spectral norms and extreme-range scaling are outside this example.\n'
     '- **Ordinary complex eigenvectors (D4a4):** 63 dense nonnormal problems, sizes 2..8, three patterns and '
     'scales. A checked Householder factor Q and invertible shear S construct A=Q*S*D*inverse(S)*Q^H from '
     'prescribed distinct complex diagonal entries.\n'
     '- **Generalized complex eigenvectors (D4b4):** 63 nonsingular matrix pairs A=Q*D*inverse(S), '
     'B=Q*inverse(S), sharing the prescribed finite spectrum. The explicit inverse shear is checked before use.',
     '',
     'Both eigenvector consumers require one-to-one eigenvalue matching, the respective GEEV/GGEV vector '
     'normalization and the right '
     'residual A*v-lambda*B*v and left residual A^H*u-conjg(lambda)*B^H*u. Eigenvector order and phase are '
     'unrestricted. Inputs must be preserved exactly. Ordinary problems use B=I. Defective, nearly clustered, '
     'infinite or ill-conditioned spectra are excluded. The generalized COMPLEX128 path is independently checked '
     'and does not change the status of the previously retained failing generalized REAL64 eigenvector consumer.',
     '',
     'Ordinary GEEV vectors have Euclidean norm one. Generalized GGEV vectors instead satisfy '
     'max(abs(real(v))+abs(aimag(v)))=1. The initial generalized consumer incorrectly required Euclidean '
     'unit norms and failed; its [exact source and full result](gams-candidates/stdlib-complex-ggev/README.md) '
     'are retained. Correcting only those two assertions passed all prescribed eigenvalue, left/right '
     'residual and input-preservation checks. This was a consumer error, not an established numerical '
     'library failure or sandbox limit.',
     '',
     '## Discrete uniform probabilities (L5a1u)',
     '',
     'Two integer32 drivers enumerate the inclusive support loc..loc+scale: loc=-8..8, scale=1..16, and queries '
     'from loc-2 through loc+scale+2 (3672 queries per driver). PMF references count equal support points; CDF '
     'references count points <=x, divided by scale+1. PMF normalization and the CDF upper endpoint are checked. '
     'These integer overloads return default REAL32, so the explicit absolute tolerance is 2e-7. Zero/negative '
     'scale and integer overflow are excluded. No random-number sampling is involved.',
     '',
     '## Masked medians, moments and pairwise deletion',
     '',
     'REAL64 median/moment data use n=3..12, patterns k=1..3 and three variables j=1..3. Values are '
     '(mod(i*i+3*j*i+2*k*j,17)-8)/8; each variable excludes its own mod(i+j+k,4)=0 observations. The reference '
     'table saves selected indices, 90 exact rational medians and 1080 exact moments. Python rational order '
     'statistics supply medians; an exact binomial expansion of raw powers supplies moments of orders 2..5 about '
     'the default selected mean, zero, or supplied center j/8. Rank-one and rank-two dim=1/2 calls are checked. '
     'The median driver also replaces excluded values with a finite sentinel and requires unchanged results.',
     '',
     'The combined COMPLEX128 covariance/correlation driver uses n=8..12, patterns k=1..3, the same real '
     'components/masks and imaginary components (mod(2*i*i+j*i+k*(j+1),19)-9)/8. Each of the 135 variable pairs '
     'uses its own mask intersection and pair-specific means/variances. Python Fraction exact raw cross-moments '
     "provide population covariance; sample correction uses that pair's N/(N-1). Correlation normalization uses "
     'mpmath 1.3.0 at 80 digits, confirmed at 120 digits within 1e-65. Constants retain 18 significant digits. '
     'Column observations conjugate the first variable; transposed row observations produce the conjugate '
     'matrix. Population/sample covariance, correlation, transpose orientation and replacement of excluded '
     'finite values are checked across 15 datasets. Pairwise deletion is not claimed to preserve positive '
     'semidefiniteness.',
     '',
     '## Limits, provenance and maintenance',
     '',
     'Unless stated otherwise, real/imaginary components must be finite and agree within '
     '2e-10*max(1,abs(reference component)); preservation and integer checks are exact. Repeated grid nodes, '
     'nonfinite data, empty selected statistics, constant-variable correlations, singular generalized B and '
     'extreme-range inputs are outside these bounded demonstrations. They are not precision or performance '
     'benchmarks.',
     '',
     'Pinned public APIs, implementations and linked author examples were reviewed. These are independent MIT '
     'consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source '
     'was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, '
     'including complex general generalized eigenproblems D4b4. Loading an example does not submit a job. The '
     '[coverage report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def integrals_tensors_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-integrals-tensors-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-integrals-tensors-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked specialized integrals, tensor interpolation and nonlinear-system drivers',
     '',
     'Ten independent drivers across QUADPACK, finterp, bspline-fortran and MINPACK passed GNU Fortran 16.2.0 '
     'and FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains and '
     'executables were compiled. The [verification report](gams-integrals-tensors-ten-validation.json) saves '
     'normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.',
     '',
     '## QUADPACK: specialized integration APIs',
     '',
     'Five drivers use module-procedure callbacks, separate workspace arrays and the pinned public wrappers. '
     'Every call requires ier=0, positive integrand evaluations, finite result and finite nonnegative estimated '
     'error. Returned error estimates are sanity-checked; the actual result is judged independently against an '
     'analytic reference. These examples do not establish that estimated error bounds are rigorous.',
     '',
     '- **DQAGI half-lines (H2a3a1):** 32 exponential tails, decay rates 1/2,1,2,4 and finite bound magnitudes '
     '0,1/2,1,3/2, on both right and left half-lines. The callback is exp(-rate*abs(x)); the exact integral is '
     'exp(-rate*bound)/rate on the tested domains. Whole-line, oscillatory-tail and divergent cases are '
     'excluded.\n'
     '- **DQAGP interior breakpoints (H2a2a1):** 18 integrals of abs(x-c)**p, p=-1/2,1/2,3/2, on [0,1] and '
     '[-1,2], at quarter/midpoint/three-quarter breakpoints. Splitting the elementary antiderivative at c '
     'supplies the reference. A value of zero at the isolated singular point does not change the integral.\n'
     '- **DQAWC principal values (H2a2a1):** 36 integrals on [0,1], [-1,2] and [-2,3], using three interior pole '
     'fractions and smooth numerator (x-c)**power, power=0..3. The integrator supplies the 1/(x-c) weight. The '
     'constant numerator has principal value log((b-c)/(c-a)); the other powers have ordinary polynomial '
     'antiderivatives.\n'
     '- **DQAWO sine/cosine weights (H2a2a1):** 72 finite exponential integrals, three rates/lengths, '
     'frequencies 1/2,4,32,-4, and both trigonometric weights. Direct elementary antiderivatives supply '
     'references, including the sign change for negative-frequency sine. Infinite Fourier integration and reuse '
     'of Chebyshev moments are outside this driver.\n'
     '- **DQAWS endpoint weights (H2a2a1):** 144 integrals on [0,1], endpoint exponents alpha,beta=-1/2,0,1/2, '
     'smooth numerators x**p, p=0..3, and all four no-log/log(x)/log(1-x)/both-log modes. The callback supplies '
     'only x**p.',
     '',
     'For DQAWS let A=alpha+p+1, B=beta+1, S=A+B and W=Beta(A,B). The four exact expressions are W, '
     'W*(psi(A)-psi(S)), W*(psi(B)-psi(S)), and W*((psi(A)-psi(S))*(psi(B)-psi(S))-psi1(S)), where psi and psi1 '
     'are digamma/trigamma. The [reference table](gams-integrals-tensors-ten-references.json) saves every '
     'configuration and 18-digit value. mpmath 1.3.0 evaluations at 80 digits were confirmed at 120 digits '
     'within absolute 1e-65; no numerical quadrature generated these references. Tests additionally reconstruct '
     'the references from integer/half-integer Gamma and polygamma recurrences.',
     '',
     '### Retained DQAWO counter probe',
     '',
     'The initial consumer failed its last>0 assertion before checking the first numerical result. The pinned '
     'DQAWOE implementation initializes Last=0 and returns directly if the initial estimate is accepted. The '
     '[original exact source and complete hosted result](gams-candidates/quadpack-oscillatory-counter/README.md) '
     'are retained. The corrected driver accepts nonnegative last, still requires positive neval and ier=0, and '
     'reports how many calls used last=0. All 72 independent numerical comparisons remain in place. This counter '
     'assertion did not establish a numerical error or sandbox limit; no upstream source was patched.',
     '',
     '## finterp: three- and four-dimensional cells (E2a)',
     '',
     'Two drivers use four nonuniform nodes per axis: [-1,-1/4,1/2,2]*j/2 for coordinate j. One dataset is the '
     'multiaffine polynomial 1+sum(j*x_j)+product(x)+x1*x2-2*x2*x3, which tensor linear interpolation must '
     "reproduce. The second adds sum(j*x_j**2). Its reference uses each cell's exact quadratic secant "
     '(a+b)*x-a*b, rather than incorrectly requiring reproduction of the original quadratic. Every cell is '
     'queried at all endpoint/midpoint combinations: 1458 queries in 3D and 13122 in 4D across the two datasets. '
     'Thus grid nodes, shared boundaries and cell interiors are checked. API statuses, finite results and '
     'input-data preservation are required; extrapolation is excluded.',
     '',
     '## bspline-fortran: tensor mixed derivatives (E3a2)',
     '',
     'Two independent cubic tensor consumers fit five dyadic nonuniform nodes per axis, [-1,-1/2,0,3/4,2]*j/2, '
     'using spline order four in every dimension. Input values use the explicit polynomial '
     '1+sum(j*x_j**3)+product(x)+2*x1**2*x2-x2*x3**2. Reference derivatives use separately recorded '
     'coefficients/exponents and analytic falling factorials; those tables are saved with the endpoint-weight '
     'references. These are not finite-difference references.',
     '',
     'The 3D example checks all 27 partial-order combinations 0..2 per coordinate at 64 interior points (1728 '
     'evaluations). The 4D example checks all 81 combinations at 256 interior points (20736 evaluations). The '
     'coefficient representation and explicit nodal formula are independently cross-checked in tests. '
     'Initialization/evaluation statuses, finite scaled agreement within 1e-8 and exact nodal-data preservation '
     'are required. Records also retain gridded-interpolation E2a assignments, while the checked drivers '
     'primarily demonstrate derivative evaluation E3a2. Extrapolation, noisy fitting and higher derivative '
     'orders are outside scope.',
     '',
     '## MINPACK: user-supplied Jacobians (F2)',
     '',
     'HYBRJ1 solves 60 triangular nonlinear systems with dimensions n=2..6, three component-scaled '
     'alternating-sign start patterns and four displacement scales. Define u_i=x_i-i/4; f_1=u_1+u_1**3/8 and '
     'f_i=u_i+u_i**3/8+u_(i-1)**2/4 for i>1. The unique real root follows by forward induction because u+u**3/8 '
     'is strictly increasing with its only real zero at zero. The Jacobian is bidiagonal, with diagonal '
     '1+3*u_i**2/8 and subdiagonal u_(i-1)/2. Tests check that analytic Jacobian against independent exact '
     'polynomial differentiation. The consumer requires info=1, both callback paths, root/residual errors <=1e-8 '
     'and returned/recomputed residual agreement within 1e-12. Singular systems and global convergence are not '
     'claimed.',
     '',
     '## Limits, provenance and maintenance',
     '',
     'Real results must be finite and agree within 2e-9*max(1,abs(reference)), except spline mixed derivatives '
     'use 1e-8 and the nonlinear-system checks use their stated tolerances. QUADPACK requests absolute and '
     'relative tolerance 1e-10. These are bounded correctness demonstrations, not performance or '
     'extreme-condition benchmarks.',
     '',
     'Pinned public APIs, implementations and linked author tests were reviewed. These are independent MIT '
     'consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source '
     'was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, '
     'including automatic half-line quadrature H2a3a1 and interpolation derivative evaluation E3a2. Loading an '
     'example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def transforms_structures_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-transforms-structures-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-transforms-structures-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked transforms, structured systems, splines and beta-function drivers',
     '',
     'Ten independent drivers across FFTPACK, SpecialMatrices, PCHIP and specfunc-fullerton passed GNU Fortran '
     '16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains '
     'and executables were compiled. The [verification report](gams-transforms-structures-ten-validation.json) '
     'saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not '
     'exhausted.',
     '',
     '## FFTPACK: real and trigonometric transforms',
     '',
     '- **DCT-I (J1a3):** 92 cases, lengths n=2..24 and four deterministic signals: constant, an impulse, an '
     'alternating signed ramp, and a dyadic modular sequence. The independent direct sum is '
     'x(0)+(-1)**k*x(n-1)+2*sum(x(j)*cos(pi*j*k/(n-1))), with j=1..n-2 and k=0..n-1. The inverse is normalized '
     'by 2*(n-1).\n'
     '- **DST-I (J1a3):** 96 cases, lengths n=1..24 and the same signal families. Direct sums use '
     '2*sum(x(j)*sin(pi*j*k/(n+1))), j,k=1..n. Two in-place transforms divide by 2*(n+1) for the inverse. The '
     'initialization workspace is reused.\n'
     '- **Packed real FFT (J1a1):** 156 cases, source lengths m=4..16, four signals, and requested lengths '
     'm-2,m,m+3, checking truncation and zero-padding. Direct Fourier sums check DC, interleaved '
     'real/negative-sine components, and the separate even-length Nyquist component. The unnormalized inverse '
     'divides by n. The API returns n real packed entries, not a complex half-spectrum.',
     '',
     'All transform results must be finite. Wrapper inputs are preserved exactly and output sizes are checked '
     'where requested lengths change them. The DST intentionally transforms a copy in place. These bounded '
     'examples do not cover invalid sizes, nonfinite inputs or extreme dynamic range. The direct sums are '
     'separate from the package fast-transform algorithms.',
     '',
     '## SpecialMatrices: structured solves',
     '',
     '- **Strang systems (D2b2a):** 276 vector/multiple-RHS solves, n=2..24, three dyadic solution patterns and '
     'iterative refinement off/on. The SPD tridiagonal matrix has diagonal 2 and adjacent diagonals -1. Explicit '
     'three-point stencil operations construct RHS vectors and recompute residuals; no package matvec or dense '
     'conversion supplies the oracle.\n'
     '- **Circulant systems (D2a1):** 132 vector/multiple-RHS solves, n=2..23 and three nonsymmetric generators. '
     'For i>=2, c(i)=(-1)**i*(1+mod(i*i+pattern,7))/32, while c(1)=2+sum(abs(c(2:n))). Strict diagonal dominance '
     'ensures nonsingularity. A locally assembled dense matrix A(i,j)=c(modulo(i-j,n)+1) supplies RHS/residual '
     'references and known solutions. This is the first-column generator convention implemented by pinned '
     'dense()/FFT routines; the constructor comment displays the transpose convention. No numerical source was '
     'changed.\n'
     '- **Rectangular Poisson systems (I2b1a1a):** 288 vector/multiple-RHS solves, nx,ny=2..7, two rectangular '
     'domains and two manufactured solutions. Lx=domain/2 and Ly=(domain+1)/2. The operator is Delta with '
     'homogeneous Dirichlet boundaries, not -Delta.',
     '',
     'For the Poisson example, u=x*(Lx-x)*y*(Ly-y) has forcing -2*(x*(Lx-x)+y*(Ly-y)), and the five-point '
     'stencil reproduces this continuous forcing exactly. A second example uses '
     'sin(pi*i/(nx+1))*sin(2*pi*j/(ny+1)) with its discrete Laplacian eigenvalue, not its continuous eigenvalue. '
     'Known grid solutions, independent five-point residuals, a second scaled RHS and exact input preservation '
     'are checked. These examples verify the specified discrete systems; they do not establish convergence rates '
     'for general continuum solutions, variable coefficients, nonzero boundaries or nearly singular systems.',
     '',
     '## PCHIP: integrating Hermite pieces and choosing spline boundaries',
     '',
     '- **Hermite integrals (E3a3):** 117 arbitrary-bound/node-index integrals of a genuinely piecewise cubic '
     'with six nonuniform nodes and caller-supplied dyadic values/slopes. The 81 arbitrary intervals include '
     'zero length, reversal, partial panels and multiple panels; another 36 use DPCHID node indices. The driver '
     'independently integrates each clipped panel with two-point Gauss quadrature, exact for a cubic. It '
     'evaluates the Hermite basis locally, rather than calling a package evaluator for the oracle. The '
     '[reference table](gams-transforms-structures-ten-references.json) additionally saves exact Python Fraction '
     'antiderivatives for the 81 arbitrary intervals. DPCHIM slope selection and extrapolation are outside this '
     'driver.\n'
     '- **Cubic spline boundaries (E1a):** 225 value/first-derivative queries for three shifted cubics '
     '(x-pattern/4)**3-2*x+pattern/8, six nonuniform nodes and '
     'not-a-knot/supplied-first-derivative/supplied-second-derivative endpoint conditions. DPCHSP constructs the '
     'slopes and DPCHFD evaluates values/derivatives, checked against explicit polynomial formulas at 25 points. '
     'The supplied endpoint conditions match each cubic; zero natural conditions are not substituted.',
     '',
     'The Hermite nodes are [-1,-1/2,1/4,1,7/4,3], values [2,-1/4,1/2,3/4,-1,3/2], and slopes '
     '[1/2,-3/4,1,0,5/4,-1/2]. Arbitrary bounds divide the full interval into eight equal subintervals. '
     'Independent tests check the saved rational antiderivatives using exact Simpson integration of each clipped '
     "Hermite panel, a different rule from the driver's Gauss oracle. Successful statuses are required; no "
     'extrapolation warnings are accepted.',
     '',
     '## Fullerton: default REAL32 beta functions',
     '',
     'The pinned specfunc-fullerton APIs accept and return default REAL32. Consumers convert the exactly '
     'representable input parameters to that kind and widen results for comparison; widening does not supply '
     'REAL64 accuracy.',
     '',
     '- **Beta/log-beta pairs (C7b):** 64 positive pairs a,b from {1/2,1,3/2,5/2,4,8,16,32}, including the '
     'larger-argument logarithmic path. Independent mpmath 1.3.0 beta/log-beta values at 80 digits were '
     'confirmed at 120 digits within absolute 1e-65. The saved table retains 18 significant digits. Beta must be '
     'positive/finite with relative error <=5e-5; log-beta uses 5e-5*max(1,abs(reference)). Independent tests '
     'additionally use integer/half-integer Gamma recurrences.\n'
     '- **Integer-shape regularized beta CDF (L5a1b):** 252 queries with a,b=1..6 and x=0,1/8,1/4,1/2,3/4,7/8,1. '
     'Exact rational references use sum(binomial(n,j)*x**j*(1-x)**(n-j)), j=a..n, n=a+b-1. Results must be '
     'finite, within [0,1], sampled monotone in x and agree within absolute 3e-6. Noninteger shapes, extreme '
     'tails, nonpositive parameters, underflow and REAL64 accuracy claims are excluded.',
     '',
     '## Retained unsuccessful probes',
     '',
     'The [2D/3D quadrature-fortran sources and full '
     'results](gams-candidates/quadrature-fortran-nested/README.md) are retained with pins and normalized source '
     'hashes. Both compiled and reused cached libraries, then segfaulted with process exit 139 before numerical '
     'output. Their procedure records remain source-supported with no checked drivers and are excluded from '
     'menus. The implementation assigns pointers to internal wrapper procedures; compatibility with that '
     'mechanism is one possible cause to investigate, not an established diagnosis. These were execution '
     'failures, not observed numerical mismatches or reported time/size limits. The separate working 1D consumer '
     'is unchanged.',
     '',
     'The initial beta-CDF consumer had a [generated literal '
     'error](gams-candidates/fullerton-beta-cdf-literals/README.md): zero/one constants appeared as integer '
     '0_wp/1_wp in a REAL64 constructor. That consumer compilation failure is preserved with exact source and '
     'response. Changing only those literals to 0._wp/1._wp passed all 252 numerical comparisons and '
     'bounds/monotonicity checks. This was a consumer error, not a package numerical failure or sandbox limit.',
     '',
     '## Limits, provenance and maintenance',
     '',
     'Except for the stated REAL32 beta-function tolerances, results must be finite and agree within '
     '2e-9*max(1,abs(reference)); integer/status and preservation checks are exact. These are bounded '
     'correctness demonstrations, not precision or performance benchmarks.',
     '',
     'Pinned public APIs, implementations and linked author tests were reviewed. These are independent MIT '
     'consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source '
     'was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, '
     'including real/trigonometric transforms, SPD tridiagonal systems, rectangular Poisson problems and '
     'fitted-function quadrature. Loading an example does not submit a job. The [coverage '
     'report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def fullerton_functions_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fullerton-functions-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-fullerton-functions-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked Fullerton special-function drivers',
     '',
     'Ten independent specfunc-fullerton drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted '
     'hosted sandbox. The existing package library was reused; only each main and executable were compiled. The '
     '[verification report](gams-fullerton-functions-ten-validation.json) saves normalized UTF-8/LF source '
     'hashes, the exact package pin, timings and complete output. GAMS categories are not exhausted.',
     '',
     '## Precision and independent references',
     '',
     'The pinned APIs accept and return default REAL32. The drivers use exact dyadic input arguments, convert '
     'them to that kind for each call, and widen the returned values solely for checking. This does not supply '
     'REAL64 accuracy. References were generated independently with mpmath 1.3.0 at 80 decimal digits and '
     'confirmed at 120 digits with absolute differences below 1e-60. The [reference '
     'table](gams-fullerton-functions-ten-references.json) records every API, argument, integer order where '
     'applicable, and 18-significant-digit expected value.',
     '',
     'Every returned value must be finite and satisfy abs(actual-reference)/max(abs(reference),1e-30)<=5e-5. The '
     'small floor makes the exact zero cases effectively exact checks without relaxing relative accuracy for '
     'tiny nonzero results. Each driver reports its actual maximum relative error under this convention. These '
     'bounded checks are not a precision or performance benchmark, and do not establish accuracy near excluded '
     'function zeros, singularities, overflow or underflow.',
     '',
     '## Checked APIs and problem classes',
     '',
     '| Driver | GAMS | Checked cases |\n'
     '| --- | --- | --- |\n'
     '| Airy values and derivatives | C10d | 56 Ai, Bi, Ai-prime and Bi-prime comparisons at 14 dyadics in '
     '[-8,8] |\n'
     '| Modified Bessel I0/I1 | C10b1 | 36 comparisons at 18 signed dyadics in [-16,16], including zero |\n'
     '| Modified Bessel K0/K1 | C10b1 | 18 comparisons at nine positive dyadics from 1/256 to 16 |\n'
     '| Exponential/logarithmic integrals | C5 | 15 real Ei and 10 real li comparisons, avoiding their singular '
     'arguments |\n'
     '| Positive exponential integrals | C5 | Nine E1 values and 20 En values, with n=1..5 |\n'
     '| Sine/cosine integrals | C6 | 18 positive-argument Si/Ci comparisons |\n'
     '| Hyperbolic integrals | C4d | 20 positive-argument Shi/Chi comparisons, including x=3/8 |\n'
     '| Dawson values and derivatives | C8c | 28 signed-argument value/first-derivative comparisons in [-8,8] |\n'
     '| Real dilogarithm | C5 | 12 Li2 comparisons on [-8,1], including zero and one |\n'
     '| Near-zero exponential/logarithm | C4b | 38 log1p/exprel comparisons, including tiny arguments and zero '
     'limits |',
     '',
     '## Definitions and scope',
     '',
     '**Airy functions:** both function values and first derivatives are compared directly with high-precision '
     'Airy references. Samples include oscillatory negative arguments and decaying/growing positive arguments, '
     'along with zero. Complex/scaled variants and arguments near function zeros are excluded. Independent tests '
     'check the ODE power series on a bounded subset, exact zero-argument gamma formulas and the Wronskian '
     'identity using the saved values.',
     '',
     '**Modified Bessel functions:** the I0/I1 driver includes both signs, testing the even/odd conventions, '
     'while K0/K1 uses strictly positive arguments. Relative comparisons retain sensitivity for the small '
     'exponentially decaying K values. Only orders zero and one are verified. The separate bessel_in/bessel_kn '
     'higher-order wrappers, fractional-order routines, scaled functions and extreme-range behavior are not '
     'promoted by these results. Independent tests reconstruct I0/I1 with their power series and check K0/K1 '
     'using their defining positive quadrature integral.',
     '',
     '**Ei, li and En:** Ei uses the real principal-value branch on nonzero real arguments. li(x) is the '
     'unoffset logarithmic integral Ei(log(x)), not the offset integral starting at 2; x=1 is excluded. E1 and '
     'En use integral_1^infinity exp(-x*t)/t**n dt for positive x. E1 is checked on nine dyadics 1/256..16; En '
     'is checked for n=1..5 at x=1/8,1/2,1,2. No conclusion is drawn about the higher-order forward recurrence '
     'at larger x. Independent tests use exponential-integral power series on a bounded subset and the En '
     'integration-by-parts recurrence.',
     '',
     '**Si/Ci and Shi/Chi:** Si(x)=integral_0^x sin(t)/t dt, while Ci(x)=EulerGamma+log(x)+integral_0^x '
     '(cos(t)-1)/t dt on the positive real domain. The hyperbolic counterparts replace sin/cos by sinh/cosh. Chi '
     'and Ci are tested only for positive arguments, with no complex-continuation claim. Independent tests use '
     'the corresponding power series on a bounded subset.',
     '',
     '**Dawson:** F(x)=sqrt(pi)*exp(-x*x)*erfi(x)/2. The high-precision derivative reference is obtained by '
     'differentiating this definition with mpmath, rather than by reusing the package derivative. Independent '
     'tests also check F-prime+2*x*F=1 and the ODE power series for bounded arguments. Extreme asymptotics and '
     'derivative zeros are excluded.',
     '',
     '**Spence/dilogarithm:** the public integral_spence routine uses integral_0^x -log(abs(1-t))/t dt. On the '
     'demonstrated domain x<=1 it equals real Li2(x), the mpmath polylog(2,x) reference. This convention differs '
     "from APIs that call Li2(1-x) Spence's function. Independent tests use the convergent dilogarithm series "
     'and negative-argument inversion identities. The x>1 real continuation and complex values are excluded.',
     '',
     '**Near zero:** lnrel(x)=log(1+x) and exprel(x)=(exp(x)-1)/x, with exprel(0)=1. Independent log1p/expm1 '
     'references avoid subtractive cancellation. The 19 arguments include signed powers down to 2**(-24), zero, '
     'and dyadic samples on both sides of the 3/8 and 1/2 approximation boundaries. All lnrel inputs are greater '
     'than -1; overflow regions are excluded.',
     '',
     '## Provenance and maintenance',
     '',
     'Pinned public APIs, implementations and available linked author tests were reviewed. Dawson and '
     'dilogarithm have no pinned author driver in the reviewed test tree; their public implementations were '
     'reviewed directly and the examples are original consumers. All ten are independent MIT consumers; upstream '
     'implementation and author-test bodies were not copied. No upstream numerical source was patched.',
     '',
     'The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies C10d Airy/Scorer, C10b1 real '
     'integer-order modified Bessel, C5 exponential/logarithmic integrals, C6 sine/cosine integrals, C4d '
     'elementary-function integrals, C8c Dawson and C4b exponential/logarithmic classifications. No new '
     'numerical failure was observed in these bounded probes. Loading an example does not submit a job. The '
     '[coverage report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def roots_structured_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-roots-structured-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-roots-structured-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked root-solver and structured-matrix drivers',
     '',
     'Ten independent REAL64 consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox, reusing '
     'existing libraries and compiling only main.f90 and playground-main. The [verification '
     'report](gams-roots-structured-ten-validation.json) retains normalized UTF-8/LF source hashes, pins, '
     'timings and full output. GAMS coverage remains unfinished.',
     '',
     '## Root solvers (F1b)',
     '',
     'Separate drivers exercise bisection, Ridders, Brent-Q, ITP and Chandrupatla through their direct solver '
     'objects. Each solves 85 manufactured problems: 17 exact dyadic roots r in [-2,2] in each of five families '
     'with z=x-r: z*(1+z*z), exp(z)-1, sin(z), log(1+z), and z/(2+z*z). Brackets are [r-0.75,r+1.25], safely '
     'inside the logarithm domain. The function shapes and slopes differ; all cases have simple smooth roots. '
     'These bounded examples do not establish performance or difficult-root robustness.',
     '',
     'Each run checks status, bracket containment, the exact root, reported residual and independently '
     'reevaluated residual. Bisection fallback is explicitly disabled and must remain unused. Requested solver '
     'tolerances are 1e-13 for function values and 1e-12 for absolute/relative root errors; acceptance uses '
     '2e-9*max(1,abs(reference)). Module callbacks avoid nested callback wrappers.',
     '',
     '## Structured matrices',
     '',
     '**Strang eigensystems (D4a1):** 17 dimensions n=2..18, manually assembled tridiagonal matrices with '
     'diagonal 2 and off-diagonals -1. Eigenvalues are compared with 4*sin(pi*k/(2*(n+1)))**2. Every returned '
     'vector is checked against the manual matrix and all columns must be orthonormal. The eigenvalues-only API '
     'is checked separately.',
     '',
     '**Rectangular Poisson eigensystems (D4a1):** twelve grids nx=2..5, ny=2..4 on side lengths 2 and 3. A '
     'manual finite-difference stencil represents the negative-spectrum Laplacian with homogeneous Dirichlet '
     'boundaries. Sorted tensor-sine eigenvalues, every vector residual and orthogonality are checked. '
     'Eigenvalues-only results are also compared. No other boundary conditions are verified.',
     '',
     '**Circulant eigenpairs (D4a2):** fifteen nonsymmetric real matrices n=3..17. The generating vector is the '
     'first column, A(i,j)=c(modulo(i-j,n)+1). Direct complex DFT sums supply independent eigenvalues; manually '
     'assembled matrices supply right-vector residuals and unitary orthogonality checks. Left eigenvectors are '
     'not verified. Caller-owned outputs are explicitly allocated as required by the pinned public interface.',
     '',
     '**Circulant singular values (D6):** magnitudes of directly summed DFT eigenvalues, sorted by a local '
     'insertion sort, independently check svdvals. This does not verify full SVD vectors or rank-deficient '
     'inputs.',
     '',
     '**Circulant inverses (D2a1):** both A*inverse and inverse*A must equal identity for fifteen manually '
     'assembled diagonally dominant matrices n=3..17. Singular or ill-conditioned matrices are excluded. All '
     'matrix checks require finite results and tolerance 2e-9*max(1,abs(reference)).',
     '',
     '## Retained unsuccessful probes and provenance',
     '',
     'The initial root_scalar convenience-wrapper probes built successfully but crashed with SIGSEGV before '
     'numerical output. Their exact sources, pins, hashes and full results are '
     '[retained](gams-candidates/roots-structured-api/README.md). The implementation creates a nested internal '
     'callback; a sandbox callback/trampoline issue is possible but not established. Successful direct-object '
     'drivers do not verify that convenience wrapper. The first circulant eig probe omitted required output '
     'allocation and stopped with an array-bound mismatch; this consumer error is preserved with the correction '
     'explained. The direct TOMS 748 probe found the exact first root (family 1, r=-2) but returned nonzero '
     'status 11021 and signalled IEEE_OVERFLOW_FLAG; a second diagnostic probe confirms this. Both are retained. '
     'The cause is undiagnosed; that path has no checked driver. Brent-Q passed the same 85 cases as a separate '
     'replacement. No assertion was relaxed and no upstream numerical source was patched.',
     '',
     'Pinned implementations and linked author tests were reviewed. These MIT consumers copy no upstream '
     'implementation or test bodies. Classifications follow the [Netlib GAMS '
     'taxonomy](https://netlib.org/misc/gams.html). Loading an example does not submit a job. See the [coverage '
     'report](gams-coverage.md) for remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def ordering_runge_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-ordering-runge-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-ordering-runge-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked ordering and Runge-Kutta drivers',
     '',
     'Ten independent consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. Existing '
     'ORDERPACK and rklib libraries were reused; only main.f90 and playground-main were compiled. The '
     '[verification report](gams-ordering-runge-ten-validation.json) records normalized UTF-8/LF source hashes, '
     'exact pins, timings and full output. GAMS coverage remains unfinished.',
     '',
     '## ORDERPACK: six distinct operations',
     '',
     'Each driver tests 325 finite REAL64 data sets: sizes 1..65, each with five deterministic patterns '
     '(unsorted duplicate-rich data, sorted repeated values, reverse repeated values, constant values, and '
     'distinct values). All are exact dyadics. The independent reference is a local insertion sort, a direct '
     'first-occurrence scan or direct counting; no second library routine supplies the oracle. Every applicable '
     'partial prefix is tested. Empty arrays, NaNs, infinities, integer and character '
     'overloads are excluded.',
     '',
     '| Operation | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Partial sort (psort) | N6a2b | Every requested prefix equals the reference prefix; the complete multiset '
     'is preserved |\n'
     '| Partial ranks (prank) | N6a1b | Every prefix contains valid, distinct indices selecting the reference '
     'values; tie stability is not assumed |\n'
     '| Stable unique (unique) | L2c | First-occurrence scan checks both the distinct count and retained order; '
     'undocumented tail entries are ignored |\n'
     '| Multiplicities (occurrences) | L1a1d | Every count agrees with direct equality counting in the original '
     'data |\n'
     '| Inverse unique ranks | N6a1b | Each original entry receives its ascending dense rank among distinct '
     'values; the public alias rank_decreasing does not mean descending sorting |\n'
     '| Median conventions | L1a1a | median averages the central pair; medianval and medianloc select the lower '
     'middle for even sizes |',
     '',
     'REAL64 median comparisons are exact here because all central values and their averages are dyadic and '
     'comfortably representable. These tests establish the demonstrated conventions and bounded data cases, not '
     'performance, asymptotic complexity or robustness to nonfinite inputs.',
     '',
     '## Four Runge-Kutta methods (I1a1a)',
     '',
     'The explicit midpoint (order 2), rk3 (order 3), Spiteri-Ruuth rkssp54 (order 4) and rk5 (order 5) drivers '
     'each integrate a five-state nonstiff system. Closed forms are exp(-t), cos(t), -sin(t), 1/(1+exp(-t)), and '
     't*t+1/4. These exercise exponential decay, a coupled oscillator, nonlinear logistic growth and explicitly '
     'time-dependent polynomial forcing. Module callbacks use the direct solver objects.',
     '',
     'Each method is checked at ten checkpoints on [0,2] for h=0.1, 0.05 and 0.025. Every state must be finite, '
     'the status must succeed, decay must stay positive and logistic growth must stay in (0,1). The maximum '
     'absolute state error must be <=2*h**p at every checkpoint. The time-dependent polynomial state has a '
     'separate 1e-11 absolute tolerance. RHS callback counts must be positive.',
     '',
     'A separate convergence assertion compares the maximum checkpoint error between successive step sizes: each '
     'ratio must lie in [0.7*2**p,1.4*2**p]. Actual errors, ratios and RHS counts are printed. These are '
     'accuracy checks for this smooth bounded system, not a speed comparison, an SSP-property or '
     'stability-region proof, nor verification of adaptive control, backward integration or stiff systems.',
     '',
     '## Retained unsuccessful probes',
     '',
     'The first median consumer treated medianloc as a function; correcting it to call medianloc(x,loc) '
     'resolved that consumer compile error without changing numerical assertions. The combined order-statistics '
     'probe found an actual orderloc mismatch for [-1.25,-2.75,1.5,0]: the third ordered value should be 0, '
     'but the routine returned index 3/value 1.5. Original and diagnostic probes, normalized hashes, pins '
     'and full outputs are [retained](gams-candidates/orderpack-statistics/README.md). Its procedure record '
     'has no checked driver; the other two order-statistic APIs were not reached for that failing case. '
     'No upstream source or assertion was changed to promote the failed routine. Inverse unique ranks '
     'are a separate verified replacement.',
     '',
     '## Provenance and scope',
     '',
     'Pinned public APIs and implementation files, ORDERPACK author tests and rklib author order tests were '
     'reviewed. Consumers are independently authored MIT examples; no upstream numerical or test body was copied '
     'or patched. GAMS classifications follow the [Netlib taxonomy](https://netlib.org/misc/gams.html): '
     'active/passive real internal sorting, data subsets, frequency, location and one-step ODE methods. Loading '
     'a driver does not submit a job. The [coverage report](gams-coverage.md) tracks remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def gamma_relative_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-gamma-relative-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-gamma-relative-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked gamma and relative-function drivers',
     '',
     'Ten independent specfunc-fullerton consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted '
     'sandbox. The cached library was reused and only main.f90 and playground-main were compiled. The '
     '[verification report](gams-gamma-relative-ten-validation.json) retains normalized UTF-8/LF source hashes, '
     'exact pins, timings and full output. GAMS coverage remains unfinished.',
     '',
     '## Precision and references',
     '',
     'All demonstrated public APIs accept and return default REAL32. Exact dyadic inputs are converted to that '
     'kind; widening outputs to REAL64 for comparison does not provide REAL64 function accuracy. Independent '
     'references were generated with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits, with '
     'absolute differences below 1e-60. The [reference table](gams-gamma-relative-ten-references.json) records '
     'every argument, integer order where relevant and 18-significant-digit expected value.',
     '',
     'All returned values must be finite and satisfy abs(actual-reference)/max(abs(reference),1e-30)<=5e-5. '
     'Exact zero references are therefore checked effectively exactly. Gamma signs are checked separately '
     'against exact +/-1. Each driver prints its actual maximum relative error. These bounded cases are not a '
     'precision or performance benchmark.',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Lower incomplete gamma | C7e | 49 unnormalized lower integrals; positive shapes 1/2..8, x=0..8 |\n'
     '| Upper gamma, positive x | C7e | 66 unnormalized tail integrals; positive and selected nonpositive '
     'shapes, strictly positive x |\n'
     '| Tricomi incomplete gamma | C7e | 49 scaled lower-gamma values, including exact x=0 limits |\n'
     '| Signed log gamma | C7a | 18 log-absolute values plus exact signs, including negative half-integers |\n'
     '| Generalized Pochhammer | C7a | 48 gamma ratios, including signed, fractional and integer shifts |\n'
     '| Relative Pochhammer | C7a | 35 cancellation-sensitive ratios and exact zero-shift digamma limits |\n'
     '| Factorials | C1 | 34 finite REAL32 factorials n=0..33 |\n'
     '| Signed cube roots | C2 | 55 dyadic inputs, signs and zero, exponents -90..90 |\n'
     '| Entire cosine integral | C6 | 11 nonnegative Cin values, zero, tiny inputs and x up to 16 |\n'
     '| Reciprocal gamma pole zeros | C7a | 13 exact pole zeros and 28 signed half-integer values |',
     '',
     '## Definitions and bounded scope',
     '',
     'The lower incomplete gamma is integral_0^x exp(-t)*t**(a-1) dt, not a regularized probability. Its '
     'positive-shape cases include x=0. The upper incomplete gamma is the corresponding tail '
     'integral_x^infinity. The positive-x driver tests x=1/8,1/2,1,2,4,8 for shapes '
     '1/2,1,3/2,2,3,4,8,-2,-1,-1/2,0. Its documented but broken x=0 path is excluded and retained separately '
     'below. Tricomi uses x**(-a)*lower_gamma(a,x)/Gamma(a), with limit 1/Gamma(a+1) at x=0; only positive '
     'shapes are verified.',
     '',
     'sign_log_gamma returns log(abs(Gamma(x))) and a separate sign, verified at eight negative half-integers '
     'and ten positive dyadics in [1/8,32]. Pochhammer uses Gamma(a+x)/Gamma(a) with positive a and a+x. poch1 '
     'uses (Gamma(a+x)/Gamma(a)-1)/x; independent expm1/loggamma references avoid cancellation for signed shifts '
     'as small as 2**(-16), and x=0 uses the digamma limit. Poles, near-pole perturbations, negative-base '
     'continuation and large-shift asymptotics are excluded.',
     '',
     'Factorials n=0..33 are compared with independent integer factorials rounded only when making reference '
     'constants. This does not claim n=33 is the largest representable factorial: 34! is also within REAL32 '
     'range but is not tested here. Signed real cube roots include zero and normal REAL32 inputs with '
     'significands 1,5/4,7/4 and exponents -90,-30,-9,-3,0,3,9,30,90. Subnormal and exceptional inputs are '
     'excluded.',
     '',
     'The misleading public name inverse_ci denotes Cin(x)=integral_0^x (1-cos(t))/t dt, not an inverse '
     'function. Only x>=0 is checked. Independent high-precision EulerGamma+log(x)-Ci(x) references handle tiny '
     'nonzero arguments; zero is supplied by the exact limit. Reciprocal gamma is checked as an entire function '
     'with exact zeros at 0,-1,...,-12 and signed half-integer values from -23/2 to 31/2.',
     '',
     '## Retained failures',
     '',
     'The broad upper-gamma probe returned NaN at a=1/2,x=0 instead of sqrt(pi). The source rejects x<=0 before '
     'an x==0 branch, making that branch unreachable. The [original '
     'probe](gams-candidates/fullerton-upper-gamma/) and [diagnostic '
     'probe](gams-candidates/fullerton-gamma-cinh/README.md) are retained with normalized hashes, pins and full '
     'hosted results. Its broad procedure record has no driver. The separate positive-x consumer does not verify '
     'or repair that endpoint.',
     '',
     'The inverse_chi/Cinh probe built but returned 2.7167096138000488 at x=-3 instead of 3.2845641411959674. '
     'Its exact source and full result are retained alongside the gamma diagnostic. This broad Cinh record has '
     'no checked driver; no assertion was relaxed and no library code was patched. The separate reciprocal-gamma '
     'consumer replaces this candidate. Other successful special functions do not establish Cinh correctness.',
     '',
     '## Provenance',
     '',
     'Pinned public APIs, implementations and linked author tests were reviewed. The cube-root example has no '
     'author test in the reviewed pinned test tree, so its implementation was reviewed directly. All ten '
     'consumers are independent MIT examples; upstream implementations and author test bodies were not copied. '
     'Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading a driver '
     'does not submit a job. See the [coverage report](gams-coverage.md) for remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def banded_products_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-banded-products-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-banded-products-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked banded-matrix and structured-product drivers',
     '',
     'Ten independent REAL64 SpecialMatrices consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted '
     'sandbox. The cached library was reused; only main.f90 and playground-main were compiled. The [verification '
     'report](gams-banded-products-ten-validation.json) saves normalized UTF-8/LF source hashes, the exact '
     'package pin, timings and full output. GAMS coverage remains unfinished.',
     '',
     '## Checked problems and independent references',
     '',
     '| Driver | GAMS | Cases and oracle |\n'
     '| --- | --- | --- |\n'
     '| Symmetric positive systems | D2b2a | 15 variable SPD tridiagonal systems; manufactured solutions, vector '
     'and three-column RHS, refinement off/on |\n'
     '| Symmetric indefinite systems | D2b1a | 15 alternating-sign symmetric tridiagonal systems; general '
     'factorization, same independent solution/residual checks |\n'
     '| Pivoted tridiagonal systems | D2a2a | 15 nonsymmetric systems requiring a first-column row pivot; vector '
     'and multiple RHS, refinement off/on |\n'
     '| Positive tridiagonal determinants | D3b2a | 15 SPD matrices; independent dense elimination with row '
     'pivoting |\n'
     '| Nonsymmetric tridiagonal determinants | D3a2a | 15 matrices with a small leading diagonal; independent '
     'pivoted dense determinants |\n'
     '| Variable tridiagonal eigenpairs | D4a5 | 15 symmetric indefinite matrices; residuals, orthogonality, '
     'spectrum invariants and eigenvalues-only agreement |\n'
     '| Rectangular Toeplitz products | D1b6 | 48 shapes; manual elementwise matrices, vector/matrix products '
     'and transpose products |\n'
     '| Rectangular Hankel products | D1b6 | 48 shapes; independent A(i,j)=v(i+j-1), vector/matrix products and '
     'transpose products |\n'
     '| Bidiagonal systems | D2a3 | 30 lower/upper systems; vector and three-column manufactured solutions |\n'
     '| Bidiagonal spectra | D4a2 | 30 lower/upper matrices; known distinct diagonal eigenvalues, trace and '
     'determinant |',
     '',
     'All scalar comparisons require finite results and abs(actual-reference)<=2e-9*max(1,abs(reference)); '
     'matrix comparisons also check shape. Square problems cover n=2..16. Matrices, RHS and expected solutions '
     'are assembled independently without dense() or another package solver supplying the oracle. Singular, '
     'extremely scaled and ill-conditioned cases are excluded.',
     '',
     '## Linear systems and determinants',
     '',
     'Positive symmetric matrices have variable positive diagonal 3+mod(i,4)/8 and small off-diagonals; strict '
     'diagonal dominance establishes positive definiteness. The indefinite family alternates the diagonal signs '
     'and uses the general symmetric tridiagonal path. The nonsymmetric family sets the first diagonal to 1/8 '
     'and first subdiagonal to 5/4, requiring a first-column pivot. Each of these three solve drivers checks '
     'three manufactured RHS together and a separate vector RHS, both with and without refinement. Dense '
     'residuals independently verify the matrix convention and returned solution.',
     '',
     'Both determinant drivers compare the structured continuant routines against an independently authored '
     'dense Gaussian-elimination routine with row pivoting, not a second implementation of the same recurrence. '
     'The bidiagonal solver checks lower and upper orientations, alternating-sign nonzero diagonals and variable '
     'off-diagonals. These bounded accuracy tests do not characterize conditioning or refinement improvement.',
     '',
     '## Spectra',
     '',
     'The variable symmetric eigensystem driver uses alternating-sign diagonal matrices and checks every dense '
     'eigenvector residual, all column inner products, ascending eigenvalue order, the trace, sum of squared '
     'eigenvalues against the dense Frobenius norm squared, and the eigenvalue product against an independent '
     'dense determinant. The eigenvalues-only API must also agree. Residuals and orthogonality establish the '
     'complete returned eigensystem without invoking a second eigensolver as a reference.',
     '',
     'A triangular bidiagonal matrix has the diagonal entries as its spectrum. Both orientations are checked '
     'against these known distinct real values using nearest matching, with additional trace and determinant '
     'checks. The pinned implementation delegates this API to a dense stdlib eigensolver; this example makes no '
     'claim that it exploits a specialized bidiagonal eigenvalue algorithm. Eigenvectors, repeated eigenvalues '
     'and strongly nonnormal conditioning are excluded.',
     '',
     '## Rectangular products',
     '',
     'Toeplitz and Hankel cases cover m=2..7 and n=2..9, including tall, wide and square shapes with odd and '
     'even dimensions. Each checks dense conversion, a three-column product, a vector product, dense transpose '
     'conversion and transpose-vector multiplication. Toeplitz entries are assembled from first-column/first-row '
     'vectors, with the first column defining the shared (1,1) entry. Hankel uses A(i,j)=v(i+j-1). The reference '
     'products use ordinary dense intrinsic operations on the manual matrices. No FFT performance or large-size '
     'claim is made.',
     '',
     '## Provenance and maintenance',
     '',
     'Pinned constructors, implementations and linked author tests were reviewed. These original MIT consumers '
     'copy no upstream numerical or author-test bodies, and no upstream source was patched. Classifications '
     'follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html), including D3 for determinants and D2 '
     'for linear systems. Loading an example does not submit a job. The [coverage report](gams-coverage.md) '
     'tracks remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def forlab_statistics_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-forlab-statistics-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-forlab-statistics-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked Forlab statistics and matrix drivers',
     '',
     'Ten independent Forlab consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The '
     'cached library was reused; only main.f90 and playground-main were compiled. The [verification '
     'report](gams-forlab-statistics-ten-validation.json) records normalized UTF-8/LF source hashes, exact pins, '
     'timings and full output. GAMS coverage remains unfinished.',
     '',
     '## Precision and acceptance',
     '',
     'The pinned Forlab module exports RPRE=4. These drivers import wp=>RPRE and explicitly verify 32-bit real '
     'storage; this is native REAL32, not REAL64. Independent references use REAL64 arithmetic on the actual '
     'input data or analytic formulas. Ordinary statistics and matrix checks require finite results and '
     'abs(actual-reference)<=3e-5*max(1,abs(reference)). Normal PDF and chi-square PDF/CDF checks instead '
     'require relative error <=3e-5 with a 1e-20 reference floor, retaining sensitivity to small positive '
     'probabilities. These bounded checks are not a high-precision or performance benchmark.',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Location and dispersion | L1a1b | 96 data sets: mean, sample/population variance and standard deviation '
     '|\n'
     '| Covariance matrices | L1c1b | 96 three-column data sets plus separate two-vector calls, both '
     'normalization choices |\n'
     '| Population shape moments | L1a1c | 90 data sets: centered third/fourth moments, population skewness and '
     'non-excess kurtosis |\n'
     '| Normal density | L5a1n | 189 values, scalar/vector APIs, three locations and three scales |\n'
     '| Even-degree chi-square | L5a1c | 24 positive inputs: PDF/CDF against finite exponential/factorial '
     'formulas |\n'
     '| Cholesky factors | D2b1b | Seven SPD matrices with known lower-triangular factors and reconstruction |\n'
     '| Symmetric eigenpairs | D4a1 | Seven known Householder-rotated spectra, dense residuals and orthogonality '
     '|\n'
     '| Tall SVD | D6 | Five known tall factorizations, status, singular values, orthogonality and '
     'reconstruction |\n'
     '| Dense inverses | D2a1 | Seven nonsymmetric diagonally dominant matrices, left/right inverse identities '
     '|\n'
     '| Polynomial differences | H1 | 48 cubic grids: first, second and third forward-difference quotients |',
     '',
     '## Statistics and distributions',
     '',
     'Data families use dyadic values and three affine transformations, with n=2..33 for '
     'location/dispersion/covariance and n=4..33 for shape moments. Covariance references explicitly center each '
     'actual column and form cross-products in REAL64. Sample normalization divides by n-1; population '
     'normalization divides by n. Only flag=1 population skewness and non-excess kurtosis are verified; '
     'bias-adjusted flag=0, constant arrays, missing values and singleton normalization are excluded.',
     '',
     'Normal PDF cases use mu=-1,0,1; sigma=1/2,1,2; and 21 standardized offsets -5..5. References use '
     'exp(-z*z/2)/(sigma*sqrt(2*pi)). Chi-square cases use degrees of freedom 2,4,6,8 and x=1/8,1/2,1,2,4,8. '
     'Setting k=degrees/2 and t=x/2 gives PDF=t**(k-1)*exp(-t)/(2*(k-1)!) and CDF=1-exp(-t)*sum_{j=0}^{k-1} '
     't**j/j!. This oracle does not call an incomplete-gamma library. Boundary x=0, odd degrees, invalid sigma '
     'and extreme tails are excluded.',
     '',
     '## Matrices and differences',
     '',
     'Cholesky inputs are formed from independently constructed dyadic lower-triangular factors for n=2..8; both '
     'the returned factor and product are checked. Symmetric eigenproblems use a local analytic Householder '
     'matrix Q and alternating-sign distinct diagonal eigenvalues: A=Q*diag(d)*transpose(Q). Every residual and '
     'column inner product is checked, as is the known eigenvalue set without prescribing vector signs or '
     'ordering.',
     '',
     'Tall SVD inputs have m=n+2,n=2..6 and known orthonormal columns scaled by distinct positive singular '
     'values. Both thin-factor orthogonality conditions, status, known singular values and reconstruction are '
     'checked. Wide/rank-deficient cases and optional-mode state behavior are excluded. Inverse cases cover '
     'n=2..8, exercising the direct 2x2/3x3 and larger LU paths, with both inverse identities checked. Singular '
     'and ill-conditioned matrices are excluded.',
     '',
     'Forward-difference cases sample p(t)=t**3+2*t*t-3*t+1 at lengths 5..20 and h=1/8,1/4,1/2. First quotient '
     'references are 3*t*t+4*t-3+(3*t+2)*h+h*h; second quotients are 6*(t+h)+4; third quotients are 6. These '
     'exact polynomial identities check all returned entries and lengths. This does not verify a general '
     'derivative error estimator or numerical quadrature.',
     '',
     '## Retained unsuccessful probes',
     '',
     'The [saved probes](gams-candidates/forlab-statistics/README.md) include exact sources, normalized hashes, '
     'pins and full hosted results. The median/percentile consumer built but crashed with SIGSEGV on the first '
     'median call at n=1; the cause is undiagnosed. Its combined procedure record has no checked driver, and '
     'unreached percentile calls or larger medians are not promoted.',
     '',
     'The initial chi-square consumer named a variable shape, hiding the SHAPE intrinsic in an unused helper; '
     'renaming it corrected that consumer compile error. The corrected driver passed stricter relative checks. A '
     'combined diff/cumsum consumer built and passed its first-difference quotients, then failed cumulative '
     'reconstruction: 4.458984375 instead of 4.486328125. The pinned cumsum sorts values before accumulation, so '
     'it does not produce input-order prefixes. That combined record has no checked driver. The published '
     'diff-only consumer separately verifies all three orders on all 48 grids and makes no cumsum claim. No '
     'upstream numerical code was patched.',
     '',
     '## Provenance',
     '',
     'Pinned public interfaces and implementations were reviewed directly. The pinned example directory contains '
     'clustering, interpolation and random-generation consumers, rather than author examples of these exact '
     'calls; author_example is therefore null for these independently authored drivers. All ten drivers use the '
     'MIT consumer license and copy no implementation bodies. Classifications follow the [Netlib GAMS '
     'taxonomy](https://netlib.org/misc/gams.html). Loading an example does not submit a job. See the [coverage '
     'report](gams-coverage.md) for remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def nafpack_factors_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-nafpack-factors-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-nafpack-factors-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked NAFPack factorization drivers',
     '',
     'Ten independent REAL64 NAFPack consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. '
     'The existing cached library was reused; only main.f90 and playground-main were compiled. The [verification '
     'report](gams-nafpack-factors-ten-validation.json) records normalized UTF-8/LF source hashes, exact pins, '
     'timings and full output. GAMS coverage remains unfinished.',
     '',
     '## Checked APIs and references',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Triangular substitution | D2a3 | 27 lower/upper pairs; known vector solutions and residuals |\n'
     '| Known LU factors | D2a1 | 27 known unit-lower/upper factorizations, reconstruction and solved RHS |\n'
     '| Known LDU factors | D2a1 | 27 known L,D,U factors, unit triangular diagonals and reconstruction |\n'
     '| Cholesky lower factor | D2b1b | 27 known lower factors; consume only written lower entries and '
     'reconstruct SPD matrices |\n'
     '| Known LDL-transpose factors | D2b1b | 27 known unit-lower/positive diagonal factors and reconstruction '
     '|\n'
     '| Householder QR | D5 | 27 full-rank square cases; orthogonality, triangularity, reconstruction and solved '
     'RHS |\n'
     '| Givens QR | D5 | Same independent checks on 27 cases |\n'
     '| Classical Gram-Schmidt QR | D5 | Same independent checks on 27 cases |\n'
     '| Modified Gram-Schmidt QR | D5 | Same independent checks on 27 cases |\n'
     '| Characteristic coefficients | D4c | 15 known spectra; independent polynomial products, scalar root '
     'evaluations and Cayley-Hamilton residuals |',
     '',
     'All drivers explicitly require NAFPack REAL64 storage and finite results. The scalar tolerance is '
     'abs(actual-reference)<=2e-9*max(1,abs(reference)); matrix checks also verify shape. No upstream numerical '
     'source was patched. These bounded tests do not establish performance, difficult-matrix accuracy or '
     'behavior outside the demonstrated domains.',
     '',
     '## Known factors and triangular solves',
     '',
     'The nine solve/factor drivers use n=2..10 at scales 1/2,1,2. Deterministic dyadic unit-lower factors and '
     'nonsingular upper factors form A=L*U. For LU, both returned factors are checked individually before '
     'reconstructing A. A manufactured solution supplies a RHS for the returned forward/backward factors. LDU '
     'checks the known diagonal and corresponding unit-upper factor separately. These unpivoted decompositions '
     'are tested only with nonzero leading minors; matrices requiring pivoting are excluded.',
     '',
     'The triangular-substitution driver independently forms RHS values from the original known triangular '
     'matrices, then checks each recovered solution and direct residual. LDL-transpose cases use '
     'A=L*D*transpose(L), with positive diagonal D and known unit-lower L. This verifies the SPD path, not '
     'pivoted indefinite LDL.',
     '',
     '## Cholesky output convention',
     '',
     'The pinned Cholesky_decomposition writes the diagonal and lower triangle of its output but leaves the '
     'upper triangle unwritten. The driver never reads those unwritten entries. It copies the lower entries into '
     'a separate zero-filled matrix, checks them against a known lower-triangular factor, and verifies '
     'A=L*transpose(L). It does not claim the returned upper triangle contains zeros. Nonpositive-definite or '
     'singular inputs are excluded.',
     '',
     '## Four QR algorithms',
     '',
     'Each direct QR API is checked separately on 27 square full-rank matrices. The driver checks '
     'transpose(Q)*Q=I, every entry below R diagonal, and Q*R=A. A known solution gives b=A*x; a local '
     'upper-triangular substitution applied to transpose(Q)*b must recover x, and the original matrix must '
     'reproduce b. This uses the returned factors to solve an actual system while keeping the known solution '
     'independent of the algorithm. Factor signs are not prescribed. Rectangular, rank-deficient and '
     'ill-conditioned cases, pivoted QR and stability comparisons are excluded.',
     '',
     '## Characteristic-polynomial coefficients',
     '',
     'For n=2..6 and three scales, the driver constructs an analytic Householder matrix Q and distinct signed '
     'eigenvalues d, then A=Q*diag(d)*transpose(Q). Independently multiplying the linear factors (lambda-d_i) '
     'supplies every expected coefficient in descending-power order. Faddeev_Leverrier results must match these '
     'coefficients, vanish at each known eigenvalue under scalar Horner evaluation, and satisfy the matrix '
     'Cayley-Hamilton identity under matrix Horner evaluation. The optional inverse output is not requested or '
     'verified. Large degree and ill-conditioned coefficient problems are excluded. D4c is the broad GAMS '
     'associated-eigenvalue-operations class; no unsupported finer leaf is invented.',
     '',
     '## Provenance and maintenance',
     '',
     'Pinned public interfaces and implementations were reviewed directly. No matching direct-call author '
     'examples for these routines were found in the reviewed pinned test tree, so author_example is null rather '
     'than pointing at unrelated Fourier or array examples. The consumers are original MIT examples and copy no '
     'implementation bodies. Classifications follow the [Netlib GAMS '
     'taxonomy](https://netlib.org/misc/gams.html). Loading a driver does not submit a job. The [coverage '
     'report](gams-coverage.md) tracks remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def fstats_summaries_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fstats-summaries-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-fstats-summaries-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked Fstats summaries, distributions and design drivers',
     '',
     'Ten independent REAL64 Fstats consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. '
     'The cached library was reused; only main.f90 and playground-main were compiled. The [verification '
     'report](gams-fstats-summaries-ten-validation.json) retains normalized UTF-8/LF source hashes, exact pins, '
     'timings and complete output. GAMS coverage remains unfinished.',
     '',
     '## Checked problems',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Median and quantile conventions | L1a1a | 99 data sets; median and seven clamped (n+1)*q quantiles |\n'
     '| Trimmed locations | L1a1a | 99 data sets at three per-tail fractions; subset means and in-place sorting '
     '|\n'
     '| Paired covariances | L1c1b | 96 paired data sets; centered sums, symmetry and affine relation |\n'
     '| Raw median deviations | L1a1b | 99 data sets; median of absolute distances from an independent median |\n'
     '| Pooled group variances | L1a1b | 15 summaries of 2..6 groups; explicit degrees-of-freedom weighting |\n'
     '| Normal tail functions | L5a1n | 66 inputs; PDF, CDF, survival and finite log density |\n'
     '| Binomial boundaries | L5a1b | 165 inputs; degenerate parameters, complete integer support and adjacent '
     'outside values |\n'
     '| Poisson tail functions | L5a1p | 35 inputs; five rates including zero, integer support and tails |\n'
     '| Student t finite values | L5a1t | 44 inputs; degrees 1,2,5,10 and signed values -8..8 |\n'
     '| Full factorial designs | L7f | 12 designs; exact dimensions, Cartesian coverage and marginal/pairwise '
     'balance |',
     '',
     '## Summaries and conventions',
     '',
     'The four raw-data summary drivers use three deterministic affine dyadic families at sizes 1..33 '
     '(covariance starts at n=2). Local insertion sorting supplies independent references. Median averages the '
     'central pair for even sizes. Quantiles explicitly use the plotting position (n+1)*q, linear interpolation '
     'and endpoint clamping, with q=0,0.1,0.25,0.5,0.75,0.9,1; method numbering is not relied upon.',
     '',
     'Trimmed means remove floor(n*p) entries from each end for p=0,1/8,1/4. The consumer also checks the '
     'documented in-place sorting of its work array. Covariances use explicit centered cross-products divided by '
     'n-1, plus argument symmetry and covariance(x,2*x+1)=2*sample_variance(x). MAD is the raw median absolute '
     'deviation, with no normal-consistency scaling. Pooled variance uses supplied sample variances and sample '
     'counts with weights n_i-1; raw-container and column overloads are not verified.',
     '',
     'Summary and finite log-density comparisons require finite results and '
     'abs(actual-reference)<=2e-10*max(1,abs(reference)). Empty arrays, nonfinite data, invalid '
     'trimming/quantile parameters, constant/near-overflow robustness and missing-value policies are not '
     'established by these bounded tests.',
     '',
     '## Probability references and tails',
     '',
     'The [reference table](gams-fstats-summaries-ten-references.json) records every distribution parameter, '
     'evaluation point, PDF/PMF, CDF and survival value. References were generated independently with mpmath '
     '1.3.0 at 80 decimal digits, confirmed at 120 digits with absolute differences below 1e-60, and written as '
     '18-significant-digit constants. Inputs are exact dyadics. Every probability must be finite and satisfy '
     'abs(actual-reference)/max(abs(reference),1e-30)<=2e-9. Exact zero references are effectively checked '
     'exactly. Finite log densities are checked against log of the independently referenced positive density; '
     'infinite log values are not requested.',
     '',
     'Normal cases use means -1,0,1, standard deviations 1/2,2, and eleven standardized offsets from -6 to 6. '
     'PDF references use the defining Gaussian exponential and CDF/survival use high-precision complementary '
     'error functions. Binomial cases use n=0,1,2,5,10, p=0,1/8,1/2,7/8,1 and every integer k=-1..n+1; '
     'independent finite binomial sums test both support boundaries and degenerate p=0/1 or n=0.',
     '',
     'Poisson rates are 0,1/8,1/2,2,8 at k=-1,0,1,2,4,8,12. PMF and CDF references use the defining '
     'exponential/factorial finite sums, retaining tails in high precision rather than subtracting rounded '
     'REAL64 CDFs. Student t degrees are 1,2,5,10 at eleven signed arguments -8..8, using high-precision '
     'gamma/beta definitions. Separate tests check the degree-1 Cauchy and degree-2 closed forms. All survival '
     'functions represent the strict upper tail P(X>x), including discrete distributions. Undefined low-degree '
     'moments, invalid parameters, fractional discrete inputs, extreme-tail underflow and inverse distributions '
     'are excluded.',
     '',
     '## Experimental designs',
     '',
     'The full-factorial consumer uses 1..4 factors with 1..4 levels, twelve combinations of factor count and '
     'level pattern. It checks dimensions against an independent product, all legal levels, unique mixed-radix '
     'keys spanning the entire Cartesian product, and exact marginal and pairwise level counts. It does not '
     'prescribe row ordering. Huge designs, fractional factorials, model fitting and statistical optimality are '
     'excluded.',
     '',
     '## Provenance and maintenance',
     '',
     'Pinned public APIs, implementations and linked author statistics/distribution/experimental-design tests '
     'were reviewed. Those tests informed API conventions; these drivers are independent MIT consumers and copy '
     'no implementation or author-test bodies. No upstream code was patched. Classifications follow the [Netlib '
     'GAMS taxonomy](https://netlib.org/misc/gams.html). Loading a driver does not submit a job. The [coverage '
     'report](gams-coverage.md) records remaining work.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def fstats_fitting_ten_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fstats-fitting-ten-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-fstats-fitting-ten-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Ten checked Fstats probability, interpolation and regression drivers',
     '',
     'Ten independent REAL64 Fstats consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox, '
     'reusing the existing library and compiling only main.f90 and playground-main. The [verification '
     'report](gams-fstats-fitting-ten-validation.json) preserves normalized UTF-8/LF source hashes, pins, '
     'timings and complete output. GAMS coverage remains unfinished.',
     '',
     '## Checked problems',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Chi-squared positive tails | L5a1c | 30 inputs; five degrees and six positive values |\n'
     '| F positive tails | L5a1f | 20 inputs; four degree pairs and five positive values |\n'
     '| Lognormal observation scale | L5a1l | 42 inputs; log-mean/log-scale conventions and nonpositive support '
     '|\n'
     '| Bivariate normal densities | L5b1n | 150 points; explicit 2-by-2 determinant/inverse references |\n'
     '| Piecewise linear values | E1a | 123 queries and 15 nodes on irregular grids |\n'
     '| Polynomial interpolation | E1b | 164 queries, degrees 1..4 |\n'
     '| Global Hermite values and derivatives | E1b | 165 queries, degrees 1..5, supplied first derivatives |\n'
     '| Linear regression residuals | L8a1a1 | 138 noisy fits, with and without intercept |\n'
     '| Quadratic regression projections | L8b1b1 | 15 quartic-contaminated fits; independent moment projection '
     '|\n'
     '| Experimental factor coding | L7g | 27 physical/coded coordinates and round trips |',
     '',
     '## Probability definitions',
     '',
     'The [reference tables](gams-fstats-fitting-ten-references.json) contain 92 parameter/value combinations '
     'generated independently with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits (absolute '
     'differences below 1e-60). Inputs are exact dyadics; references are written with 18 significant digits. '
     'Chi-squared uses its defining gamma density and lower/upper incomplete-gamma integrals. F uses its beta '
     'normalization and complementary beta-integral definitions. Lognormal uses a Gaussian change of variables: '
     'mean_value and standard_deviation describe log(X), while evaluation points are in observation space. Its '
     'negative and zero inputs must have zero density/CDF and unit survival.',
     '',
     'Each univariate consumer checks PDF, CDF, strict upper survival P(X>x), and finite log density where the '
     'reference density is positive. Probability error must be <=2e-9*max(abs(reference),1e-30), so zero '
     'references are effectively exact. Other finite scalar/log comparisons use '
     'abs(error)<=2e-10*max(1,abs(reference)). Invalid parameters, infinite log outputs, inverse functions, '
     'extreme underflow and chi-squared/F support-boundary singularities are excluded.',
     '',
     'The bivariate driver uses covariances [[2,rho],[rho,1]] with rho=-1/2,0,1/2, two mean vectors, and 25 '
     'dyadic offsets per case. Independent scalar determinants and explicit inverse quadratic forms supply PDF '
     'and log-density references, rather than repeating the package Cholesky solve. CDFs, singular/invalid '
     'covariances and higher dimensions are not verified.',
     '',
     '## Interpolation',
     '',
     'Piecewise-linear interpolation uses three irregular-grid data sets, independent segment weights, '
     'scalar/vector routes and bounded extrapolation. Polynomial interpolation reproduces explicit polynomials '
     'of degrees 1..4 at 41 points each, including bounded extrapolation. These checks do not establish '
     'high-degree conditioning or behavior for duplicate/invalid knots.',
     '',
     'Global Hermite interpolation uses three irregular nodes with supplied function values and first '
     'derivatives, and reproduces polynomials of degrees 1..5 at 33 points each, including derivative '
     'evaluation. A fresh object is allocated and released for each polynomial. This is global Hermite '
     'polynomial interpolation, not piecewise cubic Hermite. Reinitialization of an existing object failed in '
     'the retained probe and is not claimed to work.',
     '',
     '## Regression and design coding',
     '',
     'The linear consumer uses sizes 3..25 and three dyadic noisy families, with and without an intercept (138 '
     'fits). Independent centered-sum or through-origin formulas provide coefficients. It checks every fitted '
     'value, the modeled-minus-actual residual convention, and residual orthogonality to the design columns.',
     '',
     'The quadratic consumer uses five symmetric grids of 5..13 points and three quadratic signals with a '
     'quartic perturbation. An independent 2-by-2 even-moment projection supplies the fitted constant and '
     'quadratic coefficient; symmetry supplies the linear coefficient. All 15 fits check coefficients, fitted '
     'values, residuals and the three normal-equation orthogonality conditions. These bounded full-rank fits do '
     'not verify inference, confidence intervals, weighting, rank-deficient data or high-degree stability.',
     '',
     'Experimental factor coding checks nine exact dyadic levels over each of three unequal physical ranges. '
     'Both directions are compared with prescribed coordinates, including low/high/midpoint, and then '
     'round-tripped. Equal/reversed ranges and invalid shapes are excluded. This is a service routine for '
     'experimental designs, not an ANOVA solver.',
     '',
     '## Retained unsuccessful probes',
     '',
     'The [interpolation reproductions](gams-candidates/fstats-interpolation/README.md) preserve exact '
     'consumers, hashes, pins and full hosted results. The clamped cubic spline failed an independent '
     'irregular-grid cubic value check; it has no published checked driver. The initial Hermite consumer hit an '
     'allocation error when reinitializing the same object. Fresh-object consumers passed all original numerical '
     'assertions. No upstream numerical code was patched and tolerances were not relaxed.',
     '',
     '## Provenance',
     '',
     'Pinned implementations and linked author distribution, interpolation, regression and experimental-design '
     'tests informed API usage. These are independent MIT consumers; no author test or implementation bodies '
     'were copied. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). No '
     'backend redeployment or package-library rebuild is needed.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def next_numerical_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-next-numerical-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-next-numerical-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Six checked drivers from the numerical coverage audit',
     '',
     'All six ranked candidates passed GNU Fortran 16.2.0 / FPM 0.12.0 in the hosted sandbox, reusing the '
     'existing package libraries and compiling only main.f90 and playground-main. The [verification '
     'report](gams-next-numerical-validation.json) preserves exact package pins, normalized UTF-8/LF source '
     'hashes, timings and complete output. The [coverage audit](gams-driver-audit.md) now removes these '
     'completed candidates from its pending list. GAMS coverage remains unfinished.',
     '',
     '## Checked problems',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| nonlin BFGS, finite differences | G1b1a | 12 coupled SPD quadratics and three Rosenbrock starts |\n'
     '| nonlin least squares, finite differences | G1b1a | 24 exact exponential fits without a registered '
     'Jacobian |\n'
     '| RPN signed real cube roots | C2 | 55 zero, signed dyadic cube and noncube references |\n'
     '| RPN modified Bessel I0 | C10 | 29 values, signs, tiny inputs and branch-15 neighbors |\n'
     '| fortranlib tabulated interpolation | E1 | 207 scalar/vector queries on irregular knots and explicit fill '
     'values |\n'
     '| fortranlib tabulated integration | H2 | 198 clipped intervals and three full integrals |',
     '',
     '## Finite-difference optimization configurations',
     '',
     'The BFGS consumer registers only an objective callback. Twelve coupled positive-definite quadratic '
     'problems cover dimensions 2..5 with three starts each, and three further starts solve Rosenbrock. '
     'Independent known minimizers, explicit objective and analytic stationarity formulas, reported-objective '
     'agreement and normal termination flags are required. Maximum normalized parameter error is bounded by '
     '5e-5, objective by 2e-9 and gradient infinity norm by 2e-5; reported objective agreement is 1e-12 '
     'absolute. These are correctness checks, not global convergence or performance guarantees.',
     '',
     'The residual-only least-squares consumer registers no Jacobian and requires its analytic callback count to '
     'remain zero. It keeps the same 24 exact exponential fixtures and explicit step factor 1 as the separately '
     'checked analytic-Jacobian driver. Independent model formulas check the known parameters (normalized '
     'tolerance 2e-7), returned residuals (1e-11 consistency), exact-fit residual infinity norm (1e-8), squared '
     'residual norm (1e-10) and analytic J-transpose-residual (1e-6). The independently computed stationarity '
     'Jacobian is also checked by central differences at the starting points; it is never supplied to the '
     'solver.',
     '',
     'The [retained nonlin least-squares failures](gams-candidates/nonlin-least-squares/README.md) with default '
     'step factor and nonzero-residual families remain unresolved. Passing the exact-fit family in another '
     'derivative mode does not verify those cases. No stopping rule, library implementation or tolerance was '
     'patched to make this batch pass.',
     '',
     '## Elementary and special functions',
     '',
     'The [reference tables](gams-next-numerical-references.json) contain exact rational inputs and '
     '18-significant-digit outputs generated with mpmath 1.3.0 at 80 and 120 decimal digits. Definitions agree '
     'within 1e-50*max(1,abs(reference)). The consumer requires the package kind to equal REAL64 and finite '
     'relative error <=2e-12 with a reference floor of 1e-100.',
     '',
     'Cube roots include 42 signed exact cubes from dyadic roots at exponents -30..30 (input exponents around '
     '-90..90), zero and 12 additional signed noncube-family inputs. Checks compare high-precision real cube '
     'roots, signs and cube reconstruction. Some additional inputs are themselves exact cubes; no complex-root '
     'or subnormal claim is made.',
     '',
     'Unscaled modified Bessel I0 uses 29 signed inputs through 64, including zero, tiny dyadics, and '
     '15-1/1024,15,15+1/1024 on both signs around the pinned implementation branch. Positivity and evenness are '
     'checked. Independent high-precision Bessel definitions supply the values; separate Decimal-series tests '
     'check the recorded constants. Scaled Bessel functions, overflow and arbitrary extreme arguments are '
     'excluded.',
     '',
     '## Tabulated interpolation and integration',
     '',
     'Both consumers use five irregular knots [-2,-3/4,0,1/2,2] and three deterministic signed value sets. '
     'Interpolation checks 65 in-domain queries and four outside queries per set, for 207 scalar/vector '
     'comparisons. Independent segment weights supply the interior references; the caller explicitly requests '
     'bounds_error=false and fill_value=-123. Outside values are filled, not extrapolated. Increasing grids '
     'only; duplicate/descending knots and log interpolants are excluded.',
     '',
     'Integration checks every ordered pair from eleven limits (-3..3), including equal, same-segment, partial, '
     'outside and clipped intervals, for 198 subset integrals plus three full-domain integrals. Independent '
     'polynomial antiderivatives are integrated over the clipped overlap of each segment. These are areas under '
     'the piecewise-linear tabulated interpolant, not exact quadrature of an arbitrary underlying nonlinear '
     'function. Reversed limits and non-linear interpolant variants are excluded. Both consumers use '
     'absolute-scaled error <=2e-12*max(1,abs(reference)).',
     '',
     'The cached fortranlib image already contains the checksum-locked upstream lib_array fixes recorded in the '
     'catalog (matching upstream 844611933cba06d71490033e68b355f6f0ff704f). Those adaptations, dependency pins, '
     'images and build report are unchanged. This batch adds consumers only; it does not apply new package '
     'edits.',
     '',
     '## Classification, provenance and maintenance',
     '',
     'Six separate records now identify the finite-difference modes and the individual cube-root, Bessel, '
     'interpolation and integration APIs. Their classes have been removed from the older composite records, '
     'which retain their existing analytic-gradient, sinc/sech, beta and quadratic drivers. This avoids leaving '
     'fulfilled claims in the audit or suggesting one driver validates a different mode. There are now 509 '
     'checked drivers and 536 mapped procedure records; 27 records still have no dedicated checked driver.',
     '',
     'Pinned implementations and recorded author examples/tests informed API usage. These are independent MIT '
     'consumers, including reuse of the playground-owned exact-fit fixture in a distinct solver configuration. '
     'Loading a driver submits no job. No backend redeployment or library rebuilding is needed.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
    return '\n'.join(lines)


def fortranlib_tables_review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    drivers = [d for d in driver_data(root, data)
               if driver_validation_path(d) == 'docs/gams-fortranlib-tables-validation.json']
    records = {r['id']: r for r in data['procedure_mappings']}
    packages = {p['id']: p for p in json.loads((root/'fpm_catalog.json').read_text(encoding='utf-8'))['packages']}
    report = json.loads((root/'docs/gams-fortranlib-tables-validation.json').read_text(encoding='utf-8'))
    results = {r['driver_id']: r for r in report['drivers']}
    lines = ['# Five checked scientific-table drivers for fortranlib',
     '',
     'All five independent REAL64 consumers passed GNU Fortran 16.2.0 / FPM 0.12.0 with the existing cached '
     'fortranlib library. Only main.f90 and playground-main were compiled. The [verification '
     'report](gams-fortranlib-tables-validation.json) preserves exact package pins, normalized UTF-8/LF source '
     'hashes, timings and full output. No new failed probe was produced. No backend deployment or package '
     'rebuild is needed. GAMS coverage remains unfinished.',
     '',
     '## Checked problems',
     '',
     '| Driver | GAMS | Independent checks |\n'
     '| --- | --- | --- |\n'
     '| Logarithmic interpolation | E1c | 715 scalar/vector query pairs from eleven analytic families |\n'
     '| Logarithmic areas and prefixes | H2a1b2 | 726 subset areas, eleven full integrals and 55 cumulative '
     'values |\n'
     '| Conservative rebinning | H2c | 84 cell means and fourteen total-area identities |\n'
     '| Bilinear surfaces | E2a | 1875 interior/boundary values and twelve outside fills |\n'
     '| Masked histograms | L1a1d | Six weighted/unweighted 1D histograms and three 2D count maps |',
     '',
     '## Why this smaller batch',
     '',
     'The existing mapped-procedure queue is mostly retained failures, service limits or overlapping '
     'classification claims. Repeating near-identical drivers solely to fill another batch of ten would offer '
     'little benefit. These five consumers instead cover previously unreviewed public APIs and distinct '
     'scientific-data operations in an already compiled package. This does not imply that all package APIs or '
     'all GAMS branches have been exhausted.',
     '',
     'For subsequent work, prefer a named capability with a clear independent oracle, a common problem comparing '
     'multiple packages, resolution of the PCA linking limitation, or retesting an upstream repair. I recommend '
     'pausing automatic gap-filling batches rather than treating the driver count as a target. The [coverage '
     'audit](gams-driver-audit.md) retains the outstanding work.',
     '',
     '## Analytic table conventions',
     '',
     'The data consumers use the irregular positive grid [1/2,1,2,4,8]. A shared independent reference model '
     'defines four elementary families and explicit antiderivatives: linear 2+p*x; exponential 3*exp(p*x); '
     'affine-logarithm 2+p*log(x); and power law 3*x**p. Exponential parameters are -1/4,0,1/4, affine-log '
     'parameters -1/2,0,1/2, and power exponents -2,-1,0,1/2,2. Linear rebinning also uses p=-1,0,1. These are '
     'eleven log-mode families and fourteen rebinning families, not separate drivers for each variation.',
     '',
     'The upstream names linlog, loglin and loglog mean log(y) versus linear x, linear y versus log(x), and '
     'log(y) versus log(x), respectively. These conventions are stated explicitly because reversing the axes '
     'changes the mathematical problem. Constant cases and the reciprocal power-law integral are checked without '
     'dividing by a zero parameter. All finite numerical comparisons use '
     'abs(actual-reference)<=2e-11*max(1,abs(reference)).',
     '',
     '## Interpolation and integration',
     '',
     'For every log family, interpolation checks 61 in-domain queries including knots and boundaries, plus four '
     'positive outside-domain queries using bounds_error=false and fill_value=-123. Both scalar and array '
     'interfaces are checked against the defining elementary function. Invalid/nonpositive log inputs, '
     'duplicate/descending knots, extrapolation and arbitrary nonanalytic tables are excluded.',
     '',
     'The area consumer evaluates every ordered pair from eleven limits spanning [1/4,9], giving 66 intervals '
     'per family. Limits are independently clipped to [1/2,8] and the explicit antiderivative supplies the '
     'reference. Empty, outside, same-segment and knot-crossing intervals are included. Full-domain and each '
     'cumulative-prefix value are checked independently. Reversed limits, error estimation and ill-conditioned '
     'near-reciprocal/near-constant branches are not established.',
     '',
     'These tests use functions exactly representable by the selected interpolant. They do not claim that '
     'interpolating or integrating arbitrary data reproduces an unknown underlying physical function, or that an '
     'adaptive accuracy target is supported. E1c records nonpolynomial interpolation; H2a1b2 records a '
     'nonautomatic finite-grid quadrature API.',
     '',
     '## Conservative remapping',
     '',
     'All four rebin APIs map samples onto six irregular cell centers [1/2,1,3/2,5/2,4,8]. For linear-x modes '
     'the interior cell edges are arithmetic midpoints; for log-x modes they are geometric midpoints. The first '
     'and last centers themselves bound the domain, rather than extending half a cell beyond it.',
     '',
     'Each expected output is the independent analytic integral over its cell divided by cell width. The '
     'width-weighted sum of all six returned means must equal the known full-domain integral. This checks a '
     'conservation property and distinguishes cell averaging from evaluating the field at the center. Arbitrary '
     'density reconstruction, degenerate cells and invalid log inputs are excluded.',
     '',
     '## Bilinear surfaces and histograms',
     '',
     'Three fields a+b*x+c*y+d*x*y on irregular 4-by-3 grids check axis orientation and independent cross terms. '
     'Each uses a 25-by-25 query grid including all four outer edges and corners, followed by four explicit '
     'outside-fill calls. Higher-order surfaces, invalid shapes, descending coordinates and extrapolation are '
     'not checked.',
     '',
     'One-dimensional histograms use eleven exact dyadic samples spanning outside [-1,1], four equal bins, '
     'positive dyadic weights, and three masks (all, alternating, none). Each mask is checked with and without '
     'weights. Independent half-open membership enumeration supplies bin counts and weight sums, with the final '
     'upper endpoint included in the last bin. Bin centers are checked separately. The Cartesian 121-point grid '
     'supplies three masked two-dimensional count maps, checked cell by cell. 2D weighting, density '
     'normalization, variable widths, descending bounds and random-distribution quality are not asserted.',
     '',
     '## Provenance and limits',
     '',
     'Pinned lib_array APIs and implementations were reviewed directly; no matching pinned author example is '
     'recorded for these consumers. The independent MIT drivers copy no author implementation or test bodies. '
     'The source pin is 60fd094d3e137137ce00ec120b085e9b23ebf68b; the cached image already contains the '
     'checksum-locked upstream lib_array fixes matching 844611933cba06d71490033e68b355f6f0ff704f. Those existing '
     'adaptations, dependency pins, image recipe and precompiled build report remain unchanged.',
     '',
     'Classifications use the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading an example does '
     'not submit a job. The catalog now has 514 checked drivers and 541 mapped procedure records. These new APIs '
     'add an E1c class demonstration; the previously outstanding PCA class remains unverified.',
     '',
     '## Driver details',
     '']
    for d in drivers:
        lines += ['### '+d['id']+' ('+d['gams_code']+')', '', d['modifications'], '']
    lines += ['## Provenance and actual output', '']
    for d in drivers:
        record = records[d['procedure_id']]
        evidence = record['evidence'][0]
        base = f'https://github.com/{packages[d["package_id"]]["repository"]}/blob/{d["revision"]}/'
        url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={d["package_id"]}&example={d["name"]}'
        output = next(s['stdout'] for s in results[d['id']]['stages'] if s['name'] == 'Run')
        lines += ['### '+d['id'], '',
                  f'[Load driver]({url}) / [Driver source](../{d["path"]}) / '
                  f'[Pinned procedure]({base}{evidence["path"]}#L{evidence["line"]}) / ' +
                  (f'[Author test]({base}{d["author_example"]})' if d["author_example"] else 'No pinned author example; API reviewed directly.'), '', '```text', '\n'.join(line.rstrip() for line in output.splitlines()), '```', '']
    lines += ['## Maintenance', '', '```text',
              'python xverify_gams_drivers.py --drivers '+' '.join(d['id'] for d in drivers),
              'python xpackage_gams.py', 'python xfpm_examples.py', 'python xsite.py', '```', '',
              'Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. '
              'No backend redeployment or package library rebuild is required. '
              'The [coverage report](gams-coverage.md) lists remaining work.', '']
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
             f'records, {unchecked} still {"has" if unchecked == 1 else "have"} no class-specific checked driver.', '',
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
                         (SORTING_REPORT, sorting_review_text()),
                         (NUMBER_THEORY_REPORT, number_theory_review_text()),
                         (ARITHMETIC_REPORT, arithmetic_review_text()),
                         (APPLIED_METHODS_REPORT, applied_methods_review_text()),
                         (BOUNDARY_REPORT, boundary_review_text()),
                         (RESAMPLING_MARKOV_REPORT, resampling_markov_review_text()),
                         (FOURIER_GEOMETRY_REPORT, fourier_geometry_review_text()),
                         (SPARSE_INTEGRAL_REPORT, sparse_integral_review_text()),
                         (SPATIAL_NUFFT_REPORT, spatial_nufft_review_text()),
                         (PDE_REPORT, pde_review_text()),
                         (DATA_KINDS_REPORT, data_kinds_review_text()),
                         (PRODUCTS_STATUS_REPORT, products_status_review_text()),
                         (KRIGING_NETWORK_REPORT, kriging_network_review_text()),
                         (LOOKUP_FASTMATH_REPORT, lookup_fastmath_review_text()),
                         (CIRCUITS_BETA_REPORT, circuits_beta_review_text()),
                         (INVERSE_TVD_REPORT, inverse_tvd_review_text()),
                         (ROOTS_SPLINES_QUADRATURE_REPORT, roots_splines_quadrature_review_text()),
                         (IO_BOUNDS_REPORT, io_bounds_review_text()),
                         (OPTIMIZATION_SPACING_REPORT, optimization_spacing_review_text()),
                         (RASTER_DISTRIBUTIONS_REPORT, raster_distributions_review_text()),
                         (QUANTITIES_SPHERICAL_REPORT, quantities_spherical_review_text()),
                         (DELAY_EMBEDDING_REPORT, delay_embedding_review_text()),
                         (MATRIX_ROOTS_BOX_REPORT, matrix_roots_box_review_text()),
                         (DISPERSION_REPORT, dispersion_review_text()),
                         (RULES_DIFFERENCES_REPORT, rules_differences_review_text()),
                         (QR_AUTODIFF_REPORT, qr_autodiff_review_text()),
                         (DENSE_SPECTRA_REPORT, dense_spectra_review_text()),
                         (LEAST_INTERPOLATION_REPORT, least_interpolation_review_text()),
                         (RKF_QAGS_REPORT, rkf_qags_review_text()),
                         (JACOBIAN_ROOTS_REPORT, jacobian_roots_review_text()),
                         (HIGHER_AD_REPORT, higher_ad_review_text()),
                         (MOMENTS_NUFFT2D_REPORT, moments_nufft2d_review_text()),
                         (ITERATIVE_LS_REPORT, iterative_ls_review_text()),
                         (SPECTRAL_WRAPPERS_REPORT, spectral_wrappers_review_text()),
                         (REGRID_RK45_REPORT, regrid_rk45_review_text()),
                         (FITPACK_POLYNOMIALS_REPORT, fitpack_polynomials_review_text()),
                         (DIAGONAL_RESPONSE_REPORT, diagonal_response_review_text()),
                         (RANKING_MAGIC_REPORT, ranking_magic_review_text()),
                         (GEODESY_FORLAB_REPORT, geodesy_forlab_review_text()),
                         (JACOBIAN_TRANSFORMS_REPORT, jacobian_transforms_review_text()),
                         (EXPRESSION_EVALUATION_REPORT, expression_evaluation_review_text()),
                         (CONVERSION_TRIANGULATION_REPORT, conversion_triangulation_review_text()),
                         (GRAPH_SORTING_REPORT, graph_sorting_review_text()),
                         (NEIGHBORS_SPARSE_REPORT, neighbors_sparse_review_text()),
                         (ADAPTIVE_AD_REPORT, adaptive_ad_review_text()),
                         (LU_ORBITS_REPORT, lu_orbits_review_text()),
                         (DAE_FFT_REPORT, dae_fft_review_text()),
                         (PROPACK_FMM_REPORT, propack_fmm_review_text()),
                         (GMRES_INVERSE_REPORT, gmres_inverse_review_text()),
                         (PERIODIC_CALCULUS_REPORT, periodic_calculus_review_text()),
                         (EXPRESSIONS_SKY_REPORT, expressions_sky_review_text()),
                         (UNSIGNED_BITSETS_REPORT, unsigned_bitsets_review_text()),
                         (SPARSE_ADVECTION_REPORT, sparse_advection_review_text()),
                         (PRODUCTS_PARTITIONS_REPORT, products_partitions_review_text()),
                         (MULTIDIMENSIONAL_FFT_REPORT, multidimensional_fft_review_text()),
                         (SPARSE_SPECTRA_REPORT, sparse_spectra_review_text()),
                         (PROJECTION_LBFGS_REPORT, projection_lbfgs_review_text()),
                         (GRADIENT_SWARM_REPORT, gradient_swarm_review_text()),
                         (PROJECTION_TRAINING_REPORT, projection_training_review_text()),
                         (DIRECTIONS_FITTING_REPORT, directions_fitting_review_text()),
                         (RANDOM_REFERENCES_REPORT, random_references_review_text()),
                         (TANGENTS_BLOCKS_REPORT, tangents_blocks_review_text()),
                         (RADIAL_DENSE_REPORT, radial_dense_review_text()),
                         (INFERENCE_PAIRS_REPORT, inference_pairs_review_text()),
                         (HELMHOLTZ_STREAMS_REPORT, helmholtz_streams_review_text()),
                         (FRICTION_TORCH_REPORT, friction_torch_review_text()),
                         (PARETO_DIIS_REPORT, pareto_diis_review_text()),
                         (DATA_TEN_REPORT, data_ten_review_text()),
                         (STATE_TEN_REPORT, state_ten_review_text()),
                         (INTEROP_TEN_REPORT, interop_ten_review_text()),
                         (STORAGE_TEN_REPORT, storage_ten_review_text()),
                         (WORKFLOWS_TEN_REPORT, workflows_ten_review_text()),
                         (STATISTICS_SERVICES_TEN_REPORT, statistics_services_ten_review_text()),
                         (FACTORIZATION_RULES_TEN_REPORT, factorization_rules_ten_review_text()),
                         (SPECIAL_FUNCTIONS_TEN_REPORT, special_functions_ten_review_text()),
                         (SYSTEMS_SPECTRA_TEN_REPORT, systems_spectra_ten_review_text()),
                         (DISTRIBUTION_TEN_REPORT, distribution_ten_review_text()),
                         (PCA_ORDERING_TEN_REPORT, pca_ordering_ten_review_text()),
                         (ACTIVATIONS_TEN_REPORT, activations_ten_review_text()),
                         (GRIDS_TEN_REPORT, grids_ten_review_text()),
                         (COMPLEX_TEN_REPORT, complex_ten_review_text()),
                         (COMPLEX_OPERATORS_TEN_REPORT, complex_operators_ten_review_text()),
                         (STATISTICS_RANK_TEN_REPORT, statistics_rank_ten_review_text()),
                         (GRIDS_SPECTRA_TEN_REPORT, grids_spectra_ten_review_text()),
                         (INTEGRALS_TENSORS_TEN_REPORT, integrals_tensors_ten_review_text()),
                         (TRANSFORMS_STRUCTURES_TEN_REPORT, transforms_structures_ten_review_text()),
                         (FULLERTON_FUNCTIONS_TEN_REPORT, fullerton_functions_ten_review_text()),
                         (ROOTS_STRUCTURED_TEN_REPORT, roots_structured_ten_review_text()),
                         (ORDERING_RUNGE_TEN_REPORT, ordering_runge_ten_review_text()),
                         (GAMMA_RELATIVE_TEN_REPORT, gamma_relative_ten_review_text()),
                         (BANDED_PRODUCTS_TEN_REPORT, banded_products_ten_review_text()),
                         (FORLAB_STATISTICS_TEN_REPORT, forlab_statistics_ten_review_text()),
                         (NAFPACK_FACTORS_TEN_REPORT, nafpack_factors_ten_review_text()),
                         (FSTATS_SUMMARIES_TEN_REPORT, fstats_summaries_ten_review_text()),
                         (FSTATS_FITTING_TEN_REPORT, fstats_fitting_ten_review_text()),
                         (NEXT_NUMERICAL_REPORT, next_numerical_review_text()),
                         (FORTRANLIB_TABLES_REPORT, fortranlib_tables_review_text()),
                         (EVIDENCE_REPORT, mapping_evidence_text()),
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
