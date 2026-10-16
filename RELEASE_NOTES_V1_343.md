# WUNOO v1.343 — Dispatch Recovery Crash-Point Matrix

## Scope
Systematic SIGKILL testing of the v1.342 recovery transaction boundary.

## Crash points
- BEFORE_LOCK
- AFTER_LOCK
- AFTER_LEASE
- AFTER_PRE_GATE
- AFTER_RECOVERY
- AFTER_POST_GATE
- BEFORE_COMMIT

## Guarantees verified
- SQLite transaction rollback after SIGKILL
- no partial journal/recovery evidence
- no active recovery lease left after crash
- database remains usable after every crash point
- recovery transaction remains fail-closed
- migration chain includes v1.343

## Tests
- V342_OK
- CRASH_POINTS 7
- ROLLBACK_VERIFIED 7
- ACTIVE_LEASE_AFTER_CRASH 0
- POST_CRASH_DB_USABLE 1
- V343_OK
- py_compile PASS
- compileall PASS
- ZIP integrity PASS

## SHA-256
ZIP: `3e7b87928b75e77cb06b4d687ccb17ef06c9ec563375a68517c10189e10be524`
app/main.py: `aa0f423c52df8f7b95388d84599c301d8358f17854ae95210673c05d71b0a1f1`
