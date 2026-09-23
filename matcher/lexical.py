"""Deterministic lexical evidence. Scores are similarity, never probabilities."""
import math
import json
import re
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from matcher.identifiers import IdentifierIndex


def normalise(text):
    text = text.casefold().replace('″', ' inch ').replace('"', ' inch ').replace("''", ' inch ')
    text = re.sub(r'\bss(?=\s*\d)', 'stainless ', text)
    text = re.sub(r'\bsds\b', 'self drilling screw', text)
    # Preserve numerical fractions while making slash-separated words searchable.
    text = re.sub(r'(?<!\d)/|/(?!\d)', ' ', text)
    text = re.sub(r'\bz\s*\.\s*p\.?\b', 'zinc plated', text)
    for pattern, replacement in [(r'\bzp\b','zinc plated'),(r'\bs\s*/?\s*s\b','stainless'),
                                 (r'\bskru\b','screw'),(r'\bayam\b','chicken'),(r'\bsusu\b','milk')]:
        text = re.sub(pattern,replacement,text)
    return ' '.join(re.findall(r'\d+/\d+|\d+(?:\.\d+)?|[a-z]+',text))


def grams(text):
    text=' '+text+' '
    return Counter(text[i:i+3] for i in range(len(text)-2))


def cosine(a,b):
    denominator=math.sqrt(sum(v*v for v in a.values())*sum(v*v for v in b.values()))
    return sum(v*b.get(k,0) for k,v in a.items())/denominator if denominator else 0.0


def attributes(text):
    text=normalise(text)
    out={}
    for value,unit in re.findall(r'(\d+/\d+|\d+(?:\.\d+)?)\s*(mm|cm|inch|kg|g|ml|l)\b',text):
        number=float(Fraction(value))
        dimension='length' if unit in {'mm','cm','inch'} else 'weight' if unit in {'kg','g'} else 'volume'
        factor={'mm':1,'cm':10,'inch':25.4,'kg':1000,'g':1,'ml':1,'l':1000}[unit]
        out.setdefault(dimension,set()).add(round(number*factor,6))
    for key,pattern in [('colour',r'\b(red|blue|brown|white|black|yellow|green)\b'),
                        ('grade',r'\bclass ([a-z])\b'),
                        ('disc_kind',r'\b(grinding|cutting|flap)\b'),
                        ('material',r'\b(stainless|zinc plated|brass|pvc|hdg)\b'),
                        ('steel_grade',r'\bstainless (304|316|410)\b')]:
        values=set(re.findall(pattern,text))
        if values:out[key]=values
    return out


def conflicts(requested,offered):
    return tuple(sorted(key for key,values in requested.items() if key in offered and values != offered[key]))


@dataclass(frozen=True)
class Ranked:
    code: str
    score: float
    conflicts: tuple[str,...]


@dataclass(frozen=True)
class Retrieval:
    candidates: tuple[Ranked,...]
    issues: tuple[str,...]
    exact_unique: bool
    margin: float


