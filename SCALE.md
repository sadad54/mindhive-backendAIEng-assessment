# Task 6 — Scale and rollout

AI-assisted engineering analysis grounded in this repository's measurements; forecasts below are not load-test results.

## First bottleneck
The current lexical matcher scans every eligible product for each line, calculating token and trigram similarity in Python. With approximately 1,100 Acme rows, measured warm p95 is about 42 ms across the train mix. At 4M catalogue rows across 500 tenants, the mean tenant has 8,000 items, but the largest tenants matter more than the mean. Linear extrapolation puts a 40,000-item tenant well beyond 250 ms. This is a forecast, not a benchmark; instrument tenant catalogue size, candidates scanned and per-stage p95 before admitting large tenants. 150k lines/day is only 1.74 lines/sec on average, but bursts and skew can saturate serial CPU workers.

First upgrade: tenant-scoped inverted token/trigram indexes with bounded candidate retrieval and the same final contradiction checks. Benchmark recall loss against the exhaustive implementation before replacing it. Cache immutable tenant catalogue snapshots with version tags; atomically swap snapshots after changes. Identifier lookups should remain constant-time and tenant/customer-scoped. Bound warm tenant residency by memory and retain a slower review-safe path on cache misses. Never search a global catalogue as fallback.

No embeddings are delivered. A 40k-item edit therefore requires lexical index rebuild, not GPU re-embedding. Build replacement snapshots in the background, record their catalogue version, and apply changed-item eligibility/conflict checks against current data before accepting. If a snapshot cannot be reconciled, review rather than serve a potentially disabled code. If embeddings are later justified, measure update throughput, storage and recall/precision gain before choosing a model; do not invent those costs now.

## Learning without reinforcing errors
An operator confirmation is evidence, not unquestionable truth. Store original input, proposed alternatives, confirming operator, catalogue version, business context, timestamp and reversals. Never promote an automatic output directly into a trusted alias. Require review of conflicting mappings, expiry, customer scope and repeated independent confirmation for promotion. Sample even apparently successful auto matches for audit. Delay irreversible alias promotion until downstream correction/return windows have matured; quarantine aliases associated with credit notes or wrong shipments. Give operators concrete size/grade/pack differences so confirmation is more than clicking the first candidate.

## Rollout with delayed labels
Shadow a versioned candidate on live tenant-scoped traffic while the incumbent determines outputs. Measure disagreement, candidate recall on adjudicated samples, review load, reasons and latency. Then canary a small tenant-balanced cohort, preserving a per-tenant rollback switch; do not choose only easy high-volume tenants. Cap newly automated volume while outcomes mature. Compare cohorts by input/tenant mix and cost, not raw accuracy.

The offline result is 26/26 correct autos on 114 validation lines, 22.81% coverage, with a wide precision interval. That is insufficient to promise production 98% precision. Require enough adjudicated delayed outcomes to support the business's risk bound before expansion. Any tenant escape, disabled-item acceptance or contradiction bypass stops rollout immediately. Wrong-shipment growth, calibration deterioration, excessive review queues or p95 above 250 ms pauses expansion and triggers rollback/investigation. Keep new labels separate from the benchmark used to choose the policy.

## Other limits
The report completes in about 3.25 seconds at 1.12M events but keeps per-day sets and latency arrays in memory. At 50× volume, memory and full-pass time exceed the current design's budget; use incremental day summaries and exact or explicitly approximate quantile structures with a freshness contract. No permanent indexes were added, avoiding write amplification on the 40-events-per-line ledger.

Sync's strict-second cursor lacks stable snapshot pagination. Hot tenants cause repeated prefix downloads and eventually the safety cap. Track cursor lag, transfer/apply ratio and conflict/uncertain-intent age. Scale via isolated workers and a transactional server database, but vendor snapshot/change-token support is needed to remove the fundamental pagination limit.
