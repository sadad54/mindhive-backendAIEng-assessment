import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from starter.sync.fake_erp import FakeErp,Record
from sync_fixed.adapter import Store,pull,push,utc,PullCapacityError

# Original adapter expects a script-directory import. Alias the identical vendor module.
import starter.sync.fake_erp as vendor
sys.modules.setdefault('fake_erp',vendor)
from starter.sync import sync_adapter as old

class SyncTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=str(Path(self.tmp.name)/'store.sqlite')
  self.store=Store(self.path,'tenant-a');self.erp=FakeErp(timeout_rate=0)
 def tearDown(self):self.store.close();self.tmp.cleanup()
 def seed(self,n=1):
  for i in range(n):self.erp.records[str(i)]=Record(str(i),{'price':1},1,self.erp._now())
 def test_timestamp_ties_original_loses_rows_fixed_drains(self):
  self.seed(5);legacy=old.LocalStore();old.pull(self.erp,legacy,page_size=2)
  self.assertEqual(len(legacy.records),2)
  pull(self.erp,self.store,page_size=2);self.assertEqual(self.store.db.execute('SELECT count(*) FROM records').fetchone()[0],5)
 def test_cursor_atomicity_original_advanced_before_failed_apply(self):
  self.seed();legacy=old.LocalStore()
  def fail(_):raise RuntimeError('crash')
  legacy.upsert=fail
  with self.assertRaises(RuntimeError):old.pull(self.erp,legacy)
  self.assertIsNotNone(legacy.cursor)
  def crash(stage):raise RuntimeError('crash')
  with self.assertRaises(RuntimeError):pull(self.erp,self.store,crash_hook=crash)
  self.assertIsNone(self.store.cursor());self.assertIsNone(self.store.record('0'))
  pull(self.erp,self.store);self.assertIsNotNone(self.store.record('0'))
 def test_timeout_after_commit_one_logical_write(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2});self.erp.timeout_rate=1
  push(self.erp,self.store)
  self.assertEqual(len(self.erp.write_log),1);self.assertEqual(self.store.record('0')['dirty'],0)
  # Original retry creates a new key and force-rebases after conflict.
  erp=FakeErp(timeout_rate=1);erp.records['0']=Record('0',{'price':1},1,erp._now())
  legacy=old.LocalStore();old.pull(erp,legacy);legacy.records['0'].payload={'price':2};legacy.records['0'].dirty=True
  try:old.push(erp,legacy)
  except vendor.ErpTimeout:pass
  self.assertEqual(len(erp.write_log),2)
 def test_conflict_never_rebases_over_remote_edit(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2})
  self.erp.write('0',{'price':3},base_version=1);push(self.erp,self.store)
  self.assertEqual(self.erp.get('0').payload,{'price':3})
  self.assertEqual(self.store.db.execute('SELECT count(*) FROM conflicts').fetchone()[0],1)
  legacy=old.LocalStore();legacy.records['0']=old.LocalRecord('0',{'price':2},1,'2026-07-31 16:00:00',True)
  old.push(self.erp,legacy);self.assertEqual(self.erp.get('0').payload,{'price':2})
 def test_pull_does_not_drop_dirty_edit_due_to_clock_comparison(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2})
  pull(self.erp,self.store);self.assertEqual(json.loads(self.store.record('0')['payload']),{'price':2})
  legacy=old.LocalStore();legacy.records['0']=old.LocalRecord('0',{'price':2},1,'2026-07-31 16:00:01',True)
  old.pull(self.erp,legacy);self.assertEqual(legacy.records['0'].payload,{'price':1})
 def test_timestamps_are_utc_not_server_wall_clock(self):
  self.seed();pull(self.erp,self.store)
  self.assertEqual(self.store.record('0')['updated_utc'],'2026-07-31T16:00:00+00:00')
  legacy=old.LocalStore();old.pull(self.erp,legacy)
  self.assertEqual(legacy.records['0'].updated_at_utc,'2026-08-01 00:00:00')
 def test_replay_deduplicates_applied_log(self):
  self.seed();pull(self.erp,self.store);pull(self.erp,self.store,full=True)
  self.assertEqual(self.store.db.execute('SELECT count(*) FROM applied').fetchone()[0],1)
  legacy=old.LocalStore();old.pull(self.erp,legacy);legacy.cursor=None;old.pull(self.erp,legacy)
  self.assertEqual(len(legacy.applied_log),2)
 def test_restart_after_commit_and_idempotency_expiry(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2})
  def crash(stage):
   if stage=='after_remote_commit':raise RuntimeError('process died')
  with self.assertRaises(RuntimeError):push(self.erp,self.store,crash_hook=crash)
  self.store.close();self.store=Store(self.path,'tenant-a');self.erp._idem.clear();self.erp.tick(61)
  pull(self.erp,self.store);push(self.erp,self.store)
  self.assertEqual(len(self.erp.write_log),1);self.assertEqual(self.store.record('0')['dirty'],0)
 def test_creation_timeout_after_cache_expiry_uses_zero_base(self):
  self.store.edit('new',{'price':2});self.erp.timeout_rate=1
  push(self.erp,self.store,max_attempts=1);self.erp._idem.clear();self.erp.tick(61)
  push(self.erp,self.store);self.assertEqual(len(self.erp.write_log),1)
 def test_capacity_failure_does_not_advance_cursor(self):
  self.seed(5)
  with self.assertRaises(PullCapacityError):pull(self.erp,self.store,page_size=2,max_records=4)
  self.assertIsNone(self.store.cursor())
 def test_tenant_store_cannot_be_reused(self):
  with self.assertRaises(ValueError):Store(self.path,'tenant-b')
 def test_hard_process_kill_during_pull_rolls_back(self):
  script="""import os,sys
from sync_fixed.adapter import Store,pull
from starter.sync.fake_erp import FakeErp,Record
s=Store(sys.argv[1],'tenant-a');e=FakeErp();e.records['0']=Record('0',{'price':1},1,e._now())
pull(e,s,crash_hook=lambda stage:os._exit(9))
"""
  r=subprocess.run([sys.executable,'-c',script,self.path])
  self.assertEqual(r.returncode,9);self.assertIsNone(self.store.cursor());self.assertIsNone(self.store.record('0'))
 def test_new_edit_cannot_mutate_uncertain_request(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2});self.erp.timeout_rate=1
  push(self.erp,self.store,max_attempts=1)
  with self.assertRaises(ValueError):self.store.edit('0',{'price':3})
 def test_outbox_survives_crash_before_network(self):
  self.seed();pull(self.erp,self.store);self.store.edit('0',{'price':2})
  def crash(stage):
   if stage=='after_outbox_commit':raise RuntimeError('crash')
  with self.assertRaises(RuntimeError):push(self.erp,self.store,crash_hook=crash)
  key=self.store.db.execute('SELECT key FROM outbox').fetchone()[0]
  self.store.close();self.store=Store(self.path,'tenant-a');push(self.erp,self.store)
  self.assertEqual(self.store.db.execute('SELECT key FROM outbox').fetchone()[0],key)
  self.assertEqual(len(self.erp.write_log),1)
 def test_partial_batch_recovery_does_not_repeat_committed_item(self):
  self.seed(2);pull(self.erp,self.store)
  for eid in ['0','1']:self.store.edit(eid,{'price':2})
  def crash(stage):
   if stage=='after_remote_commit':raise RuntimeError('crash')
  with self.assertRaises(RuntimeError):push(self.erp,self.store,crash_hook=crash)
  self.erp._idem.clear();push(self.erp,self.store)
  self.assertEqual(len(self.erp.write_log),2)
  self.assertEqual({eid for eid,_,_ in self.erp.write_log},{'0','1'})
