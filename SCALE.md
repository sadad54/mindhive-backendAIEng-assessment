# Task 6 — Scale and rollout
Status: not written; outline only. Final document <=800 words.

- Ground the first bottleneck in measurements for 500 tenants, 4M catalogue rows and ~150k order lines/day. Label forecasts and unknowns.
- If embeddings are used, estimate re-indexing 40k edited items and define stale-index behaviour; otherwise explain applicability.
- Prevent mistaken operator confirmations from becoming self-reinforcing aliases: provenance, scoped validity, conflict quarantine and adjudication.
- Choose and justify shadow/canary rollout; define metrics, delayed-ground-truth handling and rollback criteria.
