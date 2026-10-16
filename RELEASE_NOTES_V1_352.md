# WUNOO v1.352 — Full Adversarial Multi-Process Recovery Chaos

## Scope
Combines the v1.347 property model, v1.348 differential testing, v1.349 production conformance, v1.350 crash-point conformance and v1.351 multi-process conformance into a deterministic adversarial harness.

## Coverage
- 3 deterministic seeds.
- 4 OS processes per seed.
- One real SIGKILL crash at a deterministic recovery phase.
- Durable lease takeover after the crash boundary.
- Real fencing/stale-owner rejection.
- Two concurrent post-takeover recovery workers.
- Boot recovery gate after the adversarial sequence.
- Final lease/journal cleanliness checks.

## Verification
- TEST_V352.py PASS
- v351/v350/v349/v348/v347/v346 regression suite PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS
