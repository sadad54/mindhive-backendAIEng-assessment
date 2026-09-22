# Mindhive backend assessment

Status: Task 2/3 foundation delivered: pinned inputs, tenant-scoped catalogue loading, validated result contract, review-only baseline and measured evaluation harness. Identifier evidence retrieval and a frozen grouped split are also delivered; automatic acceptance, calibration, final evaluation, report rewrite, sync fixes and holdout predictions remain unfinished.

## Assessment source
[Mindhive brief](https://github.com/mindhiveasia/2026-backend-engineer-assessment/blob/e7ab5fd523f1db783eec517214ac6e75d33f6d5d/README.md), version 2026.1.
Source revision: e7ab5fd523f1db783eec517214ac6e75d33f6d5d.
An unchanged copy is retained in docs/ASSESSMENT_BRIEF.md.

## Working order
1. Task 1: DESIGN.md and initial DECISIONS.md.
2. Tasks 2 and 3: reproducible evaluation baseline, then incremental matcher and personal error analysis.
3. Task 4: measured report diagnosis and rewrite.
4. Task 5: isolated sync reproductions and fixes.
5. Task 6: evidence-based scale/rollout analysis.
6. Freeze, generate predictions, verify offline reproduction, rehearse.

See BUILD_PLAN.md for requirement gates, stopping rules and documentation updates.

## Running
Python 3.10+; standard library only. Original assessment data and starter fixtures are included unchanged, with explicit permission to publish them in this public repository. No download or installation is needed.

Run entirely offline from this repository root:

```bash
python3 audit_data.py
python3 -m unittest discover -s tests -v
python3 evaluate.py --repeat 5 --output reports/baseline_review.json
```

The evaluation currently sends every labelled line for review. It provides a reproducible comparison point, not a completed matcher. It prints overall, tenant and overlapping input-noise-proxy metrics; `null` means a metric is undefined. Seventeen tests protect metric arithmetic, tenant/eligibility checks, label separation, leading zeros, determinism through the evaluator, and p95 calculation. Local input data and starter code were imported byte-for-byte at the pinned revision; `docs/INPUT_MANIFEST.json` records their hashes. `audit_data.py` intentionally verifies original fixtures, so later authorised starter changes require an explicit provenance/audit policy update, not silently replacing the original hashes.

Saved reports contain actual measurements and environment/code/data hashes. The p95 currently measures only review-only overhead on the execution host; it does not establish the future matcher's laptop performance. Holdout bytes are preserved but rows have not been inspected or used for tuning. No `predictions.csv` is generated yet.

## Deliverable status
| File | Status |
|---|---|
| DESIGN.md | Initial design; operating point pending measured evaluation |
| DECISIONS.md | Initial choices recorded; append when real decisions occur |
| predictions.csv | Not generated; holdout reserved for final inference |
| EVAL.md | Review baseline measured; calibration, curve and personal analysis pending |
| PERF.md | Requirements outline; no benchmarks yet |
| SYNC.md | Requirements outline; no fixes/tests yet |
| SCALE.md | Requirements outline; final analysis depends on measurements |
| Source and tests | Review baseline and evaluator; 17 tests pass |

## Assumptions and questions
- Cost convention: U = 20C - 800W - 40A (correct autos, wrong autos, abstentions). This is our explicit interpretation, not a published grader formula. Record raw counts and sensitivity to alternative cost conventions.
- Proposed review/reject boundary: review unresolved product identity; reject clear non-item content. An unknown product is not automatically a non-item.
- Proposed alias validity uses order_date, inclusive start/end dates with blank end unbounded; validate and document any conflicting evidence before implementation.
- Product identity and stock fulfilment are distinct. Do not silently substitute an in-stock alternative.
- DESIGN's 98% precision goal is provisional, not measured or mandated. Calibration and final threshold remain open.
- The README describes a bundle or private repository link for submission. This working repository is public; submission format/access remains to be resolved before delivery. No visibility change has been made.
- Requirements copy points to §9 for the decision-log format; the actual format is in §10.
- Reproduced audit: alias file has 776 rows (brief says approximately 710); 26 customer-scoped keys have multiple targets before date filtering. These are not automatically 26 simultaneously valid conflicts. See reports/data_audit.json. Simulator expiry and report-checker semantics remain for Task 4/5 verification.

## Tool attribution and authorship
ChatGPT/Codex substantially drafted the initial design, planning documents and requirement outlines with Sadad's learning discussion as context. These are proposed engineering choices, not claims that Sadad personally completed an audit or experiments. Codex also authored the initial loader, review baseline, audit/evaluation scripts and automated tests, and ran their recorded verification. These automated checks are not Sadad's personal failure analysis.
The 20-case manual failure analysis and label adjudication require Sadad's personal inspection; these sections remain unfilled. Every quantitative result must identify its command, revision/data and environment.

## Commit policy
Work directly on main as requested. Commit each coherent, verified milestone with its purpose, updating related documentation in the same commit. No force pushes, invented retrospective logs, or single final solution commit. Experimental failures may be committed with an explicit status; never label a known failure as passing.

## Fixture provenance
The user explicitly approved publishing the original data and starter files on 2026-09-22. All 13 files match their pinned original Git blob hashes, including the compressed reference. prepare_inputs.py is an optional checksum-verified recovery tool, not a required setup step.

## Identifier retrieval checkpoint
```bash
python3 split_data.py
python3 inspect_identifiers.py
```
The split is frozen (306 development / 114 validation); regeneration refuses changed assignments. Identifier inspection scores development only and compares alias-enabled versus catalogue-only retrieval. It is separate from evaluate.py's unchanged review baseline. Evidence carries candidate codes, sources and issue tokens; it makes no confidence or auto-acceptance claim. Numeric contradiction checks are deliberately conservative and do not yet distinguish all dimensions from quantities or detect brand/material conflicts. See EVAL.md.
