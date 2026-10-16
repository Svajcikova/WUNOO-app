# WUNOO v1.345 — Dispatch Recovery Full Adversarial State-Machine Chaos

## Purpose
Combine concurrent recovery workers, lease/fencing, invariant gates, randomized event ordering and SIGKILL into one deterministic adversarial harness.

## Changes
- Added ai_dispatch_recovery_adversarial_chaos_v345 audit table.
- Added v1.345 policy and full adversarial chaos harness.
- Six iterations with four concurrent recovery workers.
- Four SIGKILL scenarios covering lease, pre-gate, post-resolution and pre-release crash paths.
- Randomized event ordering with deterministic seed.
- Final journal, lease, invariant and residue checks.
- Added /api/v345/policy.
- Added /api/v345/ops/dispatch/recovery/full-adversarial-chaos.

## Verified
- ADVERSARIAL_ITERATIONS 6
- SIGKILL_SCENARIOS 4
- STALE_MUTATIONS 0
- DUPLICATE_RECOVERY_MUTATIONS 0
- PARTIAL_EVIDENCE 0
- UNRESOLVED_PROVABLE_RESIDUES 0
- V345_OK
- v1.344 regression PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS
