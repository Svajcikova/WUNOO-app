# WUNOO v1.346 — Dispatch Recovery State-Machine Model + Deterministic Fault Injection

- Explicit recovery state model with 10 states.
- Allowed transition matrix; invalid transitions fail closed.
- Deterministic fault injection at 10 boundaries.
- Only the clean path reaches COMMITTED; injected faults end BLOCKED.
- Persistent model-check audit: ai_dispatch_recovery_model_checks_v346.
- API: GET /api/v346/policy
- API: POST /api/v346/ops/dispatch/recovery/state-machine-model
- V345 regression passed.
- py_compile and compileall passed.
