"""Development-only retrieval and provisional policy experiment; no calibration claims."""
import hashlib
import json
import platform
import time
from pathlib import Path
from matcher.data import Catalogue,load_labelled
from matcher.identifiers import IdentifierIndex
from matcher.lexical import LexicalIndex
from evaluate import p95


def inspect(root):
    train=root/'data/order_lines_train.csv'
    split=json.loads((root/'docs/TRAIN_SPLIT.json').read_text())
    if hashlib.sha256(train.read_bytes()).hexdigest()!=split['train_sha256']:
        raise ValueError('Frozen split data changed')
    lines,labels=load_labelled(train)
    lines=[line for line in lines if split['assignments'][line.line_id]['partition']=='development']
    start=time.perf_counter()
    cat=Catalogue.load(root/'data')
    index=LexicalIndex(cat,IdentifierIndex.load(cat,root/'data'))
    preparation_ms=(time.perf_counter()-start)*1000
    predictions=[index.retrieve(line) for line in lines]
    durations=[]
    for line,expected in zip(lines,predictions):
        start=time.perf_counter_ns();actual=index.retrieve(line)
        durations.append((time.perf_counter_ns()-start)/1e6)
        if actual!=expected:raise ValueError('Non-deterministic retrieval')
    answerable=sum(bool(labels[line.line_id]) for line in lines)
    hits=sum(bool(labels[line.line_id]) and labels[line.line_id] in [c.code for c in result.candidates] for line,result in zip(lines,predictions))
    curve=[]
    for threshold in [.6,.7,.8,.85,.9,.95,1.0]:
        chosen=[(line,result) for line,result in zip(lines,predictions) if result.candidates and not result.issues and result.candidates[0].score>=threshold and result.margin>=.05]
        correct=sum(labels[line.line_id]==result.candidates[0].code for line,result in chosen)
        wrong=len(chosen)-correct
        curve.append({'similarity_threshold':threshold,'auto_proposals':len(chosen),'correct':correct,'wrong':wrong,'precision':correct/len(chosen) if chosen else None,'coverage':len(chosen)/len(lines),'improvement_over_review':60*correct-760*wrong})
    return {'scope':'development only; provisional rule proposals, not calibrated final predictions',
            'data_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [train,*sorted((root/'data').glob('catalogue_*.csv')),root/'data/customer_sku_map.csv']},
            'split_sha256':hashlib.sha256((root/'docs/TRAIN_SPLIT.json').read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'inspect_lexical.py',root/'evaluate.py',*sorted((root/'matcher').glob('*.py'))]},
            'lines':len(lines),'answerable':answerable,'target_in_top3':hits,'recall_at_3':hits/answerable,
            'failure_review_queue': [
                {'line_id':line.line_id,'tenant':line.tenant,'raw_text':line.raw_text,
                 'qty':line.qty,'uom_text':line.uom_text,'buyer_sku':line.buyer_sku,'raw_barcode':line.raw_barcode,
                 'supplied_label':labels[line.line_id],'proposed_item':result.candidates[0].code,
                 'candidates':[{'code':c.code,'score':c.score,'name':cat.get(line.tenant,c.code)['item_name']} for c in result.candidates],
                 'root_cause_by_sadad':None,'cost_class_by_sadad':None,'proposed_fix_by_sadad':None}
                for line,result in zip(lines,predictions)
                if result.candidates and not result.issues and result.candidates[0].score>=.9
                and result.margin>=.05 and result.candidates[0].code!=labels[line.line_id]][:20],
            'curve':curve,'timing':{'preparation_ms':preparation_ms,'warm_p95_ms':p95(durations),'samples':len(durations)},
            'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'limitations':['Development selection is optimistic; validation untouched','Numeric quantity and pack parsing incomplete','No confidence calibration or final auto policy','One timed warm pass on execution host, not laptop benchmark']}

if __name__=='__main__':
    print(json.dumps(inspect(Path(__file__).parent),indent=2))
