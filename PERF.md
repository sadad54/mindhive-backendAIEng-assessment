# Task 4 — Report performance
Status: not started; no timings or diagnosis claimed.
Predeclared target: preserve existing report output semantics/order, add nearest-rank p95 over the same tenant-day events as max latency, and finish full-window report in <=10 seconds.

## Baseline estimate
TODO: pinned data generation, environment, original-query slice definitions, repeated timings, rows/groups/tenant/day dimensions and validated extrapolation. Never execute full-window original baseline.

## Empirical diagnosis
TODO: same-slice metric-by-metric ablations and measured cost ranking; explain surprises. Query comments are hypotheses, not proof.

## Rewrite and correctness
TODO: implementation, reference equivalence, output order, rounding/exactness assumptions, NULL/count semantics and previous-day boundary cases.
TODO: independent p95 validation; adding a column does not make the supplied reference validate it.

## Measured result
TODO: exact commands, environment, repeated full-window timings, explicit budget verdict and setup/index costs. State misses honestly.

## Trade-offs and ceiling
TODO: unfixed work, index write/storage cost (~40 writes/order line at peak per brief), freshness/migration trade-offs, 50x first limit and next architecture.
