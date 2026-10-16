# WUNOO v1.326 — Adversarial Crash + Concurrency Dispatch Harness

- Combined process-level stale-command races with hard-kill/restart recovery.
- Four independent stale workers capture an old dispatch generation per iteration.
- A separate process either commits reassignment (generation bump) or is SIGKILLed mid-transaction.
- Stale commands are checked through the real v1.314 generation fence.
- Every iteration runs the v1.271 boot reconciliation plus v1.325 recovery matrix and v1.319 fence integrity.
- Test-only: no production dispatch assignment mutation is introduced.
- Added `/api/v326/policy` and `/api/v326/ops/dispatch/adversarial-chaos-runs` for policy/run evidence.
