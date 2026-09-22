"""CSV boundaries keep labels outside matcher inputs and identifiers as strings."""
import csv
from dataclasses import dataclass, fields
from pathlib import Path


def read_csv(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        names = reader.fieldnames or []
        if len(set(names)) != len(names) or not set(required) <= set(names):
            raise ValueError(f"Invalid or missing columns in {path}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed CSV row in {path}")
    return rows


@dataclass(frozen=True)
class OrderLine:
    line_id: str
    tenant: str
    customer_id: str
    order_date: str
    raw_text: str
    channel: str = ""
    qty: str = ""
    uom_text: str = ""
    unit_price: str = ""
    buyer_sku: str = ""
    raw_barcode: str = ""
    notes: str = ""


def load_labelled(path):
    rows = read_csv(path, ("line_id", "tenant", "customer_id", "order_date", "raw_text", "gt_item_code"))
    names = {field.name for field in fields(OrderLine)}
    lines, labels = [], {}
    for row in rows:
        if not row["line_id"] or row["line_id"] in labels:
            raise ValueError("Missing or duplicate line_id")
        lines.append(OrderLine(**{key: value for key, value in row.items() if key in names}))
        labels[row["line_id"]] = row["gt_item_code"]
    return lines, labels


class Catalogue:
    """Tenant boundary is enforced by lookup, not inferred from code prefixes."""

    def __init__(self, by_tenant):
        self.by_tenant = by_tenant

    @classmethod
    def load(cls, directory):
        by_tenant = {}
        paths = sorted(Path(directory).glob("catalogue_*.csv"))
        if not paths:
            raise ValueError("No catalogue files found")
        for path in paths:
            tenant = path.stem.removeprefix("catalogue_")
            items = {}
            for row in read_csv(path, ("item_code", "item_name", "disabled")):
                code = row["item_code"]
                if not code or code in items or row["disabled"] not in {"0", "1"}:
                    raise ValueError(f"Invalid/duplicate catalogue item in {tenant}: {code}")
                items[code] = row
            by_tenant[tenant] = items
        return cls(by_tenant)

    def get(self, tenant, code):
        return self.by_tenant.get(tenant, {}).get(code)

    def eligible(self, tenant, code):
        item = self.get(tenant, code)
        return bool(item and item["disabled"] == "0"
                    and not code.endswith("-OLD")
                    and item["item_name"].strip().upper() not in {"DELIVERY FEE", "OPENING BALANCE"})
