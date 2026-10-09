# Select and use engineering tools

Start with a repeatable way to control the real product and a feature map connecting user behavior to components and acceptance. Establish trust in one workflow before adding parallel helpers. Prefer architectural constraints, types and compiler/lint/CI enforcement over repeated prose instructions. Build a control CLI only when it replaces repeated improvised work, with discoverable commands, useful errors and machine-readable results.

| Need | Tool and observation |
|---|---|
| Engineering workflow | Use the installed pstack host adapter, router and relevant playbook. Record the actual loaded files. Preserve pstack's authorship and identity. |
| Planning, review or user-flow QA | Use an installed gstack skill suited to the task. Inspect its host support and permissions; Codex safety guidance is advisory rather than an enforced hook boundary. |
| Advisory review of one existing PR | Use the installed `local-clawsweeper-review` skill and the source checkout's current README. Resolve the current candidate with its owner before running. |

Installations are separate from invocation authority. Preserve current models, customized skills, authentication and settings. Do not import automatic paid reviewers, telemetry, memory services, browser sessions, hooks or automatic updates merely because upstream setup offers them. An upstream example is not permission to buy infrastructure, publish, merge or deploy.

For an authorized ClawSweeper issue/PR review, the documented advisory entrypoint is:

```sh
pnpm run review -- --local-only --target-repo owner/repo \
  --item-number 123 --target-dir /path/to/isolated-clean-checkout \
  --output-retention summary --result-format json
```

Inspect the current command and runtime requirements before use. Ordinary `review` can publish a placeholder comment; keep `--local-only` explicit. Do not run apply, repair, label, comment, close or merge commands without separate authority. Use an isolated checkout if target preparation might switch refs; never change an active owner's worktree. Local review can call the configured Codex service and is not an offline test. Preserve a report with the actual invocation, base/head, findings or exact execution dependency and useful limitations. Help output, installation and an empty report do not establish review completion.

Reuse existing required evidence and follow [verification](verification.md) for newly commissioned complete workflows. Advisory source review is distinct from hosted CI, independent acceptance, real-provider behavior and customer acceptance. Report each boundary honestly and return findings to the existing integration owner.

Primary references: [pstack router](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md), [Poteto's Part 1 article](https://x.com/poteto/status/2094457600259842065), [gstack](https://github.com/garrytan/gstack), and [ClawSweeper local skill](https://github.com/openclaw/clawsweeper/blob/main/docs/local-clawsweeper-skill.md). These are guidance; no upstream implementation or private source notes are copied here.
