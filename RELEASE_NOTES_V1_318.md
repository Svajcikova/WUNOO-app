# WUNOO v1.318 — Dispatch Fence Integrity Gate

- Adds operational integrity verification for dispatch generation fencing.
- Verifies audit generation continuity and current-generation parity.
- Adds `GET /api/v318/ops/dispatch/integrity` (admin/ops_agent), fail-closed with HTTP 503 on integrity failure.
- Adds `GET /api/v318/policy`.
- Adds startup migration/index `migrate_v318`.
- Adds `TEST_V318.py` with positive and tampered-audit fail-closed checks.
