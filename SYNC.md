# Task 5 — ERP synchronisation
Status: not started. No defect is yet reproduced or fixed in this repository.
Vendor fake_erp.py must remain unchanged. Its awkward semantics are constraints.

## Defect evidence
TODO per defect: ticket (MAIA-812/830/844 or latent), mechanism, production trigger, isolated failing-before/passing-after test, restored invariant and remaining limits.
Symptom reporter success is not sufficient evidence.

## Crash safety
TODO: interruption before/after local persistence, cursor advancement, remote commit/response, durable pending intent, retries after idempotency expiry, concurrent edits and recovery.

## Vendor contract
TODO: prioritised requested guarantees and safe behaviour while unavailable. Distinguish documented guarantees from simulator behaviour; reproduce discrepancies without editing vendor code.

## Scale and monitoring
TODO: 500 tenants at five-minute intervals; first bottleneck and leading indicators, tenant fairness, lag, retry/conflict counts and alerts.
