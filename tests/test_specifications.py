import unittest
from dataclasses import replace
from matcher.data import Catalogue,OrderLine
from matcher.lexical import LexicalIndex,attributes

class SpecificationTests(unittest.TestCase):
    def setUp(self):
        self.cat=Catalogue({'a':{'A':dict(item_name='Demo Hex Bolt M8x50 HDG',brand='Demo',disabled='0',barcode='123'),
                                 'B':dict(item_name='Demo Hex Bolt M8x50 Stainless 304',brand='Demo',disabled='0',barcode='456')}})
        self.line=OrderLine('L','a','C','2026-01-01','Demo Hex Bolt M8x50')
    def test_missing_finish_reviews(self):
        self.assertIn('missing_material',LexicalIndex(self.cat).retrieve(self.line).issues)
    def test_explicit_finish_resolves(self):
        r=LexicalIndex(self.cat).retrieve(replace(self.line,raw_text=self.line.raw_text+' HDG'))
        self.assertEqual(r.candidates[0].code,'A')
        self.assertNotIn('missing_material',r.issues)
        self.assertNotIn('B',[c.code for c in r.candidates])
    def test_identifier_supplies_omission_not_contradiction(self):
        r=LexicalIndex(self.cat).retrieve(replace(self.line,raw_barcode='123'))
        self.assertNotIn('missing_material',r.issues)
        r=LexicalIndex(self.cat).retrieve(replace(self.line,raw_barcode='123',raw_text=self.line.raw_text+' Stainless 304'))
        self.assertIn('identifier_text_conflict',r.issues)
    def test_ss_grade_and_complex_requests(self):
        self.assertEqual(attributes('SS304')['steel_grade'],{'304'})
        r=LexicalIndex(self.cat).retrieve(replace(self.line,raw_text=self.line.raw_text+' not HDG'))
        self.assertIn('complex_request',r.issues)
