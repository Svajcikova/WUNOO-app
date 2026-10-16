# WUNOO v1.382 Candidate — payout idempotency lock ordering

## Change
- The v1.20 payout endpoint now acquires the canonical PostgreSQL order row lock before reading the idempotency command log.
- This closes a same-key race where concurrent requests could both observe a cache miss, serialize later on the order lock, and the second request could attempt a duplicate unique command-log insert instead of replaying the committed response.
- Missing order is now rejected explicitly when the PostgreSQL row lock is acquired.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V382.py` — PASS (source-order invariant plus SQLite sequential replay: 3 payout rows and 1 command-log record; replay response identical)
- `TEST_V381.py` — PASS
- `TEST_V380.py` — PASS
- PostgreSQL live concurrency integration was not run in this environment; no PostgreSQL server/driver is configured.

## Release status
Candidate only; not production-approved. No GitHub push or deployment performed.
