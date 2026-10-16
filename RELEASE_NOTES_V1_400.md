# WUNOO v1.400 Candidate

## Change

Fixed the v1.062 settlement formula for low-value or invalid order totals. The previous code clamped a negative merchant payout to zero but still recorded the full 18% platform fee and 39 CZK courier amount, which could create credits greater than the order gross while marking the settlement completed.

The route now computes the breakdown through `_v400_compute_v062_settlement` before inserting the settlement or ledger entries. Non-finite, non-positive, boolean, malformed, or below-minimum amounts fail closed with HTTP 409. With the current fixed 18% fee and 39 CZK courier component, the minimum valid gross is 47.56 CZK. Valid breakdowns are checked for cent-level balance.

## Verification performed

- `TEST_V400.py`: exact lower bound, nine invalid/too-small cases, and five valid amounts passed.
- Existing v1.399 payout replay test and v1.398–v1.389 webhook/refund regressions passed.
- Python compilation and final ZIP integrity passed.

## Limitations

Local candidate only. Tests ran with SQLite/local test setup; PostgreSQL integration/concurrency, live payment provider behavior, and production deployment were not verified. No GitHub push or deployment was performed.
