# WUNOO v1.347 — Dispatch Recovery State-Machine Property-Based Chaos

- Added deterministic property-based state/event generation against the v1.346 recovery model.
- 5,000 deterministic cases, sequences up to 24 events.
- Added safety checks for invalid transition acceptance, commit without full path, stale writes, and double commit.
- Added bounded persistent evidence table `ai_dispatch_recovery_property_checks_v347`.
- Added `/api/v347/policy` and `/api/v347/ops/dispatch/recovery/property-chaos`.
- Migration chain extended through v1.347.

Validation:
- TEST_V347: PASS — 5000 cases, 0 failures, 0 invalid transition accepts, 0 stale mutations, 0 double commits.
- TEST_V346: PASS.
- py_compile: PASS.
- compileall: PASS.
- ZIP integrity: PASS.
