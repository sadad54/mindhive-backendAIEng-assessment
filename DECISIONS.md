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
