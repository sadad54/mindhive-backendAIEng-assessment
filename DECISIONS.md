# Decision log

Initial decisions on 2026-09-22. AI-assisted drafts of actual planning choices, not experimental conclusions. Sadad must review and defend them. Add entries as decisions occur; 8–15 is the brief's suggested final range, not a quota to fabricate.

## D-01 — Couple matching with evaluation before optimising coverage
**Context:** Tasks 1–3 total 65%; the brief penalises confident wrong matches and requires measured evaluation.
**Options:** Build all matching features first; build only evaluation; start with an evaluable minimal matcher and iterate.
**Chose:** Initial design, then all-review harness, then measured matcher increments. Protect Task 4/5 and final verification time.
**Evidence:** Brief §§1, 4–6 and 11. No implementation metrics exist yet.
**Reversal trigger:** A blocked prerequisite requires a bounded detour; never remove the measurement gate.

## D-02 — Begin with standard-library deterministic matching
**Context:** Offline execution, reproducibility and live explainability are required under a short timebox.
**Options:** Identifier/lexical baseline; local embeddings immediately; external LLM inference.
**Chose:** Standard-library identifier and lexical baseline first. External inference is out of scope under the rules; embeddings remain optional.
**Evidence:** Brief §5.2 explicitly requires marginal model gain and offline feasibility. This is a scope decision, not evidence that embeddings underperform.
**Reversal trigger:** Labelled development errors demonstrate a valuable retrieval gap after cheaper methods, and enough time remains to measure/package a local model.

## D-03 — Separate evidence retrieval from acceptance
**Context:** The brief warns of dirty aliases, active twins and superseded items. Learning discussion distinguished missing size from conflicting size.
**Options:** Return immediately on an exact hit; blend every score; gather evidence then apply eligibility/conflict checks.
**Chose:** Gather tenant-scoped evidence, then arbitrate. Missing text detail may be supplied by a unique identifier; contradictions trigger review.
**Evidence:** Brief §2; scenario-based reasoning, not a completed dataset audit or benchmark.
**Reversal trigger:** Adjudicated production evidence establishes an authoritative source precedence for a precisely scoped conflict. Tenant isolation remains mandatory.

## D-04 — Make cost assumptions and provisional targets explicit
**Context:** The brief gives savings/costs but no precise grader utility equation.
**Options:** Optimise accuracy; use an undocumented cost formula; document a convention and retain raw outcome counts.
**Chose:** U=20C-800W-40A, provisional >=98% observed auto precision and zero tenant escapes; final policy pending validation.
**Evidence:** Brief §§1 and 5.4; algebra in DESIGN.md. The 98% goal is our proposal, not a measured result or mandated threshold.
**Reversal trigger:** Business clarification changes cost convention or evaluation demonstrates a different defensible operating point; record any change and uncertainty.

## D-05 — Establish an all-review comparator and validate outputs before scoring
**Context:** Matcher changes need a measurable comparison; zero automatic errors can hide zero useful work.
**Options:** Begin with an unmeasured fuzzy matcher; return fake high precision for no answers; establish a review-only baseline with honest empty-denominator metrics.
**Chose:** All-review comparator, label-free input type, tenant/eligibility output validation and tests with mixed synthetic decisions.
**Evidence:** reports/baseline_review.json: 420 reviews, zero coverage, undefined auto precision, utility -16,800. Nine tests include cross-tenant rejection and independently calculated mixed-outcome utility.
**Reversal trigger:** Keep baseline for comparison even after real matching exists; extend metrics when measured use cases need them. It is not an acceptance policy for final delivery.

## D-06 — Freeze connected groups before identifier experiments
**Context:** Random rows can put repeated target products, descriptions and aliases on both sides of validation.
**Options:** Random row split; customer-only split; connected groups using target/text/identifier relations.
**Chose:** Fixed hash allocation of connected groups, 306 development and 114 validation lines. Do not reshuffle to improve scores.
**Evidence:** docs/TRAIN_SPLIT.json; transitive grouping and order-invariance test. No identifier validation performance consulted.
**Reversal trigger:** Demonstrated grouping defect or new data; version the split explicitly and disclose lost comparability. This split does not capture every fuzzy near-duplicate.

## D-07 — Measure identifier retrieval before estimating acceptance confidence
**Context:** Exact identifiers may disagree or reference disabled products; alias confidence metadata is not output calibration.
**Options:** Assign arbitrary high confidence and auto-match; measure candidates/issues independently first.
**Chose:** Separate Evidence object with codes, sources and issues; retain review baseline pending full arbitration/calibration.
**Evidence:** Development-only report finds targets for 27 lines with aliases versus 9 cold-start; 17 tests pass. Numeric checks remain incomplete; no automatic precision claimed.
**Reversal trigger:** Sufficient conflict checks and labelled evaluation support a documented confidence mapping and acceptance policy.

## D-08 — Use lexical similarity for retrieval, not as calibrated confidence
**Context:** Identifier retrieval reaches only 27 development targets with aliases; noisy product descriptions need catalogue search.
**Options:** Token-only search; combined token/character retrieval; local embeddings now.
**Chose:** Initial deterministic 55% token/45% character-trigram cosine, explicit attribute conflicts and tenant scope. Weights are starting choices, not optimised/calibrated probabilities. No embedding comparison has been run.
**Evidence:** 210/220 development targets appear in top three; tests preserve fractions and reject wrong-size/brand/material alternatives. See lexical_development.json for measurements.
**Reversal trigger:** Case inspection shows systematic retrieval failures or latency/cost evidence justifies another method; compare against this retained baseline.

