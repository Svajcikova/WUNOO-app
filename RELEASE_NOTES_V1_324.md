# WUNOO v1.324 — Dispatch Lifecycle Crash/Hard-Kill Chaos

## Scope
Process-level hard-kill validation of dispatch generation fencing and SQLite transactional rollback.

## Covered crash points
- operator-style reassignment transaction
- redispatch/invalidation transaction

## Guarantees verified
- SIGKILL before commit rolls back the whole transaction
- `dispatch_generation` is not partially advanced
- order/dispatch job pair remains unchanged
- SQLite becomes available to a fresh process after the killed worker exits
- v1.319 fence integrity remains valid after recovery
- fail-closed generation audit state is preserved

## Safety
This release adds a chaos/regression harness only. It does not enable automatic production mutation or bypass existing lifecycle gates.
