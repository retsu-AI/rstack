# rstack

Reusable engineering skills for carrying an authorized request through delivered evidence and acceptance. Rstack adds outcome ownership, bounded checkpoints, recovery and exact-revision review to an agent's existing engineering workflow. Lauren Tan's pstack remains a separate upstream workflow.

Start with [rstack](skills/rstack/SKILL.md). Load only the workflow needed for the current decision. These skills do not dispatch agents, schedule work, change permissions, or intercept tools.

| Decision | Skill |
|---|---|
| What was requested and what counts as finished? | [Outcomes](skills/rstack-outcomes/SKILL.md) |
| Who owns each write and did a Cloud Task actually start? | [Coordinate](skills/rstack-coordinate/SKILL.md) |
| Has work changed since the last checkpoint? | [Checkpoint](skills/rstack-checkpoint/SKILL.md) |
| How do we recover an interrupted or uncertain operation? | [Recover](skills/rstack-recover/SKILL.md) |
| Is local work already incorporated in an existing PR? | [Reconcile](skills/rstack-reconcile/SKILL.md) |
| Does review and verification cover this exact subject? | [Verify](skills/rstack-verify/SKILL.md) |
| Has the requested result reached its destination? | [Deliver](skills/rstack-deliver/SKILL.md) |

## Try it

Python 3.10 or newer and Git are sufficient. Clone the repository, then run the synthetic example. The commands after cloning work offline and need no packages, services, keys or installation hooks.

```sh
git clone https://github.com/retsu-AI/rstack.git
cd rstack
python3 -B scripts/rstack.py validate templates/outcome.example.json --now 2026-01-01T12:05:00Z
python3 -B scripts/rstack.py checkpoint --previous 2026-01-01T12:00:00Z --current 2026-01-01T12:16:00Z --last-progress 2026-01-01T12:01:00Z
```

The first command returns `"ok": true` for the synthetic record. The checkpoint returns `"due": true`, `"stale": true` and `"next_step": "inspect_changed_evidence"`. It reports what needs attention; it does not start a worker or change any record.

The example uses record version 2. Older records require an explicit source-backed migration; they cannot silently claim the new controls. See [the completion contract](docs/completion-contract.md).

The example is synthetic. Do not create a new register when one already exists. Export one bounded record from its owner for checking, then return a delta to that owner.

To use the skills with an agent, follow [integration](docs/integration.md). See [record format](docs/record-format.md), [feature map](docs/feature-map.md) and [independent verification](docs/verification.md) for the interfaces and limits.

## Contributing checks

Existing offline checks are retained for maintainers. Run the checks affected by a change; do not repeat unchanged suites as evidence of new behavior.

```sh
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests -v
```

## Boundaries and provenance

The checker validates supplied records; it cannot authenticate receipts, prove reviewer independence, enforce a platform permission boundary, or establish customer acceptance. Passing local fixtures proves these deterministic checks only. Skills, tests, installation, observed loading, and demonstrated agent behavior are separate evidence stages.

[Provenance](docs/provenance.md) records the source relationship and upstream attribution. [PDF adoption](docs/pdf-adoption.md) maps the research brief's 13 text pages to practices and limitations. [Workflow coverage](docs/workflow-coverage.md) explains the reusable operating practices. Rstack's original source and documentation are available under the [MIT License](LICENSE). The [third-party notice](NOTICE.md) preserves pstack's separate identity and licensing. No upstream implementation is vendored.
