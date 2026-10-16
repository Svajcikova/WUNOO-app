# WUNOO v1.377 — Existing payment-intent replay validation

## Change
- Legacy `/api/v049/orders/{order_id}/payment-intent` and `/api/v059/payment/create` now validate the existing payment intent before returning it on a replay.
- Replay is rejected with HTTP 409 if the stored intent amount differs from the current order total or its currency is not CZK.
- This closes a gap where only the concurrent-insert recovery branch validated amount/currency, while the ordinary existing-intent branch returned stale or inconsistent data.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V377.py` — PASS (static route guard for both legacy routes)
- `TEST_V377_runtime.py` — PASS (four runtime cases: amount mismatch and currency mismatch on both routes)
- Regression tests V365–V376 — PASS
- Lifecycle tests V357, V358, V359, V362 — PASS
- Live PostgreSQL concurrent integration test not run; no configured PostgreSQL DSN was available.
