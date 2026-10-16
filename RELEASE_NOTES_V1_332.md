# WUNOO v1.332 — Idempotency + Generation Cross-Fencing

- New dispatch commands require the current `X-Dispatch-Generation` after lifecycle locking.
- Exact completed idempotent replays remain non-mutating even after the dispatch generation changes.
- Replays report `replay_generation_stale=true` when the original generation differs from the current generation.
- Same idempotency key with a new payload remains rejected by v1.331 payload hashing.
- New generation-fenced commands with a stale generation are rejected before mutation.
- Current-generation commands can proceed normally.
- Added `ai_dispatch_generation_fence_v332` audit table and `/api/v332/policy`, `/api/v332/ai/dispatch/command/{order_id}`, `/api/v332/ai/dispatch/generation-fences`.

Validation:
- V331_OK
- V332_OK
- py_compile OK
- compileall OK
