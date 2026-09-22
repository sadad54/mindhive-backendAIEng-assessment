import unittest
from dataclasses import replace
from matcher.data import Catalogue, OrderLine
from matcher.identifiers import IdentifierIndex
from split_data import build_split

class IdentifierTests(unittest.TestCase):
    def setUp(self):
        self.line=OrderLine('L1','acme','C1','2026-05-01','Stallion 5 inch flap disc',raw_barcode='00123')
        self.cat=Catalogue({'acme':{'A':{'disabled':'0','item_name':'Stallion 5 inch flap disc','barcode':'00123'},'B':{'disabled':'0','item_name':'Stallion 7 inch flap disc','barcode':'00999'}},'nordic':{'N':{'disabled':'0','item_name':'milk','barcode':'00888'}}})
        self.alias={'tenant':'acme','customer_id':'C1','customer_sku':'CUSTOM','item_code':'B','valid_from':'2026-01-01','valid_to':'','source':'confirmed_order','confidence':'1.0'}

    def test_exact_barcode_preserves_leading_zeros(self):
        e=IdentifierIndex(self.cat).retrieve(self.line)
        self.assertEqual(e.codes,('A',));self.assertEqual(e.issues,())

    def test_conflicting_size_is_flagged(self):
        e=IdentifierIndex(self.cat).retrieve(replace(self.line,raw_text='Stallion 7 inch flap disc'))
        self.assertIn('numeric_text_conflict_or_unparsed_quantity',e.issues)

    def test_barcode_alias_conflict(self):
        e=IdentifierIndex(self.cat,[self.alias]).retrieve(replace(self.line,buyer_sku='CUSTOM'))
        self.assertEqual(e.codes,('A','B'));self.assertIn('identifier_conflict',e.issues)

    def test_alias_scope_date_and_trust(self):
        line=replace(self.line,raw_barcode='',buyer_sku='CUSTOM',raw_text='disc')
        self.assertEqual(IdentifierIndex(self.cat,[self.alias]).retrieve(replace(line,customer_id='OTHER')).codes,())
        expired=dict(self.alias,valid_to='2026-04-30')
        self.assertEqual(IdentifierIndex(self.cat,[expired]).retrieve(line).codes,())
        weak=dict(self.alias,confidence='0.55')
        self.assertIn('untrusted_alias_metadata',IdentifierIndex(self.cat,[weak]).retrieve(line).issues)

    def test_duplicate_barcode_is_not_unique(self):
        self.cat.by_tenant['acme']['B']['barcode']='00123'
        self.assertIn('identifier_conflict',IdentifierIndex(self.cat).retrieve(self.line).issues)

    def test_cross_tenant_lookup_and_alias_target(self):
        self.assertEqual(IdentifierIndex(self.cat).retrieve(replace(self.line,raw_barcode='00888')).codes,())
        alias=dict(self.alias,item_code='N')
        e=IdentifierIndex(self.cat,[alias]).retrieve(replace(self.line,raw_barcode='',buyer_sku='CUSTOM'))
        self.assertEqual(e.codes,());self.assertIn('ineligible_identifier_target',e.issues)

    def test_unknown_tenant_and_disabled_target(self):
        self.assertEqual(IdentifierIndex(self.cat).retrieve(replace(self.line,tenant='unknown')).issues,('unknown_tenant',))
        self.cat.by_tenant['acme']['A']['disabled']='1'
        self.assertEqual(IdentifierIndex(self.cat).retrieve(self.line).codes,())

    def test_grouped_split_is_stable_and_links_transitively(self):
        a=replace(self.line,raw_barcode='',buyer_sku='X')
        b=replace(a,line_id='L2',raw_text='different')
        c=replace(a,line_id='L3',buyer_sku='',raw_text='third')
        labels={'L1':'A','L2':'B','L3':'B'}
        result=build_split([a,b,c],labels)
        self.assertEqual(result,build_split([c,b,a],labels))
        self.assertEqual(len({v['group'] for v in result.values()}),1)
