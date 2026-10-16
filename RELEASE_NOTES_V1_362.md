# WUNOO v1.362 — Golden Order API Hardening

## Change
Fixed the canonical `/api/orders/{order_id}/pickup` endpoint to inspect the cursor returned by the timestamp UPDATE instead of the DB connection wrapper. The previous implementation could complete the state transition and then raise an AttributeError before commit when invoked through the real endpoint/function path.

## Regression coverage
Added `TEST_V362.py` covering the complete Golden Order lifecycle on a clean database:
- captured payment
- merchant accept
- merchant ready
- courier assignment
- canonical pickup
- start delivery
- delivery completion
- exactly one settlement
- courier earnings consistency
- full refund capped after courier payout
- duplicate refund rejection
- event cardinality

## Validation
v1.356, v1.357, v1.358, v1.359, v1.361, v1.328, v1.335, v1.347 and v1.362 smoke/conformance tests pass; compileall passes.

Long-running historical chaos suites v1.353/v1.354 are not claimed as newly re-certified in this candidate.
