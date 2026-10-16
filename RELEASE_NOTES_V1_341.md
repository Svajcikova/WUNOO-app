# WUNOO v1.341 — Dispatch Recovery State-Machine Formal Invariant Gate

## Scope
Centralized fail-closed invariant validation for dispatch recovery, covering:
- command journal completion ↔ valid v1.333 postcondition
- idempotency request-key uniqueness
- generation-fence referential integrity
- canonical orders ↔ dispatch_jobs lifecycle state pairs
- recovery lease owner/fencing integrity
- pre/post recovery gate and boot readiness

## New
- `ai_dispatch_recovery_invariant_gate_v341`
- `_v341_validate()`
- `_v341_gate()`
- `_v341_boot_gate()`
- `GET /api/v341/policy`
- `GET /api/v341/ops/dispatch/recovery/invariants`
- `POST /api/v341/ops/dispatch/recovery/full-gate`
- `GET /api/v341/ops/dispatch/recovery/invariants/history`

## Boot integration
Startup now executes the v1.341 invariant gate around the v1.338 recovery boot gate. Any pre- or post-recovery invariant violation blocks startup.

## Tests
- `TEST_V339.py` PASS
- `TEST_V340.py` PASS
- `TEST_V341.py` PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS

### v1.341 test result
```text
EMPTY_BOOT_READY 1
MISMATCH_FAIL_CLOSED 1
REPAIRED_PASS 1
CROSS_ORDER_ISOLATION 1
PRE_POST_GATE 1
V341_OK
```
