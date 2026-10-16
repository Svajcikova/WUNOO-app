# WUNOO v1.319 — Dispatch Fence Boot Integrity Gate

- Adds startup/recovery readiness gate for dispatch generation fencing.
- Verifies generation >= 1 for every dispatch job.
- Requires a contiguous audit chain for every generation > 1.
- Verifies current dispatch generation equals the audit-chain head.
- Rejects generation-1 jobs with unexpected fence audits.
- Rejects orphan fence audits whose dispatch job no longer exists.
- Fails closed during application startup if the generation/fence graph is inconsistent.
- Adds `GET /api/v319/policy`.
- Adds `GET /api/v319/ops/dispatch/fence-boot-integrity` for admin/ops_agent.
- Adds regression test `TEST_V319.py`.

Validation:
- V319_OK
- V318_OK
- V317_OK
- V316_OK
- V315_OK
- V314_OK
- V313_OK
- py_compile OK
- compileall OK
