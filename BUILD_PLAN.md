# Build plan and requirement gates

Status: Task 1 initial draft and Task 2/3 review-baseline foundation delivered, 22 September 2026. Task 1 first, then bounded implementation milestones. Rebase timeboxes against actual remaining deadline; these are effort budgets, not assertions of remaining time.

## Priority analysis
Task 2 (25%) has the largest individual weight, but Task 1 (20%) must precede code and Task 3 (20%) measures whether it works. Therefore build Task 1 -> Task 3 harness foundation -> Task 2/3 increments. Never finish a complex matcher before implementing evaluation.
Tasks 4 and 5 each carry 15%; protect their budgets because neither depends on perfect matching. Task 6 (5%) comes after measurements and fixes so its claims are grounded.

## Remaining-work budget
| Milestone | Budget | Stop condition / output |
|---|---:|---|
| Task 1 foundation | 1 hour | Initial design, requirements inventory, genuine initial choices |
| Task 2/3 input audit + harness | 1.5 hours | Pinned input import, all-review baseline, labels excluded from matcher |
| Task 2 cautious matcher | 2.5 hours | Identifier/lexical candidates, validation, deterministic evidence and tests |
| Task 3 evaluation + personal analysis | 3 hours | Measured curve/calibration/latency, 20 failures, >=3 label concerns |
| Task 4 performance | 3 hours | Slice measurements and ablations before rewrite; equivalence + p95 |
| Task 5 sync | 3 hours | Isolated reproductions, bounded fixes, crash-safety evidence |
| Task 6 + final docs | 1 hour | Evidence-based scale, truthful limitations, coherent documents |
| Packaging + walkthrough | 2 hours | Offline reproduction and 60-minute rehearsal |
Total: 17 focused hours. Shorten optional implementation if less time remains; never fabricate completed evidence.

## Task gates
### Task 1 — DESIGN.md (20%)
- [ ] Objective, constraints, business policy owner; final operating point justified with measurements.
- [x] Initial pipeline contracts, deterministic/probabilistic distinction.
- [x] Initial model choice and criteria to revisit.
- [x] Six costly failure modes and proposed controls.
- [x] Initial scope and production evidence required.
- [ ] Keep final design <=1,500 words and reconcile with implementation.
Initial design is drafted, not final or empirically validated.

### Task 2 — matcher (25%)
- [ ] Tenant isolation, deterministic output, machine-readable reasons.
- [ ] Offline, <=250 ms warm p95 measured; setup/run feasible within 10 minutes.
- [ ] New tenant with zero aliases works; difference measured and explained.
- [ ] Comparable calibrated confidence across lanes.
- [ ] predictions.csv: exactly line_id,item_code,confidence,decision,reason_code,candidates.
- [ ] One row per holdout ID, code blank on abstention; confidence finite in [0,1].
- [ ] decision in auto/review/reject; <=3 code:score pairs, pipe-separated, best first.
- [ ] Freeze policy before holdout inference; do not hand-tune holdout.
- [ ] If embeddings added: pin model, package build step, measure marginal gain and offline feasibility.

### Task 3 — EVAL.md (20%)
- [x] One reproducible command on labelled data (review baseline only).
- [ ] Per-tenant and defined/justified noise-class counts and metrics.
- [ ] Precision/coverage curve, chosen point, cost model, accuracy comparison.
- [ ] Calibration, candidate recall and abstention quality; denominators explicit.
- [ ] Personally inspect 20 actual failures by line_id: root cause, cost, fix, grouping.
- [ ] >=3 argued label defects/ambiguities and production adjudication response.
- [ ] Regression gates and benchmark maintenance; no data leakage or silent label edits.

### Task 4 — PERF.md (15%)
- [ ] State <=10-second full-window target before changes.
- [ ] Measure narrow original-query slices; never run full-window original baseline.
- [ ] Estimate baseline; empirically identify scaling dimension and validate extrapolation.
- [ ] Remove metrics individually; measure/rank cost before optimisation.
- [ ] Preserve original report results/order; supplied reference check passes.
- [ ] Add nearest-rank p95 on same tenant-day population as max latency; independently test.
- [ ] Repeated measured full-window runtime <=10 seconds, or candid missed-target statement.
- [ ] Explain omissions, indexes/write cost, freshness/migration trade-offs and 50x ceiling.

