import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest

from xpackage_gams import (gams_data, package_classes, review_text, subclass_module, ROOT, REPORT,
                          driver_data, g1_review_text, PILOT_REPORT, g1_procedures,
                          numerical_review, numerical_review_text, NUMERICAL_REPORT,
                          quadrature_review_text, QUADRATURE_REPORT, driver_validation_path,
                          roots_review_text, ROOTS_REPORT,
                          linear_algebra_review_text, LINEAR_ALGEBRA_REPORT,
                          ode_review_text, ODE_REPORT,
                          interpolation_review_text, INTERPOLATION_REPORT,
                          transforms_review_text, TRANSFORMS_REPORT,
                          constrained_review_text, CONSTRAINED_REPORT,
                          special_functions_review_text, SPECIAL_FUNCTIONS_REPORT,
                          statistics_review_text, STATISTICS_REPORT,
                          random_review_text, RANDOM_REPORT,
                          differentiation_review_text, DIFFERENTIATION_REPORT,
                          systems_review_text, SYSTEMS_REPORT,
                          sparse_review_text, SPARSE_REPORT,
                          cubature_review_text, CUBATURE_REPORT,
                          surfaces_review_text, SURFACES_REPORT,
                          stiff_review_text, STIFF_REPORT,
                          polynomial_review_text, POLYNOMIAL_REPORT,
                          convolution_review_text, CONVOLUTION_REPORT,
                          regression_review_text, REGRESSION_REPORT,
                          matrix_equations_review_text, MATRIX_EQUATIONS_REPORT,
                          sorting_review_text, SORTING_REPORT,
                          coverage_data, coverage_review_text, COVERAGE_REPORT,
                          class_evidence, mapping_evidence_text, EVIDENCE_REPORT)


class GamsFilterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_select = False
        self.code = None
        self.options = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'select':
            self.in_select = attrs.get('id') == 'package-gams'
        if self.in_select and tag == 'option':
            self.code = attrs.get('value', '')
            self.options[self.code] = ''

    def handle_endtag(self, tag):
        if tag == 'select':
            self.in_select = False
        if tag == 'option':
            self.code = None

    def handle_data(self, text):
        if self.in_select and self.code is not None:
            self.options[self.code] += text


