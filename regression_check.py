"""Fail closed on stale evaluation, policy/data drift, or measured regression gates."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).parent

def main(report_path=None):
 r=json.loads((report_path or ROOT/'reports/final_evaluation.json').read_text())
 for name,digest in r['sha256'].items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,f'Stale report: {name}; rerun evaluation and review changes'
 v=r['mature']['validation'];m=v['overall']
 assert m['lines']==114 and m['wrong_auto']==0,'Validation error/count regression'
 assert m['precision'] is not None and m['precision']>=.98,'Precision below gate'
 assert m['coverage']>=.20 and m['improvement_over_all_review']>=1200,'Coverage/value regression'
 assert m['recall_at_3']>=.80,'Retrieval regression'
 assert v['ece']<=.10 and v['brier']<=.16,'Calibration regression'
 for mode in ['mature','cold']:
  assert r[mode]['all']['timing']['warm_p95_ms']<=250,'Latency budget exceeded'
 manifest=json.loads((ROOT/'reports/prediction_manifest.json').read_text())
 for name,digest in manifest['sha256'].items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,f'Stale prediction: {name}'
 assert manifest['rows']==300
 print('PASS: report/source hashes, validation precision/coverage/value/recall/calibration, latency and prediction provenance')
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',type=Path)
 main(ap.parse_args().report)
