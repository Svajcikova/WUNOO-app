# WUNOO v1.350 — Production Recovery Crash-Point Conformance

## Scope
v1.350 extends v1.349 production conformance with real SIGKILL boundaries and restart/boot verification.

## Changes
- Added `ai_dispatch_recovery_crash_conformance_v350` evidence table.
- Added a subprocess crash harness using the real v337/v338/v341/v335 recovery primitives.
- Exercises all seven production recovery crash points from BEFORE_LOCK through BEFORE_COMMIT.
- Verifies SQLite transaction rollback after every hard kill.
- Verifies no active recovery lease remains after restart.
- Runs the real boot recovery gate after each crash.
- Compares the post-crash state to the reference `IDLE` recovery state.
- Added `/api/v350/policy`.
- Added `/api/v350/ops/dispatch/recovery/crash-conformance`.
- Added `/api/v350/ops/dispatch/recovery/crash-conformance-history`.

## Verification
- `TEST_V350.py` PASS
- `TEST_V349.py` PASS
- `TEST_V348.py` PASS
- `TEST_V347.py` PASS
- `TEST_V346.py` PASS
- `py_compile` PASS
- `compileall` PASS
- ZIP integrity PASS

## Result
- phases: 7
- failures: 0
- rollback verified: true
- boot recovered: true
- state mismatches: 0
