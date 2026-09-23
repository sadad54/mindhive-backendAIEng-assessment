# Task 4 — Report diagnosis and rewrite

**Target stated before the rewrite: full window including exact nearest-rank p95 in <=10 seconds.** Measured final five-run median: **3.354 seconds** (3.251–3.675), all **8,666 rows**, strict reference value equality and row order. The original full-window query was never run. AI authored the implementation and analysis; raw measurements are committed.

## Reproduction
```bash
python3 starter/make_perf_db.py --out data/perf.sqlite
python3 perf_diagnose.py
python3 perf_scale.py
python3 perf_ablate.py
python3 perf_channels.py
python3 perf_verify.py
```
Diagnosis commands only run narrow original-query slices, with a 30-second per-query interrupt. They are slower than normal verification and need not be rerun on every change. `perf_verify.py` runs the rewrite five times, checks reference values/order exactly, independently checks every p95 through SQLite window functions, and compares original SQL on a two-group slice. `tests/test_perf.py` also checks a tiny independent fixture with duplicate accepts, differing event/order days, a previous-day item, a day without events and nearest-rank p95=19 for values 1..20.

## Estimate the baseline rather than wait for it
The generated database contains 120,000 order lines and 1,119,139 events. No permanent indexes were added. Existing indexes from the generator remain. Repeated slice results (median of two, seconds):

| Tenant(s) | Days | Input lines in slice | Output groups | Seconds |
|---|---:|---:|---:|---:|
| T040 | 1 | 4 | 2 | 5.355 |
| T040 | 2 | 9 | 5 | 6.591 |
| T040 | 4 | 25 | 12 | 9.578 |
| T001 | 1 | 255 | 4 | 6.860 |
| T001 | 2 | 516 | 8 | 9.249 |
| T001 + T040 | 1 | 259 | 6 | 7.594 |

The busy tenant has ~64x the input lines of the small tenant for one day, but only ~1.28x the runtime. Multiplying by window input rows is therefore unsupported. Query plans show correlated scalar subqueries under the outer tenant/channel/day grouping, including repeated scans of match_event and order_line, and an automatic partial covering index for the EXISTS branch. Building that transient structure contributes substantial fixed cost even to tiny slices.

An ordinary least-squares fit across these six measured medians gives **seconds = 4.831 + 0.43887 × output groups**, residual sum of squares 1.50 s². A window-row predictor has SSE 10.46; tenant-days 5.18; days alone 6.28. Thus output groups explain these slices better than the tested alternatives. Within-tenant incremental slopes range from ~0.42 to ~0.60 seconds/group. Applying the group fit to 8,666 outputs estimates **3,808 seconds (~63.5 minutes)**; the within-tenant slopes imply a rough **61–87 minute** range. This is an extrapolation, not a measured full-window time or formal confidence interval; skew, cache and planner choices limit precision.

A tenant-day estimate that ignores four channel groups can be roughly fourfold too low: repeated tenant-day metrics are still evaluated for each channel row. perf_channels.py directly holds T001/May 1 fixed: one channel/group takes 4.949 s, two take 6.162 s, while the four-channel slice takes 6.860 s. This is inconsistent with cost depending only on tenant-days; fixed setup and run variability preclude a perfect linear ratio. Raw runs are in reports/perf_channels.json. Do not confuse the shipped reference's 3,050-second metadata with a baseline measured here; it was not used to fit this estimate.

## Ablation ranking before/after diagnosis
Initial two-group diagnosis preceded the rewrite: full 5.135 s versus 0.747 s with repeat_items_prev_day removed. No other one-column removal produced a comparable reduction. A later, repeated 12-group experiment checked that this was not only a tiny-slice finding; full median 10.261 s:

| Removed metric | Remaining runtime (s) | Reduction (s) |
|---|---:|---:|
| repeat_items_prev_day | 5.142 | 5.119 |
| accepted_disabled | 8.724 | 1.537 |
| avg_accept_score | 8.768 | 1.494 |
| avg_latency_ms | 8.792 | 1.470 |
| lines_accepted | 8.797 | 1.465 |
| max_latency_ms | 8.848 | 1.413 |
| candidates_considered | 9.507 | 0.755 |
| distinct_customers | 9.508 | 0.754 |

Repeat-items is clearly first at this scale. The middle metrics are effectively tied within observed run variation; their exact ordering should not be overinterpreted. The surprise is how much time remains after removing the suspect EXISTS metric: ~5.14 seconds for only 12 groups. Fixing that one expression cannot meet the full-window budget. Shared repeated scans must be removed too. Ablation savings are not additive because plans and transient structures change.

## Rewrite and equivalence
`perf_report.run(connection)` uses bounded database passes and in-memory dictionaries/sets. Load line metadata and disabled-item keys; stream events once; aggregate accepted distinct lines, candidate counts, per-day scores/latencies and item sets. Repeat-items is the intersection of today's and yesterday's tenant item sets. Sort each tenant-day latency list once; nearest-rank p95 is element ceil(0.95*n)-1, on the same event-day population as max latency.

Important original semantics are retained: accepted-line counts use event tenant plus order channel/day; candidate counts use order tenant/channel/day; score/latency/disabled/repeat metrics use event tenant/day regardless of channel. Prior-day sets include events outside the reporting window. Group row order remains tenant/channel/day. SQLite computes previous-day strings because the fixture includes invalid calendar dates which Python datetime would reject.

The first Python rewrite used ordinary sum, introducing tiny floating differences from SQLite/reference. Replacing it with math.fsum fixed the implementation error. The final strict comparison has **zero reference float delta** and exact baseline-column values; it also passes the supplied checker (five-run median 3.447 s). Final strict-check timings are in reports/perf_result.json. Earlier speculation that the reference was inconsistent was disproven by directly checking SQLite AVG; no reference or checker was altered.

## Costs accepted and work left
No schema migration, new permanent indexes, materialisation or stale cache: existing write throughput is unaffected by added indexes, and each report reads current data. All passes run in one read transaction for snapshot consistency; an existing caller transaction is preserved and never committed by the report. The benchmark fixture is static. Memory grows with line metadata, distinct day-item sets and latency arrays; this trades memory and Python CPU for avoiding thousands of database rescans. The implementation still reads all stored events, including outside the output window, because it prioritises straightforward population equivalence. A large historical ledger requires bounded event/day reads with careful preservation of order-day metrics and previous-day context.

At 50x event volume the roughly linear pass alone projects to >160 seconds, before extra sorting/memory pressure; it does not hold the budget. Next architecture: transactional incremental tenant/day aggregates, exact maintained latency frequencies where practical, an explicit freshness watermark, and periodic reconciliation. Approximate quantiles require an agreed accuracy contract. Do not add many write-amplifying indexes blindly to a ledger receiving ~40 event writes per order line. Build this only when measured growth/freshness requirements justify migration and operational complexity.

Host: Python 3.12.14, SQLite 3.53.1, Linux. Laptop reproduction remains a human delivery check; no hardware-independent runtime guarantee is claimed.
