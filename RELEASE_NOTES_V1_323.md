# WUNOO v1.323 — Process-Level Full Dispatch Lifecycle Chaos

- Added v1.323 test-only lifecycle chaos policy and run history table.
- Hardened legacy v1.311 operator reassignment so it increments `dispatch_generation` before audit completion.
- Added process-level race test covering stale courier command, operator reassignment, redispatch, recovery reopen, and final delivery.
- Required final canonical pair: `orders=delivered/cB`, `dispatch_jobs=delivered/cB` with continuous generation fence audit.
- No production dispatch mutation endpoint added by this release.
