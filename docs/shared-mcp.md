# Qualify a shared MCP service

Use this procedure for an authorized shared-service change or acceptance review. Keep the existing MCP owner and [verification](verification.md) route.

## Identify server and clients

Record the pinned server and client versions, actual server instance, transport, authentication boundary, advertised capabilities and scoped client or session identities. Read the installed implementations' current protocol guidance before choosing probes. Do not infer that every server supports resources, notifications, cancellation or resumable sessions.

Name intentionally shared state and state that belongs to a client, project, device or account. Preserve existing grants without displaying tokens. Saved configuration and a discovered catalog are prerequisites, not evidence that a running client adopted the new service.

## Exercise independent clients

1. Connect two authorized clients with distinguishable owned inputs. Verify that each receives the intended project or device state and permitted tools.
2. Run concurrent bounded operations. Check routing of responses, progress, errors and advertised notifications or resources. A matching request number in separate sessions must not confuse ownership.
3. Cancel an owned operation or close one client through the supported contract. Observe the other client's ongoing operation and shared service independently.
4. Exercise idle shutdown and reconnect where supported. Verify the actual instance and restored scope, including a previously cached client configuration.
5. Reconcile surviving sessions before replacing a service or retrying an uncertain effect. Account for background and nonforeground clients and live dependent work before declaring the last client. Foreground visibility does not establish that a service is unused. Retire an old instance only within current authority and after resolving unknown dependencies.

Do not introduce a new gateway or daemon merely to satisfy this procedure. If the implementation cannot isolate required mutable state, return that defect to its owner. A skill cannot supply the missing runtime boundary.

## Return evidence and acceptance

Return the server and client identities, capability and state map, configuration and adoption receipts, concurrent operation results, cancellation and reconnect outcomes, and unresolved dependencies. Keep configuration, protocol acceptance and resource improvement claims separate.

| Case | Required result |
|---|---|
| Normal | Two clients use the reviewed shared instance and receive correctly scoped results. Reconnecting a client restores the intended scope through the supported contract. |
| Reject | Cancelling client A's operation cannot cancel client B's work or expose B's project state to A. Preserve any counterexample as a failure. |
| Lifecycle | Closing the last client follows the declared idle policy. Closing one of several clients preserves the remaining clients and service. |
| Reject teardown | The foreground UI is empty while a background client or dependent operation remains. The service cannot qualify as unused or safe to retire. |
| Incomplete | A configuration file changed, but an existing client has not adopted it. That client's acceptance remains open. |

Record unsupported optional capabilities as outside the declared contract. Missing required behavior remains blocked or failed according to the observed cause. A short idle observation alone does not prove sustained resource savings.
