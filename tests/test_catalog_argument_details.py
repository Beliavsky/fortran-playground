import copy
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from catalog_argument_intents import signature_markup, argument_details_markup, optional_notation_markup
from catalog_reviews import digest, validate_feed
from test_catalog_reviews import fixture


class ArgumentDetailsTests(unittest.TestCase):
    def test_imported_optional_arguments_use_documentation_brackets_only(self):
        feed,_=fixture();procedure=feed['projects'][0]['classifications'][0]['procedures'][0]
        procedure['usage']='call solve(a,b)'
        procedure['argument_details']=[{'name':'A','declarations':[{'text':'real, optional :: a',
            'path':'src/solver.f90','line_start':11,'line_end':11}]}]
        original=copy.deepcopy(procedure)
        class Text(HTMLParser):
            def __init__(self):super().__init__();self.text=[]
            def handle_data(self,text):self.text.append(text)
        parsed=Text();parsed.feed(signature_markup(procedure))
        self.assertEqual(''.join(parsed.text),'CALL solve([A],B)')
        self.assertIn('not literal Fortran syntax',optional_notation_markup(procedure))
        self.assertEqual(procedure,original)

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
        self.assertIn('data-normalized-code="real(wp), intent(in) :: x(n,m)"',expanded)
        self.assertIn('Show declarations',expanded)
        self.assertIn('Hide declarations',expanded)

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
        self.assertNotIn('No explicit INTENT',markup)
        detail=argument_details_markup(procedure,'https://github.com/example/solver/blob/'+'a'*40+'/')
        self.assertEqual(detail.count('<pre>'),1)
        self.assertIn('</span> ! Allocated solution. &lt;script&gt;',detail)
        self.assertNotIn('<dt>',detail)
        self.assertNotIn('src/solver.f90:',detail)
        declaration['comments'][0]['path']='not-in-evidence'
        feed['snapshot_id']=digest(feed)
        with self.assertRaises(ValueError):validate_feed(feed)


    def test_declarations_share_one_box_with_trailing_comments_in_call_order(self):
        procedure={'signature':'call solve(n, x, l)', 'argument_details':[
            {'name':'l','declarations':[{'text':'REAL(8) :: X(N), L(N)','shared':True}]},
            {'name':'n','declarations':[{'text':'INTEGER :: N','comments':[
                {'text':'!> Number of entries.\n!! Must be positive.'}]}]},
            {'name':'x','declarations':[{'text':'REAL(8) :: X(N), L(N)','shared':True,
                'comments':[{'text':'Input <values>.'}]}]}]}
        rendered=argument_details_markup(procedure,'https://example.test/')
        self.assertEqual(rendered.count('<pre>'),1)
        self.assertEqual(rendered.count('<code>'),1)
        self.assertNotIn('<dl>',rendered)
        self.assertNotIn('Shared declaration',rendered)
        self.assertNotIn('<a ',rendered)
        self.assertIn('</span> ! Number of entries. Must be positive.',rendered)
        self.assertIn('</span> ! Input &lt;values&gt;.',rendered)
        self.assertLess(rendered.index('INTEGER :: N'),rendered.index('data-normalized-code="REAL(8) :: X(N)"'))
        self.assertLess(rendered.index('data-normalized-code="REAL(8) :: X(N)"'),rendered.index('data-normalized-code="REAL(8) :: L(N)"'))

if __name__=='__main__':unittest.main()