class LexicalIndex:
    def __init__(self,catalogue,identifiers=None):
        self.catalogue=catalogue
        self.identifiers=identifiers or IdentifierIndex(catalogue)
        self.prepared={}
        self.brands={}
        self.pack_families={}
        self.family_for={}
        for tenant,items in catalogue.by_tenant.items():
            self.brands[tenant]={normalise(i.get('brand','')) for i in items.values() if i.get('brand')}
            self.prepared[tenant]={}
            for code,item in items.items():
                if catalogue.eligible(tenant,code):
                    name=normalise(item['item_name'])
                    self.prepared[tenant][code]=(name,Counter(name.split()),grams(name),attributes(item['item_name']))
                    # Only explicit Bulk siblings with identical remaining names are grouped.
                    # Stock and prices never participate in family identity.
                    family=(tenant,normalise(item.get('brand','')),
                            re.sub(r'\bbulk\b','',name).strip(),
                            item.get('stock_uom','').casefold())
                    self.pack_families.setdefault(family,[]).append(code)
                    self.family_for[(tenant,code)]=family
        self.pack_families={key:tuple(sorted(codes)) for key,codes in self.pack_families.items()
                            if len(codes)>1 and any('bulk' in self.prepared[key[0]][c][0].split() for c in codes)
                            and len({self.pack_signature(catalogue.get(key[0],c)) for c in codes})>1}

    @staticmethod
    def pack_signature(item):
        conversions=json.loads(item.get('uom_conversions') or '[]')
        return tuple(sorted((entry['uom'].casefold(),float(entry['conversion_factor']))
                            for entry in conversions))

    def pack_choices(self,line,evidence,compatible):
        """Restrict only known pack families; unresolved families remain review evidence."""
        words=set(normalise(line.raw_text).split())
        requested=words & {'bulk','standard'}
        issues=set()
        allowed={r.code for r in compatible}
        families={self.family_for[(line.tenant,r.code)] for r in compatible}
        for family in families:
            siblings=self.pack_families.get(family)
            if not siblings:
                continue
            choices=set(siblings)
            if len(requested)==1:
                bulk='bulk' in requested
                choices={c for c in choices if ('bulk' in self.prepared[line.tenant][c][0].split())==bulk}
            if len(evidence.codes)==1 and not evidence.issues and evidence.codes[0] in siblings:
                choices &= set(evidence.codes)
            # Do not let conflicting evidence silently empty a family and promote another item.
            if not choices or len(requested)>1:
                if any(r.code in siblings and r.score>=.25 for r in compatible):
                    issues.add('pack_evidence_conflict')
            else:
                allowed -= set(siblings)-choices
        return [r for r in compatible if r.code in allowed],issues


    def retrieve(self,line):
        if line.tenant not in self.prepared:
            return Retrieval((),('unknown_tenant',),False,0)
        query=normalise(line.raw_text)
        if not query:
            return Retrieval((),('empty_text',),False,0)
        if query in {'delivery charge','delivery fee','opening balance'}:
            return Retrieval((),('not_an_item',),False,0)
        evidence=self.identifiers.retrieve(line)
        issues=set(evidence.issues)
        # Remove known identifiers before inspecting explicit numeric attributes.
        raw=line.raw_text
        for (tenant,value) in self.identifiers.identifiers:
            if tenant==line.tenant and value in raw:
                raw=re.sub(r'(?<!\w)'+re.escape(value)+r'(?!\w)',' ',raw)
        attrs=attributes(raw)
        mentioned={b for b in self.brands[line.tenant] if ' '+b+' ' in ' '+query+' '}
        qwords=Counter(query.split());qgrams=grams(query)
        ranked=[]
        for code,(name,words,chargrams,offered) in self.prepared[line.tenant].items():
            bad=set(conflicts(attrs,offered))
            item=self.catalogue.get(line.tenant,code)
            if mentioned and normalise(item.get('brand','')) not in mentioned:bad.add('brand')
            score=.55*cosine(qwords,words)+.45*cosine(qgrams,chargrams)
            if code in evidence.codes:
                score=max(score,.99)
                if bad:issues.add('identifier_text_conflict')
            # Keep conflicts visible for debugging but do not promote them over compatible candidates.
            ranked.append(Ranked(code,round(score,8),tuple(sorted(bad))))
        compatible=sorted((r for r in ranked if not r.conflicts),key=lambda r:(-r.score,r.code))
        compatible,pack_issues=self.pack_choices(line,evidence,compatible)
        issues.update(pack_issues)
        top=tuple(r for r in compatible[:3] if r.score>=.25)
        if top:
            siblings=self.pack_families.get(self.family_for[(line.tenant,top[0].code)],())
            remaining={r.code for r in compatible}
            if len(remaining.intersection(siblings))>1:
                issues.add('ambiguous_pack')
        exact=[r for r in compatible if self.prepared[line.tenant][r.code][0]==query]
        if len(exact)>1:issues.add('ambiguous_exact_names')
        if not top:issues.add('no_candidate_above_floor')
        margin=top[0].score-top[1].score if len(top)>1 else top[0].score if top else 0
        if top and margin<.05:issues.add('small_candidate_margin')
        if top:
            offered=self.prepared[line.tenant][top[0].code][3]
            # A missing critical specification is not proof of a mismatch, but requires review.
            # A unique conflict-free identifier may supply omitted information.
            supported=(len(evidence.codes)==1 and not evidence.issues
                       and evidence.codes[0]==top[0].code
                       and 'identifier_text_conflict' not in issues)
            if not supported:
                for key in ('material','steel_grade','grade','colour','disc_kind','length','weight','volume'):
                    if key in offered and key not in attrs:
                        issues.add('missing_'+key)
            if re.search(r'\b(not|except|instead|or)\b',query):
                issues.add('complex_request')
        return Retrieval(top,tuple(sorted(issues)),len(exact)==1,margin)
