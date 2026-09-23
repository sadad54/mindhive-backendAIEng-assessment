import sqlite3,unittest
from pathlib import Path
from starter.make_perf_db import DDL
from perf_report import run

class PerfTests(unittest.TestCase):
 def test_original_populations_order_and_nearest_rank(self):
  c=sqlite3.connect(':memory:');c.executescript(DDL)
  c.execute("INSERT INTO tenant VALUES ('T','tenant','plan')")
  c.execute("INSERT INTO item VALUES ('T','A','a','g',1)")
  c.executemany('INSERT INTO order_line VALUES (?,?,?,?,?,?)',[
   ('L1','T','C1','email','2026-05-01T00:00:00Z','x'),
   ('L2','T','C2','voice','2026-05-01T00:00:00Z','x'),
   ('L3','T','C3','email','2026-05-02T00:00:00Z','x')])
  events=[(i,'T','L1' if i%2 else 'L2','A','lexical',.5,1,1,i,'2026-05-01T00:00:00Z') for i in range(1,21)]
  events += [(21,'T','L3','A','lexical',.7,1,1,200,'2026-05-03T00:00:00Z'),
             (22,'T','L1','A','lexical',.2,1,0,1,'2026-04-30T00:00:00Z')]
  c.executemany('INSERT INTO match_event VALUES (?,?,?,?,?,?,?,?,?,?)',events)
  c.row_factory=sqlite3.Row
  sql=Path('starter/report_query.sql').read_text().replace("'2026-06-30'","'2026-05-02'")
  expected=[dict(r) for r in c.execute(sql)]
  actual=run(c,date_to='2026-05-02')
  self.assertTrue(c.in_transaction)
  self.assertIs(c.row_factory,sqlite3.Row)
  self.assertEqual([{k:v for k,v in r.items() if k!='p95_latency_ms'} for r in actual],expected)
  day1=[r for r in actual if r['day']=='2026-05-01']
  self.assertTrue(all(r['p95_latency_ms']==19 for r in day1))
  self.assertTrue(all(r['repeat_items_prev_day']==1 for r in day1))
  day2=[r for r in actual if r['day']=='2026-05-02'][0]
  self.assertEqual(day2['candidates_considered'],1)
  self.assertIsNone(day2['max_latency_ms']);self.assertIsNone(day2['p95_latency_ms'])
