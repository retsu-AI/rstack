# Formal architecture example

Use this bounded example when late asynchronous work can outlive disconnect/reconnect. It illustrates the existing [formal verification](formal-verification.md) and [Pele diagram](diagrams.md) contracts. It is not an implementation of a client, service or scheduler.

## Criterion and model

R1 requires every operation to be rejected while disconnected.
R2 requires a token issued in generation n to remain rejected after disconnect and reconnect advance the state to n+1.
R3 permits the current generation token while connected.

The model contains a natural-number generation and a connected flag. Disconnect increments generation and clears the flag. Reconnect sets the flag without decrementing generation. Acceptance requires connected and matching generation. Natural numbers do not wrap; an implementation with bounded integers needs separate overflow handling.

See the [editable diagram source](../templates/lease-state.mmd) and [Lean source](../templates/lease-state.lean). The diagram's eligible-operation edge means the predicate permits work. It does not prove that an effect occurred.

| Criterion | Diagram obligation | Lean obligation | Implementation evidence still required |
|---|---|---|---|
| R1 | Disconnected has no eligible-operation path | disconnected_rejects | Every real consumer checks the flag before effects |
| R2 | Disconnect advances generation; old token cannot apply after reconnect | stale_token_rejected | Token issuance, generation persistence and checking occur at the actual dispatch boundary |
| R3 | Current connected token is eligible | current_token_accepted | Real operation succeeds under its other authorization/preconditions |

Review the formal statement and missing boundaries independently before running a prover. This model omits account identity, real cancellation, resource cleanup, concurrency, storage, fairness and liveness. It does not prove a program calls the predicate atomically before effects. Add those obligations only when they are part of the actual requirement.

## Execute and inspect

Use the target project's pinned toolchain. When a suitable Lean toolchain is already available, run its Lean executable on the exact example source and retain version, command, output and file digest. The module prints theorem axioms. Apply the existing admissions/trust checks rather than accepting a file or zero exit in isolation.

For Pele, read the installed pinned version and render the exact Mermaid source using its supported API. Retain the SVG and renderer/options, then inspect actual pixels and compare each required node/edge with the model. A source parse, render receipt and visual inspection are separate results. No render or proof is established by this reference.

Challenge R2 by changing disconnect to retain generation. The stale-token theorem should then fail, and an old token would satisfy the model after reconnect. Challenge R1 by removing the connected condition. The disconnected theorem should fail. Keep these mutations isolated from the accepted source and report actual results rather than predicted failures as executed tests.

## Optional remote and Rust checks

Aristotle remains disabled unless selected and separately authorized. Follow the existing version/language, upload-scope, budget and existing-key guidance. A missing key is not permission to create one, request pasted credentials or call a paid service. Independently check returned artifacts against this exact model and classify each unresolved property.

Use Verus only for a suitable Rust implementation in its supported subset. Map requires/ensures/invariants to R1-R3 and inspect assumptions, external bodies and unverified callers. The Lean model is not a Verus result, and neither result establishes arbitrary runtime behavior.

## Final evidence

Retain requirements, diagram/model/implementation revisions, actual tool versions/commands, source/structure/render/pixel status, proof target/axioms/result, mutation results, independent verdict and remaining correspondence gaps. An example that has not run stays unobserved. Changed source or assumptions stale affected acceptance.
