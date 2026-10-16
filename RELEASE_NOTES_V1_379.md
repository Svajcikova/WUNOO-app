# WUNOO v1.379 — Pending Refund Reconciliation

## Change
- Legacy v049 payment reconciliation now includes refunds in `pending`, `processed`, and `succeeded` states, matching the refundable-balance calculation.
- The v112 payment reconciliation gate now counts pending refunds when checking whether total refunds exceed captured payment value. A pending refund reserves capacity and must not be ignored by integrity checks.

## Verification
- `python -m compileall -q app` — PASS
- `TEST_V379.py` — PASS; confirms a 30 CZK pending refund appears in v049 reconciliation and a 110 CZK pending refund against a 100 CZK captured payment is detected by the v112 refund-bound gate.
- `TEST_V378.py`, `TEST_V377.py`, `TEST_V376.py`, `TEST_V375.py` — PASS.
- Archive integrity verified after packaging.
- Live PostgreSQL concurrency integration tests have not been run; no production deployment or GitHub push is claimed.