### Task 5 — SYNC.md (15%)
- [ ] Ticket-to-defect mechanisms; include latent defects and trigger conditions.
- [ ] One isolated failing-before/passing-after test per fixed defect.
- [ ] Explicit restored invariants and crash-safety/retry/conflict tests.
- [ ] fake_erp.py unchanged; do not call vendor semantics implementation bugs.
- [ ] Prioritised desired vendor contract and safe behaviour without it.
- [ ] 500 tenants every five minutes: first bottleneck and warning signals.

### Task 6 — SCALE.md (5%)
- [ ] <=800 words; 500 tenants, 4M catalogue rows, ~150k lines/day.
- [ ] First bottleneck supported by evidence; distinguish forecasts.
- [ ] If embeddings: 40k-item update/re-index cost and stale-index behaviour.
- [ ] Prevent operator mistakes poisoning alias feedback.
- [ ] Safe rollout choice with delayed labels and concrete success/rollback criteria.

## Documentation updated with each milestone
| File | Update trigger |
|---|---|
| README.md | New verified command, dependency, limitation, ambiguity, completion status, tool attribution |
| DESIGN.md | Pipeline/contract or policy changes; final measured operating point |
| DECISIONS.md | Every real decision with alternatives, evidence and reversal trigger |
| EVAL.md | Every retained experiment; candidate personally fills manual analysis |
| PERF.md | Before/after each measured report experiment |
| SYNC.md | Each reproduced defect, fix, test and contract limitation |
| SCALE.md | New evidence about bottlenecks or rollout constraints |
| BUILD_PLAN.md | Task gate passes, cuts, remaining priorities |
| predictions.csv | Final frozen inference, or explicitly versioned regeneration after a documented change |
| docs/ASSESSMENT_BRIEF.md | Immutable pinned source; never edit to fit our solution |

## Commit milestones
Actual commit messages describe completed work, e.g.:
- docs: initialize assessment status and source provenance
- docs: define cost-aware design and prioritized delivery gates
- docs: scaffold evidence reports and initial decision log
- chore: import pinned assessment data and starter fixtures
- feat: add tenant-scoped loading and reproducible review baseline
- feat: add identifier matching with explicit conflict checks
- test: measure matcher precision coverage and latency
- perf: ... measured change and rationale ...
- fix: ... one isolated sync defect ...
Update associated documents in the code commit. Use main, no force pushes. Save unfinished experiments with explicit status, not success claims.

## Non-negotiable honesty
No invented metrics or hand-written holdout answers. Never claim AI-prepared analysis as personal inspection. Log 8–15 genuine decisions as they occur, not 15 placeholders. At each checkpoint Sadad should explain one decision and its counterexample. Preserve final two hours; cut embeddings, frameworks and optional features first.

## Checkpoint — runnable review baseline
Delivered pinned source fixtures/manifest, audit, tenant-scoped loader, label-free input type, output safety validation, review-only matching, overall/tenant/noise-proxy evaluation and nine passing tests. reports/ contains actual baseline/audit output. Not delivered: retrieval, calibrated confidence, selected operating point/curve, mature/cold-start distinction, final predictions or personal error analysis. Next milestone: fix validation grouping, then exact identifier retrieval with explicit conflicts and focused regression tests.

## Checkpoint — approved fixtures and identifier evidence
Original fixtures now included unchanged with explicit publication permission. Frozen split: 306 development / 114 validation. Identifier evidence retrieval implemented and tested separately from acceptance; 17 tests pass. Development report compares aliases versus cold start. Next: complete attribute conflict checks and lexical candidate generation, then measure confidence/acceptance. Actual auto matching, threshold curve and final calibration remain incomplete.
