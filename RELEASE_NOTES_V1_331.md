# WUNOO v1.331 — Dispatch Command Payload Idempotency Hardening

- Binds an idempotency key to a deterministic SHA-256 hash of the exact command payload.
- Same key + same actor/order/type + same payload replays the completed journal result.
- Same key + different payload is rejected with HTTP 409 `DISPATCH_REQUEST_KEY_PAYLOAD_CONFLICT`.
- Persists payload hash on `ai_dispatch_command_journal_v312`.
- Records rejected idempotency conflicts in `ai_dispatch_idempotency_conflicts_v331`.
- Adds `/api/v331/policy` and `/api/v331/ai/dispatch/idempotency-conflicts`.
- Concurrency test: 8 simultaneous identical requests => 1 mutation + 7 replays; conflicting replay => 409; 0 double mutations.
