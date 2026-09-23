# Task 5 — Durable sync and isolated defect evidence

Implemented in `sync_fixed/adapter.py`; the original starter and vendor remain byte-for-byte unchanged. Tests import both adapters and demonstrate original bad behaviour beside the corrected invariant. `python3 -m unittest discover -s tests -p 'test_sync.py' -v` runs the isolated regressions and recovery scenarios. AI authored the implementation/tests and this analysis; these are not Sadad's personal observations from production.

## Defects and evidence
| Defect / ticket | Mechanism and isolated test | Restored invariant |
|---|---|---|
| Timestamp tie loss / MAIA-812 | Original advances strict `>` cursor after a capped page: five same-second rows with page size two yield only two. `test_timestamp_ties_original_loses_rows_fixed_drains` | Re-fetch same lower bound with doubling limit until a non-full response; never advance when capacity is exceeded. |
| Cursor ahead of data / MAIA-812 | Cursor persists before applying rows; injected failure loses the page. `test_cursor_atomicity_original_advanced_before_failed_apply` | Records, applied versions and cursor commit together in SQLite. |
| Unstable retry keys / MAIA-830 | Attempt number and current time generate a new key after a post-commit 504. `test_timeout_after_commit_one_logical_write` | Durable immutable operation ID/key, payload and base version created before network. |
| Forced conflict rebase / MAIA-844 | Original retries old payload against freshly fetched remote version, overwriting the remote user's edit. `test_conflict_never_rebases_over_remote_edit` | Never advance the CAS base automatically; preserve both values in a durable conflict queue. |
| Dirty-edit loss during pull / MAIA-844 | Pull uses wall-clock last-writer-wins and can replace unsent changes even at the same remote version. `test_pull_does_not_drop_dirty_edit_due_to_clock_comparison` | Dirty local payload is retained; remote version changes become conflicts, except reconciliable own pending results. |
| Mislabeled timezone / latent | Server +08 wall time is stored as UTC. `test_timestamps_are_utc_not_server_wall_clock` | Parse the fixed vendor zone, store offset-aware UTC; retain vendor-local cursor separately. No timestamp-based winner selection. |
| Replay side effects / latent | Replaying a page appends the same version again. `test_replay_deduplicates_applied_log` | Deduplicate `(external_id,version)` and never downgrade a clean version. |
| Volatile retry state / latent crash | No durable outbox/checkpoint for a write committed before death. `test_restart_after_commit_and_idempotency_expiry`, `test_outbox_survives_crash_before_network` | Reopen SQLite and resume the original immutable operation. |

Additional tests cover actual subprocess `os._exit` during pull, partial-batch recovery, expired-key creation using base version zero, capacity failure, tenant database binding and preventing edits from mutating an unresolved request. These target conditions not exercised by the supplied symptom reporter.

## Crash and conflict protocol
A SQLite database is bound to one tenant; connect it only to that tenant's authenticated ERP client. WAL with synchronous FULL persists each local transaction. A process dying during pull exposes neither partial rows nor an advanced cursor. Outbox commit precedes the remote call; acknowledgement and clean-version update commit together afterward. Retries reuse the key AND original CAS base. If the key has expired and the ERP reports a conflict, read the current record: exact intended payload at base+1 can be reconciled as desired state reached; otherwise queue conflict. This does not prove which actor performed an identical write. We do not claim global exactly-once delivery.

Base=0 is used for creation; the simulator rejects it when the item already exists. Real deployment needs confirmed create-if-absent semantics. Local edits to an unresolved operation or conflict are refused rather than silently merged. A review UI/API to adjudicate conflicts is outside this implementation; resolution must create a new intent against the explicitly reviewed remote version. No remote notification or customer action is performed by tests.

## Vendor contract limitations and desired changes
1. Stable snapshot pagination using `(updated_at,external_id)` or an opaque change token, plus tombstones. Current strict-second cursor cannot prove completeness for an unbounded tie bucket. We overlap one second, deduplicate, and stop without advancing above 100,000 records. Periodic `pull(..., full=True)` catches older/backdated changes; without snapshots/deletion feed, complete concurrent-change and deletion detection cannot be guaranteed.
2. Durable operation lookup/idempotency retention with payload binding, and documented conditional create/update semantics. We retain original CAS base beyond key lifetime; an ambiguous divergence goes to review.
3. UTC offset-bearing timestamps and a versioned change log. Versions control conflicts; clocks do not.
4. Batch results with per-item status, rate limits and retry-after. Current correctness is per operation, not transactional across a batch. Worker retries should use bounded jitter and tenant quotas; this library performs bounded immediate attempts only.

The fake vendor's docstring says keys expire after 60 seconds, but its `_idem` dictionary has no expiry implementation. Tests clear the cache after advancing its clock to exercise the advertised contract without changing vendor code. The supplied run_sync.py is a symptom reporter and may also see its unhandled simulated 504 during setup; it is not our correctness suite.

## Scale and operational signals
500 tenants every five minutes means 1.67 tenant polls/sec on average, with burst/skew and vendor limits more important than that average. Adaptive re-fetch transfers repeated prefixes and eventually hits the cap for hot tenants; no offset/snapshot makes this the first pull bottleneck. Queue lag, cursor age, cap failures, transferred/applied ratio, uncertain operation age, conflict backlog and post-commit timeout rate should alert before customer complaints. Use tenant-isolated workers with leases, bounded concurrency and jitter; SQLite is an executable single-host durability model, not a deployed 500-tenant service. Move records/outbox/conflicts to a transactional server database with per-tenant ownership before horizontal deployment. Tests cover process death, not disk loss, filesystem corruption or every concurrent network interleaving.
