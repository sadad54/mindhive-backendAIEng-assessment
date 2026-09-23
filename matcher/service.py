"""Offline deterministic matcher with a frozen empirical confidence table."""
from matcher.core import Candidate,Result,validate_result
from matcher.lexical import LexicalIndex
from matcher.identifiers import IdentifierIndex


def evidence_bucket(retrieval,evidence):
    if not retrieval.candidates:return 'no_candidate'
    if retrieval.issues:return 'blocked'
    if len(evidence.codes)==1 and evidence.codes[0]==retrieval.candidates[0].code:
        return 'identifier'
    if retrieval.exact_unique:return 'lexical_exact'
    return 'lexical_high' if retrieval.candidates[0].score>=.9 else 'lexical_other'


class Matcher:
    def __init__(self,catalogue,identifiers,policy):
        self.catalogue=catalogue
        self.index=LexicalIndex(catalogue,identifiers)
        self.policy=policy

    def match(self,line):
        retrieval=self.index.retrieve(line)
        evidence=self.index.identifiers.retrieve(line)
        bucket=evidence_bucket(retrieval,evidence)
        row=self.policy['buckets'].get(bucket,{})
        confidence=row.get('probability',0.0)
        candidates=tuple(Candidate(r.code,min(1.0,max(0.0,r.score))) for r in retrieval.candidates)
        reason=retrieval.issues[0] if retrieval.issues else bucket
        decision='review';code=''
        if 'not_an_item' in retrieval.issues:
            decision='reject'
        elif not retrieval.issues and bucket in self.policy['enabled_buckets'] and candidates:
            decision='auto';code=candidates[0].item_code
            reason='identifier_verified' if bucket=='identifier' else bucket
        result=Result(code,confidence,decision,reason,candidates)
        validate_result(line,result,self.catalogue)
        return result
