# WUNOO v1.340 — Dispatch Recovery Full-System Crash Matrix

Adds a full-system recovery integrity harness spanning durable lease ownership, stale-owner fencing, takeover, journal reconciliation, and boot readiness.

## Highlights
- Durable SIGKILL crash scenario against a recovery lease owner.
- Expired lease takeover with strictly increasing fencing token.
- Explicit stale-owner fencing after takeover.
- Recovery resolution and v1.333 postcondition/journal integrity verification in the same recovery boundary.
- Immutable crash-matrix audit table `ai_dispatch_recovery_crash_matrix_v340`.
- New policy endpoint: `GET /api/v340/policy`.
- New matrix runner: `POST /api/v340/ops/dispatch/recovery/full-crash-matrix`.
- New history endpoint: `GET /api/v340/ops/dispatch/recovery/full-crash-matrix/history`.
- Fail-closed behavior is preserved; no stale-owner or duplicate recovery mutation is permitted.

## Verification
- V331–V340 regression suite passed.
- SIGKILL owner crash + lease takeover passed.
- Stale owner rejected after fencing-token change.
- Journal/postcondition integrity passed.
- Duplicate recovery mutations: 0.
- Unresolved provable residues: 0.
- `py_compile`: PASS.
- `compileall`: PASS.
- ZIP integrity: PASS.
