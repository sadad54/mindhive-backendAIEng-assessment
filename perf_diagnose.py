"""Bounded baseline slices and one-metric-at-a-time ablation, never full baseline."""
import json,sqlite3,time
from pathlib import Path
ROOT=Path(__file__).parent
sql=(ROOT/'starter/report_query.sql').read_text()
# Split SELECT expressions at top-level commas; comments contain commas too.
import re
clean=re.sub(r'--[^\n]*','',sql)
start=clean.index('SELECT')+6
end=clean.index('\nFROM order_line ol')
parts=[];depth=0;last=start
for i in range(start,end):
 c=clean[i]
 if c=='(':depth+=1
 elif c==')':depth-=1
 elif c==',' and depth==0:parts.append(clean[last:i]);last=i+1
parts.append(clean[last:end])

def query(tenant,days,remove=None):
 selected=[p for i,p in enumerate(parts) if i!=remove]
 q='SELECT'+','.join(selected)+clean[end:]
 q=q.replace("'2026-06-30'",f"'2026-05-{days:02d}'")
 return q.replace('GROUP BY t.tenant_id',f"AND t.tenant_id IN ({','.join(repr(t) for t in tenant)})\nGROUP BY t.tenant_id")

def timed(con,q):
 start=time.perf_counter()
 con.set_progress_handler(lambda: int(time.perf_counter()-start>30),10000)
 try:
  rows=con.execute(q).fetchall(); return {'seconds':time.perf_counter()-start,'groups':len(rows),'complete':True}
 except sqlite3.OperationalError as e:
  if 'interrupted' not in str(e):raise
  return {'seconds':time.perf_counter()-start,'complete':False}
 finally:con.set_progress_handler(None,0)

def main():
 con=sqlite3.connect(ROOT/'data/perf.sqlite')
 out={'target_seconds':10,'timeout_per_slice':30,'slices':[],'ablations':[]}
 for tenants,days in [(['T040'],1),(['T040'],2),(['T001'],1),(['T001','T040'],1)]:
  r=timed(con,query(tenants,days));r.update(tenants=tenants,days=days)
  r['window_lines']=con.execute("SELECT COUNT(*) FROM order_line WHERE tenant_id IN ("+','.join('?' for t in tenants)+") AND substr(created_at,1,10) BETWEEN '2026-05-01' AND ?",[*tenants,f'2026-05-{days:02d}']).fetchone()[0]
  out['slices'].append(r); print(r,flush=True)
 for i in range(5,len(parts)):
  name=parts[i].split('AS')[-1].strip()
  r=timed(con,query(['T040'],1,i));r['removed']=name
  out['ablations'].append(r);print(r,flush=True)
 out['full_groups']=con.execute("SELECT COUNT(*) FROM (SELECT tenant_id,channel,substr(created_at,1,10) FROM order_line WHERE substr(created_at,1,10) BETWEEN '2026-05-01' AND '2026-06-30' GROUP BY 1,2,3)").fetchone()[0]
 out['events']=con.execute('SELECT COUNT(*) FROM match_event').fetchone()[0]
 out['query_plan']=[list(r) for r in con.execute('EXPLAIN QUERY PLAN '+query(['T040'],1))]
 (ROOT/'reports/perf_diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
