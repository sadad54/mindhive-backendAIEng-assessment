import json
import unittest
from dataclasses import replace
from matcher.data import Catalogue, OrderLine
from matcher.lexical import LexicalIndex

class PackTests(unittest.TestCase):
    def setUp(self):
        def item(name, factor, barcode):
            return dict(item_name=name, brand='Demo', disabled='0', stock_uom='Packet',
                        barcode=barcode, uom_conversions=json.dumps([
                            dict(uom='Packet', conversion_factor=1),
                            dict(uom='Carton', conversion_factor=factor)]))
        self.cat=Catalogue({'a':{'S':item('Demo Flap Disc',10,'001'),
                                 'B':item('Demo Flap Disc (Bulk)',144,'002')}})
        self.line=OrderLine('L','a','C','2026-01-01','Demo Flap Disc',qty='5',uom_text='ctn')

    def test_exact_name_and_quantity_do_not_resolve_pack(self):
        for qty in ['1','5','12','50']:
            self.assertIn('ambiguous_pack',LexicalIndex(self.cat).retrieve(replace(self.line,qty=qty)).issues)

    def test_explicit_variants_resolve(self):
        for marker,code in [('Bulk','B'),('standard','S')]:
            result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_text='Demo Flap Disc '+marker))
            self.assertEqual(result.candidates[0].code,code)
            self.assertNotIn('ambiguous_pack',result.issues)

    def test_unique_identifier_resolves_but_shared_barcode_does_not(self):
        result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_barcode='002'))
        self.assertEqual(result.candidates[0].code,'B')
        self.assertNotIn('ambiguous_pack',result.issues)
        self.cat.by_tenant['a']['S']['barcode']='002'
        result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_barcode='002'))
        self.assertIn('ambiguous_pack',result.issues)
        self.assertIn('identifier_conflict',result.issues)

    def test_conflicting_variant_and_identifier_blocks(self):
        result=LexicalIndex(self.cat).retrieve(replace(self.line,raw_text='Demo Flap Disc Bulk',raw_barcode='001'))
        self.assertIn('pack_evidence_conflict',result.issues)

    def test_stock_and_price_do_not_choose_variant(self):
        self.cat.by_tenant['a']['S'].update(available_qty='0',list_price='999')
        self.cat.by_tenant['a']['B'].update(available_qty='1000',list_price='1')
        self.assertIn('ambiguous_pack',LexicalIndex(self.cat).retrieve(self.line).issues)

    def test_other_tenant_and_disabled_sibling_do_not_block(self):
        bulk=self.cat.by_tenant['a'].pop('B')
        self.cat.by_tenant['b']={'B':bulk}
        self.assertNotIn('ambiguous_pack',LexicalIndex(self.cat).retrieve(self.line).issues)
        self.cat.by_tenant['a']['B']=dict(bulk,disabled='1')
        self.assertNotIn('ambiguous_pack',LexicalIndex(self.cat).retrieve(self.line).issues)

    def test_guard_sees_bulk_outside_top_three(self):
        for code in ['S1','S2']:
            self.cat.by_tenant['a'][code]=dict(self.cat.by_tenant['a']['S'],barcode='')
        result=LexicalIndex(self.cat).retrieve(self.line)
        self.assertNotIn('B',[c.code for c in result.candidates])
        self.assertIn('ambiguous_pack',result.issues)
