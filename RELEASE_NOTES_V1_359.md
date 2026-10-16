# WUNOO v1.359 — Canonical Pickup API State Guard

## Change
Fixed the `/api/orders/{order_id}/pickup` lifecycle endpoint so it accepts both:
- `courier_assigned` (canonical dispatch/offer flow)
- `assigned` (legacy direct-dispatch flow)

The endpoint now performs the atomic state transition before writing `picked_up_at`, preventing pickup timestamp residue when the state transition is rejected.

## Validation
- v1.359 canonical pickup state test: PASS
- v1.358 regression test: PASS
- Python `compileall`: PASS
- source guard: legacy hard-coded `assigned -> picked_up` call removed

## Release status
CANDIDATE — not fully release-certified because the long-running v1.353/v1.354 chaos suites were not rerun to completion in this candidate run. No failure is being inferred from their transport timeout.

v1.357 remains the last fully release-certified version.
