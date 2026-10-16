# WUNOO v1.351 — Multi-Process Production Crash Conformance

## Scope
Extends v1.350 with multiple real OS processes, hard-kill recovery, lease takeover, stale-owner fencing and concurrent recovery workers.

## Scenarios
- CRASH_TAKEOVER: committed recovery owner is SIGKILLed; a second process takes over and completes recovery.
- STALE_OWNER_FENCING: ownership changes and the old fencing token is rejected by the real v338 fence check.
- CONCURRENT_RECOVERY_WORKERS: four independent processes execute the real recovery lifecycle concurrently.
- Final v338 boot recovery gate is executed after all scenarios.

## Verification
- TEST_V351.py PASS
- v350/v349/v348/v347/v346 regression suite PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS
