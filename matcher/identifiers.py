"""Identifier evidence only: retrieval never implies acceptance or calibrated confidence."""
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from matcher.data import read_csv


@dataclass(frozen=True)
class Evidence:
    codes: tuple[str, ...]
    sources: tuple[str, ...]
    issues: tuple[str, ...]


class IdentifierIndex:
    def __init__(self, catalogue, aliases=()):
        self.catalogue = catalogue
        self.identifiers = {}
        for tenant, items in catalogue.by_tenant.items():
            for code, item in items.items():
                for value, source in [(code,'item_code'), (item.get('barcode',''),'barcode')]:
                    if value:
                        self.identifiers.setdefault((tenant,value),set()).add((code,source))
        self.aliases = {}
        for row in aliases:
            self.aliases.setdefault((row['tenant'],row['customer_id'],row['customer_sku']),[]).append(row)

    @classmethod
    def load(cls, catalogue, directory, cold_start=False):
        aliases = [] if cold_start else read_csv(Path(directory)/'customer_sku_map.csv',
                    ('tenant','customer_id','customer_sku','item_code','valid_from','valid_to','source','confidence'))
        return cls(catalogue,aliases)

    def retrieve(self, line):
        if line.tenant not in self.catalogue.by_tenant:
            return Evidence((),(),('unknown_tenant',))
        targets, sources, issues = set(), set(), set()
        # Separate buyer SKU namespace: never interpret it as a global catalogue code.
        tokens = re.findall(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',line.raw_text)
        values = set(tokens)
        if line.raw_barcode:
            values.add(line.raw_barcode)
            if (line.tenant,line.raw_barcode) not in self.identifiers:
                issues.add('unresolved_explicit_barcode')
        for value in values:
            for code, source in self.identifiers.get((line.tenant,value),()):
                targets.add(code); sources.add(source)
        if line.buyer_sku:
            rows = self.aliases.get((line.tenant,line.customer_id,line.buyer_sku),())
            if not rows:
                issues.add('unresolved_buyer_sku')
            try:
                when = date.fromisoformat(line.order_date)
            except ValueError:
                issues.add('invalid_order_date'); rows=()
            active = 0
            for row in rows:
                try:
                    start = date.fromisoformat(row['valid_from']) if row['valid_from'] else date.min
                    end = date.fromisoformat(row['valid_to']) if row['valid_to'] else date.max
                    if start > end:
                        raise ValueError('reversed validity')
                except ValueError:
                    issues.add('invalid_alias_dates'); continue
                if not start <= when <= end:
                    continue
                active += 1; targets.add(row['item_code']); sources.add('buyer_alias')
                try:
                    confidence = float(row['confidence'])
                except ValueError:
                    confidence = -1
                if row['source'] != 'confirmed_order' or confidence != 1:
                    issues.add('untrusted_alias_metadata')
            if rows and not active:
                issues.add('no_date_valid_alias')
        if len(targets)>1:
            issues.add('identifier_conflict')
        eligible = []
        for code in sorted(targets):
            if not self.catalogue.eligible(line.tenant,code):
                issues.add('ineligible_identifier_target'); continue
            eligible.append(code)
            # Conservative initial numeric check. Dimensions/quantities are not yet fully parsed.
            item = self.catalogue.get(line.tenant,code)
            text = line.raw_text
            for value in sorted(values,key=len,reverse=True):
                if (line.tenant,value) in self.identifiers:
                    text = re.sub(r'(?<!\w)'+re.escape(value)+r'(?!\w)',' ',text)
            number = r'\d+(?:[./]\d+)?'
            requested = set(re.findall(number,text))
            described = set(re.findall(number,item['item_name']+' '+item.get('description','')))
            if requested - described:
                issues.add('numeric_text_conflict_or_unparsed_quantity')
        return Evidence(tuple(eligible),tuple(sorted(sources)),tuple(sorted(issues)))
