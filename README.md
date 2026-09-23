# Mindhive backend assessment — Sadad

A deterministic, offline, tenant-scoped matcher with cautious automatic acceptance; reproducible evaluation; a fast exact report rewrite; and a durable ERP sync adapter.

## Delivered and measured
- **Matcher:** frozen development-fit evidence-group confidence, identifier/text contradiction checks, explicit Bulk pack ambiguity and known missing-attribute guards. Validation: **26/26 correct autos, 22.81% coverage**, 84% recall@3. This small sample does not establish guaranteed 98% production precision.
- **Evaluation:** grouped 306/114 development/validation split; confidence curve, calibration, tenant/noise proxies, cold-start ablation, measured latency, 20 case judgements supplied by Sadad and four argued label concerns. Warm all-train p95 **42.37 ms** on the execution host.
- **Predictions:** all **300 holdout lines**, generated after policy freeze; 94 auto / 205 review / 1 reject. Holdout accuracy is unknown.
- **Report:** **8,666 rows**, strict equality with all supplied reference values, nearest-rank p95 independently verified. Five-run median **3.354 s**, below the 10-second budget on this host.
- **Sync:** durable SQLite outbox/cursor transactions, stable retry identity, explicit conflicts, bounded timestamp overlap and crash recovery. Original starter and vendor remain unchanged.
- **Tests:** 56 focused tests currently pass. DESIGN.md is below 1,500 words; SCALE.md below 800. See each task document for evidence and limitations.

## Run on a clean machine
Python 3.10+ and its standard library only. No installation, credentials, models or inference network calls. Run from the repository root. Data and original starter fixtures are included with explicit permission to publish them.

```bash
# Integrity and all unit/regression fixtures
python3 audit_data.py
python3 -m unittest discover -s tests -v

# Evaluate the FROZEN policy (does not train)
python3 evaluate_matcher.py --repeat 2 --output reports/final_evaluation.json
python3 predict.py
python3 regression_check.py

# Performance data generation and full rewrite verification
python3 starter/make_perf_db.py --out data/perf.sqlite
python3 perf_verify.py
```

The above workflow is designed to finish well inside ten minutes on a normal laptop; recorded timings are from the execution host, so rerun there. The generated SQLite database is not committed. Rebuilding it replaces that generated file only.

The official report checker also works:
```bash
PYTHONPATH=. python3 starter/bench_report.py check --db data/perf.sqlite --module perf_report:run --baseline data/report_reference.json.gz --repeat 5 --budget-s 10
```
`PYTHONPATH=.` is a POSIX-shell command; on other shells use perf_verify.py, which already verifies strict reference equality, row order and p95.

Sync-only tests:
```bash
python3 -m unittest discover -s tests -p 'test_sync.py' -v
```
Use `sync_fixed.adapter.Store(path, tenant)`, `pull(erp, store)` and `push(erp, store)` with the supplied fake vendor or an authenticated tenant-bound client. Unresolved conflicts are persisted; the adapter does not silently choose a winner. Tests use temporary databases.

## Reproducing experiments
```bash
python3 evaluate.py --repeat 5 --output reports/baseline_review.json
python3 inspect_identifiers.py
python3 inspect_lexical.py
# Explicit development-only fitting; not part of normal inference:
python3 fit_policy.py
# Slow-query diagnosis: bounded slices ONLY, never full original baseline:
python3 perf_diagnose.py
python3 perf_scale.py
python3 perf_ablate.py
python3 perf_channels.py
```
Historical saved reports correspond to their committed code versions; rerunning inspect_lexical.py on the final code naturally produces a later result. Original lexical and pack-only reports are retained. Do not overwrite them and claim the earlier implementation produced new numbers. Final reports and prediction manifests include code/data hashes. Re-fitting after looking at validation requires a new untouched test set before claiming independent validation.

## Files to read
| Task | Implementation | Evidence |
|---|---|---|
| 1 — framing | DESIGN.md | Objective, pipeline, six expensive failures, boundaries |
| 2 — matcher | matcher/service.py, lexical.py, identifiers.py, policy.json; predict.py | predictions.csv, prediction manifest |
| 3 — evaluation | evaluate_matcher.py, regression_check.py | EVAL.md, reports/final_evaluation.json |
| 4 — report | perf_report.py, perf_verify.py | PERF.md, diagnosis/scaling/ablation/result JSON |
| 5 — sync | sync_fixed/adapter.py, tests/test_sync.py | SYNC.md |
| 6 — scale | SCALE.md | Measured limits versus forecasts |
| Choices | DECISIONS.md | Real alternatives, evidence and reversal triggers |

## Assumptions, ambiguities and deliberate limits
- Utility is explicitly interpreted as **20C−800W−40A**, hence improvement over all-review is 60C−760W. The brief mixes savings and costs without an explicit scoring formula; raw counts and alternative cost sensitivity are reported.
- Product identity is separate from stock, commercial pricing and quantity fulfilment. Unresolved units/pricing/shortages do not silently substitute products. Whether they should block identity labels remains a business/annotation question. Official labels were never changed.
- The matcher handles known attributes and explicit Bulk siblings, not a full quantity/UOM parser, arbitrary pack naming, all thread dimensions or general multi-item/negation semantics. Low coverage and Acme validation retrieval gaps remain. No embeddings/LLMs were benchmarked or included.
- Grouped validation is small and all 20 personally discussed failure traces are Acme blank-label cases from the earlier experimental policy. Their selection is disclosed; they are not representative of every failure type or both tenants.
- The fake vendor describes 60-second idempotency expiry but implements an unexpired dictionary. Tests simulate expiry without changing it. Stable snapshot pagination, deletions and unlimited same-second buckets cannot be made fully correct with the available vendor API; the adapter stops rather than advance an unsafe cursor.
- The generated report data contains invalid calendar dates. The rewrite delegates previous-day calculation to SQLite to preserve original semantics. Ordinary Python sum initially differed from SQLite's stable AVG; math.fsum corrected it. Final supplied-reference equality is exact on this dataset.
- The brief estimates ~710 aliases; supplied data has 776. Its decision-log cross-reference points to §9; the format is actually §10.
- The assessment requests a bundle or private repository link. This working repository is public with your approval; before submitting, confirm the acceptable format or create a local archive. No visibility change or submission has been performed.

## Provenance and authorship
[Original brief](https://github.com/mindhiveasia/2026-backend-engineer-assessment/blob/e7ab5fd523f1db783eec517214ac6e75d33f6d5d/README.md), version 2026.1, pinned commit e7ab5fd523f1db783eec517214ac6e75d33f6d5d. docs/ASSESSMENT_BRIEF.md and the 13 imported data/starter files remain unchanged; docs/INPUT_MANIFEST.json and audit_data.py verify hashes.

ChatGPT/Codex substantially authored the code, tests, measurements and engineering documentation. Sadad provided each of the 20 personal case judgements through guided discussion; assistant refinements/regression proposals are attributed. Tool-produced evidence is not claimed as Sadad's unaided analysis. Sadad must review the code and defend the decisions during the live walkthrough. See WALKTHROUGH.md for the remaining preparation.