## D-09 — Do not enable the provisional similarity-threshold policy
**Context:** Retrieval success does not imply correct automatic decisions.
**Options:** Accept high scores; tune until the reported number looks good; retain review and investigate observed failures.
**Chose:** Leave evaluate.py on all-review, record the entire tested curve, and provide case traces for personal inspection before a new acceptance policy.
**Evidence:** Every tested development threshold from 0.60 to 1.00 has negative improvement over review. At 1.00, 54 of 78 proposed answers are correct against supplied labels. Validation/holdout not used to choose this decision.
**Reversal trigger:** Better evidence checks plus calibration and a frozen validation evaluation justify an operating point. Do not rewrite official labels to make the curve pass.

## D-10 — Block unresolved explicit Bulk pack siblings before score acceptance
**Context:** Personal Cases 4, 9, 13 and 18 showed that exact standard names and large score margins do not establish pack identity.
**Options:** Raise similarity thresholds; infer Bulk from quantity; inspect catalogue sibling conversions.
**Chose:** A tenant-scoped full-family guard for explicit Bulk siblings with otherwise identical names, brand and stock unit but different conversions. Literal variant wording or unique issue-free identifiers may resolve the family; quantity, stock and price cannot.
**Evidence:** 32 tests pass. At unchanged development threshold 0.90, wrong proposals fall 27 to 16 with correct proposals unchanged at 101; recall@3 remains 210/220. All tested operating points still have negative utility, so review remains enabled. See EVAL.md and reports/pack_guard_development.json.
**Reversal trigger:** Broader real catalogue pack naming or negated/multi-item wording requires a stronger parser and new fixtures; do not extend family grouping by arbitrary similarity without measuring false ambiguity. This guard is not complete packaging support.

## D-11 — Freeze coarse evidence-group confidence before validation
**Context:** Raw similarity was not calibrated and exact names often disagreed with supplied blank labels. Missing material/grade and pack ambiguity require hard review guards.
**Options:** Invent high confidence for exact names; change questionable labels; fit coarse correctness frequencies on development only.
**Chose:** Six explicit evidence groups, Beta(1,1) smoothing, minimum 10 examples and >=98% observed correctness plus positive expected utility to enable a group. Preserve original labels and freeze before validation. Missing-attribute/contradiction flags block acceptance.
**Evidence:** Development counts and Wilson intervals in matcher/policy.json; identifier 15/15, high lexical 33/33, other lexical 56/56, exact lexical 55/70. Counterintuitive exact/non-exact behaviour is disclosed as a distribution risk, not explained away.
**Reversal trigger:** Failed frozen validation or adjudicated production drift disables the policy; do not repeatedly tune on the same validation set. More data is needed for tenant-specific calibration.

## D-12 — Durable outbox and conflict quarantine, never forced rebase
**Context:** The starter loses same-second pull rows, retries with new keys and overwrites concurrent ERP edits; death can occur after remote commit.
**Options:** Retry harder/latest timestamp wins; long-lived vendor idempotency alone; durable immutable intents plus version preconditions and reconciliation.
**Chose:** SQLite transactional records/cursor/outbox/conflicts, overlapping adaptive pulls with a hard cap, stable operation keys and original CAS base across retries. Preserve conflicts for explicit resolution.
**Evidence:** Fifteen focused sync tests include original-adapter counterexamples, hard process death, key-cache expiry and partial-batch restart. Vendor code is unchanged; advertised TTL is simulated by clearing its non-expiring cache.
**Reversal trigger:** Vendor snapshot pagination, durable operation lookup and conditional create remove current caps/ambiguities; horizontal scale requires a server database and worker ownership. No claim of global exactly-once or deletion detection.

## D-13 — Replace correlated report scans with one-pass summaries
**Context:** Bounded original-query slices showed high fixed setup cost and repeated tenant/channel/day scans; repeat-items was the largest isolated cost but substantial work remained without it.
**Options:** Add many expression/covering indexes; optimise only EXISTS; aggregate once in a read snapshot with per-day sets and latency arrays.
**Chose:** Standard-library Python/SQLite bounded passes, item-set intersections, stable score summation and exact nearest-rank p95. Preserve order-day/event-day populations and row order; no permanent indexes/materialised stale views.
**Evidence:** Repeated slices fit output-group scaling better than input-row scaling; 12-group ablation reduces 10.261 s to 5.142 s without repeat-items. Full rewrite matches all 8,666 reference rows exactly and runs in approximately 3.35 seconds, including p95 checked independently on every output group.
**Reversal trigger:** At 50x volume the full scan and memory footprint fail the budget; move to incremental summaries with an explicit freshness/quantile contract, not unmeasured index proliferation.

## D-14 — Ship the frozen policy with disclosed limits rather than tune holdout
**Context:** Validation is small; exact-text label concerns remain unresolved and more language/pack features could consume the remaining time without reliable new evaluation.
**Options:** Add semantics/embeddings and retune on validation; keep the measured policy and complete report/sync/reproduction work.
**Chose:** Preserve the pre-validation policy, generate holdout once deterministically, publish explicit regression gates and prioritise complete runnable task evidence. No automatic alias learning or production deployment.
**Evidence:** 26/26 validation autos at 22.81% coverage; 300 holdout rows generated with no known accuracy. Report and sync now have separate correctness/performance evidence; all 20 candidate judgements are recorded.
**Reversal trigger:** A new untouched evaluation set or adjudicated production outcomes justify changing acceptance. Laptop verification and Sadad's live-code defence remain necessary personal work.
