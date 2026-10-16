# WUNOO v1.342 — Dispatch Recovery Transaction Boundary & Atomicity Gate

## Summary
v1.342 hardens the recovery transaction boundary. Recovery locking, lease/fencing, pre-invariant validation, recovery resolution, post-invariant validation, and durable atomicity evidence now execute on one DB connection/transaction in the v1.342 recovery harness.

## Guarantees
- SQLite uses the existing `BEGIN IMMEDIATE` recovery lock.
- PostgreSQL uses the existing transaction-scoped advisory lock.
- No second DB connection is opened inside the atomic recovery path.
- A failure before commit rolls back recovery evidence and lease changes together.
- Successful recovery writes one durable commit evidence row.
- Pre/post invariant gates run inside the same transaction boundary.
- Fail-closed behavior is preserved.

## New
- `ai_dispatch_recovery_atomicity_v342`
- `_v342_atomic_recovery()`
- `_v342_atomicity_chaos()`
- `GET /api/v342/policy`
- `POST /api/v342/ops/dispatch/recovery/atomicity-chaos`
- `GET /api/v342/ops/dispatch/recovery/atomicity-history`

## Validation
- V331 through V342 regression suite: PASS
- Injected transaction failure rollback: PASS
- Partial evidence after rollback: 0
- Lease left active after rollback: 0
- Successful atomic transaction: PASS
- py_compile: PASS
- compileall: PASS
- ZIP integrity: PASS
