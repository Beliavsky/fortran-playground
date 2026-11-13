import copy
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from catalog_argument_intents import signature_markup, argument_details_markup
from catalog_reviews import digest, validate_feed
from test_catalog_reviews import fixture


class ArgumentDetailsTests(unittest.TestCase):
    def test_shared_declaration_is_individual_in_tooltip_and_original_in_details(self):
        procedure={'signature':'CALL solve(A,B)', 'argument_details':[
            {'name':'A','dummy':'x','declarations':[{'text':'real(wp), intent(in) :: x(n,m), y(n,m)',
              'shared':True,'path':'src.f90','line_start':1,'line_end':1,
              'comments':[{'text':'Both matrices use the same units.','path':'src.f90','line_start':1,'line_end':1}]}]}]}
        markup=signature_markup(procedure)
        self.assertIn('real(wp), intent(in) :: x(n,m)',markup)
        self.assertNotIn('y(n,m)',markup)
        self.assertNotIn('Shared declaration',markup)
        self.assertIn('Shared comment: Both matrices',markup)
        expanded=argument_details_markup(procedure,'https://example.test/')
        self.assertIn('x(n,m), y(n,m)',expanded)

    def test_imported_declarations_comments_escaping_and_source_links(self):
        feed,_=fixture();procedure=feed['projects'][0]['classifications'][0]['procedures'][0]
        declaration={'path':'src/solver.f90','line_start':11,'line_end':11,
                     'text':'real, allocatable, intent(out) :: a(:,:)',
                     'comments':[{'path':'src/solver.f90','line_start':12,'line_end':12,
                                  'text':'Allocated solution. <script>bad</script>','kind':'following'}]}
        procedure['argument_details']=[{'name':'A','declarations':[declaration]}]
        feed['snapshot_id']=digest(feed);validate_feed(feed)
        markup=signature_markup(procedure)
        self.assertIn('allocatable',markup);self.assertIn('Allocated solution.',markup)
        self.assertNotIn('<script>',markup)
        self.assertIn('data-argument-intent="unspecified"',markup)
        detail=argument_details_markup(procedure,'https://github.com/example/solver/blob/'+'a'*40+'/')
        self.assertIn('#L12-L12',detail);self.assertIn('&lt;script&gt;',detail)
        declaration['comments'][0]['path']='not-in-evidence'
        feed['snapshot_id']=digest(feed)
        with self.assertRaises(ValueError):validate_feed(feed)


if __name__=='__main__':unittest.main()
