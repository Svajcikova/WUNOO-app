# WUNOO v1.381 — Finance Concurrency Regression Coverage

## Change
- Adds `TEST_V381.py`, a runtime concurrency regression test for the existing SQLite serialization guarantees on legacy cross-version refunds and settlement creation.
- Concurrent partial refunds with different requests must not exceed the captured payment: one 60 CZK refund against a 100 CZK payment succeeds and the competing request is rejected with HTTP 409.
- Concurrent settlement requests using distinct idempotency keys must return the same settlement ID and create exactly one settlement row and four ledger entries.
- No application behavior changed in this release candidate; the new version adds a repeatable regression test based on the current candidate's verified locking logic.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V381.py` — PASS on SQLite runtime with two concurrent worker threads.
- `TEST_V380.py` through `TEST_V374.py`, `TEST_V373.py` through `TEST_V365.py`, and `TEST_V362.py` — PASS.
- PostgreSQL concurrency integration remains outstanding because no PostgreSQL server/client or Python driver is configured in this environment. No production deployment or GitHub push is claimed.
