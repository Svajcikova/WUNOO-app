# WUNOO v1.378 — Cross-version refund cap consistency

## Change
- Legacy `/api/v049/orders/{order_id}/partial-refund` now reserves prior refunds with `pending`, `processed`, or `succeeded` status before calculating remaining refundable balance.
- The v049 reconciliation calculation now includes `processed` and `succeeded` refunds so it agrees with the actual completed cross-version refund paths.
- This closes a cross-version over-refund gap: v064/v120 record processed refunds, while v049 previously counted only succeeded refunds.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V378.py` — PASS; seeds a captured 100 CZK payment and prior processed refund of 60 CZK, then confirms a further 50 CZK refund is rejected with HTTP 409.
- Regression tests V365–V377 and lifecycle tests V357, V358, V359, and V362 — PASS against the patched source; the candidate ZIP was then re-extracted and V378, V377 runtime, and V362 rerun — PASS.
- Live PostgreSQL concurrency integration test not run; no configured PostgreSQL DSN was available.
