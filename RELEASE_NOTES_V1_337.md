# WUNOO v1.337 — Dispatch Recovery Distributed/Process Locking

## Purpose
Serialize dispatch command-journal recovery across concurrent application processes before traffic admission.

## Changes
- Added `ai_dispatch_recovery_lock_v337` persistent recovery lock metadata.
- SQLite recovery gate acquires `BEGIN IMMEDIATE` before journal inspection/resolution.
- PostgreSQL recovery gate acquires transaction-scoped `pg_advisory_xact_lock(hashtext('wunoo.dispatch.command.recovery.v1'))`.
- Recovery, reconciliation, postcondition validation, and boot evidence execute on the same locked DB transaction.
- Replaced startup v1.336 command recovery invocation with the v1.337 serialized gate.
- Added `/api/v337/policy`.
- Added `/api/v337/ops/dispatch/recovery/lock-status`.
- Added `/api/v337/ops/dispatch/recovery/run`.
- Fail-closed on recovery errors or unresolved command state.

## Verification
- V331 regression: PASS
- V332 regression: PASS
- V333 regression: PASS
- V334 regression: PASS
- V335 regression: PASS
- V336 regression: PASS
- V337 two-process concurrent boot gate: PASS
- Duplicate recovery mutations: 0
- py_compile: PASS
- compileall: PASS
