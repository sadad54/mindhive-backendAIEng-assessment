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
