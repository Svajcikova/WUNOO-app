# WUNOO v1.363 — Recovery Bootstrap Deadlock Fix

## Scope
Fixes the v1.356 recovery bootstrap deadlock where the fail-closed lifecycle required historical READY and observability evidence before the first boot could create that evidence.

## Changes
- Adds an explicit bootstrap mode to the v1.356 recovery lifecycle.
- On first boot, HEALTHY is derived only from current durable safety invariants: no foreign active lease, no pending journal, no unresolved recovery.
- Persists the first READY boot evidence atomically with the successful recovery transaction.
- Persists first observability evidence atomically with the same bootstrap transaction.
- Normal non-bootstrap recovery remains fail-closed and continues requiring durable readiness/observability evidence.
- Adds `TEST_V363.py` for a clean-first-boot regression.

## Certification
- v1.363 clean bootstrap: PASS
- v1.356: PASS
- v1.353: 4/4 cycles, 8/8 concurrent workers, 4/4 takeovers, 4/4 boot recovery: PASS
- v1.354: 4/4 cycles, 0 leaks: PASS
- v1.355: HEALTHY: PASS
- v1.328: PASS
- v1.335: PASS
- v1.347: 5000/5000: PASS
- v1.357: PASS
- v1.358: PASS
- v1.359: PASS
- v1.361: PASS
- v1.362 Golden Order: PASS
- compileall: PASS
- ZIP integrity: PASS
