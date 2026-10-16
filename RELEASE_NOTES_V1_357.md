# WUNOO v1.357 — Complete Dispatch Invariant Scan

## Purpose
Close the v1.341 completeness gap where the global dispatch/order invariant query used a fixed `LIMIT 500`.

## Changes
- Removed the fixed 500-row limit from the global v1.341 dispatch graph invariant scan.
- Global scans now cover every non-terminal order (`delivered` and `cancelled` are excluded from active recovery validation).
- Order-scoped validation remains unchanged.
- Added v1.357 scan evidence table and API endpoints for explicit full-scan execution/history.
- Kept fail-closed behavior: a mismatch anywhere in the active population blocks the invariant scan.

## Verification
- 501 active orders with the only mismatch at row 501: PASS — mismatch detected.
- 501 active orders repaired: PASS.
- 600 terminal historical orders excluded from active scan: PASS.
- TEST_V341: PASS after updating the historical harness to validate the v1.341 gate directly rather than the later v1.356 boot override.
- TEST_V353: PASS — 4/4 cycles, 8/8 concurrent completions, 4/4 takeovers.
- TEST_V357: PASS.
- `compileall`: PASS.

## Regression note
The legacy TEST_V354/TEST_V355 harness expects persistent readiness evidence from an earlier test sequence. In a fresh isolated DB it fails before exercising the v1.357 change. This is recorded as a test-harness dependency and is not represented as a production PASS.

## Release status
v1.357 changes the invariant-scan behavior and should replace v1.356 only after the broader release regression suite is rerun in the canonical project runtime.
