# WUNOO v1.336 — Dispatch Recovery Boot Gate & Automatic Startup Resolution

## Purpose
Make dispatch command recovery a hard startup readiness gate. After a process restart, WUNOO first resolves only crash residues backed by durable evidence; unresolved or inconsistent journal states fail closed before traffic is admitted.

## Changes
- Added `ai_dispatch_recovery_boot_v336` boot evidence/audit table.
- Added `_v336_boot_recovery_gate()` startup gate.
- Startup automatically invokes v1.335 recovery resolution before serving traffic.
- Proven crash residues can be finalized without a second dispatch mutation.
- Generation is never bumped a second time during recovery.
- Any remaining pending, unknown, or completed-without-valid-postcondition command blocks startup.
- Added `/api/v336/policy`.
- Added `/api/v336/ops/dispatch/recovery/boot-gate`.
- Added `/api/v336/ops/dispatch/recovery/boot-history`.
- Hardened migration chain by explicitly including `migrate_v331` before v1.332, because v1.332 depends on the v1.331 journal payload column.

## Verification
- V331 regression: PASS
- V332 regression: PASS
- V333 regression: PASS
- V334 regression: PASS
- V335 regression: PASS
- V336 boot gate: PASS
- `py_compile`: PASS
- `compileall`: PASS
- ZIP integrity: PASS

## V336 test summary
- `BOOT_EMPTY_READY 1`
- `AUTOMATIC_CRASH_RESOLUTION 1`
- `NO_DOUBLE_GENERATION_BUMP 1`
- `UNPROVABLE_ORPHAN_BLOCKS_BOOT 1`
- `UNRESOLVED_MUTATIONS 0`
