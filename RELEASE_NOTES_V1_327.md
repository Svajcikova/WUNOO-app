# WUNOO v1.327 — Multi-Order Dispatch Adversarial Isolation

## Scope
Extends the v1.326 adversarial dispatch harness from one order to multiple concurrent orders. This release is test/hardening focused and does not introduce a new production dispatch mutation path.

## Coverage
- 3 simultaneous dispatch jobs/orders
- 2 stale worker processes per order
- per-order generation fencing
- reassignment/generation bump on each order
- one hard-kill during reassignment transaction
- post-crash boot reconciliation
- post-recovery committed generation bump
- cross-order isolation verification
- canonical `orders ↔ dispatch_jobs` consistency

## Result
- V327_OK
- 3 orders verified
- 6/6 stale commands rejected
- 0 stale mutations
- 1 hard-kill
- 2 boot/recovery gates
- 3/3 cross-order isolation checks passed
- py_compile OK
- compileall OK
- ZIP integrity OK
