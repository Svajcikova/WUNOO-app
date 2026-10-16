# WUNOO v1.354 — Recovery Observability & Leak Detection

## Scope
Adds durable observability around the dispatch recovery subsystem. The release detects residual active leases, pending journals, unresolved recovery classifications, fencing-token regressions, and unexpected decreases in durable audit evidence.

## Changes
- Added `ai_dispatch_recovery_observability_v354`.
- Added deterministic before/after recovery snapshots.
- Added residue checks for active lease, pending journal, unresolved recovery, and durable lock state.
- Added monotonic fencing-token verification.
- Added audit-evidence growth sanity check.
- Added `/api/v354/policy`.
- Added `/api/v354/ops/dispatch/recovery/observability`.
- Added `/api/v354/ops/dispatch/recovery/observability-history`.

## Verification
- TEST_V354.py PASS
- TEST_V353.py PASS
- TEST_V346.py PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS

## Result
- 4 observed recovery cycles
- 0 detected leaks
- 4/4 residue-free cycles
- fencing token monotonicity verified
