# WUNOO v1.361 Candidate

## Dispatch cancellation fencing

v1.361 closes the consistency gap between canonical order cancellation and the active dispatch job.

### Change
- When an order is cancelled, active dispatch jobs for that order (`offered`, `accepted`, `picked_up`, `redispatched`) are cancelled in the same database transaction.
- The dispatch generation is incremented before job cancellation, fencing stale courier/worker commands.
- The courier assignment is cleared atomically.
- A `dispatch_job_cancelled` event is emitted in the same transaction.
- If the dispatch mutation cannot be completed atomically, the cancellation transaction fails closed.

### Validation
- `TEST_V361.py` — PASS
- stale dispatch generation after cancellation — PASS
- `TEST_V358.py` — PASS
- `TEST_V359.py` — PASS
- `compileall` — PASS

### Release status
CANDIDATE. This candidate is based on the v1.359 workspace available in the current runtime. The previously discussed v1.360 artifact is not present in the current workspace, so no unverified v1.360 changes are claimed here.
