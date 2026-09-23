"""Verify imported bytes and audit training/catalogue structure; never inspect holdout rows."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from matcher.data import Catalogue, load_labelled, read_csv


def audit(root):
    manifest = json.loads((root / "docs/INPUT_MANIFEST.json").read_text())
    for name, hashes in manifest["files"].items():
        raw = (root / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != hashes["sha256"]:
            raise ValueError(f"Imported file changed: {name}")
    cat = Catalogue.load(root / "data")
    lines, labels = load_labelled(root / "data/order_lines_train.csv")
    aliases = read_csv(root / "data/customer_sku_map.csv", ("tenant", "customer_id", "customer_sku", "item_code", "source", "confidence", "valid_to"))
    groups = {}
    for row in aliases:
        key = (row["tenant"], row["customer_id"], row["customer_sku"])
        groups.setdefault(key, set()).add(row["item_code"])
    return {
        "source_revision": manifest["source_revision"], "verified_imported_files": len(manifest["files"]),
        "catalogues": {tenant: {"rows": len(items),
                      "disabled": sum(r["disabled"] == "1" for r in items.values()),
                      "duplicate_visible_name_groups": sum(n > 1 for n in Counter(r["item_name"] for r in items.values()).values())}
                       for tenant, items in cat.by_tenant.items()},
        "train": {"rows": len(lines), "blank_labels": sum(not label for label in labels.values()),
                  "per_tenant": dict(Counter(line.tenant for line in lines))},
        "aliases": {"rows": len(aliases), "multiple_target_keys_without_date_filter": sum(len(v)>1 for v in groups.values()),
                    "with_end_date_not_necessarily_expired": sum(bool(r["valid_to"]) for r in aliases),
                    "inferred_source": sum(r["source"] == "inferred_match" for r in aliases),
                    "confidence_below_one": sum(float(r["confidence"]) < 1 for r in aliases)},
        "holdout": "this audit verifies bytes only; holdout inference is performed separately by predict.py",
    }


if __name__ == "__main__":
    print(json.dumps(audit(Path(__file__).parent), indent=2))
