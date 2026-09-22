# Mindhive backend assessment

Status: Task 1 initial design and build plan. No matcher, evaluation results, report rewrite, sync fixes or holdout predictions are delivered yet.

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
Current milestone is documentation only; there is no runnable assessment implementation yet.
Target environment: Python 3.10+ and SQLite, initially standard library only.
Task 2 will import the supplied data/starter files at the pinned revision, preserving their contents, and add actual verified commands here. Final delivery must run offline on a clean laptop in under 10 minutes.

## Deliverable status
| File | Status |
|---|---|
| DESIGN.md | Initial design; operating point pending measured evaluation |
| DECISIONS.md | Initial choices recorded; append when real decisions occur |
| predictions.csv | Not generated; holdout reserved for final inference |
| EVAL.md | Requirements outline; no measurements or personal analysis yet |
| PERF.md | Requirements outline; no benchmarks yet |
| SYNC.md | Requirements outline; no fixes/tests yet |
| SCALE.md | Requirements outline; final analysis depends on measurements |
| Source and tests | Not implemented |

## Assumptions and questions
- Cost convention: U = 20C - 800W - 40A (correct autos, wrong autos, abstentions). This is our explicit interpretation, not a published grader formula. Record raw counts and sensitivity to alternative cost conventions.
- Proposed review/reject boundary: review unresolved product identity; reject clear non-item content. An unknown product is not automatically a non-item.
- Proposed alias validity uses order_date, inclusive start/end dates with blank end unbounded; validate and document any conflicting evidence before implementation.
- Product identity and stock fulfilment are distinct. Do not silently substitute an in-stock alternative.
- DESIGN's 98% precision goal is provisional, not measured or mandated. Calibration and final threshold remain open.
- The README describes a bundle or private repository link for submission. This working repository is public; submission format/access remains to be resolved before delivery. No visibility change has been made.
- Requirements copy points to §9 for the decision-log format; the actual format is in §10.
- Previously inspected data/code raised additional questions (alias count, simulator expiry, report equivalence tolerance). Reproduce these against the pinned import before treating them as audited findings here.

## Tool attribution and authorship
ChatGPT/Codex substantially drafted the initial design, planning documents and requirement outlines with Sadad's learning discussion as context. These are proposed engineering choices, not claims that Sadad personally completed an audit or experiments. Future assisted code, tests and analysis will be attributed as added.
The 20-case manual failure analysis and label adjudication require Sadad's personal inspection; these sections remain unfilled. Every quantitative result must identify its command, revision/data and environment.

## Commit policy
Work directly on main as requested. Commit each coherent, verified milestone with its purpose, updating related documentation in the same commit. No force pushes, invented retrospective logs, or single final solution commit. Experimental failures may be committed with an explicit status; never label a known failure as passing.
