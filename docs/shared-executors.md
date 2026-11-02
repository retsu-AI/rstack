# Qualify shared executor lifecycles

Use the existing CI or execution owner to qualify a declared shared capacity. This procedure checks an implementation. It does not create a scheduler, capacity policy or supervisor.

## Fix the qualification scope

Record the executor revision, host or pool identity, declared capacity units, authorized workloads, trust classes and resource limits. Enumerate actual admission paths, including repository workflows, registered runners and local hooks when used. Two logical queues can consume the same physical capacity.

Keep original setup, source, required secrets and authoritative state distinct from rebuildable worker or job output. Record retention and cleanup ownership without copying secret values.

## Trace a bounded job

1. Bind the semantic job, attempt, reservation and owning runner. Verify how the existing system admits work and prevents competing entrypoints from allocating the same constrained resource.
2. Observe a useful operation on the requested executor. A queued job, active label or successful launcher return does not prove execution.
3. Inspect the exact stop operation and wrapper, including timeout and escalation. A cancellation request, stopped parent, ended child tree and released reservation are separate states.
4. Exercise authorized failure and restart cases with owned disposable work. Reconcile surviving attempts and resources before a retry. Preserve original identity on an uncertain result.
5. Check cleanup failure and interrupted cleanup. Capacity still held by a live or unaccounted resource remains reserved. Repeated cleanup must not remove another job's state or original setup.
6. Verify that restart recovers pending work and capacity accounting through the existing authoritative state. Return a concrete defect to its implementation owner.

Choose cases proportional to the requested qualification. Do not stop unrelated jobs, delete unknown output, change trust boundaries or purchase capacity to obtain a cleaner test.

## Return evidence and acceptance

Return an admission-path map, declared capacity and trust boundaries, job and attempt receipts, child-resource ownership, cleanup result, retained artifacts and remaining reservations. Use [exact-subject verification](verification.md) and the existing [coordination](coordination.md) owner.

| Case | Required result |
|---|---|
| Normal | Two permitted jobs share the declared capacity within its limits. Each completes useful work, and the actual resources and reservations become available for reuse. |
| Reject | Concurrent arrivals through different entrypoints cannot exceed the same declared constrained capacity. An admission response alone cannot satisfy this check. |
| Recovery | Cancel or restart one owned job. Its children and reservation reach the declared terminal state, another job survives, and source and setup remain intact. |
| Incomplete | Cleanup returns but resource ownership is unknown. Capacity release stays unverified and no replacement attempt assumes it is free. |

A passing isolated fixture does not establish all production admission paths or trust classes. List the exact covered paths and remaining cases.
