# WUNOO v1.344 — Dispatch Recovery Crash + Concurrency Matrix

## Purpose
Adversarially verify recovery atomicity when multiple processes recover concurrently while one worker is hard-killed at a recovery transaction boundary.

## Changes
- Added `ai_dispatch_recovery_crash_concurrency_v344` audit table.
- Added v1.344 policy and crash/concurrency harness.
- Four concurrent recovery workers per iteration.
- One worker is SIGKILLed at rotating recovery phases.
- Remaining workers exercise the same lease/fencing/invariant path.
- Recovery uses existing distributed lock, lease and fencing mechanisms.
- Final state is checked for pending journal residues, invalid completed commands, active leases and invariant failures.
- Added `/api/v344/policy`.
- Added `/api/v344/ops/dispatch/recovery/crash-concurrency-matrix`.
- Added `/api/v344/ops/dispatch/recovery/crash-concurrency-history`.

## Verified
- `CONCURRENCY_ITERATIONS 4`
- `SIGKILL_SCENARIOS 4`
- `DUPLICATE_RECOVERY_MUTATIONS 0`
- `UNRESOLVED_PROVABLE_RESIDUES 0`
- `V344_OK`
- v1.343 regression PASS
- `py_compile` PASS
- `compileall` PASS
- ZIP integrity PASS
