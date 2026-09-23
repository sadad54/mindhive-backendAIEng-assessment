"""Generate holdout outputs with the frozen policy; no fitting or label access."""
import csv,hashlib,json
from collections import Counter
from dataclasses import fields
from pathlib import Path
from matcher.data import Catalogue,OrderLine,read_csv
from matcher.identifiers import IdentifierIndex
from matcher.service import Matcher
ROOT=Path(__file__).parent

def main():
 cat=Catalogue.load(ROOT/'data');policy=json.loads((ROOT/'matcher/policy.json').read_text())
 model=Matcher(cat,IdentifierIndex.load(cat,ROOT/'data'),policy)
 names={f.name for f in fields(OrderLine)}
 inputs=read_csv(ROOT/'data/order_lines_holdout.csv',('line_id','tenant','raw_text','customer_id','order_date'))
 seen=set();counts=Counter();outputs=[]
 for row in inputs:
  if not row['line_id'] or row['line_id'] in seen:raise ValueError('Missing or duplicate holdout line ID')
  seen.add(row['line_id']);line=OrderLine(**{k:v for k,v in row.items() if k in names})
  r=model.match(line)
  if model.match(line)!=r:raise ValueError('Nondeterminism')
  outputs.append(dict(line_id=line.line_id,item_code=r.item_code,confidence=f'{r.confidence:.8f}',decision=r.decision,reason_code=r.reason_code,candidates='|'.join(f'{c.item_code}:{c.score:.8f}' for c in r.candidates)))
  counts[r.decision]+=1
 with (ROOT/'predictions.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['line_id','item_code','confidence','decision','reason_code','candidates'],lineterminator='\n');writer.writeheader();writer.writerows(outputs)
 files=[ROOT/'predictions.csv',ROOT/'data/order_lines_holdout.csv',ROOT/'matcher/policy.json',ROOT/'predict.py',*sorted((ROOT/'matcher').glob('*.py')),*sorted((ROOT/'data').glob('catalogue_*.csv')),ROOT/'data/customer_sku_map.csv']
 manifest={'rows':len(outputs),'decisions':dict(counts),'scope':'Frozen inference only; no holdout accuracy claim or label-based tuning','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 (ROOT/'reports/prediction_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest['rows'],manifest['decisions'])
if __name__=='__main__':main()
