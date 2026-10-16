# WUNOO v1.335 — Dispatch Recovery Resolution Controller

## Purpose
Deterministically resolve dispatch command crash residues only when durable journal, generation-fence, operator-audit and canonical order/dispatch state all prove that the original mutation completed.

## Changes
- Added `ai_dispatch_command_recovery_resolution_v335` audit table.
- Added deterministic per-order and global recovery resolution endpoints.
- Safe finalization of `pending` commands with an already-valid v1.333 postcondition.
- Safe recovery of orphaned `pending` commands only when:
  - the v1.332 generation fence exists and matches journal identity;
  - current generation is exactly expected generation + 1;
  - the exact generation transition is an `operator_reassignment` by the same actor;
  - the canonical order is `courier_assigned`;
  - the canonical dispatch job is `accepted` and courier IDs match;
  - the v1.311 operator override audit is present and invariant-valid.
- Recovery performs no dispatch lifecycle mutation; it only reconstructs durable command/postcondition evidence and finalizes the journal.
- Completed inconsistencies are never auto-rewritten; they remain blocked for manual review.
- Unknown or unprovable journal states remain fail-closed.
- Resolution is idempotent and does not bump dispatch generation a second time.
- Added v1.335 command endpoint that resolves provable crash residue before admitting a new command.

## Endpoints
- `GET /api/v335/policy`
- `POST /api/v335/ai/dispatch/recovery/resolve/{order_id}`
- `POST /api/v335/ai/dispatch/recovery/resolve`
- `POST /api/v335/ai/dispatch/command/{order_id}`

## Verification
- `TEST_V331.py` PASS
- `TEST_V332.py` PASS
- `TEST_V333.py` PASS
- `TEST_V334.py` PASS
- `TEST_V335.py` PASS
- `py_compile` PASS
- `compileall` PASS
- ZIP integrity PASS
