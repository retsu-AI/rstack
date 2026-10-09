# Use rstack with an agent

Clone this repository into a location the agent can read. The canonical entrypoint is `skills/rstack/SKILL.md`; the router links to the seven workflow leaves. The repository also includes `.agents/skills/<name>` links for hosts that support repository-local skill discovery. Other agents can read the canonical files directly.

Ask the agent to read `skills/rstack/SKILL.md` and the relevant leaf before working on an authorized engineering outcome. Keep the existing owner, outcome register, scope, acceptance conditions and stop gates. Reading a skill grants no new tool access or external authority.

For a separate consumer repository, add a small pointer in its existing agent instructions to the resolved checkout and pin the rstack commit in that repository's runbook. Confirm the checkout exists and that its `git rev-parse HEAD` matches the pin before loading the router. Do not silently use a moving branch or vendor a second canonical copy. Updating the pin is an explicit maintenance change, not a global installation.

Repository discovery, actual instruction loading and useful behavior are separate observations. Verify that the consuming agent actually read the router and selected leaf, then observe an authorized end-to-end task before claiming adoption. A correct directory layout alone is not that evidence.

## Optional pstack workflow

Use an existing installed pstack host adapter and its matching playbook when available. Record the actual files and upstream version loaded. If absent, the self-contained rstack references and CLI remain usable; report pstack unavailable rather than claiming its playbook ran. Do not install, replace or update pstack as a side effect.

Rstack needs no global settings, hooks, package installation, service connection or credentials. It does not dispatch agents, schedule jobs, intercept tools or enforce a runtime security boundary. Preserve any existing plugin's responsibility.

See [tool workflows](tool-workflows.md) for optional gstack and ClawSweeper use. Install only under current authority, inspect the supported host installer, preserve customized copies and licenses, and verify actual discovery and use. A Claude or Cursor installation alone does not prove Codex availability.

## Offline record checks

From the rstack checkout, run the examples in [README](../README.md). For real work, check a bounded export from the existing register with `scripts/rstack.py validate`. Return its findings to the existing record owner. Do not create a competing register to satisfy the example shape. The checker assesses supplied records and cannot authenticate receipts or determine whether the original request omitted an obligation.
