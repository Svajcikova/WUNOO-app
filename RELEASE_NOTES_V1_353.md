# WUNOO v1.353 — Recovery Durability & Long-Run Soak

## Scope
Long-run deterministic durability test combining crash points, SIGKILL, durable lease takeover, concurrent recovery workers, boot recovery and DB cleanliness checks.

## Coverage
- 4 deterministic cycles.
- 7 deterministic crash points selected by seed per cycle.
- Real SIGKILL of recovery worker.
- Durable lease takeover after forced expiry.
- 2 concurrent post-takeover recovery workers per cycle.
- Boot recovery gate after every cycle.
- Pending-journal and lease cleanliness checks.
- Fencing-token monotonicity check across the full run.

## Verification
- TEST_V353.py PASS
- v352 regression PASS
- v351/v350/v349/v348/v347/v346 regression PASS
- py_compile PASS
- compileall PASS
- ZIP integrity PASS
