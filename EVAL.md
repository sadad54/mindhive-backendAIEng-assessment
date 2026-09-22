# Task 3 — Evaluation
Status: measured review-only baseline. Retrieval, confidence calibration, validation selection, operating-point curve and personal analysis are not complete.

## Reproduction and provenance
```bash
python3 audit_data.py
python3 -m unittest discover -s tests -v
python3 evaluate.py --repeat 5 --output reports/baseline_review.json
```
The saved JSON records SHA-256 hashes for consumed data and evaluator/matcher source, plus Python/platform. Supplied inputs are pinned by docs/INPUT_MANIFEST.json. Python 3.12.14 on Linux x86_64 was used for this run. Nine tests passed. Code is standard-library Python 3.10+.

## Baseline results
All 420 labelled lines were evaluated without tuning. This is full-train baseline reporting, not held-out validation. Labels are loaded separately and never appear in OrderLine, the matcher input.

| Metric | All | Acme | Nordic |
|---|---:|---:|---:|
| Lines | 420 | 260 | 160 |
| Answerable labels | 295 | 174 | 121 |
| Blank labels | 125 | 86 | 39 |
| Auto answers / wrong autos | 0 / 0 | 0 / 0 | 0 / 0 |
| Reviews | 420 | 260 | 160 |
| Coverage | 0% | 0% | 0% |
| Auto precision | Undefined | Undefined | Undefined |
| Accuracy including correct abstentions | 29.76% | 33.08% | 24.38% |
| Blank-label abstention rate | 100% | 100% | 100% |
| Recall@3 on answerable lines | 0% | 0% | 0% |

Cost convention U=20C-800W-40A yields -16,800 seconds-equivalent, exactly the all-review reference; improvement is zero. Correct blank-label abstentions count as correct for the displayed accuracy, showing why neither accuracy nor zero wrong autos alone establishes business value.

Precision denominator is auto answers; coverage denominator is all lines. Blank-label abstention denominator is all blank-labelled lines. Recall@3 excludes blank labels; separate answerable-abstention recall uses only answerable reviewed/rejected lines. Empty denominators are null, never falsely reported as 100%.

## Timing and determinism
One unmeasured full pass warms the component, followed by five passes (2,100 timed calls). Timing excludes evaluator validation, file reads and setup. Nearest-rank p95 is sorted sample ceil(0.95*n)-1. Every repeated result is compared to its first result.

Recorded preparation: 28.307 ms. Warm p95: 0.001233 ms. This is trivial review-only overhead on the execution host, not a completed matcher or a laptop benchmark. Timing varies across runs.

## Segmentation
Input-only flags: structured buyer SKU/barcode (77 lines), pack word (76), dimension/weight token (224), selected Malay word skru/ayam/susu (3), slash/double-space (65), other (107). Rules are in noise_flags; flags overlap and are proxies rather than annotated true noise classes. Full counts/metrics are in the report. In particular, this is not yet a robust typo or missing-attribute classification; expand only with justified, manually checked definitions.

## Next evaluation gates
Before tuning an actual matcher, fix a grouped development/validation strategy to limit near-duplicate/alias leakage. Then measure identifiers-only and lexical increments, calibration by lane with uncertainty, a threshold curve, cold-start behaviour and regression thresholds. Baseline confidence is 0 because there is no candidate; it is not a fitted confidence model. Removing aliases currently changes nothing because no matching uses them: the required mature-versus-cold-start behaviour is not yet delivered.

## Personal error analysis — Sadad
Not completed. For 20 actual failures record line_id, prediction/label, evidence inspected, root cause, cost class, proposed fix and side effect; group shared bugs/capability gaps/data issues.
AI may organise evidence but must not fill this as if Sadad personally analysed it.

## Label concerns — Sadad
Not completed. At least three specific lines, supplied label, contradictory/insufficient evidence, proposed adjudication and production response.
Keep original labels for primary metrics; separate adjudicated sensitivity analysis.

