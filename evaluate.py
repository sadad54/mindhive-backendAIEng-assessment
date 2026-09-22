"""Reproducible counts plus separately measured warm baseline latency."""
import argparse
import hashlib
import json
import math
import platform
import re
import time
from pathlib import Path

from matcher.core import ReviewMatcher, validate_result
from matcher.data import Catalogue, load_labelled


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def summarise(records):
    counts = dict(lines=len(records), auto=0, correct_auto=0, wrong_auto=0,
                  review=0, reject=0, answerable=0, unanswerable=0,
                  correct_abstentions=0, answerable_abstentions=0,
                  top3_hits=0, abstained_top3_hits=0)
    for line, label, result in records:
        counts[result.decision] += 1
        counts["answerable" if label else "unanswerable"] += 1
        hit = bool(label and label in [c.item_code for c in result.candidates])
        counts["top3_hits"] += hit
        if result.decision == "auto":
            counts["correct_auto" if label and result.item_code == label else "wrong_auto"] += 1
        else:
            counts["answerable_abstentions" if label else "correct_abstentions"] += 1
            counts["abstained_top3_hits"] += hit
    c, w = counts["correct_auto"], counts["wrong_auto"]
    a = counts["review"] + counts["reject"]
    counts.update(
        precision=ratio(c, counts["auto"]), coverage=ratio(counts["auto"], counts["lines"]),
        accuracy_including_correct_abstention=ratio(c + counts["correct_abstentions"], counts["lines"]),
        blank_label_abstention_rate=ratio(counts["correct_abstentions"], counts["unanswerable"]),
        recall_at_3=ratio(counts["top3_hits"], counts["answerable"]),
        recall_at_3_on_answerable_abstentions=ratio(counts["abstained_top3_hits"], counts["answerable_abstentions"]),
        utility_seconds_equivalent=20*c - 800*w - 40*a,
        improvement_over_all_review=60*c - 760*w,
    )
    return counts


def noise_flags(line):
    """Input-only observable flags, not claims about the true cause of noise."""
    flags = []
    if line.buyer_sku or line.raw_barcode:
        flags.append("structured_identifier")
    if re.search(r"\b(?:ctn|carton|box|case|pack|packet)\b", line.raw_text + " " + line.uom_text, re.I):
        flags.append("pack_word")
    if re.search(r'\d\s*(?:mm|cm|kg|inch|"|\u2033)', line.raw_text, re.I):
        flags.append("dimension_or_weight_token")
    if re.search(r"\b(?:skru|ayam|susu)\b", line.raw_text, re.I):
        flags.append("selected_malay_word")
    if "/" in line.raw_text or "  " in line.raw_text:
        flags.append("separator_or_spacing")
    return flags or ["other"]


def p95(values):
    return sorted(values)[math.ceil(.95 * len(values)) - 1] if values else None


def run(data, repeat=5):
    if repeat < 1:
        raise ValueError("repeat must be positive")
    start = time.perf_counter()
    catalogue = Catalogue.load(data)
    lines, labels = load_labelled(Path(data) / "order_lines_train.csv")
    matcher = ReviewMatcher(catalogue)
    preparation_ms = (time.perf_counter() - start) * 1000
    records = []
    for line in lines:
        result = matcher.match(line)
        validate_result(line, result, catalogue)
        records.append((line, labels[line.line_id], result))
    # Above pass warms the matcher; timing excludes evaluator validation and file I/O.
    latencies = []
    for _ in range(repeat):
        for line, _, expected in records:
            start = time.perf_counter_ns()
            actual = matcher.match(line)
            latencies.append((time.perf_counter_ns() - start) / 1e6)
            if actual != expected:
                raise ValueError("Non-deterministic output")
    tenants = sorted({line.tenant for line in lines})
    flags = sorted({flag for line in lines for flag in noise_flags(line)})
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(Path(data).glob("catalogue_*.csv"))}
    train = Path(data) / "order_lines_train.csv"
    hashes[train.name] = hashlib.sha256(train.read_bytes()).hexdigest()
    return {
        "matcher": "review_only_v1", "evaluation_scope": "full_train_baseline_no_tuning",
        "data_sha256": hashes,
        "source_sha256": {p.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), *sorted((Path(__file__).parent / "matcher").glob("*.py"))]},
        "overall": summarise(records),
        "per_tenant": {tenant: summarise([r for r in records if r[0].tenant == tenant]) for tenant in tenants},
        "per_noise_flag": {flag: summarise([r for r in records if flag in noise_flags(r[0])]) for flag in flags},
        "timing": {"preparation_ms": preparation_ms, "warm_p95_ms": p95(latencies),
                   "samples": len(latencies), "repetitions": repeat,
                   "within_250ms": p95(latencies) <= 250 if latencies else None},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "limitations": ["No matching/retrieval/calibration implemented", "No validation split or tuning yet",
                         "Timing measures review-only overhead on this execution host, not a laptop matcher benchmark",
                         "Noise flags overlap and are observable proxies, not manually labelled noise classes"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    report = run(args.data, args.repeat)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
