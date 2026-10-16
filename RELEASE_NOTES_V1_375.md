# WUNOO v1.375 — Checkout confirmation concurrency guard

## Change
- Added PostgreSQL `SELECT ... FOR UPDATE` row locking before quote status checks in all three checkout confirmation routes: `/api/v058/checkout/confirm`, `/api/v283/checkout/confirm`, and `/api/v139/checkout/confirm`.
- This serializes confirmations of the same quote so a waiting transaction can observe the already-confirmed order instead of independently creating another order.
- Locking is backend-gated; SQLite retains its compatible query path.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V375.py` — PASS (regression guard covers all three checkout confirmation routes)
- Regression tests V365–V374 — PASS
- Additional lifecycle tests V357, V358, V359, V362 — PASS
- ZIP integrity check — PASS

## Scope / caveat
- The regression guard verifies the code path and lock ordering; a live PostgreSQL concurrent integration test was not run in this environment.
