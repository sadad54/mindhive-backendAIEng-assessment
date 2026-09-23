"""Repeated one-metric removal on a 12-group slice; raw timings retained."""
import json,sqlite3,statistics
from pathlib import Path
from perf_diagnose import query,timed,parts
ROOT=Path(__file__).parent

def main():
 c=sqlite3.connect(ROOT/'data/perf.sqlite');out=[]
 for i in [None,*range(5,len(parts))]:
  runs=[timed(c,query(['T040'],4,i)) for _ in range(2)]
  r={'removed':parts[i].split('AS')[-1].strip() if i is not None else 'none','runs':runs,'median_s':statistics.median(x['seconds'] for x in runs)}
  out.append(r);print(r,flush=True)
  (ROOT/'reports/perf_ablation.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
