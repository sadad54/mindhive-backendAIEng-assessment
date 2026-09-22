import unittest
from dataclasses import replace
from matcher.data import Catalogue,OrderLine
from matcher.identifiers import IdentifierIndex
from matcher.lexical import LexicalIndex,attributes,conflicts,normalise

class LexicalTests(unittest.TestCase):
    def setUp(self):
        self.cat=Catalogue({'acme':{
            'A':{'item_name':'Stallion Flap Disc 5"','brand':'Stallion','disabled':'0','barcode':'00123'},
            'B':{'item_name':'Stallion Flap Disc 7"','brand':'Stallion','disabled':'0','barcode':'00777'},
            'C':{'item_name':'Kanto Flap Disc 5"','brand':'Kanto','disabled':'0','barcode':''}},
            'nordic':{'N':{'item_name':'Stallion Flap Disc 5"','brand':'Stallion','disabled':'0','barcode':''}}})
        self.line=OrderLine('L1','acme','C1','2026-05-01','Stallion Flap Disc 5"')

    def test_fraction_and_material_normalisation(self):
        self.assertEqual(attributes('3/4" screw')['length'],{19.05})
        self.assertEqual(attributes('19.05mm screw')['length'],{19.05})
        self.assertIn('zinc plated',normalise('ZP screw'))
        self.assertIn('stainless',normalise('S/S screw'))
        self.assertNotEqual(normalise('3/4"'),normalise('34"'))

    def test_typo_retrieves_compatible_size_only(self):
        result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_text='Stalion flap disc 5 inch'))
        self.assertEqual(result.candidates[0].code,'A')
        self.assertNotIn('B',[r.code for r in result.candidates])
        self.assertNotIn('N',[r.code for r in result.candidates])

    def test_known_brand_is_not_substituted(self):
        result=LexicalIndex(self.cat).retrieve(self.line)
        self.assertNotIn('C',[r.code for r in result.candidates])

    def test_barcode_cannot_hide_size_conflict(self):
        result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_barcode='00777'))
        self.assertIn('identifier_text_conflict',result.issues)
        self.assertNotIn('B',[r.code for r in result.candidates])

    def test_material_and_grade_conflicts(self):
        self.assertIn('material',conflicts(attributes('ZP screw'),attributes('Stainless 410 screw')))
        self.assertIn('grade',conflicts(attributes('PVC Class E'),attributes('PVC Class C')))
        self.assertIn('steel_grade',conflicts(attributes('Stainless 304'),attributes('Stainless 316')))

    def test_duplicate_name_remains_ambiguous(self):
        self.cat.by_tenant['acme']['D']=dict(self.cat.by_tenant['acme']['A'],barcode='')
        result=LexicalIndex(self.cat).retrieve(self.line)
        self.assertFalse(result.exact_unique)
        self.assertIn('ambiguous_exact_names',result.issues)

    def test_nonitem_and_unknown_tenant(self):
        self.assertEqual(LexicalIndex(self.cat).retrieve(replace(self.line,raw_text='delivery charge')).issues,('not_an_item',))
        self.assertEqual(LexicalIndex(self.cat).retrieve(replace(self.line,tenant='unknown')).candidates,())

    def test_reordered_catalogue_is_deterministic(self):
        other=Catalogue({t:dict(reversed(list(items.items()))) for t,items in self.cat.by_tenant.items()})
        self.assertEqual(LexicalIndex(self.cat).retrieve(self.line),LexicalIndex(other).retrieve(self.line))
