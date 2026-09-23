"""Hold tenant/day fixed while changing channel output-group count."""
import json,sqlite3,statistics
from pathlib import Path
from perf_diagnose import query,timed
ROOT=Path(__file__).parent

def main():
 c=sqlite3.connect(ROOT/'data/perf.sqlite');out=[]
 for channels in [['email_pdf'],['email_pdf','voice_note']]:
  q=query(['T001'],1).replace('GROUP BY t.tenant_id',"AND ol.channel IN ("+','.join(repr(x) for x in channels)+")\nGROUP BY t.tenant_id")
  runs=[timed(c,q) for _ in range(2)]
  r={'tenant':'T001','day':'2026-05-01','channels':channels,'runs':runs,'median_s':statistics.median(x['seconds'] for x in runs)}
  out.append(r);print(r,flush=True)
 (ROOT/'reports/perf_channels.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
