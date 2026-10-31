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
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class GamsSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = build_export()

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
            self.assertIn('No procedure-level mapping', package.read_text(encoding='utf-8'))
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
