# WUNOO v1.358 — Canonical Pickup State Alignment

## Change
- Align the canonical dispatch state `courier_assigned` with the order state machine.
- Permit the valid transition `courier_assigned -> picked_up`.
- Keep the legacy `assigned -> picked_up` transition intact.
- Allow `dispatch_pending -> courier_assigned` explicitly in the state map.
- No recovery, fencing, invariant-scan, payment, or settlement logic was changed.

## Regression evidence
- TEST_V358: PASS
- TEST_V356: PASS
- TEST_V357: PASS
- Python compileall: PASS

## Not newly certified in this run
- Long-running TEST_V353 / TEST_V354 full runs hit the execution transport timeout.
- They are therefore NOT marked PASS for this v1.358 candidate.
- Existing v1.357 release certification remains unchanged.

## Release status
CANDIDATE — not fully release-certified.
