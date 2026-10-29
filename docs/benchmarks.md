# Independent model and harness evaluation

Use the existing evaluation owner and outcome. Keep task curation, execution, grading, release decisions and publication separate. A requested results website is a separate delivery obligation; a benchmark run does not authorize publication.

## Define the comparison

Decide which variable the experiment measures before running it:

- For a model comparison, hold the harness version, tools, prompts, task set, limits and grading procedure fixed; record the exact model/configuration for each candidate.
- For a harness comparison, hold the model/version/configuration and task set fixed; record the harness source revision, tool inventory, prompts, routing, retries and limits for each candidate.
- If both change, label it a system comparison. Do not attribute the difference to either component alone.

Keep release gates for model changes and harness changes distinct. Define task population/version, fixed denominator, pass criteria, timeout/cancellation policy, repetition or seed plan, resource limits and cost budget in advance. Record missing, invalid, skipped and failed runs separately. Useful completed tasks, latency, cost and rework provide different evidence; do not collapse them into a single unsupported success claim.

For Terminal-Bench or another external suite, identify the official suite version, task revision, harness/adapter and grading rules actually used. Do not claim suite compatibility or publish a named score from an improvised substitute. This guide adds no benchmark implementation or inference access.

## Protect held-out tasks

Keep private internal fixtures and expected answers in their authorized private location, outside public skill sources, examples, logs, patches and result bundles. Provide workers only permitted task inputs; restrict the independent evaluator's reference answers and grading data. Separate development examples from held-out evaluation, and record exposure or contamination. A fixture seen during tuning is not held out for that comparison.

Use stable opaque task IDs and evidence references in distributable reports. Inspect artifact and upload manifests before external transfer, including screenshots and tool traces. A user-supplied provider key does not authorize uploading private tasks. Report aggregates only within the authorized disclosure scope.

## Run and independently verify

Bind each run to an operation ID, task/version, source revision, model/provider/configuration, harness revision, environment/tool versions, input manifest, resource/time/cost limits and observed timestamps. Retain raw output, grader version, grading evidence and final disposition in the permitted private store. Distinguish requested, admitted, executing, returned, graded and independently accepted.

An independent non-author verifier checks the task/harness/grader boundaries and reproducible artifacts. Investigate grading defects independently; a grader repair changes the evaluation subject and stales affected results. Verify real execution and useful output rather than treating a submitted job, successful process exit or empty test run as task success.

Reconcile pending/uncertain run identities before retry. Set finite failure/retry budgets and preserve failed attempts in the denominator under the declared rules. Paid inference requires explicit existing spending authority and a bounded budget before submission; no available subscription, API key or benchmark request implies unlimited paid usage. Stop at the budget boundary with partial results and a concrete resumption condition.

Report exact versions, denominators, exclusions, observed results, independent verdict and limitations. Do not turn a small or unobserved difference into a general model-quality claim. Release or public reporting requires its own authorized acceptance and destination receipt.
