# WUNOO v1.330 — Multi-Order Process Chaos Hardening

## Scope
Combines multi-order isolation, process-level stale-command fencing, reassignment generation bumps, and a hard-killed transaction in one adversarial harness.

## Production/runtime additions
- v1.330 policy endpoint: `GET /api/v330/policy`
- v1.330 Ops integrity endpoint: `GET /api/v330/ops/dispatch/multi-order-chaos`
- v1.330 records adversarial run evidence in `dispatch_multi_order_chaos_runs_v330`.
- Integrity is fail-closed.

## Test scenario
- 3 concurrent orders.
- 3 stale process workers capture generation 1.
- One independent process is SIGKILLed while holding a generation-bump transaction.
- After rollback/restart, committed reassignment bumps generation and changes courier on all three orders.
- Stale workers then attempt to mutate with generation 1.

## Result
- 3/3 stale attempts rejected.
- 0 stale mutations.
- 1 hard kill with transactional rollback.
- 1 post-crash recovery.
- 0 cross-order failures.
- 0 fence failures.

## Validation
- `TEST_V330.py`: `V330_OK`
- `python -m compileall -q app`: PASS
- `python -m py_compile app/main.py TEST_V330.py`: PASS
- ZIP integrity: PASS
