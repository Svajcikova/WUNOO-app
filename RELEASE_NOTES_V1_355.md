# WUNOO v1.355 — Recovery Integrity Health Gate

## Summary
Adds a single fail-closed production recovery health gate over the recovery integrity signals established in v1.346-v1.354.

## Gate signals
- active recovery leases must be zero at the observed safe point
- pending dispatch journal entries must be zero
- unresolved recovery classifications must be zero
- boot recovery gate must report ready
- latest recovery observability run must be healthy
- fencing token is exposed for continuity/monotonicity evidence

## Behavior
- returns `HEALTHY` only when all required invariants pass
- returns `BLOCKED` with explicit reason codes when any invariant fails
- persists every gate decision for audit/history
- remains non-mutating with respect to dispatch recovery state
- exposes policy, gate execution and history endpoints

## Verification
- TEST_V355: PASS
- fail-closed synthetic pending-journal test: PASS
- TEST_V354: PASS (4 cycles, 0 failures, 0 leaks)
- TEST_V347: PASS (5000 cases, 0 failures)
- TEST_V346: PASS
- py_compile: PASS
- compileall: PASS
- ZIP integrity: PASS
