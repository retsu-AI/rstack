# Checkpoints and fresh status

During an authorized active run, make a bounded checkpoint at least every 15 minutes and on a meaningful result or failure. Store previous checkpoint time, current UTC time, computed elapsed minutes, last concrete progress time/reference, changed artifact or operation, current unit, owner and next action. The helper rejects timezone-free or future timestamps. A tool read time is not a worker execution time.

This is an in-run practice, not an automatic schedule. Use an existing authorized mechanism for unattended checks and verify its actual trigger/delivery. If none exists, say so; do not promise continued monitoring after the run ends or silently install one.

When the user asks for status, obtain a fresh bounded read of changed evidence first. Answer the question directly with what exists, what remains and the next action, then continue the authorized work. Retain earlier instructions without requiring the user to repeat them.

A 15-minute gap triggers diagnosis, not automatic replacement or a delivery SLA. Compare actual artifacts, commits, checks and receipts. A timestamp touch or repeated status paragraph is not progress. Inspect one current error and the original operation receipt. Classify admitted but no first action, reader lag, access denial, deterministic command failure, legitimate dependency wait, or elapsed work without a verifiable delta. State unknown cause when evidence is insufficient.

Stop polling unchanged state after the bounded check. Record a resumption trigger, such as owner receipt, changed revision or existing scheduled tick. No duplicate schedule, endless retry loop or competing supervisor follows. Preserve contradictory observations with their timestamps instead of replacing them with a confident label.

For [planned parts](execution-plan.md), checkpoint implemented revision, independent verdict, integrated revision, final acceptance and remaining correction budget separately. NOT OBSERVED records the natural event and bounded observation window; BLOCKED records the missing prerequisite or unusable verifier. Neither is PASS. Recommendation, delivery, application, execution and verified outcome are distinct observations.
