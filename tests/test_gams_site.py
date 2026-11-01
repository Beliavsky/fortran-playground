"""Static catalog navigation, hierarchy, provenance links and regeneration."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

from catalog_export import build_export
from xgams_site import generate_gams_site

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = []
        self.anchors = []
        self.current_anchor = None
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            self.current_anchor = [attrs.get('href', ''), '']
        if 'id' in attrs:
            self.ids.append(attrs['id'])

    def handle_data(self, data):
        if self.current_anchor is not None:
            self.current_anchor[1] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_anchor is not None:
            self.anchors.append(tuple(self.current_anchor))
            self.current_anchor = None


class GamsSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = build_export()

    def test_evidence_labels_change_with_class_specific_records_and_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] == 'stdlib']
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            sorting = (destination/'N6/index.html').read_text(encoding='utf-8')
            parent = (destination/'N/index.html').read_text(encoding='utf-8')
            self.assertIn('Verified: a checked driver', sorting)
            self.assertIn('Driver demonstrates the narrower class', parent)
            feed['demonstrations'] = []
            generate_gams_site(destination, feed)
            sorting = (destination/'N6/index.html').read_text(encoding='utf-8')
            self.assertIn('Source-supported: pinned procedure evidence', sorting)
            self.assertNotIn('Verified: a checked driver', sorting)
            feed['projects'][0]['curation']['procedures'] = []
            generate_gams_site(destination, feed)
            sorting = (destination/'N6/index.html').read_text(encoding='utf-8')
            self.assertIn('Uncertain: discovery classification', sorting)
            self.assertIn('Open default example', sorting)
            self.assertNotIn('Try in playground', sorting)

    def test_helmholtz_and_stream_pages_load_class_specific_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'spherepack','rng-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('I2','spherepack','spherepack-helmholtz-reference'),
                                        ('L6a21','rng-fortran','rng-xoroshiro-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertIn(f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}',primary)
                self.assertIn('Verified: a checked driver',html)
            scalar = (destination/'J/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-spherepack-zonal-reference',scalar)
            self.assertNotIn('example=gams-spherepack-helmholtz-reference',scalar)

    def test_fiats_and_ennuf_links_load_checked_inference_without_training_claims(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fiats','ennuf'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'K/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                for package,driver in [('fiats','fiats-inference-reference'),('ennuf','ennuf-inference-reference')]})
            self.assertIn('Verified: a checked driver',html)
            training = (destination/'G1b/index.html').read_text(encoding='utf-8')
            for package,driver in [('fiats','fiats-inference-reference'),('ennuf','ennuf-inference-reference')]:
                self.assertNotIn('example=gams-'+driver,training)
                detail = (destination/'packages'/package/'index.html').read_text(encoding='utf-8')
                card = detail.split('id="'+package+'-inference"',1)[1].split('</article>',1)[0]
                self.assertIn('Load checked GAMS driver:',card)
                self.assertIn('example=gams-'+driver,card)

    def test_radial_and_dense_links_load_checked_examples_without_narrower_claims(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'dftatom','athena'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('I1','dftatom','dftatom-hydrogen-reference'),
                                        ('K','athena','athena-dense-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            stiff = (destination/'I1a2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-dftatom-hydrogen-reference',stiff)
            training = (destination/'G1b/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-athena-dense-reference',training)
            for package,procedure,driver in [('dftatom','dftatom-radial','dftatom-hydrogen-reference'),
                                            ('athena','athena-dense','athena-dense-reference')]:
                detail = (destination/'packages'/package/'index.html').read_text(encoding='utf-8')
                card = detail.split('id="'+procedure+'"',1)[1].split('</article>',1)[0]
                self.assertIn('Load checked GAMS driver:',card)
                self.assertIn('example=gams-'+driver,card)

    def test_tangent_and_block_links_do_not_promote_stiff_or_distributed_operation(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fatode','dbcsr'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('I1','fatode','fatode-tangent-reference'),
                                        ('D1','dbcsr','dbcsr-products-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            stiff = (destination/'I1a2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-fatode-tangent-reference',stiff)
            for package,procedure,driver in [('fatode','fatode-tangent','fatode-tangent-reference'),
                                            ('dbcsr','dbcsr-block-multiply','dbcsr-products-reference')]:
                detail = (destination/'packages'/package/'index.html').read_text(encoding='utf-8')
                card = detail.split('id="'+procedure+'"',1)[1].split('</article>',1)[0]
                self.assertIn('Load checked GAMS driver:',card)
                self.assertIn('example=gams-'+driver,card)

    def test_kiss_uniform_and_normalized_spacing_links_keep_distinct_distributions(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'rndgen-fortran','pointsets'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            uniform = (destination/'L6a21/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(uniform).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                'https://beliavsky.github.io/fortran-playground/fpm/?package=rndgen-fortran&example=gams-rndgen-kiss-reference'})
            self.assertNotIn('example=gams-pointsets-random-reference',uniform)
            broad = (destination/'L6/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-pointsets-random-reference',broad)
            detail = (destination/'packages/pointsets/index.html').read_text(encoding='utf-8')
            card = detail.split('id="pointsets-random-spacing"',1)[1].split('</article>',1)[0]
            self.assertIn('Load checked GAMS driver:',card)
            self.assertIn('example=gams-pointsets-random-reference',card)
            self.assertIn('not uniform',card)

    def test_directions_and_annealing_links_do_not_publish_failed_friction_fit(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'conmin','simulated-annealing','friction'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('G2h3b1b','conmin','conmin-ball-reference'),
                                        ('G2i','simulated-annealing','annealing-rastrigin-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            fitting = (destination/'L8/index.html').read_text(encoding='utf-8')
            self.assertIn('Source-supported: pinned procedure evidence',fitting)
            self.assertNotIn('example=gams-friction-fit-reference',fitting)
            self.assertNotIn('Try in playground',{label for url,label in Page(fitting).anchors})
            detail = (destination/'packages/friction/index.html').read_text(encoding='utf-8')
            card = detail.split('id="friction-fit"',1)[1].split('</article>',1)[0]
            self.assertNotIn('Load checked GAMS driver:',card)
            self.assertIn('0.375',card)

    def test_halfspace_and_affine_training_links_load_checked_examples_without_promotion(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'optgra','neural-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('G2h3b1b','optgra','optgra-halfspace-reference'),
                                        ('G1b','neural-fortran','neural-affine-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            detailed = (destination/'G1b1b/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-neural-affine-reference',detailed)
            derivative_free = (destination/'G1b1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-neural-affine-reference',derivative_free)
            for package,procedure,driver in [('optgra','optgra-optgra','optgra-halfspace-reference'),
                                              ('neural-fortran','neural-network-train','neural-affine-reference')]:
                detail = (destination/'packages'/package/'index.html').read_text(encoding='utf-8')
                card = detail.split('id="'+procedure+'"',1)[1].split('</article>',1)[0]
                self.assertIn('Load checked GAMS driver:',card)
                self.assertIn('example=gams-'+driver,card)

    def test_fixed_gradient_and_swarm_links_load_class_specific_checked_examples(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fortimize','opti'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,expected in [('G1b',{'fortimize-nelder-reference','fortimize-gradient-reference'}),
                                  ('G2i',{'opti-rastrigin-reference'})]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                package = 'fortimize' if code=='G1b' else 'opti'
                expected_urls = {
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                    for driver in expected}
                self.assertEqual(len(primary),1)
                self.assertTrue(primary <= expected_urls)
                self.assertTrue(expected_urls <= set(Page(html).links))
                self.assertIn('Verified: a checked driver',html)
            detailed = (destination/'G1b1b/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-fortimize-gradient-reference',detailed)

    def test_projection_and_lbfgs_class_links_do_not_promote_other_configurations(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'psqp','seiscope-optimization'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('G2h3b1b','psqp','psqp-projection-reference'),
                                        ('G1b1b','seiscope-optimization','seiscope-lbfgs-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            derivative_free = (destination/'G1b1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-seiscope-lbfgs-reference',derivative_free)
            box = (destination/'G2h1a2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-psqp-projection-reference',box)

    def test_sparse_update_and_symmetric_spectra_links_load_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'lusol','scalapackfx'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D2a4','lusol','lusol-update-reference'),
                                        ('D4a1','scalapackfx','scalapackfx-eigen-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)

    def test_multidimensional_fft_links_load_direct_sum_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'dtfft','2decomp-fft'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'J1/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                for package,driver in [('dtfft','dtfft-2d-reference'),('2decomp-fft','decomp-3d-reference')]})
            self.assertEqual(html.count('Verified: a checked driver'),2)
            for code in ['J1a1','J1a2','J1a3']:
                narrower = (destination/code/'index.html').read_text(encoding='utf-8')
                self.assertNotIn('example=gams-dtfft-2d-reference',narrower)
                self.assertNotIn('example=gams-decomp-3d-reference',narrower)

    def test_product_and_partition_class_links_load_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'formatmul','metis-fpm'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D1','formatmul','formatmul-products-reference'),
                                        ('P','metis-fpm','metis-kway-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)

    def test_sparse_and_advection_class_links_keep_heatflow_evolution_unverified(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'heatflow','hrweno'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D2','heatflow','heatflow-bicg-reference'),
                                        ('I2','hrweno','hrweno-advection-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            pde = (destination/'I2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-heatflow-bicg-reference',pde)
            self.assertIn('Source-supported: pinned procedure evidence',pde)

    def test_unsigned_and_bitset_links_use_checked_examples_without_sibling_promotion(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'uint-fortran','orbs'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('A1','uint-fortran','uint-arithmetic-reference'),
                                        ('N2','orbs','orbs-bitwise-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            arithmetic = (destination/'A1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-orbs-bitwise-reference',arithmetic)
            self.assertIn('Source-supported: pinned procedure evidence',arithmetic)

    def test_expressions_and_sky_links_open_class_specific_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'feq-parse','astro-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('N3','feq-parse','feq-expression-reference'),
                                        ('P','astro-fortran','astro-sky-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)

    def test_periodic_and_calculus_links_keep_failed_skew_and_pde_claims_unverified(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'formal','raffle'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('H1','formal','formal-polynomial-reference'),
                                        ('P','raffle','raffle-orthogonal-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
                self.assertNotIn('example=gams-raffle-skew-probe',html)
            pde = (destination/'I2/index.html').read_text(encoding='utf-8')
            self.assertIn('Source-supported: pinned procedure evidence',pde)
            self.assertNotIn('example=gams-formal-polynomial-reference',pde)

    def test_gmres_and_inverse_class_links_do_not_inherit_lu_or_matrix_root_proofs(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'lightkrylov','ntpoly'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'D2/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                for package,driver in [('lightkrylov','lightkrylov-gmres-reference'),
                                       ('ntpoly','ntpoly-inverse-reference')]})
            self.assertNotIn('example=gams-ntpoly-matrix-root-reference',html)
            lu = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-lightkrylov-gmres-reference',lu)
            self.assertNotIn('example=gams-ntpoly-inverse-reference',lu)

    def test_partial_svd_and_fmm_links_keep_kernel_application_distinct_from_pde_solution(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'propack','fmm2d'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D6','propack','propack-spectrum-reference'),
                                        ('D1','fmm2d','fmm2d-laplace-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            pde = (destination/'I2/index.html').read_text(encoding='utf-8')
            self.assertIn('Source-supported: pinned procedure evidence',pde)
            self.assertNotIn('example=gams-fmm2d-laplace-reference',pde)
            eigen = (destination/'D4a1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-propack-spectrum-reference',eigen)

    def test_dae_and_fft_plan_links_do_not_promote_unchecked_sibling_classes(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'daskr','nafpack'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('I1a2','daskr','daskr-dae-reference'),
                                        ('J1a2','nafpack','nafpack-fft-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            explicit = (destination/'I1a1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-daskr-dae-reference',explicit)
            cosine = (destination/'J1a3/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-nafpack-fft-reference',cosine)

    def test_lu_and_orbital_class_links_open_their_checked_problem_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'linalg','fortran-astrodynamics-toolkit'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D2a1','linalg','linalg-lu-reference'),
                                        ('P','fortran-astrodynamics-toolkit','fat-orbit-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            positive = (destination/'D2b/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-linalg-lu-reference',positive)
            ode = (destination/'I1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-fat-orbit-reference',ode)

    def test_forwarddiff_and_flint_links_do_not_verify_unchecked_siblings(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'forwarddiff','flint'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('H1','forwarddiff','forwarddiff-analytic-reference'),
                                        ('I1a1a','flint','flint-ivp-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            stiff = (destination/'I1a2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-flint-ivp-reference',stiff)
            systems = (destination/'F2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-forwarddiff-analytic-reference',systems)

    def test_nearest_and_sparse_class_links_open_specific_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fortran-flann','sparse_fortran','coretran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('N5','fortran-flann','flann-knn-reference'),
                                        ('D1b4','sparse_fortran','sparse-matvec-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            nearest = (destination/'N5/index.html').read_text(encoding='utf-8')
            self.assertIn('Source-supported: pinned procedure evidence',nearest)
            self.assertNotIn('example=gams-coretran-sort-reference',nearest)
            sorting = (destination/'N6/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-flann-knn-reference',sorting)
            linear = (destination/'D2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-sparse-matvec-reference',linear)

    def test_graph_and_sort_class_links_do_not_promote_failed_nearest_search(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'daglib','coretran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('P','daglib','daglib-order-reference'),
                                        ('N6','coretran','coretran-sort-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            nearest = (destination/'N5/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-coretran-sort-reference',nearest)
            self.assertNotIn('example=gams-coretran-nearest-reference',nearest)
            self.assertIn('Source-supported: pinned procedure evidence',nearest)

    def test_conversion_and_triangulation_links_open_checked_problem_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fortran-string-to-real','geompack'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('A6','fortran-string-to-real','str2real-decimal-reference'),
                                        ('P','geompack','geompack-delaunay-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            data = (destination/'N3/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-str2real-decimal-reference',data)

    def test_expression_class_links_open_numeric_evaluation_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects']
                            if p['playground']['package_id'] in {'fortran_function_parser','m_calculator'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'N3/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                f'https://beliavsky.github.io/fortran-playground/fpm/?package={p}&example=gams-{d}'
                for p,d in [('fortran_function_parser','function-parser-identities'),
                            ('m_calculator','m-calculator-identities')]})
            self.assertEqual(html.count('Verified: a checked driver'),2)
            symbolic = (destination/'O/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-function-parser-identities',symbolic)
            self.assertNotIn('example=gams-m-calculator-identities',symbolic)

    def test_user_jacobian_and_transform_class_links_keep_sibling_scope(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'nonlin','fglm'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('G1b1b','nonlin','nonlin-lsq-jacobian-reference'),
                                        ('D1','fglm','fglm-transform-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                # A package can have multiple checked procedures in the same class.
                self.assertIn((
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}',
                    driver),Page(html).anchors)
                self.assertIn('Verified: a checked driver',html)
            no_jac = (destination/'G1b1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-nonlin-lsq-jacobian-reference',no_jac)

    def test_geodesy_and_forlab_links_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'maptran3d','forlab'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('P','maptran3d','maptran-wgs84-reference'),
                                        ('D9a1','forlab','forlab-least-squares-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            lu = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-forlab-least-squares-reference',lu)

    def test_ranking_and_magic_links_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'orderpack','m_la'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('N6','orderpack','orderpack-ranking-reference'),
                                        ('D1','m_la','m-la-magic-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            stats = (destination/'L1a1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-orderpack-ranking-reference',stats)

    def test_diagonal_and_response_links_use_scoped_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'specialmatrices','dynamics'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D2','specialmatrices','specialmatrices-diagonal-reference'),
                                        ('I1','dynamics','dynamics-response-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            ivp = (destination/'I1a1a/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-dynamics-response-reference',ivp)

    def test_fitpack_value_and_derivative_links_open_the_matching_driver(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id']=='fitpack']
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,driver in [('E1a','fitpack-polynomial-values'),('H1','fitpack-polynomial-derivatives')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package=fitpack&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            integration = (destination/'H2a2b2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-fitpack-polynomial-',integration)
            self.assertIn('example=gams-fitpack-spline-integral',integration)

    def test_regrid_and_rk45_class_links_open_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'regridpack','diffeq'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('E1a','regridpack','regridpack-polynomial-reference'),
                                        ('I1a1a','diffeq','diffeq-rk45-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            stiff = (destination/'I1a2/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-diffeq-rk45-reference',stiff)

    def test_spectral_wrapper_links_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'forsvd','foreig'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D6','forsvd','forsvd-spectrum-reference'),
                                        ('D4a1','foreig','foreig-symmetric-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'})
                self.assertIn('Verified: a checked driver',html)
            lu = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-forsvd',lu)
            self.assertNotIn('example=gams-foreig',lu)

    def test_iterative_least_squares_links_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'lsqr','lsmr'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'D9a1/index.html').read_text(encoding='utf-8')
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            self.assertEqual(primary,{
                f'https://beliavsky.github.io/fortran-playground/fpm/?package={p}&example=gams-{p}-least-squares-reference'
                for p in ['lsqr','lsmr']})
            self.assertEqual(html.count('Verified: a checked driver'),2)
            lu = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            self.assertNotIn('example=gams-lsqr-least-squares-reference',lu)
            self.assertNotIn('example=gams-lsmr-least-squares-reference',lu)

    def test_number_theory_primary_links_use_checked_problem_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if 'B' in p['curation']['gams_codes']]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            page = Page((destination/'B/index.html').read_text(encoding='utf-8'))
            primary = [url for url, label in page.anchors if label == 'Try in playground']
            self.assertEqual(set(primary), {
                'https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-primes&example=gams-primes-trial-division',
                'https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-gcd-lcm-reference'})
            self.assertNotIn('Open default example', [label for _, label in page.anchors])

    def test_arithmetic_class_links_do_not_verify_sibling_capabilities(self):
        import copy
        feed = copy.deepcopy(self.feed)
        names = {'rational_number','strith','ryu_fortran'}
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in names]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('A1','strith','strith-integer-reference'),
                                          ('A2','rational_number','rational-addition-reference'),
                                          ('A6','ryu_fortran','ryu-binary64-roundtrip')]:
                page = Page((destination/code/'index.html').read_text(encoding='utf-8'))
                url = f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                self.assertIn((url,'Try in playground'), page.anchors)
            a6 = Page((destination/'A6/index.html').read_text(encoding='utf-8'))
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=strith','Open default example'), a6.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=strith&example=gams-strith-integer-reference','Try in playground'), a6.anchors)

    def test_multiprecision_and_bit_class_pages_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'mpfun2020-var1','bstrith'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('A3c','mpfun2020-var1','mpfun-real-addition'),
                                          ('A4c','mpfun2020-var1','mpfun-complex-addition'),
                                          ('N2','bstrith','bstrith-bit-reference')]:
                html = (destination/code/'index.html').read_text(encoding='utf-8')
                primary = [url for url, label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_special_function_class_links_select_the_matching_problem(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'carlson-elliptic-integrals','specfun','amosf90'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('C14','carlson-elliptic-integrals','carlson-rf-reference'),
                                          ('C19','specfun','bernoulli-power-sums'),
                                          ('C10','amosf90','amos-complex-series')]:
                primary = [url for url, label in Page((destination/code/'index.html').read_text()).anchors
                           if label=='Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
            amos = (destination/'packages/amosf90/index.html').read_text()
            self.assertIn('Pinned failure', amos)
            self.assertIn('0.556', amos)

    def test_product_and_pseudoinverse_classes_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'blas-interface','fsparse','forinv'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D1b6','blas-interface','blas-gemm-reference'),
                                          ('D1b4','fsparse','fsparse-matvec-reference'),
                                          ('D1b9','fsparse','fsparse-storage-reference'),
                                          ('D9c','forinv','forinv-pseudoinverse-reference')]:
                primary = [url for url, label in Page((destination/code/'index.html').read_text()).anchors
                           if label=='Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
            conversion = (destination/'D1b9/index.html').read_text()
            self.assertIn('Verified: a checked driver', conversion)
            self.assertNotIn('Open default example', conversion)
            self.assertNotIn('example=gams-fsparse-matvec-reference', conversion)

    def test_fit_series_and_integral_classes_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'splpak','fortsa','integrate_fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('K1','splpak','splpak-paired-noise-fit'),
                                          ('L10a2a','fortsa','fortsa-autocorrelation-reference'),
                                          ('H2b1a2','integrate_fortran','integrate-nd-polynomial-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_linear_derivative_free_and_global_classes_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'conmax','powellopt','pikaia'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('G2a','conmax','conmax-linear-program-certificate'),
                                          ('G2h1a1','powellopt','bobyqa-box-reference'),
                                          ('G2i','pikaia','pikaia-rastrigin-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_boundary_and_spectral_pages_distinguish_checked_and_failed_probes(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'featom','twopnt','arpack-ng','linalg_fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            html = (destination/'I1b/index.html').read_text()
            primary = [url for url, label in Page(html).anchors if label=='Try in playground']
            self.assertEqual(primary, ['https://beliavsky.github.io/fortran-playground/fpm/?package=featom&example=gams-featom-coulomb-spectrum'])
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=twopnt','Open default example'), Page(html).anchors)
            html = (destination/'D4a1/index.html').read_text()
            primary = [url for url, label in Page(html).anchors if label=='Try in playground']
            self.assertEqual(set(primary), {
                'https://beliavsky.github.io/fortran-playground/fpm/?package=arpack-ng&example=gams-arpack-poisson-eigenpairs',
                'https://beliavsky.github.io/fortran-playground/fpm/?package=linalg_fortran&example=gams-linalg-poisson-eigenpairs'})
            self.assertNotIn('twopnt-poisson-reference', str(feed['demonstrations']))

    def test_resampling_and_markov_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'econ-toolchain', 'fjsample'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('M', 'econ-toolchain', 'econ-markov-reference'),
                                          ('L4', 'fjsample', 'fjsample-jackknife-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_real_fourier_and_geometry_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'spectrum','geodesic-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('J1a1','spectrum','spectrum-real-dft-reference'),
                                          ('P','geodesic-fortran','geodesic-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_sparse_solve_and_spline_integral_links_do_not_promote_failed_pca(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'y12m','fitpack','forpca'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D2a4','y12m','y12m-sparse-reference'),
                                          ('H2a2b2','fitpack','fitpack-spline-integral')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            pca = (destination/'L13b/index.html').read_text()
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=forpca',
                           'Open default example'), Page(pca).anchors)
            self.assertNotIn('example=gams-forpca', pca)
            self.assertIn('Source-supported:', pca)

    def test_spatial_and_nonuniform_transform_pages_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'kdtree2','delaunaysparse','nufft1d'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('N5','kdtree2','kdtree-neighbor-reference'),
                                          ('E2','delaunaysparse','delaunay-affine-reference'),
                                          ('J1','nufft1d','nufft1d-sum-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            geometry = Page((destination/'P/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=kdtree2',
                           'Open default example'), geometry.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=kdtree2&example=gams-kdtree-neighbor-reference',
                              'Try in playground'), geometry.anchors)

    def test_pde_page_opens_checked_problems_without_verifying_sibling_packages(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'fishpack','poisfft','heatflow'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            html = (destination/'I2/index.html').read_text()
            primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
            self.assertEqual(set(primary), {
                'https://beliavsky.github.io/fortran-playground/fpm/?package=fishpack&example=gams-fishpack-helmholtz-reference',
                'https://beliavsky.github.io/fortran-playground/fpm/?package=poisfft&example=gams-poisfft-periodic-reference'})
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=heatflow',
                           'Open default example'), Page(html).anchors)
            self.assertEqual(html.count('Verified: a checked driver'), 2)

    def test_parsing_fifo_and_machine_class_links_preserve_conversion_scope(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'fortran-fast-float','for_fifo_queue','penf'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('N3','fortran-fast-float','fast-float-parsing-reference'),
                                          ('N4','for_fifo_queue','fifo-storage-reference'),
                                          ('R1','penf','penf-machine-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            parsing = Page((destination/'N3/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=penf',
                           'Open default example'), parsing.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=penf&example=gams-penf-machine-reference',
                              'Try in playground'), parsing.anchors)

    def test_scalar_product_test_and_error_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'fordot','fassert','errstat'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D1','fordot','fordot-exact-reference'),
                                          ('S3','fassert','fassert-captured-reference'),
                                          ('R3','errstat','errstat-recovery-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            checking = Page((destination/'R2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fassert',
                           'Open default example'), checking.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fassert&example=gams-fassert-captured-reference',
                              'Try in playground'), checking.anchors)

    def test_kriging_and_network_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'gslib','fkb'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('L13','gslib','gslib-kriging-reference'),
                                          ('K','fkb','fkb-network-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            interpolation = Page((destination/'E2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=gslib',
                           'Open default example'), interpolation.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=gslib&example=gams-gslib-kriging-reference',
                              'Try in playground'), interpolation.anchors)

    def test_lookup_and_elementary_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'lookup-table-fortran','fastmath'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('E3','lookup-table-fortran','lookup-services-reference'),
                                          ('C4b','fastmath','fastmath-exp-log-reference'),
                                          ('C2','fastmath','fastmath-rsqrt-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            interpolation = Page((destination/'E1a/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=lookup-table-fortran',
                           'Open default example'), interpolation.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=lookup-table-fortran&example=gams-lookup-services-reference',
                              'Try in playground'), interpolation.anchors)

    def test_circuit_and_rpn_pages_open_matching_drivers_without_sibling_inheritance(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'ecx','rpn-calculator-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('A4','ecx','ecx-rlc-reference'),
                                          ('C4','rpn-calculator-fortran','rpn-sinc-sech-reference'),
                                          ('C7','rpn-calculator-fortran','rpn-beta-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            for code, driver in [('C2','rpn-sinc-sech-reference'),('C10','rpn-beta-reference')]:
                page = Page((destination/code/'index.html').read_text())
                self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran',
                               'Open default example'), page.anchors)
                self.assertNotIn((f'https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-{driver}',
                                  'Try in playground'), page.anchors)

    def test_inverse_and_tvd_pages_open_matching_drivers_without_spatial_inheritance(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'linalg_fortran','hrweno'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D2','linalg_fortran','linalg-inverse-factor-reference'),
                                          ('I1','hrweno','hrweno-tvd-ode-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            spatial = Page((destination/'I2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=hrweno&example=gams-hrweno-advection-reference',
                           'Try in playground'), spatial.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=hrweno&example=gams-hrweno-tvd-ode-reference',
                              'Try in playground'), spatial.anchors)

    def test_quadratic_spline_and_quadrature_pages_open_matching_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'fortranlib','fortran-utils','scifortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('F1','fortranlib','fortranlib-quadratic-reference'),
                                          ('E1','fortran-utils','fortran-utils-spline-reference'),
                                          ('H2','scifortran','scifortran-quadrature-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            for code in ['E1','H2']:
                page = Page((destination/code/'index.html').read_text())
                self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib',
                               'Open default example'), page.anchors)
                self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-quadratic-reference',
                                  'Try in playground'), page.anchors)
            sorting = Page((destination/'N6/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-utils',
                           'Open default example'), sorting.anchors)

    def test_numeric_io_and_bounds_pages_open_matching_drivers_without_handler_inheritance(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'io-fortran-library','fortran-error-handler'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('N1','io-fortran-library','io-numeric-file-reference'),
                                          ('R2','fortran-error-handler','error-bounds-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            handling = Page((destination/'R3/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-error-handler',
                           'Open default example'), handling.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-error-handler&example=gams-error-bounds-reference',
                              'Try in playground'), handling.anchors)

    def test_nelder_and_spacing_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'fortimize','pointsets'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('G1b','fortimize','fortimize-nelder-reference'),
                                          ('R','pointsets','pointsets-spacing-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertIn(f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}', primary)
                self.assertIn('Verified: a checked driver', html)
            details = (destination/'packages/fortimize/index.html').read_text()
            gradient = details.split('id="fortimize-gradient-descent"',1)[1].split('</article>',1)[0]
            self.assertIn('minimize with GradientDescent', gradient)
            self.assertIn('gams-fortimize-gradient-reference', gradient)
            self.assertIn('Load checked GAMS driver:', gradient)

    def test_graphics_and_distribution_pages_open_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'fortran-sdl2','rng-fortran'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('Q','fortran-sdl2','sdl-raster-reference'),
                                          ('L6','rng-fortran','rng-distributions-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)

    def test_quantity_and_spherical_pages_open_matching_drivers_without_pde_inheritance(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'quaff','spherepack'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('A','quaff','quaff-quantity-reference'),
                                          ('J','spherepack','spherepack-zonal-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            pde = Page((destination/'I2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=spherepack&example=gams-spherepack-helmholtz-reference',
                           'Try in playground'), pde.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=spherepack&example=gams-spherepack-zonal-reference',
                              'Try in playground'), pde.anchors)

    def test_delay_and_lua_pages_open_the_matching_checked_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in
                            {'dde_solver','fortran-lua54','fortran-lua53'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('I','dde_solver','dde-method-steps-reference'),
                                          ('S','fortran-lua54','lua-numeric-embedding-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            scripting = Page((destination/'S/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lua53',
                           'Open default example'), scripting.anchors)

    def test_qdutillib_and_nufft2d_pages_open_class_specific_drivers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'qdutillib','nufft2d'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('H2c','qdutillib','qdutillib-moments-reference'),
                                        ('J1','nufft2d','nufft2d-direct-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            other_quad = Page((destination/'H2a1a1/index.html').read_text())
            self.assertFalse(any('example=gams-qdutillib' in url for url,label in other_quad.anchors))
            cosine = Page((destination/'J1a3/index.html').read_text())
            self.assertFalse(any('example=gams-nufft2d' in url for url,label in cosine.anchors))

    def test_higher_ad_class_page_opens_each_checked_derivative_problem(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'dnaoad-fpm','diffstruc'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            html = (destination/'H1/index.html').read_text()
            primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
            expected = {
                'https://beliavsky.github.io/fortran-playground/fpm/?package=dnaoad-fpm&example=gams-dnaoad-higher-reference',
                'https://beliavsky.github.io/fortran-playground/fpm/?package=diffstruc&example=gams-diffstruc-hessian-reference'}
            self.assertEqual(primary,expected)
            self.assertEqual(html.count('Verified: a checked driver'),2)
            quad = Page((destination/'H2/index.html').read_text())
            self.assertFalse(any('example=gams-dnaoad' in url or 'example=gams-diffstruc' in url
                                 for url,label in quad.anchors))

    def test_user_jacobian_and_newton_class_pages_open_matching_fixtures(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'minpack','forsolver'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('G1b1b','minpack','minpack-lmder-reference'),
                                        ('F1b','forsolver','forsolver-newton-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            systems = Page((destination/'F2/index.html').read_text())
            self.assertFalse(any('example=gams-forsolver-newton' in url for url,label in systems.anchors))
            derivative_free = Page((destination/'G1b1a/index.html').read_text())
            self.assertFalse(any('example=gams-minpack-lmder' in url for url,label in derivative_free.anchors))

    def test_rkf45_and_qags_class_pages_open_exact_problems(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'rkf45','fgsl'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('I1a1a','rkf45','rkf45-analytic-reference'),
                                        ('H2a1a1','fgsl','fgsl-qags-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            stiff = Page((destination/'I1a2/index.html').read_text())
            self.assertFalse(any('example=gams-rkf45' in url for url,label in stiff.anchors))
            differentiating = Page((destination/'H1/index.html').read_text())
            self.assertFalse(any('example=gams-fgsl-qags' in url for url,label in differentiating.anchors))

    def test_least_squares_and_interp1_pages_open_the_matching_problems(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'linalg','interpolation'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('D9a1','linalg','linalg-least-squares-reference'),
                                        ('E1a','interpolation','interp1-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            lu = Page((destination/'D2a1/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-lu-reference',
                           'Try in playground'),lu.anchors)
            self.assertFalse(any('example=gams-linalg-least-squares' in url for url,label in lu.anchors))

    def test_linalg_spectrum_and_lu_pages_use_separate_proofs(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id']=='linalg']
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,driver in [('D4a1','linalg-eigen-reference'),('D6','linalg-svd-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            lu = Page((destination/'D2a1/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-lu-reference',
                           'Try in playground'),lu.anchors)
            self.assertFalse(any('example=gams-linalg-eigen' in url or 'example=gams-linalg-svd' in url
                                 for url,label in lu.anchors))

    def test_qr_autodiff_links_preserve_sibling_and_alias_scope(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if
                            p['playground']['package_id'] in {'linalg','differentia','forwarddiff'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            expected = {
                'D5': [('linalg','linalg-qr-reference')],
                'H1': [('differentia','differentia-analytic-reference'),
                       ('forwarddiff','forwarddiff-analytic-reference')]}
            for code,pairs in expected.items():
                html = (destination/code/'index.html').read_text()
                primary = {url for url,label in Page(html).anchors if label=='Try in playground'}
                self.assertEqual(primary,{
                    f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'
                    for package,driver in pairs})
            lu = Page((destination/'D2a1/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-lu-reference',
                           'Try in playground'),lu.anchors)
            h1 = Page((destination/'H1/index.html').read_text())
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=forwarddiff',
                              'Open default example'),h1.anchors)
            self.assertFalse(any('package=forwarddiff&example=gams-differentia-' in url or
                                 'package=differentia&example=gams-forwarddiff-' in url
                                 for url,label in h1.anchors))

    def test_rule_and_difference_pages_do_not_inherit_pde_verification(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'kronrod','tsunami'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination,feed)
            for code,package,driver in [('H2c','kronrod','kronrod-moments-reference'),
                                        ('H1','tsunami','tsunami-differences-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label=='Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)
            pde = Page((destination/'I2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=tsunami',
                           'Open default example'),pde.anchors)
            self.assertFalse(any('example=gams-tsunami' in url for url,label in pde.anchors))

    def test_dispersion_class_pages_open_specific_checked_consumers(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'libmbd','dftd4'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D4','libmbd','libmbd-dimer-spectrum'),
                                          ('Z','dftd4','dftd4-dispersion-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url,label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary,
                    [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver',html)

    def test_matrix_root_and_box_pages_open_matching_drivers_without_inverse_inheritance(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['playground']['package_id'] in {'ntpoly','qnstop'}]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, package, driver in [('D','ntpoly','ntpoly-matrix-root-reference'),
                                          ('G2','qnstop','qnstop-box-reference')]:
                html = (destination/code/'index.html').read_text()
                primary = [url for url, label in Page(html).anchors if label == 'Try in playground']
                self.assertEqual(primary, [f'https://beliavsky.github.io/fortran-playground/fpm/?package={package}&example=gams-{driver}'])
                self.assertIn('Verified: a checked driver', html)
            inversion = Page((destination/'D2/index.html').read_text())
            self.assertIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-inverse-reference',
                           'Try in playground'), inversion.anchors)
            self.assertNotIn(('https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-matrix-root-reference',
                              'Try in playground'), inversion.anchors)

    def test_real_catalog_is_browsable_without_javascript_and_links_resolve(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)/'gams'
            count = generate_gams_site(destination, self.feed, asset_version='abc123')
            tree = self.feed['taxonomies']['gams']['classes']
            owners = {p['repository']['owner'].lower() for p in self.feed['projects']}
            self.assertEqual(count, 2+len(tree)+len(self.feed['projects'])+len(owners))
            index = (destination/'index.html').read_text(encoding='utf-8')
            self.assertIn('catalog.css?v=abc123', index)
            self.assertIn('data-search=', index)
            self.assertIn('fortran-lapack', index)
            self.assertIn('D2/', Page(index).links)
            for path in destination.rglob('index.html'):
                parsed = Page(path.read_text(encoding='utf-8'))
                self.assertEqual(len(parsed.ids), len(set(parsed.ids)), str(path))
                for url in parsed.links:
                    if urlparse(url).scheme or not url:
                        continue
                    if url.startswith('#'):
                        self.assertIn(url[1:], parsed.ids)
                        continue
                    target = (path.parent/unquote(urlparse(url).path)).resolve()
                    if target.is_relative_to(destination.resolve()):
                        self.assertTrue((target/'index.html').is_file() if urlparse(url).path.endswith('/') else target.is_file(), (path, url))
            lapack = (destination/'packages/fortran-lapack/index.html').read_text(encoding='utf-8')
            self.assertIn('Pinned source', lapack)
            self.assertIn('?package=fortran-lapack', lapack)
            self.assertIn('Reviewed procedures', lapack)
            self.assertIn('Federico Perini (perazz)', lapack)
            self.assertIn('../../authors/perazz/', Page(lapack).links)
            without_gradient = (destination/'G1b1a/index.html').read_text(encoding='utf-8')
            with_gradient = (destination/'G1b1b/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-nonlin-rosenbrock-nm', without_gradient)
            self.assertNotIn('example=gams-nonlin-rosenbrock-bfgs', without_gradient)
            self.assertNotIn('example=gams-nlopt-rosenbrock-lbfgs', without_gradient)
            self.assertIn('example=gams-nonlin-rosenbrock-bfgs', with_gradient)
            self.assertIn('example=gams-nlopt-rosenbrock-lbfgs', with_gradient)
            self.assertNotIn('example=gams-nonlin-rosenbrock-nm', with_gradient)
            singular = (destination/'H2a2a1/index.html').read_text(encoding='utf-8')
            smooth = (destination/'H2a1a1/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-quadpack-endpoint-singular', singular)
            self.assertNotIn('example=gams-quadpack-smooth', singular)
            self.assertIn('example=gams-quadpack-smooth', smooth)
            self.assertIn('example=gams-quadrature-fortran-smooth', smooth)
            self.assertNotIn('example=gams-quadpack-endpoint-singular', smooth)
            roots = (destination/'F1b/index.html').read_text(encoding='utf-8')
            for driver in ['roots-fortran-brent', 'nonlin-roots-brent', 'nonlin-roots-newton']:
                self.assertIn('example=gams-'+driver, roots)
                self.assertNotIn('example=gams-'+driver, smooth)
            dense = (destination/'D2a1/index.html').read_text(encoding='utf-8')
            least_squares = (destination/'D9a1/index.html').read_text(encoding='utf-8')
            for package in ['fortran-lapack', 'stdlib']:
                self.assertIn('example=gams-'+package+'-dense-solve', dense)
                self.assertNotIn('example=gams-'+package+'-least-squares', dense)
                self.assertIn('example=gams-'+package+'-least-squares', least_squares)
                self.assertNotIn('example=gams-'+package+'-dense-solve', least_squares)
            one_step = (destination/'I1a1a/index.html').read_text(encoding='utf-8')
            multistep = (destination/'I1a1b/index.html').read_text(encoding='utf-8')
            for package in ['dop853', 'rklib']:
                self.assertIn('example=gams-'+package+'-decay-oscillator', one_step)
                self.assertNotIn('example=gams-'+package+'-decay-oscillator', multistep)
            self.assertIn('example=gams-ddeabm-decay-oscillator', multistep)
            self.assertNotIn('example=gams-ddeabm-decay-oscillator', one_step)
            univariate = (destination/'E1a/index.html').read_text(encoding='utf-8')
            gridded = (destination/'E2a/index.html').read_text(encoding='utf-8')
            for package in ['finterp', 'pchip', 'bspline-fortran']:
                self.assertIn('example=gams-'+package+'-shape-interpolation', univariate)
                self.assertNotIn('example=gams-'+package+'-shape-interpolation', gridded)
            complex_transform = (destination/'J1a2/index.html').read_text(encoding='utf-8')
            cosine_transform = (destination/'J1a3/index.html').read_text(encoding='utf-8')
            for package in ['fftpack', 'kissfft-f']:
                self.assertIn('example=gams-'+package+'-complex-transform', complex_transform)
                self.assertNotIn('example=gams-'+package+'-complex-transform', cosine_transform)
            self.assertIn('example=gams-fftpack-cosine-transform', cosine_transform)
            self.assertNotIn('example=gams-fftpack-cosine-transform', complex_transform)
            box = (destination/'G2h1a2/index.html').read_text(encoding='utf-8')
            nonlinear = (destination/'G2h3b1b/index.html').read_text(encoding='utf-8')
            for driver in ['lbfgsb-box-quadratic', 'nlopt-box-quadratic']:
                self.assertIn('example=gams-'+driver, box)
                self.assertNotIn('example=gams-'+driver, nonlinear)
                self.assertNotIn('example=gams-'+driver, with_gradient)
            self.assertIn('example=gams-slsqp-circle-equality', nonlinear)
            self.assertNotIn('example=gams-slsqp-circle-equality', box)
            gamma = (destination/'C7a/index.html').read_text(encoding='utf-8')
            psi = (destination/'C7c/index.html').read_text(encoding='utf-8')
            bessel = (destination/'C10b1/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-fullerton-gamma-values', gamma)
            self.assertNotIn('example=gams-fullerton-digamma-values', gamma)
            self.assertIn('example=gams-fullerton-digamma-values', psi)
            self.assertNotIn('example=gams-fullerton-gamma-values', psi)
            self.assertIn('example=gams-bessels-modified-values', bessel)
            for code, driver in [('D4a1', 'fortran-lapack-symmetric-eigen'),
                                 ('D5', 'fortran-lapack-qr-decomposition'),
                                 ('D6', 'fortran-lapack-svd-decomposition')]:
                page = (destination/code/'index.html').read_text(encoding='utf-8')
                self.assertIn('example=gams-'+driver, page)
                self.assertNotIn('example=gams-'+driver, dense)
            location = (destination/'L1a1a/index.html').read_text(encoding='utf-8')
            dispersion = (destination/'L1a1b/index.html').read_text(encoding='utf-8')
            for package in ['stdlib', 'fstats']:
                self.assertIn('example=gams-'+package+'-mean-checks', location)
                self.assertNotIn('example=gams-'+package+'-sample-variance-checks', location)
                self.assertIn('example=gams-'+package+'-sample-variance-checks', dispersion)
                self.assertNotIn('example=gams-'+package+'-mean-checks', dispersion)
            uniform = (destination/'L6a21/index.html').read_text(encoding='utf-8')
            seed = (destination/'L6c/index.html').read_text(encoding='utf-8')
            for driver in ['mt19937-64-reference-sequence', 'rngff-lcg-reference-sequence']:
                self.assertIn('example=gams-'+driver, uniform)
                self.assertNotIn('example=gams-'+driver, seed)
            self.assertIn('example=gams-stdlib-seed-replay', seed)
            self.assertNotIn('example=gams-stdlib-seed-replay', uniform)
            differentiation = (destination/'H1/index.html').read_text(encoding='utf-8')
            for driver in ['numdiff-analytic-derivatives', 'fordiff-analytic-derivatives', 'ad-dnsvm-analytic-derivatives']:
                self.assertIn('example=gams-'+driver, differentiation)
                self.assertNotIn('example=gams-'+driver, smooth)
            systems = (destination/'F2/index.html').read_text(encoding='utf-8')
            for driver in ['minpack-rosenbrock-system', 'nonlin-rosenbrock-system', 'nlesolver-rosenbrock-system']:
                self.assertIn('example=gams-'+driver, systems)
                self.assertNotIn('example=gams-'+driver, roots)
                self.assertNotIn('example=gams-'+driver, with_gradient)
            indefinite = (destination/'D2b4/index.html').read_text(encoding='utf-8')
            positive_definite = (destination/'D2b1b/index.html').read_text(encoding='utf-8')
            for driver in ['minres-indefinite-solve', 'qdldl-quasidefinite-solve']:
                self.assertIn('example=gams-'+driver, indefinite)
                self.assertNotIn('example=gams-'+driver, positive_definite)
            self.assertIn('example=gams-kiss-positive-definite-solve', positive_definite)
            self.assertNotIn('example=gams-kiss-positive-definite-solve', indefinite)
            adaptive_box = (destination/'H2b1a1/index.html').read_text(encoding='utf-8')
            rules = (destination/'H2c/index.html').read_text(encoding='utf-8')
            self.assertIn('example=gams-dcuhre-box-integrals', adaptive_box)
            self.assertNotIn('example=gams-dcuhre-box-integrals', rules)
            for driver in ['gauss-jacobi-polynomial-moments', 'cubatures-simplex-moments']:
                self.assertIn('example=gams-'+driver, rules)
                self.assertNotIn('example=gams-'+driver, adaptive_box)
            for driver in ['finterp-bilinear-surface', 'bspline-tensor-surface']:
                self.assertIn('example=gams-'+driver, gridded)
                self.assertNotIn('example=gams-'+driver, univariate)
            stiff = (destination/'I1a2/index.html').read_text(encoding='utf-8')
            for driver in ['dvode-stiff-two-scale', 'lsoda-stiff-two-scale', 'stiff3-stiff-two-scale']:
                self.assertIn('example=gams-'+driver, stiff)
                self.assertNotIn('example=gams-'+driver, one_step)
                self.assertNotIn('example=gams-'+driver, multistep)
            polynomial = (destination/'F1a/index.html').read_text(encoding='utf-8')
            for driver in ['polyroots-real-reference', 'rpoly-real-reference', 'cpolyroots-complex-reference']:
                self.assertIn('example=gams-'+driver, polynomial)
                self.assertNotIn('example=gams-'+driver, roots)
                self.assertNotIn('example=gams-'+driver, systems)
            convolution = (destination/'J2/index.html').read_text(encoding='utf-8')
            for driver in ['spectrum-convolution-reference', 'fastconv-convolution-reference']:
                self.assertIn('example=gams-'+driver, convolution)
                self.assertNotIn('example=gams-'+driver, complex_transform)
                self.assertNotIn('example=gams-'+driver, cosine_transform)
            regression = (destination/'L8/index.html').read_text(encoding='utf-8')
            for driver in ['odrpack-line-total-least-squares', 'logistic-grouped-binomial-reference']:
                self.assertIn('example=gams-'+driver, regression)
                self.assertNotIn('example=gams-'+driver, least_squares)
                self.assertNotIn('example=gams-'+driver, location)
            matrix_equations = (destination/'D8/index.html').read_text(encoding='utf-8')
            for driver in ['slicot-lyapunov-known-matrix', 'slicot-continuous-sylvester', 'slicot-discrete-sylvester']:
                self.assertIn('example=gams-'+driver, matrix_equations)
                self.assertNotIn('example=gams-'+driver, dense)
                self.assertNotIn('example=gams-'+driver, indefinite)
            sitemap = ElementTree.fromstring((destination/'sitemap.xml').read_text(encoding='utf-8'))
            self.assertEqual(len(sitemap), count)

    def test_class_primary_playground_link_selects_matching_driver_and_labels_fallback(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p.get('playground', {}).get('package_id')=='stdlib']
        default = feed['projects'][0]['playground']['url']
        sorting = next(d['url'] for d in feed['demonstrations'] if d['id']=='stdlib-sorting-reference')
        mean = next(d['url'] for d in feed['demonstrations'] if d['id']=='stdlib-mean-checks')
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            for code, expected in [('N6', sorting), ('N', sorting), ('L1a1a', mean)]:
                page = Page((destination/code/'index.html').read_text(encoding='utf-8'))
                self.assertIn((expected, 'Try in playground'), page.anchors)
                self.assertNotIn(default, page.links)
            fallback = Page((destination/'N5/index.html').read_text(encoding='utf-8'))
            self.assertIn((default, 'Open default example'), fallback.anchors)
            self.assertNotIn((default, 'Try in playground'), fallback.anchors)
            package = Page((destination/'packages/stdlib/index.html').read_text(encoding='utf-8'))
            self.assertIn((default, 'Try in playground'), package.anchors)
            # Prefer a direct-class demonstration over an earlier descendant demonstration.
            direct = copy.deepcopy(next(d for d in feed['demonstrations'] if d['id']=='stdlib-sorting-reference'))
            direct.update(id='test-direct-N', gams_code='N', url=sorting+'&test_direct=1')
            feed['demonstrations'].append(direct)
            generate_gams_site(destination, feed)
            parent = Page((destination/'N/index.html').read_text(encoding='utf-8'))
            self.assertIn((direct['url'], 'Try in playground'), parent.anchors)
            child = Page((destination/'N6/index.html').read_text(encoding='utf-8'))
            self.assertIn((sorting, 'Try in playground'), child.anchors)
            self.assertNotIn(direct['url'], child.links)

    def test_parent_membership_uses_explicit_hierarchy_and_preserves_review_scope(self):
        # C1 and C10 are siblings, not prefix-related parent/child classes.
        project = self.feed['projects'][0]
        import copy
        feed = copy.deepcopy(self.feed)
        sample = copy.deepcopy(project)
        sample['name'] = '<unsafe & title>'
        sample['description'] = '<script>alert("bad")</script>'
        sample['curation']['gams_codes'] = ['C', 'C10']
        sample['curation']['procedures'] = []
        feed['projects'] = [sample]
        feed['demonstrations'] = []
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            self.assertIn('1 matching packages', (destination/'C/index.html').read_text(encoding='utf-8'))
            self.assertIn('0 matching packages', (destination/'C1/index.html').read_text(encoding='utf-8'))
            self.assertIn('1 matching packages', (destination/'C10/index.html').read_text(encoding='utf-8'))
            index = (destination/'index.html').read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;', index)
            self.assertNotIn('<script>alert(', index)
            package = next((destination/'packages').glob('*/index.html'))
            self.assertIn('Uncertain: no procedure-level mapping', package.read_text(encoding='utf-8'))
            feed['projects'] = []
            generate_gams_site(destination, feed)
            self.assertFalse(package.exists())

    def test_owner_grouping_public_names_search_and_fallback(self):
        import copy
        feed = copy.deepcopy(self.feed)
        perazz = [p for p in feed['projects'] if p['repository']['owner'].lower() == 'perazz']
        mixed_case = copy.deepcopy(perazz[0])
        mixed_case['repository']['owner'] = 'PERAZZ'
        feed['projects'] = [*perazz, mixed_case]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            owner = (destination/'authors/perazz/index.html').read_text(encoding='utf-8')
            self.assertIn('Packages from Federico Perini (perazz)', owner)
            self.assertEqual(owner.count('<article class="package"'), len(perazz)+1)
            self.assertIn('https://github.com/perazz', Page(owner).links)
            self.assertIn('additional authors and contributors', owner)
            index = (destination/'index.html').read_text(encoding='utf-8')
            self.assertIn('data-search="'+perazz[0]['name']+' Federico Perini (perazz)', index)
            feed.pop('owners')  # Older catalog feeds remain usable.
            generate_gams_site(destination, feed)
            fallback = (destination/'authors/perazz/index.html').read_text(encoding='utf-8')
            self.assertIn('Packages from perazz', fallback)
            self.assertNotIn('Federico Perini', fallback)
            feed['projects'] = []
            generate_gams_site(destination, feed)
            self.assertFalse((destination/'authors/perazz/index.html').exists())

    def test_local_playground_catalog_link_opens_the_published_catalog(self):
        from xfortran_serve import catalog_page
        page = catalog_page()
        self.assertIn('href="https://beliavsky.github.io/fortran-playground/gams/"', page)
        self.assertNotIn('href="../gams/"', page)

    def test_source_authorship_is_searchable_without_renaming_unconfirmed_accounts(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['id']=='github:lauvergn/ad_dnsvm']
        feed['owners']['lauvergn']['display_name'] = None
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            owner = (destination/'authors/lauvergn/index.html').read_text(encoding='utf-8')
            self.assertIn('<h1>Packages from lauvergn</h1>', owner)
            self.assertIn('Credited source authors', owner)
            self.assertIn('David Lauvergnat', owner)
            self.assertIn('APP/Example_dnS.f90#L53', owner)
            index = (destination/'index.html').read_text(encoding='utf-8')
            self.assertIn('David Lauvergnat', index)
            self.assertIn('Credited source author:', index)
            package = next((destination/'packages').glob('*/index.html')).read_text(encoding='utf-8')
            self.assertIn('id="name-attribution"', package)
            feed['attributions']['owner_names']['lauvergn']['status'] = 'confirmed'
            feed['owners']['lauvergn']['display_name'] = 'Different Public Name'
            generate_gams_site(destination, feed)
            owner = (destination/'authors/lauvergn/index.html').read_text(encoding='utf-8')
            self.assertIn('Packages from David Lauvergnat (lauvergn)', owner)
            self.assertIn('Different Public Name', owner)
            self.assertIn('recorded for review', owner)

    def test_forward_and_reverse_dependencies_link_pins_without_assuming_direct_edges(self):
        import copy
        feed = copy.deepcopy(self.feed)
        feed['projects'] = [p for p in feed['projects'] if p['id'] in ('github:toml-f/jonquil', 'github:toml-f/toml-f')]
        jonquil = next(p for p in feed['projects'] if p['name']=='jonquil')
        toml = next(p for p in feed['projects'] if p['name']=='toml-f')
        self.assertNotEqual(jonquil['dependencies']['packages'][0]['revision'], toml['curation']['reviewed_revision'])
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            generate_gams_site(destination, feed)
            forward = (destination/'packages/jonquil/index.html').read_text(encoding='utf-8')
            reverse = (destination/'packages/toml-f/index.html').read_text(encoding='utf-8')
            self.assertIn('combining direct and indirect dependencies', forward)
            self.assertIn('../../packages/toml-f/', Page(forward).links)
            self.assertIn('differs from the selected catalog revision', forward)
            self.assertIn('Used by (1 selected package)', reverse)
            self.assertIn('../../packages/jonquil/', Page(reverse).links)
            self.assertIn('uses a different revision', reverse)
            self.assertIn('No additional GitHub package dependencies', reverse)
            toml.pop('dependencies')
            generate_gams_site(destination, feed)
            reverse = (destination/'packages/toml-f/index.html').read_text(encoding='utf-8')
            self.assertIn('Dependency information has not been recorded', reverse)
            self.assertIn('Used by (1 selected package)', reverse)