## Regression gates
TODO: numeric thresholds based on baseline; zero tenant escapes, deterministic/schema checks, precision/coverage/cost guards, <=250 ms p95, versioned fixtures and benchmark refresh policy.

## Identifier evidence checkpoint (development only)
Commands: `python3 split_data.py`; `python3 inspect_identifiers.py`. Saved output: reports/identifier_development.json, including data/split/source hashes. All 17 tests pass.

A frozen deterministic grouped allocation has 306 development lines and 114 validation lines. Connected components link same tenant + supplied nonblank target, normalised text, customer-scoped buyer SKU, or barcode. Group SHA-256 modulo 4 assigns validation. This uses labels only to allocate item-disjoint groups, never as matcher input. The catalogues remain available to both partitions. It is not stratified and does not guarantee grouping every fuzzy near-duplicate. Normalising punctuation may over-group; small validation/lane populations will limit calibration. No identifier performance results were measured on validation; prior all-review full-train reporting was a no-tuning baseline.

| Retrieval-only result | Aliases available | No alias history |
|---|---:|---:|
| Development lines | 306 | 306 |
| Lines with eligible candidates | 27 | 9 |
| Lines with supplied target retrieved | 27 | 9 |
| Unique candidate with no detected issue | 15 | 8 |

These are not auto precision/coverage or proof of calibration. The evidence component is not yet wired to an acceptance policy. Multiple source targets, weak alias metadata, invalid/expired mappings, unknown identifiers and numeric inconsistencies are flagged. Metadata/conflict counts can overlap. Remaining work includes brand/material checks, quantity parsing, lexical retrieval, and confidence/policy evaluation. No final predictions generated.

## Lexical development experiment — an unsafe acceptance baseline
Command: `python3 inspect_lexical.py`. Raw report: reports/lexical_development.json (input/split/source hashes and environment included). Twenty-five tests pass.

Token cosine (55%) and character-trigram cosine (45%) retrieve tenant-eligible products. These initial weights and the 0.25 retrieval floor are engineering starting choices, not learned probabilities. Known attribute contradictions filter candidates; identifier conflict flags persist. Provisional policy proposals require no detected issue, >=0.05 top-two score margin and the listed similarity threshold. They are evaluated only on development data; no policy has been enabled.

Top-three retrieval contains the supplied target for 210/220 answerable development lines (95.45%). There are 306 total development lines. Retrieval can help human review, but this does not demonstrate safe automatic decisions.

| Similarity threshold | Proposals | Correct | Wrong | Precision | Coverage | Improvement vs review |
|---|---:|---:|---:|---:|---:|---:|
| 0.60 | 196 | 166 | 30 | 84.69% | 64.05% | -12840 |
| 0.70 | 191 | 161 | 30 | 84.29% | 62.42% | -13140 |
| 0.80 | 165 | 136 | 29 | 82.42% | 53.92% | -13880 |
| 0.85 | 149 | 121 | 28 | 81.21% | 48.69% | -14020 |
| 0.90 | 128 | 101 | 27 | 78.91% | 41.83% | -14460 |
| 0.95 | 98 | 73 | 25 | 74.49% | 32.03% | -14620 |
| 1.00 | 78 | 54 | 24 | 69.23% | 25.49% | -15000 |

Recorded preparation: 171.116 ms; warm retrieval p95: 43.118 ms across 306 calls after a warm pass. This is an execution-host experiment, not a laptop certification or repeated performance study.

All tested points lose utility against all-review. Increasing the score threshold does not monotonically improve precision; the score-1.0 group still disagrees with supplied labels. No automatic policy or calibrated confidence is justified yet. These results may combine implementation limitations, missing context, and questionable labels; do not assert which without case inspection. Preserve original labels for primary metrics.

The report's failure_review_queue contains 20 wrong *proposed* answers at threshold 0.90, with source text, label and candidates. These are genuine failures of the recorded experimental policy, not production auto decisions. Root cause, cost class and proposed fix are blank for Sadad's personal work. Extracting traces does not complete the required manual analysis or three label concerns.

