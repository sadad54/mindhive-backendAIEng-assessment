"""Repeat bounded baseline slices in isolation; compare scaling predictors."""
import json,sqlite3,statistics
from pathlib import Path
from perf_diagnose import query,timed
ROOT=Path(__file__).parent

def main():
 c=sqlite3.connect(ROOT/'data/perf.sqlite');out=[]
 for tenants,days in [(['T040'],1),(['T040'],2),(['T040'],4),(['T001'],1),(['T001'],2),(['T001','T040'],1)]:
  runs=[timed(c,query(tenants,days)) for _ in range(2)]
  row={'tenants':tenants,'days':days,'runs':runs,'median_s':statistics.median(r['seconds'] for r in runs)}
  row['window_lines']=c.execute("SELECT count(*) FROM order_line WHERE tenant_id IN ("+','.join('?' for _ in tenants)+") AND substr(created_at,1,10) BETWEEN '2026-05-01' AND ?",[*tenants,f'2026-05-{days:02d}']).fetchone()[0]
  out.append(row);print(row,flush=True)
  (ROOT/'reports/perf_scaling.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
