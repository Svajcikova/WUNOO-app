# WUNOO v1.380 — Full Refund Cross-Version Cap

## Change
- The main full-refund endpoint `/api/orders/{order_id}/refund` now counts `pending`, `processed`, and `succeeded` refunds before computing remaining refundable value.
- This aligns full refunds with partial-refund paths and prevents a full refund from ignoring refunds recorded by older finance APIs.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V380.py` — PASS; a 60 CZK processed refund against a 100 CZK captured payment leaves only 40 CZK for the full-refund endpoint, with total refunds capped at 100 CZK.
- `TEST_V379.py` — PASS; pending refunds are included in reconciliation and pending total above captured payment is detected.
- `TEST_V378.py`, `TEST_V377.py`, `TEST_V376.py`, `TEST_V375.py` — PASS.
- `TEST_V374.py` through `TEST_V365.py`, `TEST_V357.py`, `TEST_V358.py`, `TEST_V359.py`, and `TEST_V362.py` — PASS.
- PostgreSQL concurrency integration tests remain outstanding; no production deployment or GitHub push is claimed.
