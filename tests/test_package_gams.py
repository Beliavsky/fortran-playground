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
                          number_theory_review_text, NUMBER_THEORY_REPORT,
                          arithmetic_review_text, ARITHMETIC_REPORT,
                          applied_methods_review_text, APPLIED_METHODS_REPORT,
                          boundary_review_text, BOUNDARY_REPORT,
                          resampling_markov_review_text, RESAMPLING_MARKOV_REPORT,
                          fourier_geometry_review_text, FOURIER_GEOMETRY_REPORT,
                          sparse_integral_review_text, SPARSE_INTEGRAL_REPORT,
                          spatial_nufft_review_text, SPATIAL_NUFFT_REPORT,
                          pde_review_text, PDE_REPORT,
                          data_kinds_review_text, DATA_KINDS_REPORT,
                          products_status_review_text, PRODUCTS_STATUS_REPORT,
                          kriging_network_review_text, KRIGING_NETWORK_REPORT,
                          lookup_fastmath_review_text, LOOKUP_FASTMATH_REPORT,
                          circuits_beta_review_text, CIRCUITS_BETA_REPORT,
                          inverse_tvd_review_text, INVERSE_TVD_REPORT,
                          roots_splines_quadrature_review_text, ROOTS_SPLINES_QUADRATURE_REPORT,
                          io_bounds_review_text, IO_BOUNDS_REPORT,
                          optimization_spacing_review_text, OPTIMIZATION_SPACING_REPORT,
                          raster_distributions_review_text, RASTER_DISTRIBUTIONS_REPORT,
                          quantities_spherical_review_text, QUANTITIES_SPHERICAL_REPORT,
                          delay_embedding_review_text, DELAY_EMBEDDING_REPORT,
                          matrix_roots_box_review_text, MATRIX_ROOTS_BOX_REPORT,
                          dispersion_review_text, DISPERSION_REPORT,
                          rules_differences_review_text, RULES_DIFFERENCES_REPORT,
                          qr_autodiff_review_text, QR_AUTODIFF_REPORT,
                          dense_spectra_review_text, DENSE_SPECTRA_REPORT,
                          least_interpolation_review_text, LEAST_INTERPOLATION_REPORT,
                          rkf_qags_review_text, RKF_QAGS_REPORT,
                          jacobian_roots_review_text, JACOBIAN_ROOTS_REPORT,
                          higher_ad_review_text, HIGHER_AD_REPORT,
                          moments_nufft2d_review_text, MOMENTS_NUFFT2D_REPORT,
                            iterative_ls_review_text, ITERATIVE_LS_REPORT,
                            spectral_wrappers_review_text, SPECTRAL_WRAPPERS_REPORT,
                            regrid_rk45_review_text, REGRID_RK45_REPORT,
                            fitpack_polynomials_review_text, FITPACK_POLYNOMIALS_REPORT,
                            diagonal_response_review_text, DIAGONAL_RESPONSE_REPORT,
                            ranking_magic_review_text, RANKING_MAGIC_REPORT,
                            geodesy_forlab_review_text, GEODESY_FORLAB_REPORT,
                          coverage_data, coverage_review_text, COVERAGE_REPORT,
                          class_evidence, class_tree, mapping_evidence_text, EVIDENCE_REPORT)


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
                          'nonlin-rosenbrock-bfgs', 'nlopt-rosenbrock-lbfgs', 'fortimize-nelder-reference',
                          'minpack-lmder-reference'})
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
        drivers = [d for d in driver_data(data=data) if d['gams_code'] == 'F1b'
                   and driver_validation_path(d) == 'docs/gams-roots-validation.json']
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
                          'fortran-lapack-svd-decomposition', 'blas-gemm-reference',
                          'fsparse-matvec-reference', 'forinv-pseudoinverse-reference',
                          'arpack-poisson-eigenpairs', 'linalg-poisson-eigenpairs',
                          'fsparse-storage-reference'})
        self.assertEqual({d['gams_code'] for d in drivers if d['problem_id'] == 'real-dense-systems'}, {'D2a1'})
        self.assertEqual({d['gams_code'] for d in drivers if d['problem_id'] == 'real-linear-least-squares'}, {'D9a1'})
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertEqual(records['stdlib-solve']['gams_codes'], ['D2a1'])
        self.assertEqual(records['stdlib-lstsq']['gams_codes'], ['D9a1'])
        self.assertEqual((ROOT / LINEAR_ALGEBRA_REPORT).read_text(encoding='utf-8'), linear_algebra_review_text())

    def test_product_and_pseudoinverse_drivers_have_independent_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        gemm = drivers['blas-gemm-reference']
        sparse = drivers['fsparse-matvec-reference']
        pinv = drivers['forinv-pseudoinverse-reference']
        self.assertEqual((gemm['gams_code'],sparse['gams_code'],pinv['gams_code']), ('D1b6','D1b4','D9c'))
        self.assertEqual(gemm['checks']['gemm_calls'], 12)
        self.assertEqual(gemm['checks']['transpose_combinations'], ['NN','NT','TN','TT'])
        self.assertEqual(sparse['checks']['matvec_calls'], 24)
        self.assertTrue(sparse['checks']['repeated_accumulation'])
        self.assertEqual(pinv['checks']['matrix_cases'], 5)
        self.assertEqual(pinv['checks']['moore_penrose_identities'], 4)
        self.assertTrue(pinv['checks']['preserves_original_matrix'])
        from xpackage_gams import class_tree, procedure_records
        assessment = class_evidence(class_tree(data),'D1b9',procedure_records(data,'fsparse'),[sparse])
        self.assertEqual(assessment['status'], 'source-supported')
        assessment = class_evidence(class_tree(data),'D1b9',procedure_records(data,'fsparse'),list(drivers.values()))
        self.assertEqual(assessment['status'], 'verified')

    def test_storage_fourier_and_geometry_drivers_record_reference_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        storage = drivers['fsparse-storage-reference']
        fourier = drivers['spectrum-real-dft-reference']
        geometry = drivers['geodesic-reference']
        self.assertEqual((storage['gams_code'],fourier['gams_code'],geometry['gams_code']), ('D1b9','J1a1','P'))
        self.assertEqual(storage['checks']['matrix_cases'], 5)
        self.assertTrue(storage['checks']['all_zero_matrix_checked'])
        self.assertFalse(storage['checks']['subnormal_threshold_behavior_verified'])
        self.assertEqual(fourier['checks']['forward_transforms'], 42)
        self.assertFalse(fourier['checks']['inverse_transform_verified'])
        self.assertTrue(geometry['checks']['direct_uses_independent_inputs'])
        self.assertEqual(geometry['checks']['simpson_panel_counts'], [2048,4096])
        records = {r['id']: r for r in data['procedure_mappings']}
        for driver in [storage,fourier,geometry]:
            self.assertEqual(records[driver['procedure_id']]['driver_id'], driver['id'])
            evidence = class_evidence(class_tree(data),driver['gams_code'],
                                      [records[driver['procedure_id']]],[driver])
            self.assertEqual(evidence['status'], 'verified')
        text = fourier_geometry_review_text()
        self.assertEqual((ROOT/FOURIER_GEOMETRY_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('not a formal quadrature error bound', text)
        self.assertIn('not certified by this driver', text)

    def test_sparse_lu_and_spline_integral_checks_retain_failed_pca_probe(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        sparse = drivers['y12m-sparse-reference']
        integral = drivers['fitpack-spline-integral']
        self.assertEqual((sparse['gams_code'],integral['gams_code']), ('D2a4','H2a2b2'))
        self.assertEqual(sparse['checks']['right_hand_sides_per_factorization'], 4)
        self.assertTrue(sparse['checks']['row_permutation_checked'])
        self.assertEqual(integral['checks']['integral_calls'], 36)
        self.assertTrue(integral['checks']['reversed_and_zero_intervals_checked'])
        self.assertNotIn('forpca-covariance-variances', drivers)
        record = next(r for r in data['procedure_mappings'] if r['id'] == 'forpca-pca')
        self.assertNotIn('driver_id', record)
        for code in ['D6','L13b']:
            self.assertEqual(class_evidence(class_tree(data),code,[record],list(drivers.values()))['status'],
                             'source-supported')
        import hashlib
        failure = json.loads((ROOT/'docs/gams-candidates/forpca/covariance-variances-result.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/failure['source_path']).read_text().encode()).hexdigest(),
                         failure['source_sha256'])
        self.assertEqual(failure['revision'], record['revision'])
        self.assertFalse(failure['result']['ok'])
        self.assertTrue(failure['result']['cache']['library_reused'])
        run = next(s for s in failure['result']['stages'] if s['name'] == 'Run')
        self.assertIn('100.000000', run['stdout'])
        self.assertIn('12.250000', run['stdout'])
        self.assertIn('known covariance eigenvalues', run['stderr'])
        text = sparse_integral_review_text()
        self.assertEqual((ROOT/SPARSE_INTEGRAL_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('not an upstream-confirmed fix', text)

    def test_spatial_and_nufft_drivers_keep_independent_reference_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        neighbors = drivers['kdtree-neighbor-reference']
        interpolation = drivers['delaunay-affine-reference']
        transform = drivers['nufft1d-sum-reference']
        self.assertEqual((neighbors['gams_code'],interpolation['gams_code'],transform['gams_code']),
                         ('N5','E2','J1'))
        self.assertEqual(neighbors['checks']['search_calls'], 36)
        self.assertTrue(neighbors['checks']['complete_radius_sets_checked'])
        self.assertEqual(neighbors['checks']['squared_radii'], [0,0.125,4])
        self.assertEqual(interpolation['checks']['dimensions'], 3)
        self.assertFalse(interpolation['checks']['empty_circumsphere_property_verified'])
        self.assertEqual(transform['checks']['transform_calls'], 24)
        self.assertEqual(transform['checks']['mode_counts'], [15,16,31,32])
        self.assertEqual(transform['checks']['normalization'], '1/source_count')
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [neighbors,interpolation,transform]:
            self.assertEqual(records[d['procedure_id']]['driver_id'], d['id'])
            result = class_evidence(class_tree(data),d['gams_code'],[records[d['procedure_id']]],[d])
            self.assertEqual(result['status'], 'verified')
        result = class_evidence(class_tree(data),'P',[records['spatial-neighbors']],[neighbors])
        self.assertEqual(result['status'], 'source-supported')
        text = spatial_nufft_review_text()
        self.assertEqual((ROOT/SPATIAL_NUFFT_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('564 checked complex coefficients', text)
        self.assertIn('not exact nonlinear-function recovery', text)

    def test_pde_drivers_separate_discrete_and_continuous_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        helmholtz = drivers['fishpack-helmholtz-reference']
        periodic = drivers['poisfft-periodic-reference']
        self.assertEqual((helmholtz['gams_code'],periodic['gams_code']), ('I2','I2'))
        self.assertEqual(helmholtz['checks']['solve_calls'], 6)
        self.assertEqual(helmholtz['checks']['helmholtz_shifts'], [0,-0.75])
        self.assertTrue(helmholtz['checks']['nonzero_dirichlet_boundaries_checked'])
        self.assertEqual(periodic['checks']['solve_calls'], 12)
        self.assertTrue(periodic['checks']['plans_reused_for_zero_forcing'])
        self.assertTrue(periodic['checks']['zero_mean_gauge_checked'])
        self.assertEqual(periodic['checks']['approximations'], ['spectral','second-order finite difference'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [helmholtz,periodic]:
            self.assertEqual(records[d['procedure_id']]['driver_id'], d['id'])
            result = class_evidence(class_tree(data),'I2',[records[d['procedure_id']]],[d])
            self.assertEqual(result['status'], 'verified')
        result = class_evidence(class_tree(data),'I2',[records['heatflow-evolution']],list(drivers.values()))
        self.assertEqual(result['status'], 'source-supported')
        text = pde_review_text()
        self.assertEqual((ROOT/PDE_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('exact discrete solution', text)
        self.assertIn('includes spatial discretization error', text)

    def test_parsing_storage_and_machine_kind_drivers_have_scoped_evidence(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        parsing = drivers['fast-float-parsing-reference']
        fifo = drivers['fifo-storage-reference']
        machine = drivers['penf-machine-reference']
        self.assertEqual((parsing['gams_code'],fifo['gams_code'],machine['gams_code']), ('N3','N4','R1'))
        self.assertEqual(parsing['checks']['parser_calls'], 154)
        self.assertEqual(parsing['checks']['invalid_or_overflow_cases'], 6)
        self.assertFalse(parsing['checks']['all_inputs_correctly_rounded_claimed'])
        self.assertEqual(fifo['checks']['primary_records']+fifo['checks']['secondary_records'], 160)
        self.assertTrue(fifo['checks']['copy_after_source_overwrite_checked'])
        self.assertTrue(machine['checks']['runtime_roundoff_experiment_checked'])
        self.assertFalse(machine['checks']['quadruple_precision_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [parsing,fifo,machine]:
            self.assertEqual(records[d['procedure_id']]['driver_id'], d['id'])
            result = class_evidence(class_tree(data),d['gams_code'],[records[d['procedure_id']]],[d])
            self.assertEqual(result['status'], 'verified')
        result = class_evidence(class_tree(data),'N3',[records['numerical-portability']],list(drivers.values()))
        self.assertEqual(result['status'], 'source-supported')
        text = data_kinds_review_text()
        self.assertEqual((ROOT/DATA_KINDS_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('least positive **normal** values', text)
        self.assertIn('not subnormal minima', text)

    def test_products_assertions_and_error_status_drivers_have_exact_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        products = drivers['fordot-exact-reference']
        assertions = drivers['fassert-captured-reference']
        errors = drivers['errstat-recovery-reference']
        self.assertEqual((products['gams_code'],assertions['gams_code'],errors['gams_code']), ('D1','S3','R3'))
        self.assertEqual(products['checks']['dot_product_calls'], 231)
        self.assertTrue(products['checks']['exact_equality_required'])
        self.assertFalse(products['checks']['coarray_mode_verified'])
        self.assertEqual(assertions['checks']['captured_comparisons'], 13)
        self.assertTrue(assertions['checks']['exact_tolerance_boundaries_checked'])
        self.assertEqual(errors['checks']['arithmetic_driver_calls'], 9)
        self.assertTrue(errors['checks']['copied_status_independence_checked'])
        self.assertFalse(errors['checks']['arithmetic_function_supplied_by_package'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [products,assertions,errors]:
            self.assertEqual(records[d['procedure_id']]['driver_id'], d['id'])
            result = class_evidence(class_tree(data),d['gams_code'],[records[d['procedure_id']]],[d])
            self.assertEqual(result['status'], 'verified')
        result = class_evidence(class_tree(data),'R2',[records['assert-values']],list(drivers.values()))
        self.assertEqual(result['status'], 'source-supported')
        text = products_status_review_text()
        self.assertEqual((ROOT/PRODUCTS_STATUS_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('exact equality', text)
        self.assertIn('error codes belong to the driver', text)

    def test_kriging_and_network_drivers_record_independent_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        kriging = drivers['gslib-kriging-reference']
        network = drivers['fkb-network-reference']
        self.assertEqual((kriging['gams_code'], network['gams_code']), ('L13', 'K'))
        self.assertEqual(kriging['checks']['linear_solves'], 21)
        self.assertEqual(kriging['checks']['covariance_models'], ['spherical', 'exponential', 'Gaussian'])
        self.assertEqual(kriging['checks']['covariance_precision'], 'real32')
        self.assertEqual(kriging['checks']['linear_solve_precision'], 'real64')
        self.assertEqual(network['checks']['layer_widths'], [2,3,2])
        self.assertEqual(network['checks']['input_cases'], 25)
        self.assertEqual(network['checks']['prediction_calls'], 50)
        self.assertTrue(network['checks']['save_reload_checked'])
        self.assertFalse(network['checks']['training_or_fit_accuracy_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [kriging, network]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data), d['gams_code'], [record], [d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data), 'E2', [records['gslib-api']],
                                        list(drivers.values()))['status'], 'source-supported')
        text = kriging_network_review_text()
        self.assertEqual((ROOT/KRIGING_NETWORK_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('**real32**', text)
        self.assertIn('**real64**', text)
        self.assertIn('not training or approximation quality', text)

    def test_lookup_and_fastmath_drivers_record_scoped_accuracy_checks(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        lookup = drivers['lookup-services-reference']
        exponential = drivers['fastmath-exp-log-reference']
        rsqrt = drivers['fastmath-rsqrt-reference']
        self.assertEqual((lookup['gams_code'],exponential['gams_code'],rsqrt['gams_code']), ('E3','C4b','C2'))
        self.assertEqual(lookup['checks']['lookup_queries'], 98)
        self.assertEqual(lookup['checks']['lookup_routes'], 4)
        self.assertTrue(lookup['checks']['copy_independence_checked'])
        self.assertFalse(lookup['checks']['nonlinear_grid_spacing_verified'])
        self.assertEqual(exponential['checks']['grid_points'], 641)
        self.assertEqual(exponential['checks']['argument_range'], [-80,80])
        self.assertEqual(exponential['checks']['max_log_absolute_error'], 1e-3)
        self.assertEqual(rsqrt['checks']['exact_dyadic_squares'], 168)
        self.assertEqual(rsqrt['checks']['max_normalized_residual'], 4e-3)
        self.assertFalse(rsqrt['checks']['performance_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [lookup,exponential,rsqrt]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'E1a',[records['lookup-interpolation']],
                                       list(drivers.values()))['status'], 'source-supported')
        self.assertIn('src/fast_log.f90', {e['path'] for e in records['fastmath-fexp']['evidence']})
        text = lookup_fastmath_review_text()
        self.assertEqual((ROOT/LOOKUP_FASTMATH_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('two-stage reference', text)
        self.assertIn('without evaluating sqrt', text)
        self.assertIn('not establish a universal error bound', text)

    def test_circuit_elementary_and_beta_drivers_have_independent_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        circuit = drivers['ecx-rlc-reference']
        elementary = drivers['rpn-sinc-sech-reference']
        beta = drivers['rpn-beta-reference']
        self.assertEqual((circuit['gams_code'],elementary['gams_code'],beta['gams_code']), ('A4','C4','C7'))
        self.assertEqual(circuit['checks']['frequency_cases'], 216)
        self.assertEqual(circuit['checks']['element_impedances'], 648)
        self.assertTrue(circuit['checks']['circuit_composition_supplied_by_driver'])
        self.assertEqual(elementary['checks']['real_arguments'], 133)
        self.assertEqual(elementary['checks']['sinc_series_terms'], 64)
        self.assertFalse(elementary['checks']['cube_root_verified'])
        self.assertEqual(beta['checks']['positive_argument_pairs'], 128)
        self.assertEqual(beta['checks']['beta_evaluations'], 512)
        self.assertTrue(beta['checks']['factorial_reference_checked'])
        self.assertFalse(beta['checks']['bessel_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [circuit,elementary,beta]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        for code,rid in [('C2','rpn-elementary'),('C10','rpn-special')]:
            self.assertEqual(class_evidence(class_tree(data),code,[records[rid]],
                                           list(drivers.values()))['status'], 'source-supported')
        text = circuits_beta_review_text()
        self.assertEqual((ROOT/CIRCUITS_BETA_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('composition is supplied by the driver', text)
        self.assertIn('references do not call gamma or beta', text)
        self.assertIn('not matching sinc/sech drivers', text)

    def test_inverse_and_tvd_drivers_record_closed_form_and_convergence_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        inverse = drivers['linalg-inverse-factor-reference']
        ode = drivers['hrweno-tvd-ode-reference']
        self.assertEqual((inverse['gams_code'],ode['gams_code']), ('D2','I1'))
        self.assertEqual(inverse['checks']['nonsingular_matrices'], 132)
        self.assertEqual(inverse['checks']['dimensions'], [1,2,3,4,5,8])
        self.assertTrue(inverse['checks']['row_permutations_checked'])
        self.assertEqual(inverse['checks']['singular_rejections'], 2)
        self.assertFalse(inverse['checks']['reference_uses_package_linear_algebra'])
        self.assertEqual(ode['checks']['integration_runs'], 12)
        self.assertEqual(ode['checks']['orders'], [1,2,3])
        self.assertEqual(ode['checks']['steps'], [8,16,32,64])
        self.assertEqual(ode['checks']['itask'], 2)
        self.assertTrue(ode['checks']['nonautonomous_stage_times_checked'])
        self.assertFalse(ode['checks']['ordinary_interval_mode_verified'])
        self.assertFalse(ode['checks']['spatial_weno_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [inverse,ode]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'I2',[records['hrweno-reconstruction']],
                                       list(drivers.values()))['status'], 'source-supported')
        text = inverse_tvd_review_text()
        self.assertEqual((ROOT/INVERSE_TVD_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('No package linear algebra', text)
        self.assertIn('ordinary interval mode; that mode is not', text)
        self.assertIn('stage-time usage', text)

    def test_quadratic_spline_and_sampled_adaptive_drivers_record_exact_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        roots = drivers['fortranlib-quadratic-reference']
        spline = drivers['fortran-utils-spline-reference']
        quad = drivers['scifortran-quadrature-reference']
        self.assertEqual((roots['gams_code'],spline['gams_code'],quad['gams_code']), ('F1','E1','H2'))
        self.assertEqual(roots['checks']['quadratic_calls'], 84)
        self.assertFalse(roots['checks']['repeated_roots_verified'])
        self.assertEqual(spline['checks']['independent_component_references'], 3120)
        self.assertEqual(spline['checks']['spline_calls'], 64)
        self.assertTrue(spline['checks']['nonuniform_grid_checked'])
        self.assertTrue(spline['checks']['reversed_queries_checked'])
        self.assertEqual(quad['checks']['sampled_rule_calls'], 240)
        self.assertEqual(quad['checks']['adaptive_calls'], 178)
        self.assertEqual(quad['checks']['gauss_kronrod_keys'], [1,2,3,4,5,6])
        self.assertEqual(quad['checks']['endpoint_singular_integrals'], 2)
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [roots,spline,quad]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        for code,rid in [('E1','fortranlib-numerics'),('H2','fortranlib-numerics'),('N6','fortran-utils-splines')]:
            self.assertEqual(class_evidence(class_tree(data),code,[records[rid]],
                                           list(drivers.values()))['status'], 'source-supported')
        text = roots_splines_quadrature_review_text()
        self.assertEqual((ROOT/ROOTS_SPLINES_QUADRATURE_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('trapezoidal discretization error', text)
        self.assertIn('consistent-cubic endpoint conditions', text)
        self.assertIn('not claim a general iterative root finder', text)

    def test_numeric_io_and_bounds_drivers_record_independent_data_and_comparisons(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        io = drivers['io-numeric-file-reference']
        bounds = drivers['error-bounds-reference']
        self.assertEqual((io['gams_code'],bounds['gams_code']), ('N1','R2'))
        self.assertEqual(io['checks']['matrix_files'], 8)
        self.assertEqual(io['checks']['matrix_shapes'], [[1,1],[2,3],[4,2],[3,4]])
        self.assertTrue(io['checks']['independent_native_reader_checked'])
        self.assertTrue(io['checks']['independent_native_writer_checked'])
        self.assertTrue(io['checks']['missing_file_diagnostic_checked'])
        self.assertEqual(bounds['checks']['criteria_calls'], 102)
        self.assertEqual(bounds['checks']['expected_rejections'], 30)
        self.assertTrue(bounds['checks']['nearest_inside_outside_values_checked'])
        self.assertTrue(bounds['checks']['equal_bounds_checked'])
        self.assertFalse(bounds['checks']['critical_error_triggering_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [io,bounds]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'R3',[records['error-validation']],
                                       list(drivers.values()))['status'], 'source-supported')
        text = io_bounds_review_text()
        self.assertEqual((ROOT/IO_BOUNDS_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('compensating reader/writer layout errors', text)
        self.assertIn('immediately adjacent', text)
        self.assertIn('No errors are triggered', text)

    def test_nelder_and_spacing_drivers_record_known_minima_and_precision(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        optimizer = drivers['fortimize-nelder-reference']
        spacing = drivers['pointsets-spacing-reference']
        self.assertEqual((optimizer['gams_code'],spacing['gams_code']), ('G1b','R'))
        self.assertEqual(optimizer['checks']['optimization_runs'], 12)
        self.assertEqual(optimizer['checks']['quadratic_dimensions'], [2,3,5])
        self.assertEqual(optimizer['checks']['function_evaluation_limit'], 50000)
        self.assertFalse(optimizer['checks']['derivative_requests_allowed'])
        self.assertFalse(optimizer['checks']['parallel_use_verified'])
        self.assertEqual(spacing['checks']['arithmetic_grids'], 20)
        self.assertEqual(spacing['checks']['geometric_grids'], 80)
        self.assertEqual(spacing['checks']['unchanged_array_guard_calls'], 7)
        self.assertEqual(spacing['checks']['max_normalized_error_multiple_of_epsilon'], 32)
        self.assertFalse(spacing['checks']['random_generators_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [optimizer,spacing]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'G1b',[records['fortimize-gradient-descent']],
                                       list(drivers.values()))['status'], 'source-supported')
        text = optimization_spacing_review_text()
        self.assertEqual((ROOT/OPTIMIZATION_SPACING_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('wp=real32', text)
        self.assertIn('not a success flag', text)
        self.assertIn('ratio 1 does not fill a uniform grid', text)

    def test_raster_and_distribution_drivers_separate_exact_pixels_from_moment_smoke_checks(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        graphics = drivers['sdl-raster-reference']
        distributions = drivers['rng-distributions-reference']
        self.assertEqual((graphics['gams_code'],distributions['gams_code']), ('Q','L6'))
        self.assertEqual(graphics['checks']['exact_pixel_checks'], 11050)
        self.assertEqual(graphics['checks']['image_dimensions'], [85,65])
        self.assertTrue(graphics['checks']['png_round_trip_pixels_checked'])
        self.assertFalse(graphics['checks']['interactive_rendering_verified'])
        self.assertEqual(distributions['checks']['normal_samples'], 60000)
        self.assertEqual(distributions['checks']['poisson_rates'], [.5,2,8])
        self.assertTrue(distributions['checks']['fresh_object_exact_replay_checked'])
        self.assertFalse(distributions['checks']['randomness_quality_certified'])
        self.assertFalse(distributions['checks']['normal_reseeding_cache_verified'])
        self.assertFalse(distributions['checks']['poisson_rejection_branch_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [graphics,distributions]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        text = raster_distributions_review_text()
        self.assertEqual((ROOT/RASTER_DISTRIBUTIONS_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('That issue remains unresolved', text)
        self.assertIn('do not certify statistical quality', text)
        preview = (ROOT/'docs/gams-raster-distributions.png').read_bytes()
        self.assertEqual(preview[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual((int.from_bytes(preview[16:20],'big'),int.from_bytes(preview[20:24],'big')), (85,65))

    def test_quantity_and_zonal_transform_drivers_record_si_and_independent_coefficients(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        quantities = drivers['quaff-quantity-reference']
        spherical = drivers['spherepack-zonal-reference']
        self.assertEqual((quantities['gams_code'],spherical['gams_code']), ('A','J'))
        self.assertEqual(quantities['checks']['scalar_references'], 180)
        self.assertTrue(quantities['checks']['typed_speed_round_trip_checked'])
        self.assertFalse(quantities['checks']['invalid_dimensions_compile_checks_verified'])
        self.assertEqual(spherical['checks']['harmonic_fixtures'], 18)
        self.assertEqual(spherical['checks']['analysis_calls'], 18)
        self.assertEqual(spherical['checks']['synthesis_calls'], 36)
        self.assertTrue(spherical['checks']['independent_coefficient_injection_checked'])
        self.assertFalse(spherical['checks']['nonzero_nonzonal_modes_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [quantities,spherical]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        spherepack_records = [r for r in data['procedure_mappings'] if r['package_id'] == 'spherepack']
        self.assertEqual(class_evidence(class_tree(data),'I2',spherepack_records,
                                       list(drivers.values()))['status'], 'source-supported')
        text = quantities_spherical_review_text()
        self.assertEqual((ROOT/QUANTITIES_SPHERICAL_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('0.3048 m/ft', text)
        self.assertIn('compensating normalization error', text)
        self.assertIn('18 analyses and 36 syntheses', text)

    def test_delay_and_lua_drivers_record_analytic_solutions_and_error_recovery(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        delay = drivers['dde-method-steps-reference']
        embedding = drivers['lua-numeric-embedding-reference']
        self.assertEqual((delay['gams_code'],embedding['gams_code']), ('I','S'))
        self.assertEqual(delay['checks']['integration_runs'], 15)
        self.assertEqual(delay['checks']['dense_output_references'], 975)
        self.assertEqual(delay['checks']['constant_history_values'], [1,-2])
        self.assertFalse(delay['checks']['state_dependent_delays_verified'])
        self.assertEqual(embedding['checks']['exact_integer_calls'], 128)
        self.assertEqual(embedding['checks']['real_norm_calls'], 5)
        self.assertTrue(embedding['checks']['stack_balance_checked'])
        self.assertTrue(embedding['checks']['state_recovery_checked'])
        self.assertFalse(embedding['checks']['external_script_files_used'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [delay,embedding]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertNotEqual(class_evidence(class_tree(data),'I1',[records['dde-solver-api']],
                                          list(drivers.values()))['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'S',[records['lua53-interface']],
                                       list(drivers.values()))['status'], 'source-supported')
        text = delay_embedding_review_text()
        self.assertEqual((ROOT/DELAY_EMBEDDING_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('method-of-steps reference', text)
        self.assertIn('a subsequent factorial(6) must return 720', text)
        self.assertIn('ordinary ODE subclasses', text)

    def test_qdutillib_and_nufft2d_drivers_check_moments_and_direct_sums(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        rule = drivers['qdutillib-moments-reference']
        transform = drivers['nufft2d-direct-reference']
        self.assertEqual((rule['gams_code'],transform['gams_code']),('H2c','J1'))
        self.assertEqual(rule['checks']['orders'],[1,2,3,4,6,8,12])
        self.assertEqual(rule['checks']['quadrature_rules'],14)
        self.assertEqual(rule['checks']['total_moment_checks'],191)
        self.assertEqual(rule['checks']['legendre_gaussian_moments']+rule['checks']['shifted_legendre_moments'],191)
        self.assertTrue(rule['checks']['deallocation_checked'])
        self.assertFalse(rule['checks']['other_rule_families_verified'])
        self.assertEqual(transform['checks']['transform_calls'],144)
        self.assertEqual(transform['checks']['coefficient_checks'],22416)
        self.assertIn([9,11],transform['checks']['mode_grids'])
        self.assertTrue(transform['checks']['both_signs_checked'])
        self.assertTrue(transform['checks']['zero_strengths_checked'])
        self.assertTrue(transform['checks']['input_preservation_checked'])
        self.assertFalse(transform['checks']['type2_type3_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [rule,transform]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        text = moments_nufft2d_review_text()
        self.assertEqual((ROOT/MOMENTS_NUFFT2D_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('full-function weights',text)
        self.assertIn('absolute contributions',text)
        self.assertIn('22,416',text)
        self.assertIn('Type-2/type-3 transforms',text)
        self.assertIn('two-dimensional NUFFT2D driver',transforms_review_text())

    def test_geodesy_and_forlab_drivers_keep_units_precision_and_failed_wide_scope(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('maptran-wgs84-reference','P'),('forlab-least-squares-reference','D9a1')]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        geo = drivers['maptran-wgs84-reference']['checks']
        self.assertEqual(geo['geodetic_cases'],336)
        self.assertEqual(geo['conversion_calls'],680)
        self.assertEqual(geo['forward_polar_axis_calls'],8)
        self.assertTrue(geo['inverse_independent_cartesian_inputs'])
        self.assertFalse(geo['inverse_poles_verified'])
        ls = drivers['forlab-least-squares-reference']['checks']
        self.assertEqual(ls['matrix_fixtures'],36)
        self.assertEqual(ls['solver_calls'],108)
        self.assertEqual(ls['real_storage_bits'],32)
        self.assertFalse(ls['underdetermined_verified'])
        self.assertFalse(ls['square_branch_verified'])
        folder = ROOT/'docs/gams-candidates/forlab'
        metadata = json.loads((folder/'wide-least-squares.json').read_text())
        source = (folder/metadata['source']).read_text().replace('\r\n','\n').encode()
        self.assertEqual(hashlib.sha256(source).hexdigest(),metadata['source_sha256'])
        result = json.loads((folder/metadata['result']).read_text())
        stages = {s['name']: s for s in result['stages']}
        self.assertTrue(stages['Build']['ok'])
        self.assertFalse(stages['Run']['ok'])
        self.assertIn('Failure m,n,scale',stages['Run']['stdout'])
        self.assertIn('ERROR STOP vector solution',stages['Run']['stderr'])
        text = geodesy_forlab_review_text()
        self.assertEqual((ROOT/GEODESY_FORLAB_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['680 conversion calls','108 solver calls','32-bit real storage','Wide systems are not verified']:
            self.assertIn(phrase,text)

    def test_ranking_and_magic_drivers_check_independent_discrete_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('orderpack-ranking-reference','N6'),('m-la-magic-reference','D1')]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        ranking = drivers['orderpack-ranking-reference']['checks']
        self.assertEqual(ranking['exhaustive_permutations'],5913)
        self.assertEqual(ranking['ranking_fixtures'],5997)
        self.assertEqual(ranking['overload_calls'],23988)
        self.assertEqual(len(ranking['overloads']),4)
        self.assertTrue(ranking['empty_input_checked'])
        self.assertTrue(ranking['permutation_integrity_checked'])
        self.assertFalse(ranking['stable_tie_order_verified'])
        self.assertFalse(ranking['nan_ordering_verified'])
        magic = drivers['m-la-magic-reference']['checks']
        self.assertEqual(magic['generator_calls'],124)
        self.assertEqual(magic['entry_checks'],45744)
        self.assertEqual(magic['line_sum_checks'],4456)
        self.assertEqual(sum(magic[k] for k in ['odd_orders','doubly_even_orders','singly_even_orders']),31)
        self.assertTrue(magic['padded_leading_dimension_checked'])
        self.assertTrue(magic['exact_integer_checks'])
        self.assertFalse(magic['other_matrix_utilities_verified'])
        text = ranking_magic_review_text()
        self.assertEqual((ROOT/RANKING_MAGIC_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['23,988 rank calls','45,744 entry checks','4,456 exact line-sum checks','stable tie ordering']:
            self.assertIn(phrase,text)

    def test_diagonal_and_harmonic_drivers_keep_failed_response_scope_explicit(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('specialmatrices-diagonal-reference','D2'),('dynamics-response-reference','I1')]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        diagonal = drivers['specialmatrices-diagonal-reference']['checks']
        self.assertEqual(diagonal['matrix_fixtures'],36)
        self.assertEqual(diagonal['solve_calls'],180)
        self.assertEqual(diagonal['solution_coordinate_checks'],3024)
        self.assertFalse(diagonal['singular_diagonals_verified'])
        self.assertFalse(diagonal['other_structures_verified'])
        response = drivers['dynamics-response-reference']['checks']
        self.assertEqual(response['response_fixtures'],24)
        self.assertEqual(response['complex_coordinate_checks'],384)
        self.assertTrue(response['diagonal_stiffness_only'])
        self.assertFalse(response['coupled_systems_checked'])
        self.assertFalse(response['nonunit_mass_verified'])
        self.assertFalse(response['initial_value_integration_verified'])
        folder = ROOT/'docs/gams-candidates/dynamics'
        for name in ['nonunit-mass','coupled-unit-mass']:
            metadata = json.loads((folder/(name+'.json')).read_text())
            source = (folder/metadata['source']).read_text().replace('\r\n','\n').encode()
            self.assertEqual(hashlib.sha256(source).hexdigest(),metadata['source_sha256'])
            result = json.loads((folder/metadata['result']).read_text())
            stages = {s['name']: s for s in result['stages']}
            self.assertTrue(stages['Build']['ok'])
            self.assertFalse(stages['Run']['ok'])
            self.assertIn('Mismatch',stages['Run']['stdout'])
        text = diagonal_response_review_text()
        self.assertEqual((ROOT/DIAGONAL_RESPONSE_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['3,024 solution-coordinate','384 complex-coordinate','0.5153882032','0.5625']:
            self.assertIn(phrase,text)

    def test_fitpack_values_and_derivatives_have_separate_polynomial_evidence(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code,count in [('fitpack-polynomial-values','E1a',11016),
                                 ('fitpack-polynomial-derivatives','H1',44352)]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            self.assertEqual(d['checks']['polynomial_fits'],144)
            self.assertEqual(d['checks']['reference_checks'],count)
            self.assertEqual(d['checks']['spline_degrees'],[1,3,5])
            self.assertTrue(d['checks']['scalar_vector_checked'])
            self.assertTrue(d['checks']['reversed_nonuniform_sources_checked'])
            self.assertTrue(d['checks']['destruction_checked'])
            self.assertFalse(d['checks']['positive_smoothing_verified'])
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        differentiation = drivers['fitpack-polynomial-derivatives']['checks']
        self.assertEqual(differentiation['positive_derivative_checks'],34848)
        self.assertEqual(differentiation['zeroth_derivative_checks'],9504)
        self.assertEqual(differentiation['max_derivative_order'],5)
        self.assertFalse(differentiation['arbitrary_callback_differentiation_verified'])
        text = fitpack_polynomials_review_text()
        self.assertEqual((ROOT/FITPACK_POLYNOMIALS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['11,016 total value references','44,352 references','orders through five','not an arbitrary']:
            self.assertIn(phrase,text)
        interpolation = interpolation_review_text()
        self.assertIn('FITPACK polynomial review',interpolation)
        self.assertNotIn('/None)',interpolation)

    def test_regrid_and_rk45_drivers_check_exact_values_and_requested_times(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('regridpack-polynomial-reference','E1a'),('diffeq-rk45-reference','I1a1a')]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        interpolation = drivers['regridpack-polynomial-reference']['checks']
        self.assertEqual(interpolation['successful_calls'],127)
        self.assertEqual(interpolation['analytical_value_checks'],3614)
        self.assertEqual(interpolation['expected_rejections'],8)
        self.assertTrue(interpolation['post_error_recovery_checked'])
        self.assertFalse(interpolation['multidimensional_verified'])
        ode = drivers['diffeq-rk45-reference']['checks']
        self.assertEqual(ode['ivp_runs'],24)
        self.assertEqual(ode['requested_solution_points'],408)
        self.assertTrue(ode['both_directions_checked'])
        self.assertTrue(ode['callback_state_checked'])
        self.assertTrue(ode['reused_solver_checked'])
        self.assertFalse(ode['stiff_problems_verified'])
        self.assertFalse(ode['events_verified'])
        text = regrid_rk45_review_text()
        self.assertEqual((ROOT/REGRID_RK45_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['3,614 analytical value checks','408 checked solution points','clear_buffer','extrapolation']:
            self.assertIn(phrase,text)
        self.assertNotIn('/None)',text)

    def test_spectral_wrappers_check_prescribed_spectra_and_reduced_factor_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code,fixtures,calls in [('forsvd-spectrum-reference','D6',144,432),
                                          ('foreig-symmetric-reference','D4a1',96,96)]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            self.assertEqual(d['checks']['matrix_fixtures'],fixtures)
            self.assertEqual(d['checks']['solver_calls'],calls)
            self.assertTrue(d['checks']['known_spectrum_checked'])
            self.assertTrue(d['checks']['orthogonality_checked'])
            self.assertFalse(d['checks']['complex_overloads_verified'])
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        svd = drivers['forsvd-spectrum-reference']['checks']
        self.assertEqual(svd['methods'],['default','gesvd','gesdd'])
        self.assertTrue(svd['input_copy_used'])
        self.assertTrue(svd['reduced_factors_only'])
        eig = drivers['foreig-symmetric-reference']['checks']
        self.assertTrue(eig['upper_triangle_checked'])
        self.assertTrue(eig['input_preservation_checked'])
        self.assertFalse(eig['nonsymmetric_verified'])
        text = spectral_wrappers_review_text()
        self.assertEqual((ROOT/SPECTRAL_WRAPPERS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['432 decompositions','96 fixtures','fresh input copy','Neither wrapper exposes LAPACK INFO']:
            self.assertIn(phrase,text)

    def test_iterative_least_squares_drivers_check_exact_minimum_norm_answers(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for package in ['lsqr','lsmr']:
            d = drivers[package+'-least-squares-reference']
            self.assertEqual(d['gams_code'],'D9a1')
            self.assertEqual(d['checks']['matrix_fixtures'],72)
            self.assertEqual(d['checks']['solver_calls'],216)
            self.assertEqual(d['checks']['nonzero_residual_fixtures'],18)
            self.assertTrue(d['checks']['minimum_norm_checked'])
            self.assertTrue(d['checks']['normal_equation_checked'])
            self.assertFalse(d['checks']['damping_verified'])
            self.assertFalse(d['checks']['rank_deficiency_verified'])
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),'D9a1',[record],[d])['status'],'verified')
        text = iterative_ls_review_text()
        self.assertEqual((ROOT/ITERATIVE_LS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['216 vector solves','72 fixtures','minimum-norm','zero damping','Rank deficiency']:
            self.assertIn(phrase,text)

    def test_higher_ad_drivers_check_complex_orders_and_polynomial_hessians(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        complex_ad = drivers['dnaoad-higher-reference']
        hessian = drivers['diffstruc-hessian-reference']
        self.assertEqual((complex_ad['gams_code'],hessian['gams_code']),('H1','H1'))
        self.assertEqual(complex_ad['checks']['requested_orders'],[0,1,2,3,4,5])
        self.assertEqual(complex_ad['checks']['dual_expressions'],450)
        self.assertEqual(complex_ad['checks']['derivative_reference_checks'],1575)
        self.assertEqual(sum(complex_ad['checks'][key] for key in
                             ['scaled_exp_sin_checks','composed_exp_checks','polynomial_checks']),1575)
        self.assertFalse(complex_ad['checks']['multivariate_verified'])
        self.assertFalse(complex_ad['checks']['nonanalytic_functions_verified'])
        self.assertEqual(hessian['checks']['polynomial_sample_points'],5)
        self.assertEqual(hessian['checks']['exact_reference_checks'],95)
        self.assertEqual(hessian['checks']['hessian_entry_checks'],45)
        self.assertEqual(hessian['checks']['forward_calls'],30)
        self.assertEqual(hessian['checks']['reverse_calls'],20)
        self.assertTrue(hessian['checks']['zero_direction_checked'])
        self.assertFalse(hessian['checks']['graph_disposal_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [complex_ad,hessian]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),'H1',[record],[d])['status'],'verified')
        text = higher_ad_review_text()
        self.assertEqual((ROOT/HIGHER_AD_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('1,575 exact complex references',text)
        self.assertIn('45 Hessian entries',text)
        self.assertIn('full [1,1,1] direction mask is restored',text)
        self.assertIn('All graphs are retained',text)

    def test_user_jacobian_and_newton_drivers_check_independent_minima_and_roots(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        fit = drivers['minpack-lmder-reference']
        root = drivers['forsolver-newton-reference']
        self.assertEqual((fit['gams_code'],root['gams_code']),('G1b1b','F1b'))
        self.assertEqual(fit['checks']['nonlinear_fits'],40)
        self.assertEqual(fit['checks']['exact_fit_runs'],24)
        self.assertEqual(fit['checks']['nonzero_residual_runs'],16)
        self.assertEqual(fit['checks']['jacobian_entries_checked'],400)
        self.assertTrue(fit['checks']['stopping_status_checked'])
        self.assertTrue(fit['checks']['both_callback_modes_checked'])
        self.assertFalse(fit['checks']['general_scalar_optimization_verified'])
        self.assertEqual(root['checks']['root_fixtures'],96)
        self.assertEqual(root['checks']['solver_calls'],288)
        self.assertEqual(len(root['checks']['methods']),3)
        self.assertFalse(root['checks']['returned_status_available'])
        self.assertFalse(root['checks']['vector_systems_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [fit,root]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertNotEqual(class_evidence(class_tree(data),'F2',[records[root['procedure_id']]],
                                          [root])['status'],'verified')
        text = jacobian_roots_review_text()
        self.assertEqual((ROOT/JACOBIAN_ROOTS_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('400 entries',text)
        self.assertIn('14*rho**2',text)
        self.assertIn('normal stopping info in 1..4',text)
        self.assertIn('288 solves',text)
        self.assertIn('Agreement alone is insufficient',text)

    def test_rkf45_and_qags_drivers_check_known_solutions_and_requested_status(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        ode = drivers['rkf45-analytic-reference']
        quad = drivers['fgsl-qags-reference']
        self.assertEqual((ode['gams_code'],quad['gams_code']),('I1a1a','H2a1a1'))
        self.assertEqual(ode['checks']['integration_runs'],24)
        self.assertEqual(ode['checks']['target_calls'],384)
        self.assertEqual(ode['checks']['targets_per_run'],16)
        self.assertTrue(ode['checks']['forward_and_backward_checked'])
        self.assertFalse(ode['checks']['stiff_systems_verified'])
        self.assertFalse(ode['checks']['one_step_mode_verified'])
        self.assertEqual(quad['checks']['integral_fixtures'],20)
        self.assertEqual(quad['checks']['integration_calls'],40)
        self.assertEqual(quad['checks']['absolute_relative_tolerances'],[1e-7,1e-10])
        self.assertTrue(quad['checks']['workspace_reuse_checked'])
        self.assertTrue(quad['checks']['endpoint_singular_integrals_checked'])
        self.assertTrue(quad['checks']['status_checked'])
        self.assertTrue(quad['checks']['error_estimate_checked'])
        self.assertFalse(quad['checks']['error_estimate_rigorous_bound_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [ode,quad]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertNotEqual(class_evidence(class_tree(data),'I1a2',[records[ode['procedure_id']]],
                                          [ode])['status'],'verified')
        text = rkf_qags_review_text()
        self.assertEqual((ROOT/RKF_QAGS_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('384 calls',text)
        self.assertIn('40 calls',text)
        self.assertIn('normal flag 2',text)
        self.assertIn('does not establish a rigorous upper bound',text)

    def test_least_squares_and_interp1_drivers_check_residuals_and_exact_polynomials(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        least = drivers['linalg-least-squares-reference']
        interp = drivers['interp1-reference']
        self.assertEqual((least['gams_code'],interp['gams_code']),('D9a1','E1a'))
        self.assertEqual(least['checks']['matrix_fixtures'],72)
        self.assertEqual(least['checks']['solver_calls'],288)
        self.assertEqual(least['checks']['nonzero_residual_fixtures'],18)
        self.assertTrue(least['checks']['underdetermined_minimum_norm_checked'])
        self.assertFalse(least['checks']['rank_deficient_verified'])
        self.assertIsNone(least['author_example'])
        self.assertEqual(interp['checks']['overloads_checked'],4)
        self.assertEqual(interp['checks']['exact_reference_checks'],3286)
        self.assertEqual(sum(interp['checks'][key] for key in
                             ['affine_reference_checks','cubic_reference_checks','knot_reference_checks']),3286)
        self.assertEqual(interp['checks']['nan_checks'],36)
        self.assertEqual(interp['checks']['interval_bound_checks'],1032)
        self.assertEqual(interp['checks']['monotonicity_checks'],512)
        self.assertFalse(interp['checks']['invalid_inputs_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [least,interp]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertEqual(class_evidence(class_tree(data),'D2a1',[records['linalg-lu-factor']],
                                       [least])['status'],'source-supported')
        text = least_interpolation_review_text()
        self.assertEqual((ROOT/LEAST_INTERPOLATION_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('288 solver calls',text)
        self.assertIn('not 72 distinct matrices',text)
        self.assertIn('endpoint secant slopes',text)
        self.assertNotIn('/None)',text)

    def test_dense_spectrum_drivers_check_one_sided_vectors_and_retain_link_failures(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        eigen = drivers['linalg-eigen-reference']
        svd = drivers['linalg-svd-reference']
        self.assertEqual((eigen['gams_code'],svd['gams_code']),('D4a1','D6'))
        self.assertEqual(eigen['checks']['matrix_fixtures'],96)
        self.assertEqual(eigen['checks']['eigen_calls'],192)
        self.assertTrue(eigen['checks']['unused_upper_triangle_poisoned'])
        self.assertTrue(eigen['checks']['eigenvalues_only_checked'])
        self.assertEqual(svd['checks']['matrix_fixtures'],144)
        self.assertEqual(svd['checks']['svd_calls'],576)
        self.assertEqual(svd['checks']['output_modes'],['full','values-only','U-only','VT-only'])
        self.assertEqual(svd['checks']['max_normalized_singular_vector_residual'],1e-11)
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [eigen,svd]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
            self.assertFalse(d['checks']['complex_verified'])
            self.assertFalse(d['checks']['invalid_inputs_verified'])
        folder = ROOT/'docs/gams-candidates/fortran-lapack'
        for identity,record_id in [('lapack-eigen-reference','fortran-lapack-eigh'),
                                   ('lapack-svd-reference','fortran-lapack-svd')]:
            self.assertNotIn('driver_id',records[record_id])
            source = (folder/(identity+'.f90')).read_text(encoding='utf-8')
            result = json.loads((folder/(identity+'-result.json')).read_text())
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),result['source_sha256'])
            self.assertEqual(result['revision'],records[record_id]['revision'])
            self.assertFalse(result['ok'])
            self.assertTrue(result['cache']['library_reused'])
            build = next(s for s in result['stages'] if s['name']=='Build')
            self.assertFalse(build['ok'])
            self.assertIn('File size limit exceeded',build['stdout']+build['stderr'])
            self.assertFalse(any(s['name']=='Run' for s in result['stages']))
        text = dense_spectra_review_text()
        self.assertEqual((ROOT/DENSE_SPECTRA_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('192 calls',text)
        self.assertIn('576 calls',text)
        self.assertIn('full-storage null vectors',text)
        self.assertIn('Neither probe ran',text)

    def test_qr_and_autodiff_drivers_check_rectangular_factors_and_analytic_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        qr = drivers['linalg-qr-reference']
        ad = drivers['differentia-analytic-reference']
        self.assertEqual((qr['gams_code'],ad['gams_code']),('D5','H1'))
        self.assertEqual(qr['checks']['matrix_fixtures'],192)
        self.assertEqual(qr['checks']['factorization_calls'],576)
        self.assertEqual(qr['checks']['pivot_modes'],['none','free','first-column-locked'])
        self.assertTrue(qr['checks']['rank_deficient_included'])
        self.assertFalse(qr['checks']['linear_solve_verified'])
        self.assertFalse(qr['checks']['complex_verified'])
        self.assertEqual(ad['checks']['scalar_derivative_calls'],99)
        self.assertEqual(ad['checks']['gradient_calls'],33)
        self.assertEqual(ad['checks']['dense_jacobian_calls'],66)
        self.assertEqual(ad['checks']['dimension_guards'],2)
        self.assertTrue(ad['checks']['workspace_reuse_checked'])
        self.assertFalse(ad['checks']['sparse_jacobians_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [qr,ad]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertEqual(class_evidence(class_tree(data),'D2a1',[records['linalg-lu-factor']],
                                       [qr])['status'],'source-supported')
        self.assertEqual(class_evidence(class_tree(data),'H1',[records['forwarddiff-derivative']],
                                       [ad])['status'],'source-supported')
        text = qr_autodiff_review_text()
        self.assertEqual((ROOT/QR_AUTODIFF_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('576 QR calls',text)
        self.assertIn('99 scalar calls',text)
        self.assertIn('not finite differences',text)
        self.assertIn('separate forwarddiff catalog alias',text)

    def test_rules_and_differences_drivers_retain_failed_order_one_probe(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        rule = drivers['kronrod-moments-reference']
        diff = drivers['tsunami-differences-reference']
        self.assertEqual((rule['gams_code'],diff['gams_code']),('H2c','H1'))
        self.assertEqual(rule['checks']['gauss_orders'],[2,3,4,5,6,7,10])
        self.assertEqual(sum(rule['checks'][key] for key in
                             ['kronrod_even_moments','gauss_even_moments','translated_moments']),155)
        self.assertFalse(rule['checks']['order_one_verified'])
        self.assertFalse(rule['checks']['adaptive_integration_verified'])
        self.assertEqual(diff['checks']['fourier_fixtures'],90)
        self.assertEqual(diff['checks']['nonsmooth_constant_fixtures'],10)
        self.assertFalse(diff['checks']['pde_evolution_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [rule,diff]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertNotEqual(class_evidence(class_tree(data),'I2',[records[diff['procedure_id']]],
                                          [diff])['status'],'verified')
        folder = ROOT/'docs/gams-candidates/kronrod'
        source = (folder/'order-one-moments.f90').read_text(encoding='utf-8')
        result = json.loads((folder/'order-one-result.json').read_text())
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),result['source_sha256'])
        self.assertEqual(result['revision'],rule['revision'])
        self.assertFalse(result['ok'])
        run = next(s for s in result['stages'] if s['name']=='Run')
        self.assertFalse(run['ok'])
        self.assertIn('Failed n=1 power=0',run['stdout'])
        self.assertIn('exact polynomial moment',run['stderr'])
        text = rules_differences_review_text()
        self.assertEqual((ROOT/RULES_DIFFERENCES_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('155 exact polynomial moments',text)
        self.assertIn('Gauss order 1 is not verified',text)
        self.assertIn('does not verify PDE evolution',text)

    def test_dispersion_drivers_check_spectra_and_all_cartesian_gradients(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        mbd = drivers['libmbd-dimer-spectrum']
        d4 = drivers['dftd4-dispersion-reference']
        self.assertEqual((mbd['gams_code'],d4['gams_code']), ('D4','Z'))
        self.assertEqual(mbd['checks']['two_oscillator_fixtures'],36)
        self.assertEqual(mbd['checks']['hamiltonian_calls'],72)
        self.assertEqual(mbd['checks']['eigenvector_fixtures'],36)
        self.assertFalse(mbd['checks']['screened_model_verified'])
        self.assertEqual(d4['checks']['cartesian_derivatives'],48)
        self.assertTrue(d4['checks']['rigid_rotation_checked'])
        self.assertFalse(d4['checks']['three_body_verified'])
        self.assertEqual(d4['reuse'],'adapted')
        self.assertTrue(any('NOTICE' in p for p in d4['license_files']))
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [mbd,d4]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertNotIn('driver_id',records['forpca-pca'])
        text = dispersion_review_text()
        self.assertEqual((ROOT/DISPERSION_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('not a general-purpose eigensolver API',text)
        self.assertIn('99 evaluations',text)
        self.assertIn('physical model against experiment',text)

    def test_matrix_root_and_box_drivers_retain_failed_active_bound_probes(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        matrix = drivers['ntpoly-matrix-root-reference']
        box = drivers['qnstop-box-reference']
        self.assertEqual((matrix['gams_code'],box['gams_code']), ('D','G2'))
        self.assertEqual(matrix['checks']['spd_matrix_fixtures'], 24)
        self.assertEqual(matrix['checks']['matrix_function_calls'], 48)
        self.assertEqual(matrix['checks']['mpi_processes'], 1)
        self.assertFalse(matrix['checks']['inversion_api_verified'])
        self.assertEqual(box['checks']['seeded_optimization_runs'], 4)
        self.assertEqual(box['checks']['interior_minima'], 4)
        self.assertEqual(box['checks']['face_minima'], 0)
        self.assertEqual(box['checks']['corner_minima'], 0)
        self.assertFalse(box['checks']['active_bounds_verified'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for d in [matrix,box]:
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'], d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'], 'verified')
        self.assertEqual(class_evidence(class_tree(data),'D2',[records['ntpoly-inversion']],
                                       list(drivers.values()))['status'], 'source-supported')
        folder = ROOT/'docs/gams-candidates/qnstop'
        for iterations in [500,2000]:
            source = (folder/f'box-{iterations}-iterations.f90').read_text(encoding='utf-8')
            result = json.loads((folder/f'box-{iterations}-result.json').read_text())
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),result['source_sha256'])
            self.assertEqual(result['revision'],box['revision'])
            self.assertFalse(result['ok'])
            run = next(s for s in result['stages'] if s['name'] == 'Run')
            self.assertFalse(run['ok'])
            self.assertIn('Fixture=4',run['stdout'])
            self.assertIn('projected box minimum',run['stderr'])
        text = matrix_roots_box_review_text()
        self.assertEqual((ROOT/MATRIX_ROOTS_BOX_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('Active-bound accuracy is not verified', text)
        self.assertIn('corner fixture in those probes was not reached', text)

    def test_fit_series_and_integral_drivers_record_independent_references(self):
        drivers = {d['id']: d for d in driver_data()}
        fit = drivers['splpak-paired-noise-fit']
        series = drivers['fortsa-autocorrelation-reference']
        integral = drivers['integrate-nd-polynomial-reference']
        self.assertEqual((fit['gams_code'],series['gams_code'],integral['gams_code']), ('K1','L10a2a','H2b1a2'))
        self.assertEqual(fit['checks']['value_derivative_checks'], 126)
        self.assertEqual(fit['checks']['noisy_fit_sse'], 1.5)
        self.assertEqual(series['checks']['covariance_calls'], 12)
        self.assertEqual(series['checks']['correlation_calls'], 9)
        self.assertFalse(series['checks']['constant_series_correlation_requested'])
        self.assertEqual(integral['checks']['polynomial_integrals'], 67)
        self.assertEqual(integral['checks']['gauss_nodes_per_panel_per_dimension'], 6)
        text = applied_methods_review_text()
        self.assertEqual((ROOT / APPLIED_METHODS_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('panel counts per dimension, not quadrature orders', text)
        self.assertIn('nonzero-residual check', text)

    def test_boundary_and_spectral_drivers_reject_unverified_twopnt_probe(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        self.assertNotIn('twopnt-poisson-reference', drivers)
        featom = drivers['featom-coulomb-spectrum']
        arpack = drivers['arpack-poisson-eigenpairs']
        dense = drivers['linalg-poisson-eigenpairs']
        self.assertEqual(featom['gams_code'], 'I1b')
        self.assertEqual(featom['checks']['energy_checks'], 12)
        self.assertFalse(featom['checks']['wavefunction_accuracy_verified'])
        self.assertEqual(arpack['gams_code'], 'D4a1')
        self.assertEqual(dense['gams_code'], 'D4a1')
        self.assertEqual(arpack['problem_id'], dense['problem_id'])
        self.assertTrue(arpack['checks']['analytic_eigenvectors_checked'])
        self.assertEqual(dense['checks']['eigenpairs_checked'], 20)
        records = {r['id']:r for r in data['procedure_mappings']}
        self.assertNotIn('driver_id', records['twopnt-solve'])
        import hashlib
        failure = json.loads((ROOT/'docs/gams-candidates/twopnt/poisson-returned-iterate-result.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/failure['source_path']).read_text().encode()).hexdigest(),
                         failure['source_sha256'])
        self.assertFalse(failure['result']['ok'])
        run = next(s for s in failure['result']['stages'] if s['name']=='Run')
        self.assertIn('PROBLEM SOLVED', run['stdout'])
        self.assertIn('known Poisson profile/residual', run['stderr'])
        text = boundary_review_text()
        self.assertEqual((ROOT/BOUNDARY_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('upstream-confirmed diagnosis', text)

    def test_resampling_and_markov_drivers_have_independent_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        markov = drivers['econ-markov-reference']
        jackknife = drivers['fjsample-jackknife-reference']
        self.assertEqual(markov['gams_code'], 'M')
        self.assertEqual(markov['checks']['normal_cell_probability_checks'], 2883)
        self.assertFalse(markov['checks']['random_sampling_verified'])
        self.assertEqual(jackknife['gams_code'], 'L4')
        self.assertEqual(jackknife['checks']['sample_sizes'], [2, 6, 4, 6, 8])
        self.assertIn('no factor n-1', jackknife['checks']['bias_convention'])
        records = {r['id']: r for r in data['procedure_mappings']}
        for driver in [markov, jackknife]:
            self.assertEqual(records[driver['procedure_id']]['driver_id'], driver['id'])
            evidence = class_evidence(class_tree(data), driver['gams_code'],
                                      [records[driver['procedure_id']]], [driver])
            self.assertEqual(evidence['status'], 'verified')
        text = resampling_markov_review_text()
        self.assertEqual((ROOT/RESAMPLING_MARKOV_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('full_estimate+(n-1)*package_bias', text)
        self.assertIn('independently certifying', text)

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
                          'slsqp-circle-equality': 'G2h3b1b', 'conmax-linear-program-certificate': 'G2a',
                          'bobyqa-box-reference': 'G2h1a1', 'pikaia-rastrigin-reference': 'G2i'})
        self.assertEqual(len({d['problem_id'] for d in drivers}), 4)
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertEqual(records['nlopt-lbfgs']['gams_codes'], ['G1b1b'])
        self.assertEqual(records['nlopt-lbfgs-bounds']['gams_codes'], ['G2h1a2'])
        self.assertEqual((ROOT / CONSTRAINED_REPORT).read_text(encoding='utf-8'), constrained_review_text())

    def test_linear_derivative_free_and_global_optimization_checks_are_distinct(self):
        drivers = {d['id']: d for d in driver_data()}
        lp = drivers['conmax-linear-program-certificate']
        box = drivers['bobyqa-box-reference']
        global_search = drivers['pikaia-rastrigin-reference']
        self.assertTrue(lp['checks']['dual_certificate_checked'])
        self.assertEqual(lp['checks']['linear_programs'], 3)
        self.assertFalse(box['checks']['objective_derivatives_supplied'])
        self.assertFalse(box['checks']['has_returned_status_flag'])
        self.assertEqual(box['problem_id'], drivers['lbfgsb-box-quadratic']['problem_id'])
        self.assertEqual(global_search['checks']['seeds'], [12345,6789,24680])
        self.assertFalse(global_search['checks']['global_convergence_guaranteed'])
        text = constrained_review_text()
        self.assertIn('primal-dual gap', text)
        self.assertIn('no returned status flag', text)
        self.assertIn('does not guarantee global convergence', text)

    def test_special_function_drivers_keep_gamma_psi_and_bessel_evidence_separate(self):
        data = gams_data()
        drivers = [d for d in driver_data(data=data)
                   if driver_validation_path(d) == 'docs/gams-special-functions-validation.json']
        self.assertEqual({d['id']: d['gams_code'] for d in drivers},
                         {'fullerton-gamma-values': 'C7a', 'fullerton-digamma-values': 'C7c',
                          'bessels-modified-values': 'C10b1', 'amos-complex-series': 'C10',
                          'carlson-rf-reference': 'C14', 'bernoulli-power-sums': 'C19'})
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertNotIn('digamma', records['specfunc-fullerton-fgamma']['procedure'])
        self.assertIn('reciprocal_gamma', records['specfunc-fullerton-fgamma']['procedure'])
        self.assertEqual((ROOT / SPECIAL_FUNCTIONS_REPORT).read_text(encoding='utf-8'), special_functions_review_text())

    def test_complex_elliptic_and_bernoulli_references_document_pinned_limits(self):
        drivers = {d['id']: d for d in driver_data()}
        self.assertEqual(drivers['carlson-rf-reference']['checks']['simpson_intervals'], [2048,4096])
        self.assertFalse(drivers['bernoulli-power-sums']['checks']['unassigned_odd_outputs_read'])
        self.assertEqual(drivers['bernoulli-power-sums']['checks']['integer_power_sum_cases'], 24)
        self.assertEqual(drivers['amos-complex-series']['checks']['complex_value_checks'], 39)
        self.assertTrue(drivers['amos-complex-series']['checks']['series_convergence_required'])
        import hashlib
        candidate = json.loads((ROOT/'docs/gams-candidates/amosf90/lower-half-plane-result.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/candidate['source_path']).read_text().encode()).hexdigest(),
                         candidate['source_sha256'])
        self.assertFalse(candidate['result']['ok'])
        self.assertEqual(candidate['independent_reference']['decimal_digits'], 80)
        report = special_functions_review_text()
        self.assertIn('leaves odd output positions above B1 unassigned', report)
        self.assertIn('no package patch or tolerance relaxation', report)

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

    def test_arithmetic_drivers_have_exact_references_and_class_specific_scope(self):
        data = gams_data()
        drivers = driver_data(data=data)
        selected = {d['id']: d for d in drivers if driver_validation_path(d)=='docs/gams-arithmetic-validation.json'}
        self.assertEqual({d['gams_code'] for d in selected.values()}, {'A1','A2','A6','A3c','A4c','N2'})
        self.assertEqual(selected['rational-addition-reference']['checks']['addition_cases'], 5832)
        self.assertFalse(selected['rational-addition-reference']['checks']['negative_reduction_claimed'])
        self.assertEqual(selected['strith-integer-reference']['checks']['small_arithmetic_cases'], 3362)
        self.assertTrue(selected['ryu-binary64-roundtrip']['checks']['bitwise_roundtrip'])
        self.assertFalse(selected['ryu-binary64-roundtrip']['checks']['shortest_length_proved'])
        from xpackage_gams import class_tree, procedure_records
        strith_records = procedure_records(data, 'strith')
        self.assertEqual(class_evidence(class_tree(data), 'A6', strith_records, drivers)['status'], 'source-supported')
        self.assertEqual(class_evidence(class_tree(data), 'A1', strith_records, drivers)['status'], 'verified')
        text = arithmetic_review_text()
        self.assertEqual((ROOT / ARITHMETIC_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('negative or zero numerators can remain', text)
        self.assertIn('not all binary64 patterns', text)

    def test_multiprecision_and_bit_drivers_keep_distinct_problem_classes(self):
        data = gams_data()
        drivers = driver_data(data=data)
        selected = {d['id']: d for d in drivers}
        real = selected['mpfun-real-addition']
        complex_sum = selected['mpfun-complex-addition']
        bits = selected['bstrith-bit-reference']
        self.assertEqual((real['gams_code'],complex_sum['gams_code'],bits['gams_code']), ('A3c','A4c','N2'))
        self.assertEqual(real['checks']['exact_additions'], 6)
        self.assertEqual(complex_sum['checks']['exact_complex_sums'], 5)
        self.assertEqual(real['checks']['requested_decimal_digits'], 120)
        self.assertTrue(complex_sum['checks']['each_component_checked'])
        self.assertEqual(bits['checks']['exact_checks'], 5120)
        from xpackage_gams import class_tree, procedure_records
        tree = class_tree(data)
        records = procedure_records(data,'mpfun2020-var1')
        self.assertEqual(class_evidence(tree,'A3c',records,[complex_sum])['status'], 'source-supported')
        self.assertEqual(class_evidence(tree,'A4c',records,[real])['status'], 'source-supported')
        self.assertEqual(class_evidence(tree,'A1',procedure_records(data,'bstrith'),[bits])['status'], 'source-supported')

    def test_number_theory_packages_have_matching_checked_drivers_and_documented_limits(self):
        data = gams_data()
        packages = {name for name, codes in data['packages'].items() if 'B' in codes}
        drivers = [d for d in driver_data(data=data) if d['gams_code'] == 'B']
        self.assertEqual({d['package_id'] for d in drivers}, packages)
        by_id = {d['id']: d for d in drivers}
        self.assertEqual(by_id['primes-trial-division']['checks']['int32_cases'], 1021)
        self.assertEqual(by_id['rpn-gcd-lcm-reference']['checks']['gcd_cases'], 4225)
        self.assertFalse(by_id['rpn-gcd-lcm-reference']['checks']['lcm_zero_zero_checked'])
        text = number_theory_review_text()
        self.assertEqual((ROOT / NUMBER_THEORY_REPORT).read_text(encoding='utf-8'), text)
        self.assertIn('lcm(0,0)', text)
        self.assertIn('3215031751', text)
        import hashlib
        for name in ['large-int64-primality', 'signed-int32-boundary']:
            record = json.loads((ROOT / f'docs/gams-candidates/fortran-primes/{name}-result.json').read_text())
            self.assertEqual(hashlib.sha256((ROOT / record['source_path']).read_text().encode()).hexdigest(),
                             record['source_sha256'])
            self.assertFalse(record['result']['ok'])
            run = next(s for s in record['result']['stages'] if s['name']=='Run')
            self.assertIn('Timed out', run['error'])

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
        self.assertEqual({r['code'] for r in coverage['top_level'] if r['driver_ids']}, set('ABCDEFGHIJKLMNPQRSZ'))
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
