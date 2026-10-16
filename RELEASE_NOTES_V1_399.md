# WUNOO v1.399 Candidate

## Change

Hardened the replay path for `POST /api/v120/finance/orders/{order_id}/payout`.
Previously, any existing payout row could cause the endpoint to return a successful `completed` / `idempotent` response. The endpoint now validates the entire existing payout set before treating a request as a successful replay.

The set must contain exactly the expected beneficiaries (merchant, platform, and courier unless a legacy courier credit already represents that payout), with each row completed, bound to the current settlement, carrying the expected beneficiary identity, and matching the expected amount. Partial, pending, altered, or cross-settlement rows fail closed with HTTP 409 `PAYOUT_LEDGER_INCONSISTENT`.

## Verification performed

- `TEST_V399.py`: valid complete replay passes; partial set, pending status, amount mismatch, beneficiary mismatch, settlement mismatch, and legacy courier double-payment cases are rejected.
- `TEST_V398.py` through `TEST_V389.py`: passed.
- `TEST_V362.py`: golden order lifecycle passed.
- `TEST_V372.py`, `TEST_V377_runtime.py` through `TEST_V387.py`: passed, including SQLite concurrency regressions and payout idempotency lock-order test.
- Python compilation (`python -m compileall -q app`): passed.
- Final ZIP integrity and tests after re-extracting the archive: passed.

## Limitations

This is a local candidate build. Tests ran against the local SQLite test setup; PostgreSQL concurrency/integration, live payment provider behavior, and production deployment were not verified. No GitHub push or deployment was performed.
