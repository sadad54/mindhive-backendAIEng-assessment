"""Strict equality on baseline columns, explicit order, and independent p95 oracle."""
import argparse,gzip,hashlib,json,platform,sqlite3,statistics,time
from pathlib import Path
from perf_report import run
ROOT=Path(__file__).parent

def main(output=None):
 ref=json.load(gzip.open(ROOT/'data/report_reference.json.gz','rt'))
 times=[]
 for _ in range(5):
  con=sqlite3.connect(ROOT/'data/perf.sqlite');start=time.perf_counter();rows=run(con);times.append(time.perf_counter()-start);con.close()
  # Check exact values as well as the supplied rounded comparison.
  assert len(rows)==len(ref['rows'])
  assert [{k:r[k] for k in ref['columns']} for r in rows]==ref['rows'],'Strict reference mismatch'
  from starter.bench_report import normalise
  assert normalise(rows,ref['columns'])==normalise(ref['rows'],ref['columns']),'Reference mismatch'
  assert [(r['tenant_id'],r['channel'],r['day']) for r in rows]==[(r['tenant_id'],r['channel'],r['day']) for r in ref['rows']],'Order mismatch'
 con=sqlite3.connect(ROOT/'data/perf.sqlite')
 oracle={(t,d):p for t,d,p in con.execute('''WITH ranked AS (
 SELECT tenant_id,substr(created_at,1,10) day,latency_ms,
 row_number() OVER (PARTITION BY tenant_id,substr(created_at,1,10) ORDER BY latency_ms) rn,
 count(latency_ms) OVER (PARTITION BY tenant_id,substr(created_at,1,10)) n
 FROM match_event WHERE latency_ms IS NOT NULL)
 SELECT tenant_id,day,latency_ms FROM ranked WHERE rn=(95*n+99)/100''')}
 assert all(r['p95_latency_ms']==oracle.get((r['tenant_id'],r['day'])) for r in rows)
 # Also compare original SQL on a bounded slice; never run the full baseline.
 from perf_diagnose import query
 con.row_factory=sqlite3.Row
 baseline=[dict(r) for r in con.execute(query(['T040'],1))]
 subset=[{k:r[k] for k in ref['columns']} for r in rows if r['tenant_id']=='T040' and r['day']=='2026-05-01']
 exact_original=subset==baseline
 for a,b in zip(subset,baseline):
  for k in ref['columns']:
   if isinstance(a[k],float):assert abs(a[k]-b[k])<1e-12
   else:assert a[k]==b[k]
 max_delta=max(abs(a['avg_accept_score']-b['avg_accept_score']) for a,b in zip(rows,ref['rows']) if a['avg_accept_score'] is not None)
 report={'times_s':times,'median_s':statistics.median(times),'within_budget':statistics.median(times)<=10,
 'rows':len(rows),'strict_reference_equality':True,'max_reference_float_delta':max_delta,'strict_original_slice_equality':exact_original,'original_slice_within_1e_12':True,'reference_rounded_check':True,'p95_oracle_all_rows':True,'sqlite':sqlite3.sqlite_version,
 'python':platform.python_version(),'platform':platform.platform(),
 'source_sha256':hashlib.sha256((ROOT/'perf_report.py').read_bytes()).hexdigest()}
 (output or ROOT/'reports/perf_result.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
 if not report['within_budget']:raise SystemExit('Over budget')
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path)
 main(ap.parse_args().output)
