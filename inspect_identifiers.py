"""Measure retrieval on the frozen development set; not an automatic-match policy."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from matcher.data import Catalogue, load_labelled
from matcher.identifiers import IdentifierIndex

if __name__ == '__main__':
    root=Path(__file__).parent
    split=json.loads((root/'docs/TRAIN_SPLIT.json').read_text())
    if hashlib.sha256((root/'data/order_lines_train.csv').read_bytes()).hexdigest()!=split['train_sha256']:
        raise SystemExit('Training data changed; split is stale')
    lines,labels=load_labelled(root/'data/order_lines_train.csv')
    cat=Catalogue.load(root/'data')
    results={}
    for mode in ['mature','cold_start']:
        index=IdentifierIndex.load(cat,root/'data',cold_start=mode=='cold_start')
        counts=Counter()
        for line in lines:
            if split['assignments'][line.line_id]['partition']!='development':
                continue
            counts['lines']+=1
            evidence=index.retrieve(line)
            counts['with_candidates']+=bool(evidence.codes)
            counts['target_retrieved']+=bool(labels[line.line_id] and labels[line.line_id] in evidence.codes)
            counts['unique_without_detected_issue']+=len(evidence.codes)==1 and not evidence.issues
            counts.update(evidence.issues)
        results[mode]=dict(counts)
    print(json.dumps({'scope':'development only; retrieval evidence, no autos or confidence claims','train_sha256':split['train_sha256'],'split_sha256':hashlib.sha256((root/'docs/TRAIN_SPLIT.json').read_bytes()).hexdigest(),'source_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['inspect_identifiers.py','split_data.py','matcher/data.py','matcher/identifiers.py']},'results':results},indent=2))
