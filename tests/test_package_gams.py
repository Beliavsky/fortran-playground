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
                            jacobian_transforms_review_text, JACOBIAN_TRANSFORMS_REPORT,
                            expression_evaluation_review_text, EXPRESSION_EVALUATION_REPORT,
                            conversion_triangulation_review_text, CONVERSION_TRIANGULATION_REPORT,
                            graph_sorting_review_text, GRAPH_SORTING_REPORT,
                            neighbors_sparse_review_text, NEIGHBORS_SPARSE_REPORT,
                            adaptive_ad_review_text, ADAPTIVE_AD_REPORT,
                            lu_orbits_review_text, LU_ORBITS_REPORT,
                            dae_fft_review_text, DAE_FFT_REPORT,
                            propack_fmm_review_text, PROPACK_FMM_REPORT,
                            gmres_inverse_review_text, GMRES_INVERSE_REPORT,
                            periodic_calculus_review_text, PERIODIC_CALCULUS_REPORT,
                            expressions_sky_review_text, EXPRESSIONS_SKY_REPORT,
                            unsigned_bitsets_review_text, UNSIGNED_BITSETS_REPORT,
                            sparse_advection_review_text, SPARSE_ADVECTION_REPORT,
                            products_partitions_review_text, PRODUCTS_PARTITIONS_REPORT,
                            multidimensional_fft_review_text, MULTIDIMENSIONAL_FFT_REPORT,
                            sparse_spectra_review_text, SPARSE_SPECTRA_REPORT,
                            projection_lbfgs_review_text, PROJECTION_LBFGS_REPORT,
                            gradient_swarm_review_text, GRADIENT_SWARM_REPORT,
                            projection_training_review_text, PROJECTION_TRAINING_REPORT,
                            directions_fitting_review_text, DIRECTIONS_FITTING_REPORT,
                            random_references_review_text, RANDOM_REFERENCES_REPORT,
                            tangents_blocks_review_text, TANGENTS_BLOCKS_REPORT,
                            radial_dense_review_text, RADIAL_DENSE_REPORT,
                            inference_pairs_review_text, INFERENCE_PAIRS_REPORT,
                            helmholtz_streams_review_text, HELMHOLTZ_STREAMS_REPORT,
                            friction_torch_review_text, FRICTION_TORCH_REPORT,
                            pareto_diis_review_text, PARETO_DIIS_REPORT,
                            data_ten_review_text, DATA_TEN_REPORT,
                            state_ten_review_text, STATE_TEN_REPORT,
                            interop_ten_review_text, INTEROP_TEN_REPORT,
                            storage_ten_review_text, STORAGE_TEN_REPORT,
                            workflows_ten_review_text, WORKFLOWS_TEN_REPORT,
                            statistics_services_ten_review_text, STATISTICS_SERVICES_TEN_REPORT,
                            factorization_rules_ten_review_text, FACTORIZATION_RULES_TEN_REPORT,
                            special_functions_ten_review_text, SPECIAL_FUNCTIONS_TEN_REPORT,
                            systems_spectra_ten_review_text, SYSTEMS_SPECTRA_TEN_REPORT,
                            distribution_ten_review_text, DISTRIBUTION_TEN_REPORT,
                            pca_ordering_ten_review_text, PCA_ORDERING_TEN_REPORT,
                            activations_ten_review_text, ACTIVATIONS_TEN_REPORT,
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
                          'minpack-lmder-reference', 'nonlin-lsq-jacobian-reference', 'seiscope-lbfgs-reference', 'fortimize-gradient-reference', 'neural-affine-reference'})
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
                                       [ode])['status'], 'source-supported')
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
                                       [optimizer])['status'], 'source-supported')
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
        # A transform driver alone cannot establish PDE coverage.
        self.assertEqual(class_evidence(class_tree(data),'I2',spherepack_records,
                                       [spherical])['status'], 'source-supported')
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
                                       [delay,embedding])['status'], 'source-supported')
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

    def test_complex_operator_drivers_record_matching_procedures_oracles_and_limits(self):
        from xpackage_gams import complex_operators_ten_review_text, COMPLEX_OPERATORS_TEN_REPORT
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-complex-operators-ten-validation.json'}
        expected = {'complex-determinants': ('D3c1', 'cases', 72),
                    'complex-inverses': ('D2c1', 'cases', 72),
                    'complex-pseudoinverses': ('D9c', 'cases', 150),
                    'complex-qr': ('D5', 'factorizations', 150),
                    'complex-schur': ('D4a4', 'cases', 63),
                    'complex-matrix-exponential': ('D', 'evaluations', 180),
                    'complex-general-systems': ('D2c1', 'calls', 144),
                    'complex-positive-systems': ('D2d1b', 'calls', 288),
                    'complex-weighted-fits': ('D9a1', 'cases', 45),
                    'complex-equality-fits': ('D9b1', 'cases', 72)}
        self.assertEqual(set(drivers), {'stdlib-'+name+'-reference' for name in expected})
        reviewed = numerical_review(data=data)['packages']['stdlib']['procedure_ids']
        for name, (code, field, count) in expected.items():
            driver = drivers['stdlib-'+name+'-reference']
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(record['gams_codes'], [code])
            self.assertEqual(driver['gams_code'], code)
            self.assertEqual(driver['checks'][field], count)
            self.assertIn(record['id'], reviewed)
            self.assertIn('COMPLEX128', record['procedure'])
            self.assertEqual(class_evidence(class_tree(data), code, [record], [driver])['status'], 'verified')
        self.assertEqual(drivers['stdlib-complex-pseudoinverses-reference']['checks']['rtol'], 1e-12)
        self.assertEqual(drivers['stdlib-complex-weighted-fits-reference']['checks']['weights'], [1, 4, 16])
        self.assertEqual(drivers['stdlib-complex-equality-fits-reference']['checks']['equalities'], 1)
        text = complex_operators_ten_review_text()
        self.assertEqual((ROOT/COMPLEX_OPERATORS_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['all four Moore-Penrose', 'one-to-one', 'finite sum', 'weighted stationarity',
                       'C^H*lambda', '2e-10', 'near-cutoff', 'pivoted QR',
                       'No upstream numerical source was patched', 'categories are not exhausted']:
            self.assertIn(phrase.lower(), text.lower())

    def test_complex_linear_algebra_drivers_keep_problem_classes_and_oracles_explicit(self):
        from xpackage_gams import complex_ten_review_text, COMPLEX_TEN_REPORT
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-complex-ten-validation.json'}
        expected = {'matrix-trace': ('D1b', 'shapes', 90),
                    'identity-matrices': ('D1b1', 'rectangles', 90),
                    'conjugate-transpose': ('D1b3', 'shapes', 90),
                    'matrix-structure': ('R2', 'one_hot_positions', 204),
                    'vector-norms': ('D1a3', 'scales', 17),
                    'pivoted-lu-systems': ('D2a1', 'calls', 120),
                    'complex-cholesky': ('D2d1b', 'factorizations', 144),
                    'complex-hermitian-eigenpairs': ('D4a3', 'solves', 320),
                    'complex-thin-svd': ('D6', 'cases', 150),
                    'complex-least-squares': ('D9a1', 'cases', 45)}
        self.assertEqual(set(drivers), {'stdlib-'+name+'-reference' for name in expected})
        reviewed = numerical_review(data=data)['packages']['stdlib']['procedure_ids']
        for name, (code, field, count) in expected.items():
            driver = drivers['stdlib-'+name+'-reference']
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(driver['gams_code'], code)
            self.assertEqual(driver['checks'][field], count)
            self.assertIn(record['id'], reviewed)
            self.assertNotIn('linalg_state_type', record['procedure'])
            self.assertEqual(class_evidence(class_tree(data), code, [record], [driver])['status'], 'verified')
        for name in ['complex-hermitian-eigenpairs', 'complex-thin-svd', 'complex-least-squares']:
            source = (ROOT/drivers['stdlib-'+name+'-reference']['path']).read_text()
            self.assertIn('q(i,j)=q(i,j)-2*v(i)*conjg(v(j))/denominator', source)
            self.assertIn('call check_matrix(matmul(conjg(transpose(q)),q),identity(n))', source)
        text = complex_ten_review_text()
        self.assertEqual((ROOT/COMPLEX_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['320 solves', '150 cases', '45 full-column-rank', '144 lower/upper',
                       'Q^H*Q', 'nonzero residual', 'Eigenvector phases are unrestricted',
                       'No upstream numerical source was patched', 'categories are not exhausted',
                       'poisoned-unused-triangle behavior is not tested']:
            self.assertIn(phrase, text)

    def test_grid_utility_drivers_preserve_reference_provenance_and_tested_scope(self):
        from fractions import Fraction
        from xpackage_gams import grids_ten_review_text, GRIDS_TEN_REPORT
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-grids-ten-validation.json'}
        expected = {'gcd': 'B', 'linear-grids': 'D1a11', 'logarithmic-grids': 'D1a11',
                    'stepped-ranges': 'D1a11', 'cartesian-grids': 'D1b1',
                    'bounded-clipping': 'A3a', 'tolerance-comparison': 'R2',
                    'complex-phase': 'C4a', 'angle-units': 'R', 'vector-exchange': 'D1a5'}
        self.assertEqual(set(drivers), {'stdlib-'+name+'-reference' for name in expected})
        reviewed = numerical_review(data=data)['packages']['stdlib']['procedure_ids']
        for name, code in expected.items():
            driver = drivers['stdlib-'+name+'-reference']
            record = records[driver['procedure_id']]
            self.assertEqual(driver['gams_code'], code)
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), code, [record], [driver])['status'], 'verified')
        refs = json.loads((ROOT/'docs/gams-grids-ten-references.json').read_text())['tables']
        points = refs['logarithmic-grids']
        self.assertEqual(len(points), 372)
        self.assertEqual(len({(p['base'], p['start'], p['end'], p['n']) for p in points}), 60)
        source = (ROOT/drivers['stdlib-logarithmic-grids-reference']['path']).read_text()
        for point in points:
            self.assertIn(point['value']+'_real64', source)
        truth = refs['tolerance-comparison']['expected']
        self.assertEqual(len(truth), 289)
        for j in range(17):
            for i in range(17):
                a, b = Fraction(i-8, 4), Fraction(j-8, 4)
                self.assertEqual(truth[i+17*j],
                                 abs(a-b) <= max(Fraction(1, 8)*max(abs(a), abs(b)), Fraction(1, 16)))
        self.assertEqual(drivers['stdlib-gcd-reference']['checks']['signed_pairs'], 6561)
        self.assertEqual(drivers['stdlib-linear-grids-reference']['checks']['grids_per_kind'], 2916)
        self.assertEqual(drivers['stdlib-stepped-ranges-reference']['checks']['real_ranges'], 867)
        self.assertEqual(drivers['stdlib-cartesian-grids-reference']['checks']['rectangles'], 42)
        self.assertEqual(drivers['stdlib-bounded-clipping-reference']['checks']['real_references'], 1935)
        self.assertEqual(drivers['stdlib-tolerance-comparison-reference']['checks']['complex_policy'], 'componentwise')
        text = grids_ten_review_text()
        self.assertEqual((ROOT/GRIDS_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['6,561', '372', '289', 'componentwise', 'singleton returns the end',
                       'Aliasing', 'No upstream numerical source was patched', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_activation_drivers_keep_independent_references_and_gradient_scope_explicit(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-activations-ten-validation.json'}
        self.assertEqual(len(drivers), 10)
        scalar = [d for d in drivers.values() if d['id'] != 'stdlib-softmax-normalization-reference']
        self.assertEqual(len(scalar), 9)
        self.assertEqual(sum(d['checks']['value_references'] for d in scalar), 1261)
        self.assertEqual(sum(d['checks']['derivative_references'] for d in scalar), 1059)
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'], 'verified')
        for fun in ['gelu', 'silu']:
            driver = drivers['stdlib-activation-'+fun+'-reference']
            self.assertFalse(driver['checks']['gradient_verified'])
            self.assertEqual(driver['checks']['derivative_references'], 0)
            source = (ROOT/driver['path']).read_text()
            self.assertNotIn(fun+'_grad', source)
        refs = json.loads((ROOT/'docs/gams-activations-ten-references.json').read_text())
        self.assertEqual(sum(map(len, refs['tables'].values())), 1261)
        for name, points in refs['tables'].items():
            source = (ROOT/drivers['stdlib-'+name+'-reference']['path']).read_text()
            for point in points:
                self.assertIn(point['value']+'_real64', source)
                if point['derivative'] is not None and name not in {'activation-gelu', 'activation-silu'}:
                    self.assertIn(point['derivative']+'_real64', source)
        softmax = drivers['stdlib-softmax-normalization-reference']['checks']
        self.assertEqual(softmax['common_shifts'], [-1000, 0, 1000])
        self.assertEqual(softmax['rank_one_vectors'], 144)
        self.assertEqual(softmax['rank_two_arrays'], 24)
        self.assertEqual(softmax['reference_entries_per_function'], 1224)
        self.assertEqual(softmax['gradient_scope'], 'Jacobian diagonal only')
        self.assertIsNone(drivers['stdlib-activation-softplus-reference']['author_example'])
        text = activations_ten_review_text()
        self.assertEqual((ROOT/ACTIVATIONS_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['1,261', '1,059', '3,672', 'Jacobian diagonal only', 'value-only',
                       'No upstream numerical source was patched', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_activation_gradient_failures_retain_sources_without_promoting_value_success(self):
        import hashlib
        data = gams_data()
        drivers = list(driver_data(data=data))
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        for fun in ['gelu', 'silu']:
            record = next(r for r in data['procedure_mappings'] if r['id'] == 'stdlib-activation-'+fun+'-gradient')
            self.assertNotIn('driver_id', record)
            self.assertIn(record['id'], reviewed)
            self.assertFalse(any(d['procedure_id'] == record['id'] for d in drivers))
            self.assertEqual(class_evidence(class_tree(data), 'C19', [record], drivers)['status'], 'source-supported')
            failure = json.loads((ROOT/f'docs/gams-candidates/stdlib-activations/{fun}-gradient-result.json').read_text())
            self.assertEqual(failure['revision'], record['revision'])
            source = (ROOT/failure['source_path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), failure['source_sha256'])
            self.assertIn(fun+'_grad(x)', source)
            result = failure['result']
            self.assertFalse(result['ok'])
            self.assertTrue(result['cache']['library_reused'])
            self.assertTrue(next(s for s in result['stages'] if s['name'] == 'Build')['ok'])
            run = next(s for s in result['stages'] if s['name'] == 'Run')
            self.assertFalse(run['ok'])
            self.assertIn('Independent differentiated activation reference', run['stderr'])
            actual, expected = map(float, run['stdout'].split()[-2:])
            self.assertGreater(abs(actual-expected), 1e-10)

    def test_ordering_array_drivers_preserve_exact_oracles_and_interface_scope(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-pca-ordering-ten-validation.json'}
        self.assertEqual(len(drivers), 10)
        self.assertNotIn('stdlib-pca-reference', drivers)
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        expected = {'select': ('N5', 'calls', 2976), 'arg-select': ('N5', 'calls', 2976),
                    'sort-index': ('N6', 'calls', 780), 'sort-adjoint': ('N6', 'calls', 780),
                    'unique': ('N6', 'calls', 390), 'differences': ('D1a11', 'calls', 325),
                    'cross-product': ('D1a11', 'pairs', 2154), 'kronecker': ('D1b', 'products', 432),
                    'diagonals': ('D1b1', 'constructions', 84), 'outer-product': ('D1b6', 'products', 224)}
        for name, (code, field, count) in expected.items():
            driver = drivers['stdlib-'+name+'-reference']
            record = records[driver['procedure_id']]
            self.assertEqual(driver['gams_code'], code)
            self.assertEqual(driver['checks'][field], count)
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), code, [record], [driver])['status'], 'verified')
        self.assertEqual(class_tree(data)['D1a11']['parent'], 'D1a')
        self.assertEqual(class_tree(data)['D1b6']['parent'], 'D1b')
        self.assertTrue(drivers['stdlib-sort-index-reference']['checks']['ties_stable'])
        self.assertTrue(drivers['stdlib-sort-adjoint-reference']['checks']['ascending_descending'])
        self.assertTrue(drivers['stdlib-unique-reference']['checks']['sorted_output'])
        self.assertEqual(drivers['stdlib-unique-reference']['checks']['tolerance'], 0)
        self.assertTrue(drivers['stdlib-differences-reference']['checks']['padding_checked'])
        self.assertTrue(drivers['stdlib-kronecker-reference']['checks']['column_major_vec_identity'])
        self.assertEqual(drivers['stdlib-diagonals-reference']['checks']['extractions'], 168)
        text = pca_ordering_ten_review_text()
        self.assertEqual((ROOT/PCA_ORDERING_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['not a passive-only argsort', 'not a step-scaled numerical derivative',
                       'Levi-Civita', '16 MiB', 'No checked PCA driver', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_stdlib_pca_limit_probe_is_retained_without_numerical_promotion(self):
        import hashlib
        data = gams_data()
        record = next(r for r in data['procedure_mappings'] if r['id'] == 'stdlib-pca')
        drivers = list(driver_data(data=data))
        self.assertNotIn('driver_id', record)
        self.assertFalse(any(d['procedure_id'] == record['id'] for d in drivers))
        self.assertEqual(class_evidence(class_tree(data), 'L13b', [record], drivers)['status'], 'source-supported')
        self.assertIn(record['id'], numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        failure = json.loads((ROOT/'docs/gams-candidates/stdlib-pca/analytic-pca-result.json').read_text())
        self.assertEqual(record['revision'], failure['revision'])
        source = (ROOT/failure['source_path']).read_text(encoding='utf-8')
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), failure['source_sha256'])
        self.assertFalse(failure['result']['ok'])
        self.assertTrue(failure['result']['cache']['library_reused'])
        stages = failure['result']['stages']
        self.assertEqual([s['name'] for s in stages], ['Build'])
        self.assertFalse(stages[0]['ok'])
        self.assertIn('main.f90  done.', stages[0]['stdout'])
        self.assertIn('File size limit exceeded', stages[0]['stdout'])

    def test_distribution_drivers_pair_densities_and_probabilities_with_independent_references(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-distribution-ten-validation.json'}
        self.assertEqual(len(drivers), 10)
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        for distribution, code, counts in [
                ('uniform', 'L5a1u', [1625, 1625]), ('normal', 'L5a1n', [585, 585]),
                ('exponential', 'L5a1e', [1170, 1170]), ('gamma', 'L5a1g', [486, 567]),
                ('beta', 'L5a1b', [4428, 4428])]:
            self.assertEqual(class_tree(data)[code]['parent'], 'L5a1')
            for kind, count in zip(['pdf', 'cdf'], counts):
                driver = drivers['stdlib-'+distribution+'-'+kind+'-reference']
                record = records[driver['procedure_id']]
                self.assertEqual(driver['gams_code'], code)
                self.assertEqual(record['driver_id'], driver['id'])
                self.assertIn(record['id'], reviewed)
                self.assertEqual(driver['checks']['references'], count)
                self.assertEqual(class_evidence(class_tree(data), code, [record], [driver])['status'], 'verified')
        self.assertEqual(sum(d['checks']['references'] for d in drivers.values()), 16669)
        pdf = drivers['stdlib-gamma-pdf-reference']['checks']
        cdf = drivers['stdlib-gamma-cdf-reference']['checks']
        self.assertNotIn(0.5, pdf['shapes'])
        self.assertIn(0.5, cdf['shapes'])
        self.assertTrue(any(int(shape) != shape for shape in pdf['shapes']))
        self.assertEqual(pdf['parameterization'], 'shape/rate, optional location supplied')
        self.assertEqual(drivers['stdlib-exponential-cdf-reference']['checks']['overloads'],
                         ['location/scale', 'zero-location/rate'])
        self.assertEqual(drivers['stdlib-uniform-pdf-reference']['checks']['endpoint_density_convention'],
                         'both endpoints included')
        refs = json.loads((ROOT/'docs/gams-distribution-ten-references.json').read_text())
        self.assertEqual({name: len(points) for name, points in refs['tables'].items()}, {
            'normal-pdf': 65, 'normal-cdf': 65, 'exponential-pdf': 65, 'exponential-cdf': 65,
            'gamma-pdf': 54, 'gamma-cdf': 63})
        for name, points in refs['tables'].items():
            source = (ROOT/drivers['stdlib-'+name+'-reference']['path']).read_text()
            for point in points:
                self.assertIn(point['value']+'_real64', source)
        report = json.loads((ROOT/'docs/gams-distribution-ten-validation.json').read_text())
        for result in report['drivers']:
            output = next(stage['stdout'] for stage in result['stages'] if stage['name'] == 'Run')
            self.assertIn(str(drivers[result['driver_id']]['checks']['references']), output)
        text = distribution_ten_review_text()
        self.assertEqual((ROOT/DISTRIBUTION_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['16,669', 'rate is not scale', 'not random-number generators',
                       'Singular density endpoints', 'monotonicity', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_system_spectral_drivers_keep_kernel_and_eigenvalue_scope_explicit(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-systems-spectra-ten-validation.json'}
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['gams_code'] for d in drivers.values()},
                         {'D2b1b', 'D2a1', 'D9a1', 'D9b1', 'D4a2', 'D4b2'})
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        self.assertEqual(class_tree(data)['D4b2']['parent'], 'D4b')
        self.assertEqual(class_tree(data)['D9b1']['parent'], 'D9b')
        for name in ['spd-solve', 'factored-spd-solve']:
            self.assertEqual(drivers['stdlib-'+name+'-reference']['checks']['solve_calls'], 288)
        generalized = drivers['stdlib-generalized-eig-reference']
        self.assertTrue(generalized['checks']['eigenvalues_only'])
        self.assertFalse(generalized['checks']['left_right_vectors'])
        source = (ROOT/generalized['path']).read_text()
        self.assertIn('call eig(a,b,values,err=err)', source)
        self.assertNotIn('right=', source)
        for name in ['cg', 'pcg', 'bicgstab']:
            driver = drivers['stdlib-'+name+'-kernel-reference']
            self.assertEqual(records[driver['procedure_id']]['procedure'], 'stdlib_solve_'+name+'_kernel')
            self.assertEqual(driver['checks']['systems'], 102)
            self.assertEqual(driver['checks']['interface'], 'public kernel with module-level callbacks')
            source = (ROOT/driver['path']).read_text()
            self.assertIn('module driver_operators', source)
            self.assertIn('operator%matvec=>multiply', source)
            self.assertIn('workspace=workspace', source)
            self.assertIn('if(any(matrix/=saved))', source)
        text = systems_spectra_ten_review_text()
        self.assertEqual((ROOT/SYSTEMS_SPECTRA_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['eigenvalue-only', 'real-only', 'segfaulted', 'module-level callbacks',
                       'No upstream numerical source was patched', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_system_spectral_failed_consumers_retain_exact_sources_and_full_results(self):
        import hashlib
        candidate = ROOT/'docs/gams-candidates/stdlib-systems'
        records = list(candidate.glob('*-result.json'))
        self.assertEqual(len(records), 6)
        for path in records:
            record = json.loads(path.read_text())
            self.assertEqual(record['revision'], '58eb9133966c2797e0593281169ef57c43eccc1d')
            source = (ROOT/record['source_path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            result = record['result']
            self.assertFalse(result['ok'])
            self.assertTrue(result['cache']['library_reused'])
            self.assertTrue(next(s for s in result['stages'] if s['name'] == 'Build')['ok'])
            run = next(s for s in result['stages'] if s['name'] == 'Run')
            self.assertFalse(run['ok'])
            if 'dense-wrapper' in path.name:
                self.assertIn('SIGSEGV', run['stderr'])
            if 'complex-vectors' in path.name:
                self.assertIn('F', run['stdout'].split())
                self.assertGreater(float(run['stdout'].split()[-1]), 0.3)

    def test_special_function_drivers_keep_normalization_precision_and_oracles_explicit(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-special-functions-ten-validation.json'}
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['gams_code'] for d in drivers.values()},
                         {'C3a2', 'C7a', 'C7b', 'C7e', 'C7f'})
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        self.assertEqual(class_tree(data)['C3a2']['parent'], 'C3a')
        self.assertEqual(class_tree(data)['C7f']['parent'], 'C7')
        self.assertEqual(drivers['stdlib-log-factorial-reference']['checks']['native_result_kind'], 'real32')
        self.assertEqual(drivers['stdlib-incomplete-beta-reference']['checks']['normalization'],
                         'regularized I_x(a,b)')
        for ident, key, count in [('legendre', 'derivative_references', 363),
                                  ('complex-gamma', 'complex_references', 24),
                                  ('complex-loggamma', 'complex_references', 24),
                                  ('log-factorial', 'references', 201),
                                  ('lower-gamma', 'reference_pairs', 264),
                                  ('upper-gamma', 'reference_pairs', 264),
                                  ('regularized-gamma', 'reference_pairs', 264),
                                  ('beta', 'references', 288), ('log-beta', 'references', 288),
                                  ('incomplete-beta', 'references', 2112)]:
            self.assertEqual(drivers['stdlib-'+ident+'-reference']['checks'][key], count)
        refs = json.loads((ROOT/'docs/gams-special-functions-ten-references.json').read_text())
        for name, points in refs['points'].items():
            self.assertEqual(len(points), 24)
            source = (ROOT/drivers['stdlib-'+name+'-reference']['path']).read_text()
            for point in points:
                self.assertIn(point['reference_real']+'_real64', source)
                self.assertIn(point['reference_imag']+'_real64', source)
                if name == 'complex-loggamma':
                    self.assertGreater(point['real'], 0)
        text = special_functions_ten_review_text()
        self.assertEqual((ROOT/SPECIAL_FUNCTIONS_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['returns REAL32', 'regularized I_x(a,b)', 'Rodrigues', 'binomial',
                       '80 decimal digits', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_factorization_rule_drivers_add_reviewed_stdlib_procedures(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-factorization-rules-ten-validation.json'}
        self.assertEqual(set(drivers), {
            'stdlib-qr-reference', 'stdlib-cholesky-reference', 'stdlib-eigh-reference',
            'stdlib-svd-reference', 'stdlib-pinv-reference', 'stdlib-matrix-norms-reference',
            'stdlib-expm-reference', 'stdlib-simpson-reference', 'stdlib-gauss-reference',
            'stdlib-lobatto-reference'})
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        self.assertEqual(class_tree(data)['D1b2']['parent'], 'D1b')
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertIn(record['id'], reviewed)
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        for ident, field, count in [
                ('stdlib-qr-reference', 'factorizations', 128),
                ('stdlib-cholesky-reference', 'factorizations', 112),
                ('stdlib-eigh-reference', 'eigenvalue_references', 528),
                ('stdlib-svd-reference', 'singular_value_references', 144),
                ('stdlib-pinv-reference', 'entry_references', 1120),
                ('stdlib-matrix-norms-reference', 'norm_references', 525),
                ('stdlib-expm-reference', 'entry_references', 858),
                ('stdlib-simpson-reference', 'integral_references', 432),
                ('stdlib-gauss-reference', 'moment_references', 462),
                ('stdlib-lobatto-reference', 'moment_references', 396)]:
            self.assertEqual(drivers[ident]['checks'][field], count)
        self.assertEqual(drivers['stdlib-expm-reference']['gams_code'], 'D')
        self.assertTrue(drivers['stdlib-simpson-reference']['checks']['odd_lengths_only'])
        text = factorization_rules_ten_review_text()
        self.assertEqual((ROOT/FACTORIZATION_RULES_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['first verification runs', 'positive-diagonal', 'all four Moore-Penrose',
                       'particular choice of factor signs', 'No arbitrary basis',
                       'not test the spectral 2-norm', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_statistics_services_drivers_add_reviewed_numerical_procedures(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-statistics-services-ten-validation.json'}
        self.assertEqual(set(drivers), {
            'stdlib-median-reference', 'stdlib-covariance-reference', 'stdlib-correlation-reference',
            'stdlib-moments-reference', 'stdlib-determinant-reference', 'stdlib-inverse-reference',
            'stdlib-trapezoid-reference', 'timer-brackets-reference', 'assert-enforcement-reference',
            'mpifx-identity-reference'})
        tree = class_tree(data)
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(class_evidence(tree, driver['gams_code'], [record], [driver])['status'], 'verified')
        expected_classes = {'L1a1c': 'L1a1', 'L1c1b': 'L1c1', 'L1c1': 'L1c',
                            'L1c': 'L1', 'D3a1': 'D3a', 'D3a': 'D3',
                            'H2a1b2': 'H2a1b', 'H2a1b': 'H2a1'}
        for code, parent in expected_classes.items():
            self.assertEqual(tree[code]['parent'], parent)
        reviewed = set(numerical_review(data=data)['packages']['stdlib']['procedure_ids'])
        self.assertTrue({d['procedure_id'] for d in drivers.values() if d['package_id'] == 'stdlib'} <= reviewed)
        for ident, field, count in [
                ('stdlib-median-reference', 'finite_medians', 768),
                ('stdlib-covariance-reference', 'matrix_entries', 1044),
                ('stdlib-correlation-reference', 'matrix_entries', 522),
                ('stdlib-moments-reference', 'value_references', 1152),
                ('stdlib-determinant-reference', 'matrices', 96),
                ('stdlib-inverse-reference', 'entry_references', 1152),
                ('stdlib-trapezoid-reference', 'integral_references', 864),
                ('timer-brackets-reference', 'timer_pairs', 16),
                ('assert-enforcement-reference', 'intentional_failure_children', 1),
                ('mpifx-identity-reference', 'mpi_processes', 1)]:
            self.assertEqual(drivers[ident]['checks'][field], count)
        text = statistics_services_ten_review_text()
        self.assertEqual((ROOT/STATISTICS_SERVICES_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['INT64 arithmetic', 'pairwise differences', 'nonzero exit',
                       'not a certification', '1.944083652', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_random_helper_range_failure_keeps_exact_probe_and_remains_unverified(self):
        import hashlib
        folder = ROOT/'docs/gams-candidates/test-helper-bounds'
        source = (folder/'driver.f90').read_text(encoding='utf-8')
        notes = (folder/'README.md').read_text(encoding='utf-8')
        result = json.loads((folder/'result.json').read_text(encoding='utf-8'))
        self.assertIn(hashlib.sha256(source.encode()).hexdigest(), notes)
        self.assertIn(result['packages'][0]['revision'], notes)
        self.assertFalse(result['ok'])
        self.assertTrue(result['cache']['library_reused'])
        self.assertTrue(result['stages'][0]['ok'])
        self.assertFalse(result['stages'][1]['ok'])
        self.assertIn('Requested bounds violated', result['stages'][1]['stderr'])
        record = next(r for r in gams_data()['procedure_mappings']
                      if r['id'] == 'fortran-test-helper-create-r64-array')
        self.assertNotIn('driver_id', record)

    def test_ten_workflow_drivers_keep_independent_oracles_and_scope(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-workflows-ten-validation.json'}
        self.assertEqual(set(drivers), {
            'argparse-options-reference', 'veggies-results-reference', 'system-files-reference',
            'tcl-sums-reference', 'julienne-diagnosis-reference', 'process-lines-reference',
            'gftl-prefix-reference', 'history-edit-reference', 'cli-namelist-reference', 'fy-list-reference'})
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        self.assertEqual(drivers['argparse-options-reference']['checks']['value_references'], 72)
        self.assertEqual(drivers['veggies-results-reference']['checks']['equality_cases'], 289)
        self.assertEqual(drivers['system-files-reference']['checks']['byte_lengths'], [0, 64])
        self.assertTrue(drivers['tcl-sums-reference']['checks']['syntax_rejection'])
        self.assertEqual(drivers['julienne-diagnosis-reference']['checks']['total_comparisons'], 1054)
        self.assertEqual(drivers['process-lines-reference']['checks']['record_references'], 170)
        self.assertEqual(drivers['gftl-prefix-reference']['checks']['value_references'], 55872)
        self.assertEqual(drivers['history-edit-reference']['checks']['buffer_length'], 1024)
        self.assertEqual(drivers['cli-namelist-reference']['checks']['value_references'], 224)
        self.assertTrue(drivers['fy-list-reference']['checks']['integer_insert_delete'])
        text = workflows_ten_review_text()
        self.assertEqual((ROOT/WORKFLOWS_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['first verification runs', 'integer inequalities', 'no failed service probes',
                       'executes no recorded text as shell code', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_ten_storage_drivers_keep_exact_references_and_scoped_limits(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-storage-ten-validation.json'}
        self.assertEqual(set(drivers), {
            'graph-storage-reference', 'smart-lifetime-reference', 'nc4-layout-reference',
            'regex-language-reference', 'lmdb-rollback-reference', 'aotus-config-reference',
            'gftl-container-reference', 'log-filter-reference', 'curl-url-reference',
            'netcdf-slices-reference'})
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        self.assertEqual(drivers['graph-storage-reference']['checks']['graphs'], 12)
        self.assertEqual(drivers['smart-lifetime-reference']['checks']['max_aliases'], 3)
        self.assertEqual(drivers['nc4-layout-reference']['checks']['value_references'], 420)
        self.assertEqual(drivers['nc4-layout-reference']['checks']['native_api'], 'C')
        self.assertEqual(drivers['regex-language-reference']['checks']['comparisons'], 680)
        self.assertEqual(drivers['lmdb-rollback-reference']['checks']['deleted_keys'], 21)
        self.assertEqual(drivers['aotus-config-reference']['checks']['value_references'], 160)
        self.assertEqual(drivers['gftl-container-reference']['checks']['value_references'], 49920)
        self.assertEqual(drivers['log-filter-reference']['checks']['accepted_records'], 64)
        self.assertEqual(drivers['curl-url-reference']['checks']['network_requests'], 0)
        self.assertEqual(drivers['netcdf-slices-reference']['checks']['value_references'], 420)
        text = storage_ten_review_text()
        self.assertEqual((ROOT/STORAGE_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['independently written character-state grammar',
                       'APIs share the native NetCDF library', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_storage_native_module_probe_remains_a_preparation_failure(self):
        import hashlib
        folder = ROOT/'docs/gams-candidates/storage-ten-native-module'
        source = (folder/'driver.f90').read_text(encoding='utf-8')
        notes = (folder/'README.md').read_text(encoding='utf-8')
        result = json.loads((folder/'result.json').read_text(encoding='utf-8'))
        self.assertIn(hashlib.sha256(source.encode()).hexdigest(), notes)
        self.assertIn(result['packages'][0]['revision'], notes)
        self.assertFalse(result['ok'])
        self.assertTrue(result['cache']['library_reused'])
        self.assertEqual([stage['name'] for stage in result['stages']], ['Build'])
        self.assertIn('Unable to find source for module dependency', result['stages'][0]['stderr'])

    def test_ten_interop_drivers_keep_independent_references_and_limits(self):
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        drivers = {d['id']: d for d in driver_data(data=data)
                   if d.get('validation_path') == 'docs/gams-interop-ten-validation.json'}
        self.assertEqual(set(drivers), {
            'rojff-json-reference', 'erloff-filter-reference', 'npy-payload-reference',
            'ftl-state-reference', 'unix-files-reference', 'os-path-reference',
            'lua53-stack-reference', 'forpy-numpy-reference', 'yaml-values-reference',
            'flook-table-reference'})
        for driver in drivers.values():
            record = records[driver['procedure_id']]
            self.assertEqual(record['driver_id'], driver['id'])
            self.assertEqual(class_evidence(class_tree(data), driver['gams_code'], [record], [driver])['status'],
                             'verified')
        self.assertEqual(drivers['rojff-json-reference']['checks']['typed_references'], 294)
        npy = drivers['npy-payload-reference']['checks']
        self.assertEqual(npy['payload_values'], 420)
        self.assertFalse(npy['package_reader_used'])
        self.assertEqual(drivers['ftl-state-reference']['checks']['checkpoints'], 1024)
        self.assertEqual(drivers['unix-files-reference']['checks']['byte_lengths'], [0, 128])
        self.assertEqual(drivers['os-path-reference']['checks']['files'], 33)
        self.assertEqual(drivers['lua53-stack-reference']['checks']['numeric_references'], 258)
        self.assertEqual(drivers['forpy-numpy-reference']['checks']['norm_relative_tolerance'], 1e-13)
        self.assertEqual(drivers['yaml-values-reference']['checks']['value_references'], 240)
        self.assertEqual(drivers['flook-table-reference']['checks']['numeric_references'], 306)
        text = interop_ten_review_text()
        self.assertEqual((ROOT/INTEROP_TEN_REPORT).read_text(encoding='utf-8'), text)
        for phrase in ['little-endian GNU/Linux', 'array-axis or memory-layout',
                       'consumer corrections', 'categories are not exhausted']:
            self.assertIn(phrase, text)

    def test_interop_failed_probes_preserve_hashes_pins_and_full_results(self):
        import hashlib
        folder = ROOT/'docs/gams-candidates/interop-ten-first-probes'
        notes = (folder/'README.md').read_text(encoding='utf-8')
        self.assertEqual(len(list(folder.glob('*.json'))), 2)
        for path in folder.glob('*.json'):
            source = path.with_suffix('.f90').read_text(encoding='utf-8')
            result = json.loads(path.read_text(encoding='utf-8'))
            self.assertIn(hashlib.sha256(source.encode()).hexdigest(), notes)
            self.assertIn(result['packages'][0]['revision'], notes)
            self.assertFalse(result['ok'])
            self.assertTrue(result['cache']['library_reused'])
            self.assertTrue(any(not stage['ok'] for stage in result['stages']))

    def test_ten_state_drivers_keep_nonempty_and_binary_only_scope(self):
        data = gams_data()
        records = {r['id']:r for r in data['procedure_mappings']}
        drivers = {d['id']:d for d in driver_data(data=data)
                   if d.get('validation_path')=='docs/gams-state-ten-validation.json'}
        self.assertEqual(set(drivers),{
            'array-bounds-reference','any-values-reference','fed-format-reference','keyvars-config-reference',
            'config-file-reference','fdict-values-reference','qcontainers-state-reference',
            'sqlite-transactions-reference','shunting-yard-reference','codata-photon-reference'})
        for d in drivers.values():
            r = records[d['procedure_id']]
            self.assertEqual(r['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[r],[d])['status'],'verified')
        self.assertEqual(drivers['array-bounds-reference']['checks']['arrays'],784)
        wrapped = drivers['any-values-reference']['checks']
        self.assertEqual(wrapped['value_references'],1712)
        self.assertFalse(wrapped['empty_arrays_verified'])
        self.assertFalse(wrapped['empty_strings_verified'])
        formats = drivers['fed-format-reference']['checks']
        self.assertEqual(formats['format_comparisons'],550)
        self.assertEqual(formats['zero_minimum_policy'],'omit .m')
        self.assertEqual(drivers['config-file-reference']['checks']['value_references'],228)
        self.assertEqual(drivers['fdict-values-reference']['checks']['typed_lookup_references'],488)
        containers = drivers['qcontainers-state-reference']['checks']
        self.assertEqual(containers['value_presence_references'],51080)
        self.assertTrue(containers['map_clear_reuse_verified'])
        self.assertFalse(containers['vector_clear_reuse_verified'])
        self.assertFalse(drivers['shunting-yard-reference']['checks']['unary_registration_verified'])
        self.assertEqual(drivers['sqlite-transactions-reference']['checks']['remaining_ordered_rows'],43)
        text = state_ten_review_text()
        self.assertEqual((ROOT/STATE_TEN_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['1,712','51,080','437','2.22045e-16','consumer reference errors',
                       'segfaulted at array extraction','Unary registration is intentionally absent',
                       'categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_photon_vectors_reproduce_exact_rational_references_and_hashes(self):
        import hashlib
        import importlib.util
        path = ROOT/'fpm_catalog/gams-drivers/references/photon_vectors.py'
        spec = importlib.util.spec_from_file_location('photon_reference',path)
        oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(oracle)
        vectors = json.loads(path.with_name('photon-vectors.json').read_text())
        self.assertEqual(oracle.vectors(),vectors)
        self.assertEqual(len(vectors['photons']),12)
        driver = next(d for d in driver_data() if d['id']=='codata-photon-reference')
        for name,sha in driver['checks']['reference_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode()).hexdigest(),sha)

    def test_state_batch_failed_consumers_retain_exact_sources_and_results(self):
        import hashlib
        folder = ROOT/'docs/gams-candidates/state-ten-first-probes'
        reports = list(folder.rglob('result.json'))
        self.assertGreaterEqual(len(reports),11)
        for path in reports:
            source = path.with_name('driver.f90').read_text(encoding='utf-8')
            notes = path.with_name('README.md').read_text(encoding='utf-8')
            report = json.loads(path.read_text())
            self.assertFalse(report['ok'],str(path))
            self.assertTrue(report['cache']['library_reused'])
            self.assertIn(hashlib.sha256(source.encode()).hexdigest(),notes)
            self.assertIn(report['packages'][0]['revision'],notes)
            self.assertTrue(any(not s['ok'] for s in report['stages']))

    def test_ten_data_drivers_record_exact_oracles_and_scoped_limits(self):
        data = gams_data()
        records = {r['id']:r for r in data['procedure_mappings']}
        drivers = {d['id']:d for d in driver_data(data=data)
                   if d.get('validation_path')=='docs/gams-data-ten-validation.json'}
        self.assertEqual(set(drivers),{
            'vector-edits-reference','integer-set-reference','linked-list-reference','scanner-cursor-reference',
            'tokenizer-fields-reference','enclose-delimiters-reference','rearray-growth-reference',
            'utf8-codepoints-reference','flibcpp-sort-search-reference','modbus-registers-reference'})
        for d in drivers.values():
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],d['id'])
            self.assertEqual(class_evidence(class_tree(data),d['gams_code'],[record],[d])['status'],'verified')
        self.assertEqual(drivers['vector-edits-reference']['checks']['element_references'],143017)
        self.assertFalse(drivers['vector-edits-reference']['checks']['unique_verified'])
        self.assertEqual(drivers['integer-set-reference']['checks']['value_references'],218354)
        self.assertFalse(drivers['integer-set-reference']['checks']['int64_sort_verified'])
        self.assertEqual(drivers['linked-list-reference']['checks']['typed_element_references'],601)
        self.assertFalse(drivers['linked-list-reference']['checks']['empty_iterator_verified'])
        self.assertEqual(drivers['scanner-cursor-reference']['checks']['checked_positions'],3232)
        self.assertFalse(drivers['scanner-cursor-reference']['checks']['empty_input_verified'])
        self.assertEqual(drivers['tokenizer-fields-reference']['checks']['retained_fields'],423)
        self.assertEqual(drivers['enclose-delimiters-reference']['checks']['fixtures'],2460)
        self.assertEqual(drivers['rearray-growth-reference']['checks']['scalar_references'],2096)
        self.assertEqual(drivers['utf8-codepoints-reference']['checks']['exact_checks'],825)
        self.assertFalse(drivers['utf8-codepoints-reference']['checks']['graphemes_verified'])
        self.assertEqual(drivers['flibcpp-sort-search-reference']['checks']['search_queries'],31980)
        self.assertFalse(drivers['flibcpp-sort-search-reference']['checks']['first_duplicate_match_verified'])
        self.assertEqual(drivers['modbus-registers-reference']['checks']['setter_checks'],1056)
        self.assertEqual(drivers['modbus-registers-reference']['checks']['getter_checks'],1056)
        self.assertFalse(drivers['modbus-registers-reference']['checks']['paired_roundtrip_only'])
        text = data_ten_review_text()
        self.assertEqual((ROOT/DATA_TEN_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['Ten independently written','143,017','218,354','31,980','compensating encoder/decoder',
                       'code points','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_pareto_and_diis_drivers_keep_successful_checks_with_explicit_limits(self):
        data = gams_data()
        records = {r['id']:r for r in data['procedure_mappings']}
        drivers = {d['id']:d for d in driver_data(data=data)}
        for ident,code in [('vtmop-pareto-reference','G2'),('ddpcm-jacobi-reference','D2')]:
            d = drivers[ident]
            r = records[d['procedure_id']]
            self.assertEqual(r['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[r],[d])['status'],'verified')
        diis = drivers['ddpcm-jacobi-reference']['checks']
        self.assertEqual((diis['linear_systems'],diis['scalar_reference_entries']),(192,1472))
        self.assertEqual(diis['diis_history'],[0,25])
        self.assertFalse(diis['small_history_bug_fixed'])
        self.assertFalse(diis['molecular_coupling_verified'])
        pareto = drivers['vtmop-pareto-reference']['checks']
        self.assertEqual((pareto['searches'],pareto['returned_points'],pareto['near_front_points']),(4,108,66))
        self.assertEqual(pareto['minimum_near_front_points_per_search'],5)
        self.assertTrue(pareto['identical_archives_for_two_seeds_observed'])
        self.assertFalse(pareto['entire_archive_uniform_accuracy_verified'])
        self.assertFalse(pareto['general_convergence_verified'])
        text = pareto_diis_review_text()
        self.assertEqual((ROOT/PARETO_DIIS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['192 solves','1,472 scalar','index -5','default history 25','66 points met',
                       '0.181848','not four demonstrably independent','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_pareto_and_diis_failed_probes_remain_exact_and_unsuccessful(self):
        import hashlib
        for name,fragment in [('ddpcm-diis-history',"Index '-5'"),
                               ('vtmop-archive-distance','VTMOP Pareto-segment distance')]:
            folder = ROOT/'docs/gams-candidates'/name
            source = (folder/'driver.f90').read_text(encoding='utf-8')
            report = json.loads((folder/'result.json').read_text())
            notes = (folder/'README.md').read_text(encoding='utf-8')
            self.assertIn(hashlib.sha256(source.encode()).hexdigest(),notes)
            self.assertIn(report['packages'][0]['revision'],notes)
            self.assertFalse(report['ok'])
            self.assertTrue(report['cache']['library_reused'])
            run = next(s for s in report['stages'] if s['name']=='Run')
            self.assertNotEqual(run['exit_code'],0)
            self.assertIn(fragment,run['stderr'])
            self.assertNotIn('PASS '+('ddpcm-jacobi-reference' if name.startswith('ddpcm') else 'vtmop-pareto-reference'),
                             run['stdout'])

    def test_lugre_and_torch_scope_keeps_private_fitting_and_training_unverified(self):
        data = gams_data()
        records = {r['id']:r for r in data['procedure_mappings']}
        drivers = {d['id']:d for d in driver_data(data=data)}
        for ident,code in [('friction-lugre-reference','I1'),('ftorch-affine-reference','K')]:
            d = drivers[ident]
            r = records[d['procedure_id']]
            self.assertEqual(r['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[r],[d])['status'],'verified')
        self.assertNotIn('driver_id',records['friction-internal-state'])
        self.assertNotIn('driver_id',records['friction-fit'])
        self.assertEqual(class_evidence(class_tree(data),'L8',[records['friction-fit']],list(drivers.values()))['status'],
                         'source-supported')
        lugre = drivers['friction-lugre-reference']['checks']
        self.assertEqual((lugre['histories'],lugre['segments'],lugre['reference_points']),(72,288,1440))
        self.assertFalse(lugre['private_fit_callbacks_verified'])
        self.assertFalse(lugre['parameter_fitting_verified'])
        torch = drivers['ftorch-affine-reference']['checks']
        self.assertEqual((torch['tensor_configurations'],torch['forward_calls'],torch['scalar_reference_entries']),
                         (10,130,1742))
        self.assertEqual(torch['asymmetric_permutations'],[[2,1],[2,3,1]])
        self.assertFalse(torch['nonlinear_model_verified'])
        self.assertFalse(torch['training_verified'])
        text = friction_torch_review_text()
        self.assertEqual((ROOT/FRICTION_TORCH_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['72 histories','1,440 requested','closed-form reference propagates its own exact endpoint',
                       'private callbacks and parameter fitting remain unverified','1,742 scalar',
                       'not verify a trained scientific model','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_torch_embedded_model_is_the_existing_auditable_affine_fixture(self):
        import hashlib
        import re
        import zipfile
        from io import BytesIO
        def model(path):
            text = path.read_text(encoding='utf-8')
            literal = text.split('character(*), parameter :: model_hex = &',1)[1].split('integer(int8) :: bytes',1)[0]
            return bytes.fromhex(''.join(re.findall("'([0-9a-fA-F]+)'",literal)))
        driver = next(d for d in driver_data() if d['id']=='ftorch-affine-reference')
        content = model(ROOT/driver['path'])
        self.assertEqual(content,model(ROOT/'fpm_catalog/demos/ftorch.f90'))
        self.assertEqual(len(content),1766)
        self.assertEqual(hashlib.sha256(content).hexdigest(),driver['checks']['existing_model_sha256'])
        with zipfile.ZipFile(BytesIO(content)) as archive:
            code = archive.read('tiny/code/__torch__.py').decode()
        self.assertIn('torch.add(torch.mul(x, 2.), 1.)',code)

    def test_helmholtz_and_stream_driver_scope_and_review(self):
        data = gams_data()
        drivers = {d['id']:d for d in driver_data(data=data)}
        records = {r['id']:r for r in data['procedure_mappings']}
        for ident,code in [('spherepack-helmholtz-reference','I2'),('rng-xoroshiro-reference','L6a21')]:
            d = drivers[ident]
            r = records[d['procedure_id']]
            self.assertEqual(r['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[r],[d])['status'],'verified')
        sphere = drivers['spherepack-helmholtz-reference']['checks']
        self.assertEqual(sphere['solves'],258)
        self.assertEqual(sphere['grid_point_references'],86000)
        self.assertTrue(sphere['nonzonal_modes_verified'])
        self.assertTrue(sphere['zero_mean_poisson_verified'])
        self.assertFalse(sphere['resonant_shifts_verified'])
        rng = drivers['rng-xoroshiro-reference']['checks']
        self.assertEqual(rng['integer_draws'],61440)
        self.assertEqual(rng['uniform_draws'],61440)
        self.assertEqual(rng['independent_hashes'],30)
        self.assertFalse(rng['statistical_quality_verified'])
        self.assertFalse(rng['normal_reseeding_fixed'])
        text = helmholtz_streams_review_text()
        self.assertEqual((ROOT/HELMHOLTZ_STREAMS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['258 solves','86,000 grid-point','zero-constant gauge','T**(2**64)',
                       'cached-normal reseeding defect remains unresolved','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_xoroshiro_oracle_vectors_hashes_and_matrix_powers(self):
        import hashlib
        import importlib.util
        path = ROOT/'fpm_catalog/gams-drivers/references/xoroshiro_vectors.py'
        spec = importlib.util.spec_from_file_location('xoroshiro_reference',path)
        oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(oracle)
        vectors = json.loads(path.with_name('xoroshiro-vectors.json').read_text())
        self.assertEqual(oracle.vectors(),vectors)
        columns = [oracle.transition(1<<bit) for bit in range(128)]
        for power in range(7):
            for seed in [1,1<<127,0xFEDCBA98765432100123456789ABCDEF]:
                expected = seed
                for _ in range(2**power):
                    expected = oracle.transition(expected)
                self.assertEqual(oracle.apply(columns,seed),expected)
            columns = [oracle.apply(columns,c) for c in columns]
        d = next(d for d in driver_data() if d['id']=='rng-xoroshiro-reference')
        for name,sha in d['checks']['reference_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode()).hexdigest(),sha)

    def test_fiats_and_ennuf_inference_keep_scalar_channel_and_model_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident in ['fiats-inference-reference','ennuf-inference-reference']:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),'K',[record],[d])['status'],'verified')
        fiats = drivers['fiats-inference-reference']['checks']
        self.assertEqual(fiats['networks'],48)
        self.assertEqual(fiats['inference_calls'],576)
        self.assertEqual(fiats['output_reference_entries'],792)
        self.assertEqual(fiats['exact_replay_entries'],72)
        self.assertTrue(fiats['real64_scalar_oracle'])
        self.assertTrue(fiats['output_layer_activated'])
        self.assertTrue(fiats['identity_range_maps_only'])
        self.assertFalse(fiats['nonidentity_range_maps_verified'])
        ennuf = drivers['ennuf-inference-reference']['checks']
        self.assertEqual(ennuf['pipeline_batches'],2640)
        self.assertEqual(ennuf['dense_calls'],5940)
        self.assertEqual(ennuf['all_stage_reference_entries'],35200)
        self.assertEqual(ennuf['final_layer_reference_entries'],10560)
        self.assertEqual(ennuf['channels'],[1,2,5])
        self.assertTrue(ennuf['stable_softmax_reference'])
        self.assertFalse(ennuf['extreme_softmax_logits_verified'])
        text = inference_pairs_review_text()
        self.assertEqual((ROOT/INFERENCE_PAIRS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['48 fixed networks','792 output entries','2,640 pipeline batches','35,200 layer-output',
                       'stabilization is in the reference','not a trained scientific surrogate',
                       'categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_ennuf_generated_reference_uses_the_existing_pinned_asset(self):
        import hashlib
        d = next(d for d in driver_data() if d['id']=='ennuf-inference-reference')
        checks = d['checks']
        self.assertEqual(checks['generated_model_evaluations'],81)
        self.assertEqual(checks['generated_model_relu_region_counts'],[21,29,14,17])
        self.assertFalse(checks['external_model_conversion_verified'])
        self.assertFalse(checks['training_verified'])
        path = ROOT/checks['generated_asset_path']
        self.assertEqual(hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest(),
                         checks['generated_asset_sha256'])
        package = next(p for p in json.loads((ROOT/'fpm_catalog.json').read_text())['packages'] if p['id']=='ennuf')
        recipe = package['catalog_build']['source_packages']['metoffice/ennuf']['generated']
        self.assertEqual(recipe['sha256'],checks['generated_asset_sha256'])
        self.assertEqual(recipe['asset'],path.name)

    def test_radial_states_and_dense_layers_keep_independent_reference_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('dftatom-hydrogen-reference','I1'),('athena-dense-reference','K')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        radial = drivers['dftatom-hydrogen-reference']['checks']
        self.assertEqual(radial['eigenproblems'],36)
        self.assertEqual(radial['P_reference_entries'],135036)
        self.assertEqual(radial['Q_reference_entries'],135036)
        self.assertEqual(radial['nuclear_charges'],[1,2,4])
        self.assertEqual(radial['moment_references'],72)
        self.assertTrue(radial['common_wavefunction_sign_alignment'])
        self.assertTrue(radial['independent_trapezoidal_integrals'])
        self.assertFalse(radial['relativistic_dirac_verified'])
        dense = drivers['athena-dense-reference']['checks']
        self.assertEqual(dense['layers'],192)
        self.assertEqual(dense['output_reference_entries'],4928)
        self.assertEqual(dense['exact_replay_entries'],448)
        self.assertEqual(dense['forward_calls'],2304)
        self.assertTrue(dense['real64_scalar_oracle'])
        self.assertTrue(dense['persistent_input_marked_non_temporary'])
        self.assertFalse(dense['training_verified'])
        self.assertFalse(dense['dataset_approximation_quality_verified'])
        text = radial_dense_review_text()
        self.assertEqual((ROOT/RADIAL_DENSE_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['36 eigenproblems','135,036 P entries','135,036 Q entries','192 fixed layers',
                       '4,928 independent output entries','is_temporary=.false.','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_temporary_athena_input_probe_is_preserved_as_a_consumer_error(self):
        import hashlib
        probe = json.loads((ROOT/'docs/gams-candidates/athena-temporary-input/temporary-input-result.json').read_text())
        source = (ROOT/probe['source_path']).read_text(encoding='utf-8')
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),probe['source_sha256'])
        self.assertFalse(probe['result']['ok'])
        self.assertTrue(probe['result']['cache']['library_reused'])
        self.assertEqual(probe['revision'],next(r['revision'] for r in gams_data()['procedure_mappings']
                                               if r['id']=='athena-dense'))
        run = next(s for s in probe['result']['stages'] if s['name']=='Run')
        self.assertIn('invalid pointer',run['stderr'])
        self.assertIn('SIGABRT',run['stderr'])
        good = (ROOT/'fpm_catalog/gams-drivers/athena-dense-reference.f90').read_text()
        self.assertIn('feature(1,1)%is_temporary=.false.',good)
        self.assertNotIn('feature(1,1)%is_temporary=.false.',source)

    def test_tangent_and_block_drivers_keep_analytic_and_serial_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('fatode-tangent-reference','I1'),('dbcsr-products-reference','D1')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        tangent = drivers['fatode-tangent-reference']['checks']
        self.assertEqual(tangent['integrations'],540)
        self.assertEqual(tangent['state_entries'],2160)
        self.assertEqual(tangent['tangent_entries'],8640)
        self.assertEqual(tangent['methods'],[4,6])
        self.assertTrue(tangent['analytic_jacobian_used'])
        self.assertTrue(tangent['tangent_error_control_enabled'])
        self.assertTrue(tangent['backward_time_checked'])
        self.assertFalse(tangent['stiff_integrators_verified'])
        product = drivers['dbcsr-products-reference']['checks']
        self.assertEqual(product['products'],32)
        self.assertEqual(product['scalar_reference_entries'],496)
        self.assertEqual(product['transpose_pairs'],['NN','NT','TN','TT'])
        self.assertTrue(product['independent_scalar_loop_reference'])
        self.assertTrue(product['native_diagnostics_retained'])
        self.assertFalse(product['full_scalar_cartesian_product_verified'])
        self.assertFalse(product['mpi_verified'])
        text = tangents_blocks_review_text()
        self.assertEqual((ROOT/TANGENTS_BLOCKS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['540 integrations','8,640 tangent entries','535,978','32 products','496 scalar reference',
                       '200,000-byte output limit','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_dbcsr_consumer_and_output_limit_probes_remain_distinct_from_accuracy_failures(self):
        import hashlib
        for path,diagnostic in [('dbcsr-consumer-intent/read-only-handle-result.json','no specific subroutine'),
                                ('dbcsr-output-limit/full-cartesian-result.json','200000-byte stage limit')]:
            probe = json.loads((ROOT/'docs/gams-candidates'/path).read_text(encoding='utf-8'))
            source = (ROOT/probe['source_path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),probe['source_sha256'])
            self.assertFalse(probe['result']['ok'])
            self.assertTrue(probe['result']['cache']['library_reused'])
            self.assertEqual(probe['revision'],next(r['revision'] for r in gams_data()['procedure_mappings']
                                                   if r['id']=='dbcsr-block-multiply'))
            stages = json.dumps(probe['result']['stages'])
            self.assertIn(diagnostic,stages)
        report = json.loads((ROOT/'docs/gams-tangents-blocks-validation.json').read_text(encoding='utf-8'))
        product = next(d for d in report['drivers'] if d['driver_id']=='dbcsr-products-reference')
        run = next(s for s in product['stages'] if s['name']=='Run')
        self.assertTrue(run['ok'])
        self.assertIn('array temporary',run['stderr'])
        self.assertIn('PASS dbcsr-products-reference',run['stdout'])

    def test_kiss_and_spacing_references_keep_distribution_and_arithmetic_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('rndgen-kiss-reference','L6a21'),('pointsets-random-reference','L6')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        kiss = drivers['rndgen-kiss-reference']['checks']
        self.assertEqual(kiss['uniform_outputs'],28672)
        self.assertEqual(kiss['exact_prefix_entries'],56)
        self.assertEqual(kiss['independent_stream_checksums'],7)
        self.assertEqual(kiss['saved_state_replay_entries'],1799)
        self.assertTrue(kiss['independent_integer_reference'])
        self.assertFalse(kiss['cross_compiler_wraparound_verified'])
        spacing = drivers['pointsets-random-reference']['checks']
        self.assertEqual(spacing['fixtures'],63)
        self.assertEqual(spacing['reference_coordinates'],1584)
        self.assertEqual(spacing['empty_singleton_noop_fixtures'],18)
        self.assertEqual(spacing['three_point_law_samples'],60000)
        self.assertTrue(spacing['random_state_consumption_checked'])
        self.assertFalse(spacing['uniform_order_statistics_verified'])
        self.assertEqual(records['pointsets-random-spacing']['gams_codes'],['L6'])
        self.assertNotEqual(class_evidence(class_tree(data),'L6a21',
                            [records['pointsets-random-spacing']],[drivers['pointsets-random-reference']])['status'],
                            'verified')
        text = random_references_review_text()
        self.assertEqual((ROOT/RANDOM_REFERENCES_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['28,672 outputs','63 fixtures','60,000 law samples','not a collision-free',
                       'not uniform draws or uniform order statistics','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_independent_kiss_vectors_match_the_verified_consumer_constants(self):
        import hashlib
        import subprocess
        import sys
        d = next(d for d in driver_data() if d['id']=='rndgen-kiss-reference')
        for path,digest in d['checks']['reference_files'].items():
            source = (ROOT/path).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),digest)
        result = subprocess.run([sys.executable,'-X','utf8',
                    str(ROOT/'fpm_catalog/gams-drivers/references/kiss_vectors.py')],
                    cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('consumer constants agree',result.stdout)

    def test_feasible_directions_and_annealing_keep_reference_and_failure_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('conmin-ball-reference','G2h3b1b'),('annealing-rastrigin-reference','G2i')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        directions = drivers['conmin-ball-reference']['checks']
        self.assertEqual(directions['problems'],48)
        self.assertEqual(directions['optimizer_entries'],160)
        self.assertEqual(directions['analytic_derivative_mode'],1)
        self.assertEqual(directions['user_gradient_requests'],426)
        self.assertTrue(directions['noncollinear_feasible_infeasible_starts_checked'])
        self.assertTrue(directions['analytic_multipliers_checked'])
        self.assertFalse(directions['multiple_constraints_verified'])
        annealing = drivers['annealing-rastrigin-reference']['checks']
        self.assertEqual(annealing['runs'],6)
        self.assertEqual(annealing['global_minimizer_entries'],12)
        self.assertEqual(annealing['objective_callbacks'],271406)
        self.assertEqual(annealing['main_loop_runs'],1)
        self.assertEqual(annealing['seed_pairs'],[[1,2],[1234,5678],[91,2718]])
        self.assertTrue(annealing['callback_counts_checked'])
        self.assertFalse(annealing['known_minimum_early_stop_enabled'])
        self.assertFalse(annealing['three_dimensional_global_search_verified'])
        self.assertFalse(annealing['multiple_main_loop_runs_verified'])
        text = directions_fitting_review_text()
        self.assertEqual((ROOT/DIRECTIONS_FITTING_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('[Verification](gams-directions-fitting-validation.json)',constrained_review_text())
        for phrase in ['48 problems','NFDG=1','six two-dimensional','271,406','0.994959',
                       '0.7499999991182843','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_failed_friction_and_annealing_probes_are_preserved_without_false_verification(self):
        import hashlib
        data = gams_data()
        records = {r['id']: r for r in data['procedure_mappings']}
        self.assertNotIn('driver_id',records['friction-fit'])
        drivers = driver_data(data=data)
        self.assertEqual(class_evidence(class_tree(data),'L8',[records['friction-fit']],drivers)['status'],
                         'source-supported')
        paths = ['friction-double-subtraction/fit-result.json','annealing-loop-count/zero-loops-result.json',
                 'annealing-finite-budget/one-loop-result.json','annealing-finite-budget/slow-one-loop-result.json',
                 'annealing-reset-objective/two-loops-result.json']
        for path in paths:
            probe = json.loads((ROOT/'docs/gams-candidates'/path).read_text(encoding='utf-8'))
            source = (ROOT/probe['source_path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),probe['source_sha256'])
            self.assertFalse(probe['result']['ok'])
            self.assertTrue(probe['result']['cache']['library_reused'])
            self.assertEqual(probe['revision'],next(p['revision'] for p in
                             json.loads((ROOT/'fpm_catalog.json').read_text())['packages']
                             if p['id']==probe['package_id']))
        fit = json.loads((ROOT/'docs/gams-candidates/friction-double-subtraction/fit-result.json').read_text())
        run = next(s for s in fit['result']['stages'] if s['name']=='Run')
        self.assertIn('7.499999991182843E-01',run['stdout'])
        self.assertIn('known Coulomb fit differs',run['stderr'])
        self.assertNotIn('friction-fit-reference',{d['id'] for d in drivers})

    def test_halfspace_and_affine_training_drivers_keep_analytic_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('optgra-halfspace-reference','G2h3b1b'),('neural-affine-reference','G1b')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        projection = drivers['optgra-halfspace-reference']['checks']
        self.assertEqual(projection['problems'],48)
        self.assertEqual(projection['optimizer_entries'],160)
        self.assertTrue(projection['analytic_multipliers_checked'])
        self.assertTrue(projection['analytic_derivative_callbacks_checked'])
        self.assertFalse(projection['nonlinear_constraints_verified'])
        training = drivers['neural-affine-reference']['checks']
        self.assertEqual(training['runs'],24)
        self.assertEqual(training['prediction_entries'],3168)
        self.assertTrue(training['network_train_called'])
        self.assertTrue(training['full_batch_and_stochastic_checked'])
        self.assertTrue(training['real64_prediction_oracle'])
        self.assertFalse(training['nonlinear_networks_verified'])
        self.assertFalse(training['general_optimizer_verified'])
        text = projection_training_review_text()
        self.assertEqual((ROOT/PROJECTION_TRAINING_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('[Verification](gams-projection-training-validation.json)',constrained_review_text())
        for phrase in ['48 projections','24 training runs','3,168 output entries','Varder=1',
                       'random contiguous batches with replacement','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_gradient_and_swarm_drivers_keep_lagged_objective_and_seed_limits_explicit(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('fortimize-gradient-reference','G1b'),('opti-rastrigin-reference','G2i')]:
            d = drivers[ident]
            self.assertEqual(records[d['procedure_id']]['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[records[d['procedure_id']]],[d])['status'],'verified')
        gradient = drivers['fortimize-gradient-reference']['checks']
        self.assertEqual(gradient['runs'],240)
        self.assertEqual(gradient['analytic_iterate_entries'],800)
        self.assertTrue(gradient['gradient_call_counts_checked'])
        self.assertTrue(gradient['returned_objective_lags_one_iteration'])
        self.assertTrue(gradient['endpoint_objective_recomputed'])
        self.assertFalse(gradient['adaptive_stopping_verified'])
        swarm = drivers['opti-rastrigin-reference']['checks']
        self.assertEqual(swarm['runs'],12)
        self.assertEqual(swarm['global_minimizer_entries'],30)
        self.assertEqual(swarm['seeds'],[314159,271828,161803])
        self.assertTrue(swarm['independent_objective_identity_checked'])
        self.assertFalse(swarm['global_convergence_guaranteed'])
        self.assertFalse(swarm['cross_compiler_rng_reproducibility_verified'])
        text = gradient_swarm_review_text()
        self.assertEqual((ROOT/GRADIENT_SWARM_REPORT).read_text(encoding='utf-8'),text)
        self.assertIn('[Verification](gams-gradient-swarm-validation.json)',constrained_review_text())
        for phrase in ['240 runs','800 coordinate','644,800','0.625','0.15625','licensing remains unspecified',
                       'not a global-convergence guarantee','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_projection_and_lbfgs_drivers_have_analytic_answers_and_precision_limits(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('psqp-projection-reference','G2h3b1b'),('seiscope-lbfgs-reference','G1b1b')]:
            d = drivers[ident]
            self.assertEqual(records[d['procedure_id']]['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[records[d['procedure_id']]],[d])['status'],'verified')
        projection = drivers['psqp-projection-reference']['checks']
        self.assertEqual(projection['problems'],48)
        self.assertEqual(projection['optimizer_entries'],160)
        self.assertTrue(projection['analytic_multipliers_checked'])
        self.assertTrue(projection['user_gradient_calls_checked'])
        self.assertTrue(projection['feasible_infeasible_starts_checked'])
        self.assertFalse(projection['box_active_optima_verified'])
        self.assertFalse(projection['nonconvex_constraints_verified'])
        lbfgs = drivers['seiscope-lbfgs-reference']['checks']
        self.assertEqual(lbfgs['problems'],108)
        self.assertEqual(lbfgs['minimizer_entries'],360)
        self.assertTrue(lbfgs['independent_real64_callback_audit'])
        self.assertTrue(lbfgs['existing_catalog_fix_reused'])
        self.assertFalse(lbfgs['nonquadratic_objectives_verified'])
        self.assertFalse(lbfgs['constrained_operation_verified'])
        text = projection_lbfgs_review_text()
        self.assertEqual((ROOT/PROJECTION_LBFGS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['48 problems','108 minimizations','independent analytic multipliers','real32',
                       'uninitialized workspace-length','statuses 1 through 4','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_sparse_updates_and_symmetric_spectra_keep_limited_scope(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('lusol-update-reference','D2a4'),('scalapackfx-eigen-reference','D4a1')]:
            d = drivers[ident]
            self.assertEqual(records[d['procedure_id']]['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[records[d['procedure_id']]],[d])['status'],'verified')
        sparse = drivers['lusol-update-reference']['checks']
        self.assertEqual(sparse['factorizations'],32)
        self.assertEqual(sparse['column_replacements'],32)
        self.assertEqual(sparse['solves'],384)
        self.assertEqual(sparse['known_solution_entries'],1728)
        self.assertTrue(sparse['normal_transpose_checked'])
        self.assertFalse(sparse['sequential_updates_checked'])
        spectral = drivers['scalapackfx-eigen-reference']['checks']
        self.assertEqual(spectral['eigensystems'],384)
        self.assertEqual(spectral['eigenvalue_references'],1728)
        self.assertTrue(spectral['unused_triangle_nan_checked'])
        self.assertTrue(spectral['repeated_eigenvalues_checked'])
        self.assertEqual(spectral['mpi_processes'],1)
        self.assertFalse(spectral['distributed_execution_verified'])
        candidate = ROOT/'docs/gams-candidates/lusol-drop-tolerance'
        meta = json.loads((candidate/'drop-reference.json').read_text())
        self.assertEqual(hashlib.sha256((candidate/meta['source']).read_text().encode()).hexdigest(),meta['source_sha256'])
        result = json.loads((candidate/'drop-reference-result.json').read_text())
        self.assertFalse(result['ok'])
        self.assertTrue(next(s for s in result['stages'] if s['name']=='Build')['ok'])
        self.assertIn('known sparse solution',next(s for s in result['stages'] if s['name']=='Run')['stderr'])
        text = sparse_spectra_review_text()
        self.assertEqual((ROOT/SPARSE_SPECTRA_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['384 solves','1,728','quiet NaNs','not an established algorithm defect',
                       'relaxed comparison','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_multidimensional_fft_references_include_independent_inverse_and_layouts(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,total in [('dtfft-2d-reference',2952),('decomp-3d-reference',4896)]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),'J1',[record],[d])['status'],'verified')
            c = d['checks']
            self.assertEqual(c['fixtures'],24)
            self.assertEqual(c['transform_calls'],72)
            self.assertEqual(c['total_complex_references'],total)
            self.assertEqual(c['mpi_processes'],1)
            self.assertTrue(c['independent_inverse_input'])
            self.assertTrue(c['off_origin_impulse_checked'])
            self.assertTrue(c['axis_dependent_modes_checked'])
            self.assertFalse(c['distributed_execution_verified'])
            self.assertFalse(c['real_transforms_verified'])
            self.assertNotEqual(class_evidence(class_tree(data),'J1a2',[record],[d])['status'],'verified')
        dtfft = drivers['dtfft-2d-reference']['checks']
        self.assertTrue(dtfft['fourier_output_axes_reversed'])
        self.assertTrue(dtfft['fresh_plan_per_shape'])
        self.assertFalse(dtfft['destroyed_plan_recreation_verified'])
        candidate = ROOT/'docs/gams-candidates/dtfft-plan-recreate'
        meta = json.loads((candidate/'plan-recreate.json').read_text())
        self.assertEqual(hashlib.sha256((candidate/meta['source']).read_text().encode()).hexdigest(),
                         meta['source_sha256'])
        result = json.loads((candidate/'plan-recreate-result.json').read_text())
        self.assertFalse(result['ok'])
        self.assertTrue(next(s for s in result['stages'] if s['name']=='Build')['ok'])
        self.assertIn('already allocated',next(s for s in result['stages'] if s['name']=='Run')['stderr'])
        text = multidimensional_fft_review_text()
        self.assertEqual((ROOT/MULTIDIMENSIONAL_FFT_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['2,952','4,896','Y-aligned pencil','self%fft_mapping','scandir(/sys/class/net)',
                       'No comparison was relaxed','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_products_and_partitions_keep_exact_objectives_and_option_failures(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('formatmul-products-reference','D1'),('metis-kway-reference','P')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        products = drivers['formatmul-products-reference']['checks']
        self.assertEqual(products['matrix_matrix_calls'],360)
        self.assertEqual(products['matrix_vector_calls'],216)
        self.assertEqual(products['scalar_product_entries'],6588)
        self.assertTrue(products['exact_dyadic_checks'])
        self.assertFalse(products['single_transpose_flag_matrix_calls_verified'])
        self.assertFalse(products['distributed_execution_verified'])
        partitions = drivers['metis-kway-reference']['checks']
        self.assertEqual(partitions['partition_calls'],108)
        self.assertEqual(partitions['assigned_vertices'],3024)
        self.assertEqual(partitions['weighted_cut_references'],108)
        self.assertTrue(partitions['typed_imbalance_argument_used'])
        self.assertTrue(partitions['csr_preservation_checked'])
        self.assertFalse(partitions['global_optimality_verified'])
        self.assertFalse(partitions['mesh_partitioning_verified'])
        candidate = ROOT/'docs/gams-candidates/metis-option-indices'
        meta = json.loads((candidate/'option-indices.json').read_text())
        self.assertEqual(hashlib.sha256((candidate/meta['source']).read_text().encode()).hexdigest(),
                         meta['source_sha256'])
        self.assertNotEqual(meta['fortran_ufactor_index'],meta['c_ufactor_index'])
        result = json.loads((candidate/'option-indices-result.json').read_text())
        self.assertFalse(result['ok'])
        self.assertTrue(next(s for s in result['stages'] if s['name']=='Build')['ok'])
        self.assertIn('Incorrect numflag',next(s for s in result['stages'] if s['name']=='Run')['stdout'])
        text = products_partitions_review_text()
        self.assertEqual((ROOT/PRODUCTS_PARTITIONS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['6,588','3,024','coarse population check','not prove global optimality',
                       'ubvec=[1.1_real_t]','single-false-transpose-flag','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_sparse_bicg_and_advection_keep_independent_answers_and_k2_scope(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('heatflow-bicg-reference','D2'),('hrweno-advection-reference','I2')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        sparse = drivers['heatflow-bicg-reference']['checks']
        self.assertEqual(sparse['matrices'],36)
        self.assertEqual(sparse['solves'],216)
        self.assertEqual(sparse['known_solution_entries'],3456)
        self.assertTrue(sparse['nonsymmetric_systems_checked'])
        self.assertTrue(sparse['nonzero_initial_guess_checked'])
        self.assertFalse(sparse['pde_evolution_verified'])
        self.assertEqual(class_evidence(class_tree(data),'I2',[records['heatflow-evolution']],
                                       [drivers['heatflow-bicg-reference']])['status'],'source-supported')
        advection = drivers['hrweno-advection-reference']['checks']
        self.assertEqual(advection['problems'],72)
        self.assertEqual(advection['analytic_cell_average_references'],21504)
        self.assertEqual(advection['weno_k'],[3])
        self.assertTrue(advection['exact_reference_at_returned_time'])
        self.assertTrue(advection['both_advection_directions_checked'])
        self.assertFalse(advection['k2_verified'])
        self.assertFalse(advection['shocks_verified'])
        candidate = ROOT/'docs/gams-candidates/hrweno-k2-accuracy'
        meta = json.loads((candidate/'advection-reference.json').read_text())
        self.assertEqual(hashlib.sha256((candidate/meta['source']).read_text().encode()).hexdigest(),
                         meta['source_sha256'])
        result = json.loads((candidate/'advection-reference-result.json').read_text())
        self.assertFalse(result['ok'])
        self.assertTrue(next(s for s in result['stages'] if s['name']=='Build')['ok'])
        self.assertIn('analytic cell-average solution',next(s for s in result['stages'] if s['name']=='Run')['stderr'])
        text = sparse_advection_review_text()
        self.assertEqual((ROOT/SPARSE_ADVECTION_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['3,456','21,504','actual returned time','not an established algorithm defect',
                       'no comparison was relaxed','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_unsigned_and_bitset_drivers_keep_exact_checks_and_sibling_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('uint-arithmetic-reference','A1'),('orbs-bitwise-reference','N2')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        integers = drivers['uint-arithmetic-reference']['checks']
        self.assertEqual(integers['widths'],[8,16,32])
        self.assertEqual(integers['operand_pairs'],1728)
        self.assertEqual(integers['exact_checks'],17307)
        self.assertTrue(integers['six_comparisons_checked'])
        self.assertFalse(integers['multiplication_verified'])
        self.assertFalse(integers['uint64_verified'])
        bits = drivers['orbs-bitwise-reference']['checks']
        self.assertEqual(bits['operand_pairs'],2816)
        self.assertEqual(bits['binary_string_references'],37760)
        self.assertIn(129,bits['widths'])
        self.assertTrue(bits['all_documented_interior_shifts_checked'])
        self.assertFalse(bits['mixed_widths_verified'])
        self.assertFalse(bits['invalid_input_verified'])
        self.assertEqual(class_evidence(class_tree(data),'A1',[records['orbs-bitsets']],
                                       [drivers['orbs-bitwise-reference']])['status'],'source-supported')
        text = unsigned_bitsets_review_text()
        self.assertEqual((ROOT/UNSIGNED_BITSETS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['17,307','37,760','schoolbook carry/borrow','patterns can coincide'.capitalize(),
                       'Mixed widths','categories are not exhausted','Multiplication, powers']:
            self.assertIn(phrase,text)

    def test_expressions_and_sky_have_independent_references_and_limited_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('feq-expression-reference','N3'),('astro-sky-reference','P')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        parser = drivers['feq-expression-reference']['checks']
        self.assertEqual(parser['expressions'],12)
        self.assertEqual(parser['formula_references'],16464)
        self.assertTrue(parser['scalar_batch_checked'])
        self.assertTrue(parser['reordered_variables_checked'])
        self.assertFalse(parser['invalid_input_verified'])
        self.assertFalse(parser['symbolic_algebra_verified'])
        sky = drivers['astro-sky-reference']['checks']
        self.assertEqual(sky['direction_fixtures'],1296)
        self.assertEqual(sky['conversion_calls'],2592)
        self.assertEqual(sky['angle_range_roundoff_absolute_eps_factor'],64)
        self.assertTrue(sky['poles_checked'])
        self.assertFalse(sky['pole_longitude_identity_required'])
        self.assertFalse(sky['physical_frame_accuracy_verified'])
        text = expressions_sky_review_text()
        self.assertEqual((ROOT/EXPRESSIONS_SKY_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['16,464','1,296','array-temporary warnings','exactly 2*pi','64 real64',
                       'does not copy the library matrix','categories are not exhausted']:
            self.assertIn(phrase,text)

    def test_polynomial_calculus_and_periodic_distances_keep_skew_failure_separate(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('formal-polynomial-reference','H1'),('raffle-orthogonal-reference','P')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        formal = drivers['formal-polynomial-reference']['checks']
        self.assertEqual(formal['field_pairs'],162)
        self.assertEqual(formal['pointwise_derivative_references'],24354)
        self.assertEqual(formal['analytic_integral_references'],486)
        self.assertEqual(formal['orders'],[2,4])
        self.assertEqual(formal['images'],1)
        self.assertFalse(formal['pde_solver_verified'])
        self.assertFalse(formal['nonpolynomial_convergence_verified'])
        self.assertFalse(formal['multi_image_verified'])
        self.assertEqual(class_evidence(class_tree(data),'I2',[records['formal-divergence']],
                                       [drivers['formal-polynomial-reference']])['status'],'source-supported')
        periodic = drivers['raffle-orthogonal-reference']['checks']
        self.assertEqual(periodic['cell_queries'],360)
        self.assertEqual(periodic['distance_references'],2520)
        self.assertEqual(periodic['image_offsets_per_axis'],[-4,4])
        self.assertTrue(periodic['exact_atom_queries_checked'])
        self.assertTrue(periodic['rotated_orthogonal_cells_checked'])
        self.assertTrue(periodic['failed_skew_probe_preserved'])
        self.assertFalse(periodic['general_skew_cells_verified'])
        self.assertNotIn('raffle-skew-probe',drivers)
        candidate = ROOT/'docs/gams-candidates/raffle-skew'
        meta = json.loads((candidate/'skew-image-reference.json').read_text())
        source = (candidate/meta['source']).read_text(encoding='utf-8').encode()
        self.assertEqual(hashlib.sha256(source).hexdigest(),meta['source_sha256'])
        result = json.loads((candidate/'skew-image-reference-result.json').read_text())
        self.assertFalse(result['ok'])
        self.assertTrue(next(s for s in result['stages'] if s['name']=='Build')['ok'])
        run = next(s for s in result['stages'] if s['name']=='Run')
        self.assertIn('skew-cell nearest-image mismatch',run['stderr'])
        text = periodic_calculus_review_text()
        self.assertEqual((ROOT/PERIODIC_CALCULUS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['24,354','2,520','2e-4+2/n**2','real32','enhancements clause',
                       '729 integer image offsets','0.31679647220910667','not registered as a checked driver']:
            self.assertIn(phrase,text)

    def test_gmres_and_ntpoly_inverse_have_independent_answers_and_limited_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident in ['lightkrylov-gmres-reference','ntpoly-inverse-reference']:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),'D2',[record],[d])['status'],'verified')
        gmres = drivers['lightkrylov-gmres-reference']['checks']
        self.assertEqual(gmres['gmres_solves'],288)
        self.assertEqual(gmres['known_solution_entries'],2016)
        self.assertEqual(gmres['multiple_outer_cycle_solves'],100)
        self.assertTrue(gmres['normal_transpose_checked'])
        self.assertTrue(gmres['nonzero_initial_guess_checked'])
        self.assertTrue(gmres['actual_restart_cycles_required'])
        self.assertFalse(gmres['zero_rhs_exact_initial_verified'])
        self.assertFalse(gmres['preconditioners_verified'])
        inverse = drivers['ntpoly-inverse-reference']['checks']
        self.assertEqual(inverse['spd_inversions'],48)
        self.assertEqual(inverse['analytic_inverse_entries'],1224)
        self.assertEqual(inverse['prescribed_condition_numbers'],[2,10,50])
        self.assertEqual(inverse['mpi_processes'],1)
        self.assertTrue(inverse['left_right_identity_checked'])
        self.assertTrue(inverse['input_preservation_checked'])
        self.assertFalse(inverse['nonsymmetric_indefinite_verified'])
        self.assertFalse(inverse['singular_inputs_verified'])
        self.assertFalse(inverse['multi_process_verified'])
        text = gmres_inverse_review_text()
        self.assertEqual((ROOT/GMRES_INVERSE_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['2,016','1,224','100 such solves','true residuals','DTRTRS','UCX discovery',
                       'no returned convergence-status','MPI_SUCCESS','one-process configuration']:
            self.assertIn(phrase,text)
        self.assertIn('GMRES and inverse review',linear_algebra_review_text())

    def test_propack_and_fmm_drivers_use_spectra_and_direct_kernel_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('propack-spectrum-reference','D6'),('fmm2d-laplace-reference','D1')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        svd = drivers['propack-spectrum-reference']['checks']
        self.assertEqual(svd['partial_svd_calls'],108)
        self.assertEqual(svd['leading_triplets'],216)
        self.assertEqual(svd['row_offsets'],[-3,0,3])
        self.assertEqual(svd['requested_triplets'],[1,3])
        self.assertTrue(svd['two_sided_residuals_checked'])
        self.assertTrue(svd['complete_returned_orthogonality_checked'])
        self.assertTrue(svd['both_operator_directions_checked'])
        self.assertFalse(svd['restarted_algorithm_verified'])
        self.assertFalse(svd['repeated_zero_singular_values_verified'])
        self.assertFalse(svd['error_bound_sharpness_verified'])
        self.assertIsNone(drivers['propack-spectrum-reference']['author_example'])
        fmm = drivers['fmm2d-laplace-reference']['checks']
        self.assertEqual(fmm['potential_calls'],120)
        self.assertEqual(fmm['direct_target_references'],2880)
        self.assertEqual(fmm['source_counts'],[1,7,64,257,1024])
        self.assertTrue(fmm['clustered_sources_checked'])
        self.assertTrue(fmm['zero_charge_checked'])
        self.assertTrue(fmm['input_preservation_checked'])
        self.assertFalse(fmm['complete_pde_solver_verified'])
        self.assertFalse(fmm['source_potentials_verified'])
        self.assertFalse(fmm['derivatives_dipoles_verified'])
        self.assertEqual(class_evidence(class_tree(data),'I2',[records['fmm2d-potentials']],
                                       [drivers['fmm2d-laplace-reference']])['status'],'source-supported')
        text = propack_fmm_review_text()
        self.assertEqual((ROOT/PROPACK_FMM_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['108 calls','216 checked','2,880','historical SciPy PROPACK 2.1',
                       'a writable K','D1 driver must not promote I2','small fixtures may use direct',
                       'sum_j abs(q(j)*log(distance))','No pinned author example']:
            self.assertIn(phrase.lower(),text.lower())
        self.assertNotIn('/None)',text)
        self.assertIn('PROPACK and FMM2D review',linear_algebra_review_text())

    def test_dae_and_fft_drivers_use_direct_closed_form_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('daskr-dae-reference','I1a2'),('nafpack-fft-reference','J1a2')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        dae = drivers['daskr-dae-reference']['checks']
        self.assertEqual(dae['trajectories'],96)
        self.assertEqual(dae['checkpoints'],768)
        self.assertEqual(dae['analytic_state_derivative_entries'],4608)
        self.assertEqual(dae['user_jacobian_trajectories'],48)
        self.assertTrue(dae['bdf_history_continued'])
        self.assertTrue(dae['polynomial_backward_checked'])
        self.assertTrue(dae['scalar_vector_tolerances_checked'])
        self.assertFalse(dae['krylov_verified'])
        self.assertFalse(dae['root_finding_verified'])
        self.assertFalse(dae['inconsistent_initialization_verified'])
        fft = drivers['nafpack-fft-reference']['checks']
        self.assertEqual(fft['plan_fixtures'],168)
        self.assertEqual(fft['fft_calls'],672)
        self.assertEqual(fft['direct_coefficient_references'],24384)
        self.assertEqual(fft['algorithms'],['RADIX2_DIT','RADIX2_DIF'])
        self.assertEqual(fft['implementations'],['ITERATIVE','recursive'])
        self.assertTrue(fft['input_preservation_checked'])
        self.assertFalse(fft['inverse_transforms_verified'])
        self.assertFalse(fft['other_radices_verified'])
        self.assertFalse(fft['parallel_methods_verified'])
        text = dae_fft_review_text()
        self.assertEqual((ROOT/DAE_FFT_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['4,608','24,384','dG/dy+cj*dG/dy_prime','IDID 2 or 3','consistent initial',
                       'already-rounded','Parseval','all bins','Each implementation is called twice']:
            self.assertIn(phrase,text)
        self.assertIn('DASKR review',ode_review_text())
        self.assertIn('NAFPack plan review',transforms_review_text())

    def test_lu_and_orbit_drivers_check_known_solutions_and_physical_invariants(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('linalg-lu-reference','D2a1'),('fat-orbit-reference','P')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        lu = drivers['linalg-lu-reference']['checks']
        self.assertEqual(lu['nonsingular_factorizations'],96)
        self.assertEqual(lu['solve_calls'],384)
        self.assertEqual(lu['known_solution_entries'],3072)
        self.assertEqual(lu['singular_diagnostics'],8)
        self.assertEqual(lu['factorizations_with_row_swaps'],48)
        self.assertTrue(lu['vector_matrix_rhs_checked'])
        self.assertTrue(lu['pivot_permutation_checked'])
        self.assertTrue(lu['factorization_identity_checked'])
        self.assertFalse(lu['complex_sparse_verified'])
        self.assertFalse(lu['ill_conditioned_accuracy_verified'])
        orbit = drivers['fat-orbit-reference']['checks']
        self.assertEqual(orbit['state_conversions'],864)
        self.assertEqual(orbit['cartesian_component_references'],5184)
        self.assertEqual(orbit['scalar_invariant_direction_checks'],6912)
        self.assertEqual(orbit['eccentricities'],[0,0.2,0.7,1,1.5])
        self.assertEqual(orbit['undefined_angles'],'canonical zero')
        self.assertTrue(orbit['inclinations_include_polar_retrograde'])
        self.assertFalse(orbit['inverse_conversion_verified'])
        self.assertFalse(orbit['singularity_thresholds_verified'])
        self.assertFalse(orbit['propagation_verified'])
        text = lu_orbits_review_text()
        self.assertEqual((ROOT/LU_ORBITS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['384 solve calls','3,072','6,912','P*A=L*U','NaN','canonical zero',
                       'not merely a forward/inverse round trip','parabolic zero energy']:
            self.assertIn(phrase,text)

    def test_adaptive_ivp_and_forwarddiff_drivers_have_analytic_references(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('forwarddiff-analytic-reference','H1'),('flint-ivp-reference','I1a1a')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        derivative = drivers['forwarddiff-analytic-reference']['checks']
        self.assertEqual(derivative['scalar_derivative_calls'],1749)
        self.assertEqual(derivative['analytic_value_slope_checks'],3498)
        self.assertEqual(derivative['monomial_and_constant_calls']+derivative['composite_calls'],1749)
        self.assertFalse(derivative['finite_differences_used'])
        self.assertFalse(derivative['higher_derivatives_verified'])
        self.assertFalse(derivative['gradient_jacobian_verified'])
        ode = drivers['flint-ivp-reference']['checks']
        self.assertEqual(ode['adaptive_integrations'],96)
        self.assertEqual(ode['methods'],['DOP853','DOP54','VERNER98R','VERNER65E'])
        self.assertEqual(ode['endpoint_reference_entries'],288)
        self.assertEqual(ode['dense_output_reference_entries'],9792)
        self.assertTrue(ode['forward_and_backward_checked'])
        self.assertTrue(ode['scalar_vector_tolerances_checked'])
        self.assertTrue(ode['repeated_dense_output_checked'])
        self.assertFalse(ode['events_verified'])
        self.assertFalse(ode['stiff_systems_verified'])
        text = adaptive_ad_review_text()
        self.assertEqual((ROOT/ADAPTIVE_AD_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['1,749','3,498','9,792','0*x+3','dual exponents','SaveInterpCoeffs=false',
                       'different meanings','1.6699e-9']:
            self.assertIn(phrase,text)
        self.assertIn('forwarddiff review',differentiation_review_text())
        self.assertIn('FLINT review',ode_review_text())
        self.assertIn('Other consumers',ode_review_text())

    def test_nearest_and_sparse_drivers_have_independent_references_and_specific_scope(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('flann-knn-reference','N5'),('sparse-matvec-reference','D1b4')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        nearest = drivers['flann-knn-reference']['checks']
        self.assertEqual(nearest['trees'],60)
        self.assertEqual(nearest['query_points'],2472)
        self.assertEqual(nearest['batched_searches'],180)
        self.assertEqual(nearest['returned_neighbors'],96072)
        self.assertEqual(nearest['exact_search_checks'],-1)
        self.assertFalse(nearest['tie_index_order_required'])
        self.assertFalse(nearest['approximate_search_verified'])
        self.assertFalse(nearest['radius_search_verified'])
        sparse = drivers['sparse-matvec-reference']['checks']
        self.assertEqual(sparse['matrix_order_fixtures'],250)
        self.assertEqual(sparse['products'],1500)
        self.assertEqual(sparse['checked_result_entries'],9300)
        self.assertTrue(sparse['transpose_products_checked'])
        self.assertTrue(sparse['zero_matrix_checked'])
        self.assertFalse(sparse['incremental_edits_verified'])
        self.assertFalse(sparse['zero_dimensions_verified'])
        failed = records['coretran-neighbor']
        self.assertNotIn('driver_id',failed)
        self.assertEqual(class_evidence(class_tree(data),'N5',[failed],
                                       [drivers['flann-knn-reference']])['status'],'source-supported')
        text = neighbors_sparse_review_text()
        self.assertEqual((ROOT/NEIGHBORS_SPARSE_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['96,072','9,300','already-rounded','transpose(A)*x','1e-15 threshold',
                       '32*epsilon(float32)','not coretran','Complete diagnostics']:
            self.assertIn(phrase,text)

    def test_graph_and_sort_drivers_keep_failed_coretran_capabilities_separate(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('daglib-order-reference','P'),('coretran-sort-reference','N6')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        graph = drivers['daglib-order-reference']['checks']
        self.assertEqual(graph['acyclic_graph_fixtures'],2051)
        self.assertEqual(graph['successful_sorts'],4102)
        self.assertEqual(graph['edge_precedence_checks'],20492)
        self.assertEqual(graph['expected_cycle_rejections'],6)
        self.assertTrue(graph['post_cycle_recovery_checked'])
        sorting = drivers['coretran-sort-reference']['checks']
        self.assertEqual(sorting['sorting_fixtures'],5997)
        self.assertEqual(sorting['typed_sort_calls'],23988)
        self.assertEqual(sorting['flag_settings'],['stable_true'])
        self.assertFalse(sorting['stable_tie_order_verified'])
        self.assertFalse(sorting['nearest_neighbor_verified'])
        nearest = records['coretran-neighbor']
        self.assertNotIn('driver_id',nearest)
        self.assertEqual(class_evidence(class_tree(data),'N5',[nearest],
                                       [drivers['coretran-sort-reference']])['status'],'source-supported')
        for folder,name in [('coretran-nearest','nearest-direct-reference'),('coretran-sort','default-and-stable')]:
            path = ROOT/'docs/gams-candidates'/folder
            meta = json.loads((path/(name+'.json')).read_text())
            source = (path/meta['source']).read_text().replace('\r\n','\n').encode()
            self.assertEqual(hashlib.sha256(source).hexdigest(),meta['source_sha256'])
            stages = {s['name']:s for s in json.loads((path/meta['result']).read_text())['stages']}
            self.assertTrue(stages['Build']['ok'])
            self.assertFalse(stages['Run']['ok'])
        text = graph_sorting_review_text()
        self.assertEqual((ROOT/GRAPH_SORTING_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['4,102 successful sorts','20,492 independent','23,988 typed calls','does not establish a default-mode failure']:
            self.assertIn(phrase,text)

    def test_conversion_and_triangulation_drivers_check_numeric_and_mesh_invariants(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('str2real-decimal-reference','A6'),('geompack-delaunay-reference','P')]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],code)
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        conversion = drivers['str2real-decimal-reference']['checks']
        self.assertEqual(conversion['valid_conversions'],244)
        self.assertEqual(conversion['independent_references_per_conversion'],2)
        self.assertEqual(conversion['generated_strings']+conversion['long_mantissa_strings'],244)
        self.assertFalse(conversion['malformed_input_verified'])
        self.assertFalse(conversion['correct_rounding_verified'])
        mesh = drivers['geompack-delaunay-reference']['checks']
        self.assertEqual(mesh['triangulations'],36)
        self.assertEqual(mesh['checked_triangles'],432)
        self.assertEqual(mesh['empty_circumcircle_checks'],3360)
        self.assertTrue(mesh['neighbor_reciprocity_checked'])
        self.assertTrue(mesh['boundary_cycle_checked'])
        self.assertTrue(mesh['coordinate_restoration_checked'])
        self.assertFalse(mesh['specific_triangle_order_required'])
        self.assertFalse(mesh['degenerate_input_verified'])
        text = conversion_triangulation_review_text()
        self.assertEqual((ROOT/CONVERSION_TRIANGULATION_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['244 conversions','3,360 tests','four-edge cycle','not a bitwise-rounding claim']:
            self.assertIn(phrase,text)

    def test_expression_drivers_use_shared_numeric_references_and_checked_recovery(self):
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,count,rejections in [('function-parser-identities',286,6),('m-calculator-identities',283,3)]:
            d = drivers[ident]
            self.assertEqual(d['gams_code'],'N3')
            self.assertEqual(d['checks']['expression_formulas'],14)
            self.assertEqual(d['checks']['input_pairs'],20)
            self.assertEqual(d['checks']['normal_value_references'],280)
            self.assertEqual(d['checks']['total_value_references'],count)
            self.assertEqual(d['checks']['expected_rejections'],rejections)
            self.assertEqual(d['checks']['post_error_recoveries'],rejections)
            self.assertFalse(d['checks']['symbolic_algebra_verified'])
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),'N3',[record],[d])['status'],'verified')
        self.assertEqual(drivers['function-parser-identities']['checks']['evaluation_error_checks'],3)
        self.assertTrue(drivers['function-parser-identities']['checks']['input_preservation_checked'])
        self.assertEqual(drivers['m-calculator-identities']['checks']['variable_assignment_checks'],560)
        self.assertFalse(drivers['m-calculator-identities']['checks']['domain_error_handling_verified'])
        text = expression_evaluation_review_text()
        self.assertEqual((ROOT/EXPRESSION_EVALUATION_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['280 ordinary references','286 successful','283 successful','560 assignment','not symbolic algebra']:
            self.assertIn(phrase,text)

    def test_user_jacobian_and_transform_drivers_keep_verified_configuration_scope(self):
        import hashlib
        data = gams_data()
        drivers = {d['id']: d for d in driver_data(data=data)}
        records = {r['id']: r for r in data['procedure_mappings']}
        for ident,code in [('nonlin-lsq-jacobian-reference','G1b1b'),('fglm-transform-reference','D1')]:
            d = drivers[ident]
            record = records[d['procedure_id']]
            self.assertEqual(record['driver_id'],ident)
            self.assertEqual(class_evidence(class_tree(data),code,[record],[d])['status'],'verified')
        d = drivers['nonlin-lsq-jacobian-reference']
        record = records[d['procedure_id']]
        self.assertEqual(class_evidence(class_tree(data),'G1b1a',[record],[d])['status'],'source-supported')
        self.assertEqual(d['checks']['nonlinear_fits'],24)
        self.assertEqual(d['checks']['starting_jacobian_entries'],240)
        self.assertEqual(d['checks']['initial_step_bound_factor'],1)
        self.assertFalse(d['checks']['nonzero_residual_minima_verified'])
        self.assertFalse(d['checks']['default_step_bound_verified'])
        transform = drivers['fglm-transform-reference']['checks']
        self.assertEqual(transform['rigid_transforms'],72)
        self.assertEqual(transform['point_and_direction_coordinate_checks'],864)
        self.assertEqual(transform['rotation_orthogonality_checks'],648)
        self.assertEqual(transform['rotation_determinant_checks'],72)
        self.assertFalse(transform['arbitrary_3d_rotations_verified'])
        folder = ROOT/'docs/gams-candidates/nonlin-least-squares'
        for name in ['default-step-bound','nonzero-residual-step-one']:
            meta = json.loads((folder/(name+'.json')).read_text())
            source = (folder/meta['source']).read_text().replace('\r\n','\n').encode()
            self.assertEqual(hashlib.sha256(source).hexdigest(),meta['source_sha256'])
            stages = {s['name']: s for s in json.loads((folder/meta['result']).read_text())['stages']}
            self.assertTrue(stages['Build']['ok'])
            self.assertFalse(stages['Run']['ok'])
            self.assertIn('convergence flags:',stages['Run']['stdout'])
        text = jacobian_transforms_review_text()
        self.assertEqual((ROOT/JACOBIAN_TRANSFORMS_REPORT).read_text(encoding='utf-8'),text)
        for phrase in ['24 fits','864 output coordinates','default step setting','240 starting Jacobian entries']:
            self.assertIn(phrase,text)

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
                                       [matrix])['status'], 'source-supported')
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
        self.assertEqual(set(by_class['J1a2']['driver_ids']), {
            'fftpack-complex-transform','kissfft-f-complex-transform','nafpack-fft-reference'})
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
