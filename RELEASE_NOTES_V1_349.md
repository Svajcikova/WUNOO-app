# WUNOO v1.349 — Production Recovery State-Machine Conformance

## Scope
v1.349 closes the gap between the v1.348 independent differential model and the real DB-backed recovery lifecycle.

## Changes
- Added `ai_dispatch_recovery_conformance_v349` evidence table.
- Added production conformance runner using the real v337/v338/v341/v335 recovery primitives.
- Compares every production phase against the reference state contract:
  `LOCKED → LEASED → FENCED → PRE_GATE → RESOLVING → POST_GATE → COMMITTABLE → COMMITTED`.
- Added real transaction rollback verification using the existing v342 injected-failure path.
- Added real stale-owner/lease-expiry fencing verification.
- Added `/api/v349/policy`.
- Added `/api/v349/ops/dispatch/recovery/production-conformance`.
- Added `/api/v349/ops/dispatch/recovery/conformance-history`.

## Verification
- `TEST_V349.py` PASS
- `TEST_V348.py` PASS
- `TEST_V347.py` PASS
- `TEST_V346.py` PASS
- `py_compile` PASS
- `compileall` PASS
- ZIP integrity PASS

## Result
- scenarios: 3
- failures: 0
- phase mismatches: 0
- rollback verified: true
- stale owner fenced: true
