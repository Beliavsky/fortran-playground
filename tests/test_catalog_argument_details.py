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
        self.assertIn('</span> ! Allocated solution. …',detail)
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;',detail)
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
        self.assertIn('</span> ! Number of entries. …',rendered)
        self.assertIn('Full argument documentation',rendered)
        self.assertIn('Must be positive.',rendered)
        self.assertIn('</span> ! Input &lt;values&gt;.',rendered)
        self.assertLess(rendered.index('INTEGER :: N'),rendered.index('data-normalized-code="REAL(8) :: X(N)"'))
        self.assertLess(rendered.index('data-normalized-code="REAL(8) :: X(N)"'),rendered.index('data-normalized-code="REAL(8) :: L(N)"'))

    def test_long_comments_are_bounded_and_full_documentation_is_preserved(self):
        from catalog_argument_intents import comment_preview
        self.assertEqual(comment_preview('First sentence. Second sentence.'),'First sentence. …')
        self.assertEqual(comment_preview('Value 3.14 is supported.'),'Value 3.14 is supported.')
        self.assertEqual(comment_preview('Short comment.'),'Short comment.')
        long=' '.join(['Long argument explanation']*20)
        preview=comment_preview(long)
        self.assertLessEqual(len(preview),100)
        self.assertTrue(preview.endswith(' …'))
        self.assertIn(preview[:-2].split()[-1],long.split())
        self.assertEqual(comment_preview('X'*200),'…')
        procedure={'signature':'call solve(x, y)', 'argument_details':[
            {'name':'x','declarations':[{'text':'REAL :: X','comments':[{'text':long}]}]},
            {'name':'y','declarations':[{'text':'REAL :: Y','comments':[
                {'text':'This routine solves a general problem.'},
                {'text':'Input vector. Further details follow.'}]}]}]}
        markup=argument_details_markup(procedure,'https://example.test/')
        code=markup.split('<pre><code>',1)[1].split('</code></pre>',1)[0]
        self.assertIn(preview,code)
        self.assertIn('! Input vector. …',code)
        self.assertNotIn('This routine',code)
        self.assertNotIn('Further details',code)
        self.assertEqual(code.count('class="declaration-code"'),2)
        self.assertIn(long,markup.split('Full argument documentation',1)[1])
        self.assertIn('This routine solves a general problem.',markup)

    def test_output_markers_are_explicit_aligned_and_outside_copied_code(self):
        procedure={'signature':'call solve(a, b, c, d, e, f, g, h)', 'argument_details':[
            {'name':'a','declarations':[{'text':'REAL, INTENT(OUT) :: A'}]},
            {'name':'b','declarations':[{'text':'REAL, INTENT(IN OUT) :: B'}]},
            {'name':'c','declarations':[{'text':'REAL, INTENT(IN) :: C'}]},
            {'name':'d','declarations':[{'text':"CHARACTER(*) :: D = 'intent(out)'",'comments':[{'text':'intent(out) in prose is not evidence.'}]}]},
            {'name':'e','declarations':[{'text':'REAL :: E'},{'text':'INTENT(OUT) E'}]},
            {'name':'f','declarations':[{'text':'REAL, INTENT(OUT) :: F'}]},
            {'name':'g','declarations':[{'text':'REAL, INTENT(OUT) :: G'},{'text':'REAL, INTENT(INOUT) :: G'}]},
            {'name':'h','declarations':[{'text':'REAL :: H'}]}],
            'arguments':[{'name':'f','intent':'conditional'},{'name':'h','intent':'out'}]}
        rendered=argument_details_markup(procedure,'https://example.test/')
        class Rows(HTMLParser):
            def __init__(self):super().__init__();self.markers=[];self.in_code=False;self.code=[]
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if tag=='code':self.in_code=True
                if attrs.get('class')=='declaration-row':self.markers.append(attrs.get('data-output-marker',''))
            def handle_endtag(self,tag):
                if tag=='code':self.in_code=False
            def handle_data(self,text):
                if self.in_code:self.code.append(text)
        parser=Rows();parser.feed(rendered)
        self.assertEqual(parser.markers,['*','**','','','*','','','','','*'])
        code=''.join(parser.code)
        self.assertEqual(len(code.splitlines()),10)
        self.assertFalse(any(line.lstrip().startswith('*') for line in code.splitlines()))
        self.assertNotIn('Markers:',code)
        self.assertIn('Markers: * intent(out); ** intent(inout).',rendered)
        # No legend or output marker for an input-only declaration.
        only_input={'signature':'call solve(c)','argument_details':[procedure['argument_details'][2]]}
        plain=argument_details_markup(only_input,'https://example.test/')
        self.assertNotIn('data-output-marker=',plain)
        self.assertNotIn('Markers:',plain)

if __name__=='__main__':unittest.main()
