# Task 3 — Evaluation
Status: not run. This is an evidence collection outline, not results.

## Reproduction and data
TODO: exact command, code/data revision, Python/environment, split/grouping/seed, label leakage controls and noise-segmentation definitions.
Baseline: all-review has 0% coverage and undefined auto precision.

## Measurements
TODO: correct/wrong autos and abstentions, precision, coverage, defined accuracy, utility, blank-label abstention, recall@3 including answerable reviews; denominators and per-tenant/noise counts.
TODO: precision-versus-coverage curve and chosen operating point; validation versus full-training results distinguished.
TODO: confidence calibration by lane, sample counts/uncertainty, warm p95 and preparation cost, cold-start comparison.
No measured numbers are available.

## Personal error analysis — Sadad
Not completed. For 20 actual failures record line_id, prediction/label, evidence inspected, root cause, cost class, proposed fix and side effect; group shared bugs/capability gaps/data issues.
AI may organise evidence but must not fill this as if Sadad personally analysed it.

## Label concerns — Sadad
Not completed. At least three specific lines, supplied label, contradictory/insufficient evidence, proposed adjudication and production response.
Keep original labels for primary metrics; separate adjudicated sensitivity analysis.

## Regression gates
TODO: numeric thresholds based on baseline; zero tenant escapes, deterministic/schema checks, precision/coverage/cost guards, <=250 ms p95, versioned fixtures and benchmark refresh policy.
