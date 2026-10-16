# WUNOO v1.376 — Legacy payment-intent concurrency recovery

## Change
- Legacy `/api/v049/orders/{order_id}/payment-intent` and `/api/v059/payment/create` now use a savepoint around payment-intent insertion.
- If another request wins the database `UNIQUE(order_id)` race, the losing request rolls back only its savepoint, reads the existing intent, verifies its amount against the order, and returns the existing intent instead of surfacing an avoidable server error.
- If no winning intent exists or its amount differs, the request fails closed.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V376.py` — PASS (static regression guard for both legacy creation routes)
- Prior regression suite V365–V375 and lifecycle tests V357, V358, V359, V362 — PASS
- Live PostgreSQL concurrent integration test not run: no configured production DSN was provided.
