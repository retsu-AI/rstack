# Plan and independently verify bounded parts

Use the existing outcome and register. Scale the written plan to the request. For multipart engineering work, retain the following before implementation or dispatch.

## Plan and feature inventory

Record the user journey, intended result, selected design and shared contracts. Name deliberate omissions, constraints, permissions, dependencies, failure/recovery behavior and the exact source being changed. Do not invent a second provider, adapter or extension merely to demonstrate generality.

Assign stable feature IDs. List each main feature and each extension explicitly, with its parent feature, required or optional disposition, acceptance IDs, observable expected result, rejecting conditions and evidence method. An extension requested by the user is required unless the user defers it. Keep deferred obligations visible in the original outcome.

Turn the inventory into an ordered checklist using [the plan template](../templates/execution-plan.md). Each row names its prerequisites, worker, independent verifier, owned paths, checks and stop condition. Order assertions by actual prerequisites; split a check that otherwise creates a dependency cycle. Parallelize only disjoint work whose contracts are stable. Reserve time for integration and verification.

## Manager and verifier pairs

Use the existing manager (M), an independent manager verifier (VM), and a worker/verifier pair (W1/V1, W2/V2, ...) for each bounded part. These are responsibilities, not a new dispatch system. Keep the user's agent limits and the host's concurrency limit; record queued assignments as queued. An existing capable worker may own successive parts, but every verdict must come from a non-author context. One person or agent cannot accept its own work as independent verification. A different role name does not establish independence or a different model family.

Before workers start, VM reviews the plan, feature/checklist coverage, acceptance and rejecting conditions, dependency order, role separation, permitted checks and correction budget. Record its verdict and any unresolved findings. A missing verifier leaves the independent gate pending; do not simulate a verdict or silently replace it with self-review. Continue independent authorized preparation around a blocked gate.

M owns canonical plans and integration. Workers own the assigned production changes and separate reports. Verifiers receive original criteria, exact source, raw artifacts and permitted actions; forward-test evaluators do not receive expected answers or the author's conclusions. They may create an isolated test harness, but must not fix the production subject they then accept. Return a finding to its worker. A verifier-tool repair is a distinct changed subject requiring independent review.

## Per-part acceptance and correction

Keep implementation, worker checks, independent verification, integration and final acceptance separate. For every acceptance ID, record:

| Field | Required observation |
|---|---|
| Subject | Repository/base/head, or content revision; dirty delta or manifest when relevant |
| Scope | Feature/extension, changed paths, requirement and proof/runtime boundaries |
| Execution | Actor, environment, tool/configuration, invocation, timestamp and raw evidence reference |
| Result | Literal expected and observed behavior, verdict, findings and coverage limits |
| Independence | Non-author reviewer identity and actual review context; model/family only if observed |

Use PASS for an observed satisfied criterion, FAIL for an observed violation, BLOCKED for a missing prerequisite/access or unusable verifier, and NOT OBSERVED for a specified natural event that did not occur in a bounded observation window. A required check that was not run stays NOT RUN. None of the latter states counts as PASS. Preserve partial passing scope without accepting the entire feature.

Define the correction attempt/time budget before the loop. W repairs a concrete finding within its paths, records the changed revision and returns raw evidence; V repeats the affected checks on that revision. Changed bytes stale affected verdicts. Reuse unchanged scoped evidence only with explicit identity and relevance. Repeated deterministic failure requires a changed cause or design decision. At the budget or authority boundary, preserve artifacts and record the exact blocker, owner and resumption trigger. Do not create another worker to repeat the same pending unit.

## Integration acceptance

M incorporates independently accepted parts in dependency order and records which source revisions were integrated. Check the actual combined artifact after each material integration. An accepted extension on a separate branch does not establish integrated behavior.

VM separately reviews the final combined revision against every required main feature and extension, including interactions and applicable failure, concurrency, cancellation and recovery paths. Keep source review, local checks, formal claims, live runtime observations and delivery distinct. Close the original outcome only when its required checklist and delivery are accepted; otherwise identify each open part and its next executable step.

The existing record validator checks its documented schema. This plan, role assignment and reviewer independence require actual evidence; a consistent exported record does not enforce or authenticate them.
