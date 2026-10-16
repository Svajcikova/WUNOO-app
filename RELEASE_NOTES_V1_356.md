# WUNOO v1.356 — Recovery Lifecycle Health Gate

## Summary
Integrates the recovery health gate directly into the dispatch recovery lifecycle.

## Lifecycle guarantees
- `HEALTHY/BLOCKED` gate runs before recovery.
- Gate runs again immediately before commit.
- The current recovery owner's lease is excluded from the foreign-active-lease check.
- Gate evidence is written on the same database transaction as recovery work.
- A `BLOCKED` gate cannot reach commit; the transaction is rolled back.
- Fail-closed behavior is preserved.
- Health snapshots are observational and never recursively start another recovery cycle.

## Verification
- TEST_V356 integration: PASS
- current-lease exclusion: PASS
- PRE_RECOVERY HEALTHY path: PASS
- PRE_COMMIT HEALTHY path: PASS
- successful commit path: PASS
- BLOCKED path: PASS
- blocked evidence rollback: PASS
- TEST_V355 regression: PASS
- TEST_V354 regression: PASS (4 cycles, 0 failures, 0 leaks)
- TEST_V353 regression: PASS (4 cycles, 0 failures)
- TEST_V347 regression: PASS (5000 cases, 0 failures)
- TEST_V346 regression: PASS
- compileall: PASS
- ZIP integrity: PASS
