# WUNOO v1.320 — Dispatch Lifecycle Chaos Harness

v1.320 adds an end-to-end concurrency regression harness for the dispatch generation fence.

## Coverage
- canonical order + dispatch job pair seeded in `courier_assigned` / `accepted`
- concurrent stale courier worker and operator reassignment
- stale worker attempts a conditional lifecycle mutation using the observed generation
- reassignment increments `dispatch_generation` and changes the canonical courier
- stale mutation must be rejected atomically
- final order/job courier IDs and statuses must remain converged
- v1.319 generation-fence integrity must remain healthy after the race
- audit must contain the expected `1 -> 2` generation transition

## Safety
This release adds a deterministic test harness only. It does not introduce a production endpoint that can mutate dispatch state.
