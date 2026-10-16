# WUNOO v1.311 — Operator Dispatch Override & Safe Reassignment

- Adds audited ops/admin courier reassignment for orders in `courier_assigned`.
- Serializes through the canonical courier lifecycle transaction boundary.
- Reuses the existing unique `dispatch_jobs.order_id` row to avoid violating the one-job-per-order invariant.
- Updates order and dispatch job atomically to the replacement courier.
- Adds immutable SHA-256 evidence and operator override history.
- Blocks terminal/incompatible lifecycle states and unavailable couriers.
- Fail-closed post-condition requires `orders.courier_assigned` and `dispatch_jobs.accepted` with matching courier IDs.
