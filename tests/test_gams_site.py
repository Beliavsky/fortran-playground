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
