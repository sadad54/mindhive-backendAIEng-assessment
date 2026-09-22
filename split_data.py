"""Freeze a deterministic grouped 75/25 development/validation allocation."""
import hashlib
import json
import re
from pathlib import Path
from matcher.data import load_labelled


def normalise(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def build_split(lines, labels):
    parent = {line.line_id: line.line_id for line in lines}
    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    seen = {}
    for line in sorted(lines, key=lambda x: x.line_id):
        keys = [('text', line.tenant, normalise(line.raw_text))]
        if labels[line.line_id]:
            keys.append(('target', line.tenant, labels[line.line_id]))
        if line.buyer_sku:
            keys.append(('alias', line.tenant, line.customer_id, line.buyer_sku))
        if line.raw_barcode:
            keys.append(('barcode', line.tenant, line.raw_barcode))
        for key in keys:
            if key in seen:
                a, b = find(line.line_id), find(seen[key])
                parent[max(a,b)] = min(a,b)
            seen[key] = line.line_id
    groups = {}
    for line in lines:
        groups.setdefault(find(line.line_id), []).append(line.line_id)
    assignments = {}
    for members in groups.values():
        identity = '|'.join(sorted(members))
        digest = hashlib.sha256(('mindhive-split-v1|' + identity).encode()).hexdigest()
        partition = 'validation' if int(digest[:8],16) % 4 == 0 else 'development'
        for lid in members:
            assignments[lid] = {'partition': partition, 'group': digest}
    return dict(sorted(assignments.items()))


if __name__ == '__main__':
    root = Path(__file__).parent
    lines, labels = load_labelled(root/'data/order_lines_train.csv')
    output = root/'docs/TRAIN_SPLIT.json'
    record = {'version': 'grouped-v1', 'train_sha256': hashlib.sha256((root/'data/order_lines_train.csv').read_bytes()).hexdigest(), 'assignments': build_split(lines, labels)}
    if output.exists() and json.loads(output.read_text()) != record:
        raise SystemExit('Existing split differs: refusing to overwrite a frozen allocation')
    output.write_text(json.dumps(record,indent=2)+'\n')
    print({p: sum(v['partition']==p for v in record['assignments'].values()) for p in ['development','validation']})
