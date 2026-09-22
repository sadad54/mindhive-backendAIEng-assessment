# Task 1 — Problem framing and initial design

Status: pre-implementation design. Proposed policies and targets are not measured results. AI-assisted draft; Sadad must understand and defend the choices. Final operating point will be updated after evaluation.

## 1. Objective and operating point
Resolve an order line to exactly one eligible catalogue item for its tenant or abstain. Wrong automatic matches can ship wrong goods and contaminate future aliases; ordinary spelling errors matter mainly when they lead to those outcomes.

Let C be correct automatic answers, W wrong automatic answers, A abstentions, and N=C+W+A. Interpret the brief as utility U=20C-800W-40A in seconds-equivalent. This convention treats correct matches as +20, review as -40, wrong matches as -800. Relative to reviewing every line, improvement is 60C-760W. The brief mixes savings and costs without an explicit scoring formula; retain raw counts and report sensitivity rather than presenting our convention as the grader's formula.

Choose the evaluated policy maximising estimated utility subject to zero cross-tenant resolutions, evidence/eligibility checks, and a provisional observed auto-precision target of at least 98%. The target is a cautious starting constraint, not a demonstrated guarantee. Report sample counts and uncertainty. If unattainable, disclose the measured frontier and missed target; do not tune the holdout or claim all-review precision is 100%. For zero autos it is undefined.

For genuinely calibrated correctness probability p, this utility favours auto when 20p-800(1-p)>-40, or p>760/820 (~92.68%). This theoretical threshold does not replace the stricter initial precision goal, calibration checks or hard rules. At 3× review cost the boundary becomes 80/140 (~57.14%) under the same convention. A different zero-cost-correct convention yields a different boundary; state assumptions before changing policy.

Operations/business owns acceptable loss and review capacity; engineering validates and enforces the operating point. Tenant isolation is never a tunable trade-off.

## 2. Pipeline and contracts
Input: tenant, customer_id, order_date, raw_text, optional buyer_sku/barcode, quantity, UOM and price/notes. Ground-truth labels belong only to the evaluator. Preserve identifier strings and leading zeros.

1. Scope and validate. Select tenant-specific indexes; unknown tenants review without searching other tenants.
2. Normalise conservatively. Preserve original text; extract brand, family, dimensions, material and pack clues. Tolerate casing/spacing but preserve fractions and meaningful letters.
3. Gather identifier evidence. Lookup barcode/item codes within tenant. Alias lookup additionally uses customer and order date; inspect validity, source/confidence, conflicting targets and target eligibility. Exact hits do not return early before contradiction checks.
4. Retrieve lexical candidates. Use deterministic token/character similarity to retrieve a small set. Keep explicit attributes alongside scores. Measure identifiers-only before adding lexical logic.
5. Validate and arbitrate. Reject disabled/non-item targets; detect conflicting identifiers and critical attributes, unresolved twins and insufficient evidence. Missing text detail can be supplied by a unique eligible identifier; explicit contradiction cannot be averaged away.
6. Decide and explain. Return auto with a single code or review/reject with blank code. Include a stable reason token, comparable confidence and up to three tenant-scoped candidates. Tie-break consistently by item code for display; ties do not justify acceptance.

All initial computations are deterministic for fixed inputs/configuration. Confidence is a probabilistic interpretation derived from labelled evidence, not random execution. Raw similarity is not correctness probability. Establish a development/validation procedure before tuning; measure reliability by lane and confidence band, acknowledge small samples, and validate any score-to-confidence mapping separately. Proposed confidence means estimated correctness of the top eligible candidate, including review cases; no candidate yields 0. Candidate scores have separately documented retrieval semantics.

Index preparation happens once; measure it separately from warm per-line p95 (target <=250 ms, no network). Cold start uses the catalogue-only path with no alias history. Measure its coverage, errors and reasons separately rather than borrowing mature-tenant performance.

## 3. Model choice
Start with standard-library identifier checks and lexical retrieval. No LLM or embedding is currently included or benchmarked. Local embeddings could help missing multilingual synonyms but may conflate near-identical sizes/materials; external inference is prohibited. Consider a permitted local model only if labelled development failures demonstrate missing retrieval capability that cheaper normalisation/lexical methods do not fix. Pin/package it, measure marginal precision/coverage/net value and latency against the baseline, and retain catalogue-only fallback. Do not claim a rejected model lost an experiment we never ran.

## 4. Six expensive failure modes
| Failure | Planned protection |
|---|---|
| Other tenant's code accepted, including misleading buyer SKU | Scope every index and final output to tenant; adversarial tests |
| Stale, inferred or conflicting alias treated as fact | Customer/date/provenance validation; evidence conflicts review |
| Superseded or non-item entry selected | Explicit eligibility checks before acceptance |
| Wrong size, material or brand among similar names | Attribute contradiction checks; no blanket punctuation/number removal |
| Pack twin or outer-unit price interpreted as unique identity | Item-specific UOM evidence; unresolved pack distinctions review; no universal carton conversion |
| Exact barcode/SKU overrides contradictory text or another identifier | Gather evidence before arbitration; conflict reason and useful candidates |

Feedback contamination amplifies these errors: do not promote automatic predictions to confirmed aliases; preserve provenance and require adjudication before learning from conflicts.

## 5. Scope and evidence
Deliver a service-shaped Python component and command-line harness; no HTTP server, UI, OCR, cloud deployment or external integration is needed. Stock substitution and full quantity fulfilment are out of scope. Proposed reject means clear non-item; ambiguity/unknown products review.

Evaluation reports precision, coverage, utility, accuracy with its definition, top-3 recall, abstention quality, tenant/noise segmentation, threshold curve, cold start and p95. Define denominators; blank labels mean expected abstention. Keep validation distinct from repeated tuning. Official labels remain unchanged for primary metrics; adjudicated sensitivity is separate. Sadad personally investigates 20 actual failures and at least three label concerns.

Production expansion requires measured traffic, review capacity, adjudicated delayed outcomes, tenant skew and latency evidence. Revisit models only for measured retrieval gaps; infrastructure only for demonstrated limits. Protected timeboxes cover report and sync tasks; preserve packaging and rehearsal rather than spending the entire assessment on matching.