class PackageGamsTests(unittest.TestCase):
    def test_mapping_evidence_is_specific_to_procedure_and_class(self):
        tree = {'G': {'parent': None}, 'G1': {'parent': 'G'},
                'G1a': {'parent': 'G1'}, 'G1b': {'parent': 'G1'}}
        records = [{'id': 'solver', 'gams_codes': ['G1a', 'G1b']}]
        drivers = [{'procedure_id': 'solver', 'gams_code': 'G1a'}]
        self.assertEqual(class_evidence(tree, 'G1a', records, drivers)['status'], 'verified')
        self.assertEqual(class_evidence(tree, 'G1', records, drivers)['status'], 'verified')
        self.assertEqual(class_evidence(tree, 'G1b', records, drivers)['status'], 'source-supported')
        self.assertEqual(class_evidence(tree, 'G1a', [], drivers)['status'], 'uncertain')
        other_driver = [{'procedure_id': 'another-solver', 'gams_code': 'G1a'}]
        self.assertEqual(class_evidence(tree, 'G1a', records, other_driver)['status'], 'source-supported')

    def test_mapping_evidence_report_is_current_and_keeps_review_queue(self):
        text = mapping_evidence_text()
        self.assertEqual((ROOT / EVIDENCE_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('Mappings requiring source review', text)
        self.assertIn('stdlib-sort', text)
        self.assertIn('| N6 | verified |', text)
        self.assertIn('sandbox failure alone does not disprove an algorithm', text)

    def test_public_assignments_cover_catalog_and_preserve_pins(self):
        data = gams_data()
        original = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
        public = json.loads((ROOT / 'site/fpm/packages.json').read_text(encoding='utf-8'))
        all_packages = {p['repository'].lower(): p for p in json.loads(
            (ROOT / 'site/fpm/all-packages.json').read_text(encoding='utf-8'))}
        self.assertEqual(set(data['packages']), {p['id'] for p in public})
        for package in original:
            with self.subTest(package=package['id']):
                entry = next(p for p in public if p['id'] == package['id'])
                self.assertEqual(entry['gams'], package_classes(data, package['id']))
                self.assertEqual(all_packages[package['repository'].lower()]['gams'], entry['gams'])
                for field in ('revision', 'archive_sha256', 'dependencies'):
                    self.assertEqual(entry.get(field), package.get(field))
        self.assertEqual(data['packages']['mersenne-twister-fortran'], ['L'])
        self.assertEqual(data['packages']['dvode'], ['I'])
        self.assertEqual(data['packages']['rational_number'], ['A'])
        self.assertEqual(data['packages']['minpack'], ['F', 'G', 'K'])
        self.assertEqual(data['subclass_assignments']['mersenne-twister-fortran'], ['L6'])
        self.assertEqual(data['subclass_assignments']['dvode'], ['I1'])
        self.assertEqual(data['subclass_assignments']['rational_number'], ['A2'])
        self.assertEqual(data['subclass_assignments']['minpack'], ['F2', 'G1', 'K1'])
        self.assertNotIn('datetime-fortran', data['subclass_assignments'])
        self.assertEqual(package_classes(data, 'datetime-fortran'), [
            {'code': 'R', 'label': data['classes']['R'], 'parent': None}])

    def test_subclass_tree_generated_module_and_natural_order(self):
        data = gams_data()
        self.assertEqual((ROOT / 'site/fpm/gams_classes.mjs').read_text(encoding='utf-8'), subclass_module(data))
        self.assertEqual(data['subclasses']['L6'], {'label': 'Random number generation', 'parent': 'L'})
        self.assertEqual(data['subclasses']['C10']['parent'], 'C')
        self.assertNotEqual(data['subclasses']['C10']['parent'], 'C1')
        self.assertEqual(data['subclasses']['L10']['parent'], 'L')
        self.assertNotEqual(data['subclasses']['L10']['parent'], 'L1')
        self.assertTrue(all(info['parent'] not in 'BOPQZ' for info in data['subclasses'].values()))
        self.assertEqual([c['code'] for c in package_classes(data, 'specfun')], ['C', 'C7', 'C10', 'C19'])

    def test_filter_matches_all_twenty_official_labels(self):
        parser = GamsFilterParser()
        parser.feed((ROOT / 'site/fpm/index.html').read_text(encoding='utf-8'))
        self.assertEqual(parser.options, {'': 'All classes', **{
            code: f'{code} — {label}' for code, label in gams_data()['classes'].items()}})

    def test_review_page_is_current_and_lists_each_package_once(self):
        text = review_text()
        self.assertEqual((ROOT / REPORT).read_text(encoding='utf-8'), text)
        for name in gams_data()['packages']:
            self.assertEqual(text.count(f'| [{name}](https://github.com/'), 1, name)

    def test_validation_rejects_missing_unknown_and_duplicate_classes(self):
        data = gams_data()
        data['packages'] = {'example': ['D']}
        data['subclass_assignments'] = {'example': ['D2']}
        data['review_notes'] = {}
        data['procedure_mappings'] = []
        invalid = []
        for codes in ([], ['d'], ['D1'], ['T'], ['D', 'D'], [None]):
            broken = copy.deepcopy(data)
            broken['packages']['example'] = codes
            invalid.append(broken)
        for assignments in ({}, {'unknown': ['D']}):
            broken = copy.deepcopy(data)
            broken['packages'] = assignments
            invalid.append(broken)
        broken = copy.deepcopy(data)
        del broken['classes']['Z']
        invalid.append(broken)
        for codes in (['D99'], ['d2'], ['D2', 'D2'], ['G1'], ['D'], [], [None]):
            broken = copy.deepcopy(data)
            broken['subclass_assignments']['example'] = codes
            invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclasses']['D2']['parent'] = 'G'
        invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclasses']['D1a'] = {'label': 'Too deep for this schema', 'parent': 'D'}
        invalid.append(broken)
        broken = copy.deepcopy(data)
        broken['subclass_assignments']['unknown'] = ['D2']
        invalid.append(broken)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_text(json.dumps({'packages': [{'id': 'example'}]}))
            path = root / 'fpm_catalog/gams.json'
            for metadata in invalid:
                with self.subTest(metadata=metadata['packages']):
                    path.write_text(json.dumps(metadata))
                    with self.assertRaises(ValueError):
                        gams_data(root)
            path.write_text(json.dumps(data))
            self.assertEqual(gams_data(root), data)

    def test_g1_procedures_and_verified_drivers(self):
        data = gams_data()
        mappings = g1_procedures(data)
        self.assertEqual(len(mappings), 12)
        self.assertEqual(len({m['package_id'] for m in mappings}), 8)
        self.assertEqual(data['detailed_classes']['G1a']['parent'], 'G1')
        self.assertEqual(data['detailed_classes']['G1b']['parent'], 'G1')
        self.assertIn('G1a', {c['code'] for c in package_classes(data, 'fmin')})
        self.assertIn('G1b', {c['code'] for c in package_classes(data, 'minpack')})
        self.assertIn('G1b', {c['code'] for c in package_classes(data, 'seiscope-optimization')})
        self.assertNotIn('G1a', {c['code'] for c in package_classes(data, 'nonlin')})
        self.assertEqual({d['id'] for d in driver_data() if d['procedure_id'] in {m['id'] for m in mappings}},
                         {'fmin-sine', 'minpack-bard', 'libdogleg-bard', 'nonlin-rosenbrock-nm',
                          'nonlin-rosenbrock-bfgs', 'nlopt-rosenbrock-lbfgs'})
        tree = data['detailed_classes']
        self.assertEqual(tree['G1b1b']['parent'], 'G1b1')
        self.assertEqual(tree['G1b1']['parent'], 'G1b')
        by_id = {m['id']: m for m in mappings}
        self.assertEqual(by_id['fmin-scalar']['gams_codes'], ['G1a1a'])
        self.assertEqual(by_id['nonlin-nelder-mead']['gams_codes'], ['G1b1a'])
        self.assertEqual(by_id['nlopt-lbfgs']['gams_codes'], ['G1b1b'])
        self.assertEqual(by_id['nonlin-bfgs']['gams_codes'], ['G1b1a', 'G1b1b'])
        self.assertEqual((ROOT / PILOT_REPORT).read_text(encoding='utf-8'), g1_review_text())
        examples = json.loads((ROOT / 'site/fpm/examples.json').read_text(encoding='utf-8'))
        for driver in driver_data():
            example = next(e for e in examples if e.get('gams_driver_id') == driver['id'])
            self.assertEqual(example['revision'], driver['revision'])
            self.assertEqual(example['source'], (ROOT / driver['path']).read_text(encoding='utf-8'))

    def test_g1_rejects_stale_procedure_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_bytes((ROOT / 'fpm_catalog.json').read_bytes())
            data = gams_data()
            data['procedure_mappings'][0]['revision'] = '0' * 40
            (root / 'fpm_catalog/gams.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'stale revision'):
                gams_data(root)

    def test_changed_driver_requires_new_verification(self):
        data = gams_data()
        drivers = driver_data(data=data)
        paths = ['fpm_catalog/gams-drivers.json', *{driver_validation_path(d) for d in drivers}]
        paths += list({p for d in drivers for p in [d['path'], *d['license_files']]})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in paths:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / path).read_bytes())
            self.assertEqual(driver_data(root, data), drivers)
            validation_path = root / 'docs/gams-g1-validation.json'
            checks = json.loads(validation_path.read_text(encoding='utf-8'))
            for failure in ('no reuse', 'failed run', 'build-only marker'):
                broken = copy.deepcopy(checks)
                record = broken['drivers'][0]
                run = next(s for s in record['stages'] if s['name'] == 'Run')
                if failure == 'no reuse':
                    record['library_reused'] = False
                elif failure == 'failed run':
                    run['ok'], run['exit_code'] = False, 1
                else:
                    record['stages'][0]['stdout'] += run['stdout']
                    run['stdout'] = ''
                validation_path.write_text(json.dumps(broken), encoding='utf-8')
                with self.subTest(failure=failure), self.assertRaisesRegex(ValueError, 'passing GNU 16 verification'):
                    driver_data(root, data)
            validation_path.write_text(json.dumps(checks), encoding='utf-8')
            quadrature_path = root / 'docs/gams-quadrature-validation.json'
            quadrature = json.loads(quadrature_path.read_text(encoding='utf-8'))
            broken = copy.deepcopy(quadrature)
            broken['drivers'][0]['source_sha256'] = '0'*64
            quadrature_path.write_text(json.dumps(broken), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'quadpack-smooth: current source requires'):
                driver_data(root, data)
            quadrature_path.write_text(json.dumps(quadrature), encoding='utf-8')
            path = root / drivers[0]['path']
            path.write_text(path.read_text(encoding='utf-8') + '\n! Changed source\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'passing GNU 16 verification'):
                driver_data(root, data)

    def test_quadrature_drivers_have_specific_classes_and_separate_evidence(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data) if driver_validation_path(d) == 'docs/gams-quadrature-validation.json']
        self.assertEqual({d['id'] for d in drivers},
                         {'quadpack-smooth', 'quadrature-fortran-smooth', 'quadpack-endpoint-singular'})
        self.assertEqual(data['detailed_classes']['H2a2a1']['parent'], 'H2a2a')
        record = next(r for r in data['procedure_mappings'] if r['id'] == 'quadpack-dqags')
        self.assertEqual(record['gams_codes'], ['H2a2a1'])
        self.assertEqual(record['procedure'], 'dqags')
        self.assertEqual((ROOT / QUADRATURE_REPORT).read_text(encoding='utf-8'), quadrature_review_text())
        for invalid in ['../outside.json', 'docs/../outside.json', 'C:/outside.json']:
            with self.subTest(path=invalid), self.assertRaises(ValueError):
                driver_validation_path({'validation_path': invalid})

    def test_scalar_root_drivers_share_problem_class_and_separate_evidence(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data) if d['gams_code'] == 'F1b']
        self.assertEqual({d['id'] for d in drivers},
                         {'roots-fortran-brent', 'nonlin-roots-brent', 'nonlin-roots-newton'})
        self.assertEqual({driver_validation_path(d) for d in drivers}, {'docs/gams-roots-validation.json'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'nonpolynomial-scalar-roots'})
        self.assertEqual(data['detailed_classes']['F1b']['parent'], 'F1')
        record = next(r for r in data['procedure_mappings'] if r['id'] == 'nonlin-newton-1var')
        self.assertEqual(record['gams_codes'], ['F1b'])
        self.assertEqual(record['procedure'], 'newton_1var_solver%solve')
        self.assertEqual((ROOT / ROOTS_REPORT).read_text(encoding='utf-8'), roots_review_text())

    def test_linear_algebra_drivers_match_reviewed_real_configurations(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-linear-algebra-validation.json']
        self.assertEqual({d['id'] for d in drivers},
                         {'fortran-lapack-dense-solve', 'stdlib-dense-solve',
                          'fortran-lapack-least-squares', 'stdlib-least-squares',
                          'fortran-lapack-symmetric-eigen', 'fortran-lapack-qr-decomposition',
                          'fortran-lapack-svd-decomposition'})
        self.assertEqual({d['gams_code'] for d in drivers if d['problem_id'] == 'real-dense-systems'}, {'D2a1'})
        self.assertEqual({d['gams_code'] for d in drivers if d['problem_id'] == 'real-linear-least-squares'}, {'D9a1'})
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertEqual(records['stdlib-solve']['gams_codes'], ['D2a1'])
        self.assertEqual(records['stdlib-lstsq']['gams_codes'], ['D9a1'])
        self.assertEqual((ROOT / LINEAR_ALGEBRA_REPORT).read_text(encoding='utf-8'), linear_algebra_review_text())

    def test_decomposition_drivers_identify_the_verified_lower_level_apis(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        self.assertEqual(drivers['fortran-lapack-symmetric-eigen']['procedure_id'], 'fortran-lapack-syev')
        self.assertEqual(drivers['fortran-lapack-svd-decomposition']['procedure_id'], 'fortran-lapack-gesvd')
        self.assertEqual(drivers['fortran-lapack-qr-decomposition']['gams_code'], 'D5')
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertNotIn('driver_id', records['fortran-lapack-eigh'])
        self.assertNotIn('driver_id', records['fortran-lapack-svd'])
        for name in ['fortran-lapack-eigh', 'fortran-lapack-svd']:
            self.assertTrue((ROOT/'docs/gams-candidates'/f'{name}.f90').is_file())

    def test_ode_drivers_distinguish_one_step_and_multistep_configurations(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-ode-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'dop853-decay-oscillator': 'I1a1a', 'rklib-decay-oscillator': 'I1a1a',
                          'ddeabm-decay-oscillator': 'I1a1b'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'nonstiff-decay-oscillator'})
        self.assertEqual((ROOT / ODE_REPORT).read_text(encoding='utf-8'), ode_review_text())

    def test_interpolation_drivers_share_data_and_identify_method_configuration(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-interpolation-validation.json']
        self.assertEqual({d['id'] for d in drivers},
                         {'finterp-shape-interpolation', 'pchip-shape-interpolation',
                          'bspline-fortran-shape-interpolation'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'E1a'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'one-dimensional-shape-interpolation'})
        self.assertEqual({d['package_id'] for d in drivers if d['checks']['piecewise_linear_reference_checked']},
                         {'finterp', 'bspline-fortran'})
        self.assertEqual((ROOT / INTERPOLATION_REPORT).read_text(encoding='utf-8'), interpolation_review_text())

    def test_transform_drivers_distinguish_complex_and_cosine_classes(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-transforms-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'fftpack-complex-transform': 'J1a2', 'kissfft-f-complex-transform': 'J1a2',
                          'fftpack-cosine-transform': 'J1a3'})
        self.assertEqual(data['detailed_classes']['J1a3']['parent'], 'J1a')
        self.assertEqual((ROOT / TRANSFORMS_REPORT).read_text(encoding='utf-8'), transforms_review_text())

    def test_constrained_drivers_distinguish_bounds_from_nonlinear_constraints(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-constrained-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'lbfgsb-box-quadratic': 'G2h1a2', 'nlopt-box-quadratic': 'G2h1a2',
                          'slsqp-circle-equality': 'G2h3b1b'})
        self.assertEqual(len({d['problem_id'] for d in drivers}), 2)
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertEqual(records['nlopt-lbfgs']['gams_codes'], ['G1b1b'])
        self.assertEqual(records['nlopt-lbfgs-bounds']['gams_codes'], ['G2h1a2'])
        self.assertEqual((ROOT / CONSTRAINED_REPORT).read_text(encoding='utf-8'), constrained_review_text())

    def test_special_function_drivers_keep_gamma_psi_and_bessel_evidence_separate(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-special-functions-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'fullerton-gamma-values': 'C7a', 'fullerton-digamma-values': 'C7c',
                          'bessels-modified-values': 'C10b1'})
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertNotIn('digamma', records['specfunc-fullerton-fgamma']['procedure'])
        self.assertIn('reciprocal_gamma', records['specfunc-fullerton-fgamma']['procedure'])
        self.assertEqual((ROOT / SPECIAL_FUNCTIONS_REPORT).read_text(encoding='utf-8'), special_functions_review_text())

    def test_statistics_drivers_separate_location_dispersion_and_normalization(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-statistics-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'stdlib-mean-checks': 'L1a1a', 'fstats-mean-checks': 'L1a1a',
                          'stdlib-sample-variance-checks': 'L1a1b', 'fstats-sample-variance-checks': 'L1a1b'})
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertEqual(records['stdlib-var']['gams_codes'], ['L1a1b'])
        self.assertEqual(records['fstats-variance']['author_examples'][0]['path'], 'tests/fstats_statistics_tests.f90')
        self.assertEqual((ROOT / STATISTICS_REPORT).read_text(encoding='utf-8'), statistics_review_text())

    def test_random_drivers_distinguish_uniform_generation_and_seed_support(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-random-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers}, {
            'mt19937-64-reference-sequence': 'L6a21', 'rngff-lcg-reference-sequence': 'L6a21',
            'stdlib-seed-replay': 'L6c'})
        self.assertEqual((ROOT / RANDOM_REPORT).read_text(encoding='utf-8'), random_review_text())
        mt = next(d for d in drivers if d['id'] == 'mt19937-64-reference-sequence')
        self.assertEqual(mt['checks']['bit_reference_positions'][-5:], [312, 313, 624, 625, 1000])
        for path in mt['checks']['reference_files']:
            self.assertTrue((ROOT/path).is_file())

    def test_differentiation_drivers_share_problem_with_explicit_method_settings(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-differentiation-validation.json']
        self.assertEqual({d['package_id'] for d in drivers}, {'numdiff', 'fordiff', 'ad_dnsvm'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'H1'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'exp-sine-derivatives'})
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual(by_package['numdiff']['checks']['requested_absolute_errors'], [1e-8, 1e-8, 1e-6])
        self.assertEqual(by_package['fordiff']['checks']['methods'], ['forward', 'backward', 'central', 'complex-step'])
        self.assertEqual(by_package['ad_dnsvm']['checks']['orders'], [0, 1, 2, 3])
        self.assertEqual((ROOT / DIFFERENTIATION_REPORT).read_text(encoding='utf-8'), differentiation_review_text())

    def test_system_drivers_have_common_root_and_separate_solver_termination(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-systems-validation.json']
        self.assertEqual({d['package_id'] for d in drivers}, {'minpack', 'nonlin', 'nlesolver-fortran'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'F2'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'rosenbrock-square-system'})
        for d in drivers:
            self.assertEqual(d['checks']['starting_points'], [[-1.2, 1], [2, 2]])
            self.assertEqual(d['checks']['expected_root'], [1, 1])
            self.assertEqual(d['checks']['max_residual_infinity_norm'], 1e-8)
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual(by_package['minpack']['checks']['required_status'], 1)
        self.assertIn('analytic', by_package['nonlin']['checks']['configuration'])
        self.assertIn('no Broyden', by_package['nlesolver-fortran']['checks']['configuration'])
        self.assertEqual((ROOT / SYSTEMS_REPORT).read_text(encoding='utf-8'), systems_review_text())

    def test_sparse_drivers_distinguish_indefinite_and_positive_definite_configurations(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-sparse-validation.json']
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual({d['package_id']: d['gams_code'] for d in drivers}, {
            'minres': 'D2b4', 'qdldl-fortran': 'D2b4', 'kiss': 'D2b1b'})
        for d in drivers:
            self.assertEqual(d['checks']['right_hand_sides'], 2)
            self.assertEqual(d['checks']['max_scaled_backward_error'], 1e-11)
        self.assertEqual(by_package['minres']['problem_id'], by_package['qdldl-fortran']['problem_id'])
        self.assertTrue(by_package['qdldl-fortran']['checks']['factors_reused'])
        self.assertEqual(by_package['qdldl-fortran']['checks']['expected_inertia'], [3, 2, 0])
        self.assertEqual(by_package['qdldl-fortran']['checks']['orderings'], ['natural', 'RCM', 'AMD'])
        self.assertEqual(by_package['kiss']['checks']['storage'], 'dense')
        self.assertEqual((ROOT / SPARSE_REPORT).read_text(encoding='utf-8'), sparse_review_text())

    def test_cubature_drivers_distinguish_adaptive_integration_and_rule_generation(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-cubature-validation.json']
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual({d['package_id']: d['gams_code'] for d in drivers}, {
            'dcuhre': 'H2b1a1', 'gaussjacobiquad': 'H2c', 'fortran_cubatures': 'H2c'})
        self.assertEqual(by_package['dcuhre']['checks']['dimensions'], [2, 3])
        self.assertEqual(by_package['dcuhre']['checks']['required_status'], 0)
        self.assertEqual(by_package['gaussjacobiquad']['checks']['alpha_beta'], [[0, 0], [1, 0]])
        self.assertEqual(by_package['gaussjacobiquad']['checks']['monomial_degrees'], list(range(8)))
        self.assertEqual(by_package['fortran_cubatures']['checks']['moments_per_element'], [21, 35, 36])
        self.assertEqual((ROOT / CUBATURE_REPORT).read_text(encoding='utf-8'), cubature_review_text())

    def test_surface_drivers_share_grid_and_distinguish_bilinear_from_bicubic(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-surfaces-validation.json']
        self.assertEqual({d['package_id'] for d in drivers}, {'finterp', 'bspline-fortran'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'E2a'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'nonuniform-bilinear-surface'})
        self.assertEqual(drivers[0]['checks']['grid_x'], drivers[1]['checks']['grid_x'])
        self.assertEqual(drivers[0]['checks']['grid_y'], drivers[1]['checks']['grid_y'])
        for d in drivers:
            self.assertEqual(d['checks']['node_checks_per_case'], 30)
            self.assertEqual(d['checks']['cell_samples_per_case'], 500)
            self.assertFalse(d['checks']['extrapolation_checked'])
        spline = next(d for d in drivers if d['package_id']=='bspline-fortran')
        self.assertEqual(spline['checks']['polynomial_orders'], [4, 4])
        self.assertEqual(spline['checks']['partial_derivatives'], [[0, 0], [1, 0], [0, 1], [1, 1]])
        self.assertEqual((ROOT / SURFACES_REPORT).read_text(encoding='utf-8'), surfaces_review_text())

    def test_stiff_drivers_share_exact_problem_and_preserve_solver_configuration(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-stiff-validation.json']
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual(set(by_package), {'dvode', 'odepack', 'stiff3'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'I1a2'})
        self.assertEqual({d['problem_id'] for d in drivers}, {'autonomous-stiff-two-scale-system'})
        for d in drivers:
            self.assertEqual(d['checks']['initial_state'], [2, 1])
            self.assertEqual(d['checks']['output_times'], [0.001, 0.01, 0.1, 1])
            self.assertEqual(d['checks']['eigenvalues'], [-1000, -1])
        self.assertEqual(by_package['dvode']['checks']['method_flag'], 22)
        self.assertTrue(by_package['odepack']['checks']['bdf_indicator_required'])
        self.assertTrue(by_package['stiff3']['checks']['analytic_jacobian'])
        self.assertEqual((ROOT / STIFF_REPORT).read_text(encoding='utf-8'), stiff_review_text())

    def test_polynomial_drivers_keep_algorithm_evidence_and_complex_scope_separate(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data) if driver_validation_path(d) == 'docs/gams-polynomial-validation.json']
        by_algorithm = {d['checks']['algorithm']: d for d in drivers}
        self.assertEqual(set(by_algorithm), {'polyroots', 'rpoly', 'cpolyroots'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'F1a'})
        self.assertEqual(len({d['procedure_id'] for d in drivers}), 3)
        ledger = numerical_review(data=data)['packages']['polyroots-fortran']
        self.assertTrue({d['procedure_id'] for d in drivers}.issubset(ledger['procedure_ids']))
        for d in drivers:
            self.assertEqual(d['checks']['coefficient_scales'], [1, 1e80, 1e-80])
            self.assertTrue(d['checks']['distinct_roots_only'])
        self.assertFalse(by_algorithm['rpoly']['checks']['complex_coefficients_checked'])
        self.assertTrue(by_algorithm['cpolyroots']['checks']['complex_coefficients_checked'])
        self.assertEqual((ROOT / POLYNOMIAL_REPORT).read_text(encoding='utf-8'), polynomial_review_text())

    def test_convolution_drivers_keep_output_conventions_and_precision_explicit(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-convolution-validation.json']
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual(set(by_package), {'spectrum', 'fastconv'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'J2'})
        self.assertEqual(by_package['spectrum']['checks']['kernel_lengths'], by_package['fastconv']['checks']['kernel_lengths'])
        self.assertEqual(by_package['spectrum']['checks']['output_modes'], ['full', 'central'])
        self.assertEqual(by_package['fastconv']['checks']['output_modes'], ['valid'])
        self.assertEqual(by_package['spectrum']['checks']['native_precision'], 'real64')
        self.assertEqual(by_package['fastconv']['checks']['native_precision'], 'real32')
        self.assertFalse(by_package['fastconv']['checks']['preserve_shape'])
        self.assertEqual((ROOT / CONVOLUTION_REPORT).read_text(encoding='utf-8'), convolution_review_text())

    def test_regression_drivers_preserve_distinct_error_models_and_covariance_convention(self):
        drivers = [d for d in driver_data() if driver_validation_path(d) == 'docs/gams-regression-validation.json']
        by_package = {d['package_id']: d for d in drivers}
        self.assertEqual(set(by_package), {'odrpack95', 'lib_statistics'})
        self.assertEqual({d['gams_code'] for d in drivers}, {'L8'})
        self.assertNotEqual(by_package['odrpack95']['problem_id'], by_package['lib_statistics']['problem_id'])
        self.assertTrue(by_package['odrpack95']['checks']['unit_x_y_weights'])
        self.assertEqual(by_package['odrpack95']['checks']['job'], 20)
        logistic = by_package['lib_statistics']
        self.assertEqual(logistic['reuse'], 'original')
        self.assertIsNone(logistic['author_example'])
        self.assertEqual(logistic['checks']['residual_degrees_of_freedom'], 4)
        self.assertEqual(logistic['checks']['dispersion'], 'max(1,Pearson chi-square/ndf)')
        self.assertEqual((ROOT / REGRESSION_REPORT).read_text(encoding='utf-8'), regression_review_text())

    def test_matrix_equation_drivers_preserve_equations_scaling_and_source_evidence(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data) if driver_validation_path(d) == 'docs/gams-matrix-equations-validation.json']
        self.assertEqual({d['gams_code'] for d in drivers}, {'D8'})
        self.assertEqual({d['package_id'] for d in drivers}, {'slicot'})
        self.assertEqual(len({d['procedure_id'] for d in drivers}), 3)
        ledger = numerical_review(data=data)['packages']['slicot']
        self.assertTrue({d['procedure_id'] for d in drivers}.issubset(ledger['procedure_ids']))
        by_id = {d['id']: d for d in drivers}
        lyapunov = by_id['slicot-lyapunov-known-matrix']['checks']
        self.assertEqual(lyapunov['equations'], ['continuous', 'discrete'])
        self.assertEqual(lyapunov['factor_modes'], ['N', 'F'])
        self.assertTrue(lyapunov['returned_scale_honored'])
        self.assertEqual(by_id['slicot-continuous-sylvester']['checks']['equation'], 'A*X+X*B=C')
        self.assertEqual(by_id['slicot-discrete-sylvester']['checks']['equation'], 'X+A*X*B=C')
        self.assertEqual((ROOT / MATRIX_EQUATIONS_REPORT).read_text(encoding='utf-8'), matrix_equations_review_text())

    def test_stdlib_sorting_driver_has_checked_n6_source(self):
        driver = next(d for d in driver_data() if d['id']=='stdlib-sorting-reference')
        self.assertEqual(driver['gams_code'], 'N6')
        self.assertEqual(driver['procedure_id'], 'stdlib-sort')
        self.assertTrue(driver['checks']['ascending_and_descending'])
        self.assertEqual((ROOT / SORTING_REPORT).read_text(encoding='utf-8'), sorting_review_text())

    def test_coverage_separates_source_review_from_class_specific_driver_evidence(self):
        data = gams_data()
        coverage = coverage_data(data=data)
        self.assertEqual(coverage['procedure_count'], len(data['procedure_mappings']))
        self.assertEqual(coverage['driver_count'], len(driver_data(data=data)))
        by_class = {r['code']: r for r in coverage['procedure_classes']}
        self.assertIn('nonlin-bfgs', by_class['G1b1a']['procedure_ids'])
        self.assertNotIn('nonlin-bfgs', by_class['G1b1a']['checked_procedure_ids'])
        self.assertIn('nonlin-bfgs', by_class['G1b1b']['checked_procedure_ids'])
        self.assertEqual(len(by_class['J1a2']['driver_ids']), 2)
        self.assertEqual(len(by_class['J1a3']['driver_ids']), 1)
        self.assertTrue(any(not r['driver_ids'] for r in coverage['procedure_classes']))
        self.assertEqual({r['code'] for r in coverage['top_level'] if r['driver_ids']}, set('CDEFGHIJLN'))
        self.assertEqual((ROOT / COVERAGE_REPORT).read_text(encoding='utf-8'), coverage_review_text())

    def test_numerical_review_covers_catalog_scope_and_preserves_evidence(self):
        data = gams_data()
        review = numerical_review(data=data)
        expected = {name for name, codes in data['packages'].items() if set(codes) & set('ABCDEFGHIJKLMP')}
        self.assertEqual(set(review['packages']), expected)
        mapped = {p['package_id'] for p in data['procedure_mappings']}
        self.assertEqual({name for name, entry in review['packages'].items()
                          if entry['status'] == 'procedure-reviewed'}, expected & mapped)
        self.assertEqual(review['packages']['kinds']['status'], 'support-only')
        self.assertTrue(review['packages']['kinds']['evidence'])
        self.assertEqual((ROOT / NUMERICAL_REPORT).read_text(encoding='utf-8'), numerical_review_text())
        by_id = {p['id']: p for p in data['procedure_mappings']}
        for entry in review['packages'].values():
            for identity in entry['procedure_ids']:
                record = by_id[identity]
                self.assertEqual(entry['revision'], record['revision'])
                self.assertTrue(record['evidence'])
        for name, code in [('dop853', 'I1a1a'), ('dvode', 'I1a2'), ('lbfgsb', 'G2h1a2'),
                           ('gaussjacobiquad', 'H2c'), ('dcuhre', 'H2b1a1'), ('specfun', 'C19')]:
            self.assertIn(code, {c['code'] for c in package_classes(data, name)})
        self.assertEqual(data['detailed_classes']['L6a21']['parent'], 'L6a')

    def test_detailed_class_rejects_sibling_as_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'fpm_catalog').mkdir()
            (root / 'fpm_catalog.json').write_bytes((ROOT / 'fpm_catalog.json').read_bytes())
            data = gams_data()
            data['detailed_classes']['L10a']['parent'] = 'L1'
            (root / 'fpm_catalog/gams.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'invalid detailed GAMS class or parent'):
                gams_data(root)


if __name__ == '__main__':
    unittest.main()
