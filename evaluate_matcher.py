"""Evaluate the frozen policy without refitting; includes cold-start ablation."""
import argparse,hashlib,json,platform,time
from dataclasses import replace
from pathlib import Path
from matcher.data import Catalogue,load_labelled
from matcher.identifiers import IdentifierIndex
from matcher.service import Matcher,evidence_bucket
from matcher.core import validate_result
from evaluate import summarise,noise_flags,p95
ROOT=Path(__file__).parent

def report(records,latencies,prep):
 groups={}
 for line,label,r in records:
  key=f'{r.confidence:.6f}'
  b=groups.setdefault(key,{'n':0,'correct':0,'confidence':r.confidence});b['n']+=1
  b['correct']+=int(bool(r.candidates) and r.candidates[0].item_code==label)
 for b in groups.values():b['observed']=b['correct']/b['n']
 return {'overall':summarise(records),
 'per_tenant':{t:summarise([r for r in records if r[0].tenant==t]) for t in sorted({r[0].tenant for r in records})},
 'per_noise_flag':{f:summarise([r for r in records if f in noise_flags(r[0])]) for f in sorted({f for r in records for f in noise_flags(r[0])})},
 'calibration':groups,'ece':sum(b['n']*abs(b['confidence']-b['observed']) for b in groups.values())/len(records),
 'brier':sum((r.confidence-int(bool(r.candidates) and r.candidates[0].item_code==label))**2 for _,label,r in records)/len(records),
 'curve':[{'threshold':v,**summarise([(l,y,replace(r,item_code='',decision='review',reason_code='threshold_review') if r.decision=='auto' and r.confidence<v else r) for l,y,r in records])} for v in [0,.93,.95,.975,.99,1]],
 'timing':{'preparation_ms':prep,'warm_p95_ms':p95(latencies),'samples':len(latencies)},
 'wrong_autos':[{'line_id':l.line_id,'label':y,'item_code':r.item_code,'reason':r.reason_code} for l,y,r in records if r.decision=='auto' and r.item_code!=y]}

def run(repeat):
 split=json.loads((ROOT/'docs/TRAIN_SPLIT.json').read_text());policy=json.loads((ROOT/'matcher/policy.json').read_text())
 train=ROOT/'data/order_lines_train.csv'
 if hashlib.sha256(train.read_bytes()).hexdigest()!=policy['train_sha256']:raise ValueError('Data drift')
 if hashlib.sha256((ROOT/'docs/TRAIN_SPLIT.json').read_bytes()).hexdigest()!=policy['split_sha256']:raise ValueError('Split drift')
 lines,labels=load_labelled(train);out={}
 for cold in [False,True]:
  start=time.perf_counter();cat=Catalogue.load(ROOT/'data')
  matcher=Matcher(cat,IdentifierIndex.load(cat,ROOT/'data',cold_start=cold),policy)
  prep=(time.perf_counter()-start)*1000
  records=[];times={}
  for line in lines:
   r=matcher.match(line);validate_result(line,r,cat);records.append((line,labels[line.line_id],r))
  for _ in range(repeat):
   for line,_,expected in records:
    start=time.perf_counter_ns();actual=matcher.match(line);dt=(time.perf_counter_ns()-start)/1e6
    if actual!=expected:raise ValueError('Nondeterminism')
    times.setdefault(line.line_id,[]).append(dt)
  out['cold' if cold else 'mature']={}
  for partition in ['development','validation','all']:
   selected=[r for r in records if partition=='all' or split['assignments'][r[0].line_id]['partition']==partition]
   out['cold' if cold else 'mature'][partition]=report(selected,[v for r in selected for v in times[r[0].line_id]],prep)
 paths=[ROOT/'matcher/policy.json',ROOT/'docs/TRAIN_SPLIT.json',ROOT/'evaluate_matcher.py',ROOT/'evaluate.py',*sorted((ROOT/'matcher').glob('*.py')),*sorted((ROOT/'data').glob('catalogue_*.csv')),ROOT/'data/customer_sku_map.csv',train]
 out['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 out['environment']={'python':platform.python_version(),'platform':platform.platform()}
 out['scope']='Frozen policy; validation measured after policy commit; all-train includes development and is not an unbiased estimate'
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--repeat',type=int,default=2);ap.add_argument('--output',type=Path,default=ROOT/'reports/final_evaluation.json');a=ap.parse_args()
 if a.repeat<1:ap.error('repeat must be positive')
 r=run(a.repeat);a.output.write_text(json.dumps(r,indent=2)+'\n')
 for mode in ['mature','cold']:
  for partition in ['development','validation','all']:print(mode,partition,r[mode][partition]['overall'],r[mode][partition]['timing'],flush=True)
