"""Fit only frozen development partition; never reads holdout or validation outcomes."""
import hashlib,json,math
from pathlib import Path
from matcher.data import Catalogue,load_labelled
from matcher.identifiers import IdentifierIndex
from matcher.lexical import LexicalIndex
from matcher.service import evidence_bucket
ROOT=Path(__file__).parent

def main():
 split=json.loads((ROOT/'docs/TRAIN_SPLIT.json').read_text())
 train=ROOT/'data/order_lines_train.csv'
 if hashlib.sha256(train.read_bytes()).hexdigest()!=split['train_sha256']:raise ValueError('Split drift')
 lines,labels=load_labelled(train);cat=Catalogue.load(ROOT/'data')
 ix=LexicalIndex(cat,IdentifierIndex.load(cat,ROOT/'data'))
 buckets={}
 for line in lines:
  if split['assignments'][line.line_id]['partition']!='development':continue
  r=ix.retrieve(line);e=ix.identifiers.retrieve(line);key=evidence_bucket(r,e)
  b=buckets.setdefault(key,{'n':0,'correct':0});b['n']+=1
  b['correct']+=int(bool(r.candidates) and r.candidates[0].code==labels[line.line_id])
 for key,b in buckets.items():
  b['probability']=(b['correct']+1)/(b['n']+2) if key!='no_candidate' else 0.0
  b['observed_precision']=b['correct']/b['n']
  # Wilson 95% interval conveys uncertainty; not used as a retrofitted policy gate.
  n=b['n'];p=b['observed_precision'];z=1.96
  centre=(p+z*z/(2*n))/(1+z*z/n);half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
  b['wilson95']=[max(0,centre-half),min(1,centre+half)]
 enabled=[k for k,b in buckets.items() if k not in {'blocked','no_candidate'} and b['n']>=10 and b['observed_precision']>=.98 and b['probability']>760/820]
 policy={'version':1,'scope':'fit on frozen development only','method':'Beta(1,1) posterior mean by evidence bucket; no-candidate confidence zero',
         'minimum_bucket_n':10,'observed_precision_target':.98,'utility_probability_floor':760/820,
         'enabled_buckets':sorted(enabled),'buckets':buckets,'train_sha256':split['train_sha256'],
         'split_sha256':hashlib.sha256((ROOT/'docs/TRAIN_SPLIT.json').read_bytes()).hexdigest()}
 (ROOT/'matcher/policy.json').write_text(json.dumps(policy,indent=2)+'\n');print(json.dumps(policy,indent=2))
if __name__=='__main__':main()