Known limits: incomplete pack/quantity distinction, brand spelling not canonicalised as authoritative evidence, partial attribute vocabularies, and a single global score rule. Validation remains unscored for this experiment. Next decisions should follow the personal case review and development evidence, not repeated validation tuning.

## Personal review 01 — ACM-T-0009
Status: Sadad supplied his judgement in the guided review; clarification remains unresolved. AI organised the source evidence and edited this entry. This is 1 of 20 cases discussed, not completion of the full analysis.

**Observed failure:** The threshold-0.90 experimental policy proposes ACM-BALL0659 for `Remax/Ball/Valve/2"/SS304`; supplied gt_item_code is blank. Similarity is 1.0. This is a false-positive proposal against the official label, not an enabled production auto-match.

**Evidence:** The tenant's catalogue contains one exact-name match, disabled=0, available_qty=0, stock_uom=Nos and carton conversion 12. Order quantity is 50, with no UOM, buyer SKU or barcode. No price is supplied. Other inspected Remax 2-inch valves differ in material.

**Sadad's judgement:** The product appears correctly identified, but stock prevents current fulfilment. Flag the disagreement for label/business-rule clarification rather than immediately changing the identity matcher. Keeping the distinction permits a specific customer response and an inventory notification.

**Root-cause assessment:** Suspected specification/label ambiguity, not a confirmed label defect. We have not established that zero stock explains the blank label or that the catalogue stock snapshot represents inventory on the order date. Missing UOM is another unresolved detail; full quantity conversion is not inferred.

**Cost class:** Wrong-auto proposal under supplied labels (800 seconds-equivalent in our convention); if identity is confirmed, the operational issue is fulfilment rather than demonstrated wrong-product shipment.

**Proposed response:** Ask whether item resolution must abstain for unavailable stock and how inventory timing/UOM are treated in annotation. Preserve official labels and primary metrics. Record any adjudication separately. A production inventory message should use current verified stock and a defined fulfilment policy; notifications are outside this assessment's matching scope.

**Regression proposal (assistant-suggested, not yet implemented):** Under an explicitly confirmed identity-only contract, changing stock availability alone should not change the resolved product. If availability is a separate acceptance rule, test its review reason independently. Do not encode a per-line exception or replace the label before adjudication.

**Grouping:** First candidate in the specification/label-clarification group. No assumption that other blank-labelled cases share this cause.

## Personal review 02 — ACM-T-0022
Status: Sadad supplied judgement during guided review; clarification remains unresolved. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-NITR0925 for Kanto Nitrile Glove M Blue; supplied label is blank. Wrong-auto proposal under official labels, not a live automatic decision.

**Evidence:** Exact active catalogue-name match; order 100 box versus stock 900 Box. Structured unit_price is 94.66 versus list_price 99.48. The price is absent from raw_text but is present in the order record.

**Sadad's judgement:** Price difference alone should not reject product identity. Escalate the discrepancy to the pricing/business owner for clarification rather than assume it changes the intended item.

**Root-cause assessment:** Suspected label/business-rule ambiguity; neither a label error nor the source of the price difference has been established. A discount, timing or data error is possible but unproven.

**Cost class:** Wrong-auto proposal against the official label (800 seconds-equivalent under our convention). Actual wrong-product shipment is not established by price mismatch.

**Proposed response:** Preserve original labels and reported metrics; clarify price semantics and any acceptance rule. Keep pricing escalation separate from identity resolution. Do not create an arbitrary price cutoff or silently change the supplied answer.

**Regression proposal (assistant-suggested):** Under a confirmed identity-only contract, an otherwise identical item request with a different commercial price should retain its identity; any price-related review rule needs separate evidence and tests.

**Grouping:** Specification/label clarification, with pricing evidence distinct from Case 1's inventory question.
