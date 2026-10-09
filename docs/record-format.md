# Outcome record version 2

[The synthetic example](../templates/outcome.example.json) is executable. Export a selected row from the existing register; this file is not a second canonical register. Only its existing owner writes canonical state.

| Field | Meaning |
|---|---|
| `schema_version`, `outcome_id` | Format version 2 and stable outcome identity |
| `original_request` | Original request reference and outcome summary |
| `approval` | Current scoped reference, allowed/denied action kinds and stop state |
| `register`, `owner` | Canonical reference/writer and accountable execution owner |
| `scope.write_paths` | Literal repository-relative POSIX files/directories; no globs or traversal |
| `writers` | Optional disjoint owner/path leases; overlaps across owners fail |
| `acceptance` | Unique IDs, descriptions, pending/passed/failed/unverified, evidence IDs |
| `stop_conditions` | Finite outcome and dependency stops |
| `subject` | Revision, named SHA-256 manifest, authors and whether independent review is required |
| `execution` | Admitted/running/completed/interrupted/cancelled/held/waiting, task ID, admission/first-action receipts, last actual progress time |
| `checkpoint` | Previous/current timezone-aware time, concrete progress reference, next action |
| `evidence` | Unique IDs, kind/ref/status, exact revision and entire subject manifest; review adds reviewer and independence receipt; tests add executed/failed/skipped counts |
| `delivery` | not_delivered/delivered/uncertain; delivered requires nonempty string receipt, artifact_ref and revision plus the exact subject manifest |
| `next_action` | Scoped action kind and proposed write paths; inspect requires empty paths; report/preserve may list only their approved writes |
| `completion_contract`, `outcome_results` | Approved obligation inventory and one result for each required part; see [completion contract](completion-contract.md) |
| `native_goal` | Selected lifecycle binding/readback or truthful capability dependency |
| `handoff_receipts` | Separate selected transport and incorporation evidence |
| `claim_status` | admitted/running/waiting/delivered/complete, checked separately from execution state |
| `operation` | Required for retry: nonempty string original ID, known status, integer attempts/max_attempts and boolean retry_authorized; other actions may omit it |
| `recovery` | Current resume approval reference and actual state readback for held/cancelled/interrupted execution |
| `metrics` | Named population/revision/time; numerator/denominator/percentage, with null percentage meaning Unknown |
| `reconciliation` | Incorporation decision from the read-only helper, with underlying receipt retained by the owner |

Every passing evidence entry must bind the complete current manifest. Keep historical evidence in its own retained receipt rather than pretending it passed for the current record. Passing schema/consistency checks do not authenticate reference strings or establish that the acceptance criterion is meaningful. Review that judgment separately.

Running/completed execution and running/delivered/complete claims require a nonempty first-action receipt. A delivered artifact also requires that receipt even while the task waits. An admitted execution cannot claim those later stages; reconcile its state first. Waiting without delivery can retain an empty first-action receipt, and partial artifact delivery with pending acceptance remains distinct from completion.

For canceled/uncertain retries, an absent-effect readback must have a nonempty string receipt. The readback result enum is `absent`, `present` or `unknown`; only `absent` permits this retry check to pass. Missing readback keeps the action uncertain. Boolean, numeric, null and whitespace references are invalid. A valid string is still a supplied claim, not an authenticated receipt. Reporting and preservation during a stop retain their existing scoped authority; labeling proposed writes as inspection is invalid even without a stop.

`--now` is mandatory so historical fixtures are reproducible and a live status check cannot silently reuse an old observation time. Use the actual current time for operational checks. A stale checkpoint invalidates a current claim; stale progress triggers diagnosis without automatic cancellation. A stopped task can still inspect/report/preserve when those exact actions remain allowed.

For `metrics`, null means unknown, not zero. The CLI does not calculate a whole-program percentage. For tests, only include checks required by the chosen outcome; skipped optional work belongs in an explicit separate limit.

Version 1 inputs fail closed with `INVALID_INPUT`. Migration requires the actual approved inventory and selected lifecycle/delivery contract; the CLI never fabricates them. Historical fixture bytes are preserved; tests use an explicitly synthetic in-memory adapter, not a production migration.
