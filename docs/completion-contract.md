# Approved completion contract

Use this reference from Outcomes, Coordinate, Recover and Deliver when the selected assignment has a native goal, supporting work, multipart delivery or a coordinator handoff. The CLI only checks supplied records. Read actual supported tools and source evidence before supplying them. These fields neither authorize operations nor authenticate their receipts.

## Original obligations and outcome scope

Version 2 requires `completion_contract`, `outcome_results`, `native_goal` and `handoff_receipts`. Version 1 is rejected rather than silently receiving stronger completion assurance. Export the approved inventory from the existing canonical writer. Preserve the original request and latest scoped approval references. Do not reduce a requested delivery to a report just to close a goal.

`completion_contract` contains `request_ref`, `approval_ref`, `outcome_kind`, `parent_outcome_id`, `native_goal_required`, `obligations` and `handoff`. `request_ref` and `approval_ref` must match the record. `outcome_kind` is `delivery` or `support`. A supporting outcome names a distinct parent outcome; a root delivery has a null parent. A report can itself be a delivery when that was the original requested result. A report that merely prepares another result is supporting work.

Each obligation retains a stable `id`, original `source_ref`, `description`, `kind`, nonempty unique `part_ids` and `acceptance_ids`. The union of acceptance IDs must match the record's acceptance list exactly. Each part has one `outcome_results` entry with `obligation_id`, `part_id`, matching `kind`, `status` (`pending`, `blocked`, `complete`) and `evidence_ids`. Keep missing or blocked parts visible. A complete part needs passing evidence at the current revision and manifest. Supporting results cannot satisfy delivery obligations. Required parts must all be complete before completion is supported.

`completion_scope` always identifies this record's outcome; `parent_completion_supported` is always false. Completing a supporting analysis, recovery, slice or missing-history search does not close its parent. The canonical owner evaluates the parent's own approved obligations separately. Do not invent original delivery criteria when history is unavailable.

The checker compares the supplied inventory and results. It cannot discover an obligation omitted from both, verify that a source reference contains the claimed approval, or judge semantic usefulness. The owner and independent reviewer must compare the inventory with the actual original request and steering. Do not advertise this as automatic protection against falsified or incompletely transcribed source material.

## Native goal lifecycle

First discover the supported read and lifecycle capabilities on the current executor. Inspect the actual current goal before dependent work. Retain a compatible unfinished objective. Create only if the readback establishes no unfinished goal and the existing approval explicitly covers creation. A conflicting goal or an unavailable tool is a lifecycle dependency, not permission to replace it, fabricate absence or invent a resume operation. Continue authorized independent preparation while that dependency remains open.

| `native_goal.state` | Required record and effect |
|---|---|
| `not_selected` | Valid for completion only when `native_goal_required` is false in the selected contract. No native operation is implied. |
| `unavailable`, `conflict`, `absent` | `dependency` names `action`, `owner`, `observation_ref`, `resume_when`. The outcome can report/wait honestly, but cannot claim complete. |
| `retained` | `id`, this `outcome_id`, `prior_readback` and `current_readback`. Prior state is `same_unfinished` with the same goal/outcome IDs and a nonempty `ref`. |
| `created` | Same binding and current readback, plus prior state `none_unfinished`, `creation_approval_ref` and `creation_receipt`. Current scoped approval must include `create_goal`, with no denial or stop. |

A current readback contains `ref`, `goal_id`, `outcome_id`, normalized `status` (`unfinished` or `complete`) and the actual `native_status`. Normalization is an evidence classification; it is not a native tool command or a claim that pause/resume exists. Preserve the underlying response. If the tool is unsupported, record the observation rather than inventing a readback.

A proposed `create_goal` action requires state `absent` and a prior readback with `state: none_unfinished` and `ref`. Ordinary action permission checks still apply. A proposed `complete_goal` requires a retained/created binding. All approved acceptance, part, independent-review and selected handoff checks must pass before proposing or reporting native completion. A final `claim_status: complete` needs the actual completed goal readback when a goal is selected. An unfinished goal can remain a consistent waiting record. Never call a native tool from this validator.

## Contract-specific handoff evidence

`completion_contract.handoff` selects the expected `artifact_ref`, `destination`, `recipient` and nonempty unique `required_stages`. Select stages from the actual delivery contract, not a universal checklist. Local artifact delivery may require only persistence; an external handoff can additionally require attachment and recipient readback. Selected coordinator incorporation remains a separate completion requirement.

`handoff_receipts` is keyed by `persistence`, `attachment`, `recipient_readback`, or `incorporation`. Each has `status` (`pending`, `uncertain`, `confirmed`). A confirmed stage requires a nonempty string `ref`, matching `artifact_ref`, `destination`, `recipient`, exact `revision` and entire `manifest`. Retain distinct source events for persistence, attachment and recipient readback; one storage success cannot be relabeled as proof of later stages. The checker rejects reuse of one event reference across confirmed stages, but cannot authenticate the events.

Confirmed incorporation also requires the existing `register_ref` and `writer`, a `readback_ref`, a nonempty `detail`, and `disposition: incorporated` or `retained`. A retained disposition records the canonical writer's explicit decision about this exact delta, such as intentionally local or already represented. A bare acknowledgment or worker-ended event is insufficient. Retention satisfies the handoff stage only; it does not waive pending original delivery obligations or acceptance.

A `delivered` claim requires selected transport stages. It may precede incorporation or final acceptance. A `complete` claim and native goal completion require every selected stage. Uncertain stages remain open; inspect original effects before any authorized retry. Artifact delivery, CI, deployment, customer acceptance, agent discovery and actual adoption remain separate outcomes.
