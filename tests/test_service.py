import unittest
from dataclasses import replace
from matcher.data import Catalogue,OrderLine
from matcher.identifiers import IdentifierIndex
from matcher.service import Matcher

class ServiceTests(unittest.TestCase):
 def setUp(self):
  self.cat=Catalogue({'a':{'A':dict(item_name='Demo Disc',brand='Demo',disabled='0',barcode='001')}})
  self.line=OrderLine('L','a','C','2026-01-01','Demo Disc',raw_barcode='001')
  self.policy={'enabled_buckets':['identifier'],'buckets':{'identifier':{'probability':.94},'lexical_exact':{'probability':.7}}}
 def test_identifier_acceptance_and_cold_catalogue(self):
  r=Matcher(self.cat,IdentifierIndex(self.cat),self.policy).match(self.line)
  self.assertEqual((r.item_code,r.decision,r.confidence),('A','auto',.94))
 def test_non_enabled_bucket_reviews_with_candidates(self):
  r=Matcher(self.cat,IdentifierIndex(self.cat),self.policy).match(replace(self.line,raw_barcode=''))
  self.assertEqual((r.item_code,r.decision),('','review'))
  self.assertEqual(r.candidates[0].item_code,'A')
 def test_unknown_tenant_never_escapes(self):
  r=Matcher(self.cat,IdentifierIndex(self.cat),self.policy).match(replace(self.line,tenant='b'))
  self.assertEqual((r.item_code,r.candidates),('',()))
 def test_unknown_barcode_blocks_even_enabled_group(self):
  r=Matcher(self.cat,IdentifierIndex(self.cat),self.policy).match(replace(self.line,raw_barcode='999'))
  self.assertEqual(r.decision,'review')
