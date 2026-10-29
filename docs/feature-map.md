# Feature map

| User need | Entrypoint | Observable check |
|---|---|---|
| Validate one canonical outcome export | `scripts/rstack.py validate` | JSON result, exit 0 consistent, 1 conflicting claim/action, 2 invalid input |
| Preserve original multipart delivery and supporting outcomes | Outcomes; `validate` | `test_completion_contract.py`: missing parts, substituted report, parent scope, valid neighbors |
| Bind native goals without implied authority | Coordinate/Recover; `validate` | Actual readback structure, absence versus unavailable/conflict, creation authority, premature completion |
| Distinguish selected delivery and incorporation stages | Deliver; `validate` | Destination/subject binding, stage-specific gaps, canonical readback, retained disposition |
| Compare checkpoint times | `scripts/rstack.py checkpoint` | UTC-aware elapsed minutes, due/stale state and bounded next step |
| Check existing incorporation | `scripts/rstack.py reconcile` | Real Git ancestry/tree/file/patch evidence, no writes |
| Discover a skill | `.agents/skills/` local links or `skills/` direct paths | Repository check verifies entrypoints and links |
| Validate packaging | `scripts/check_repository.py` | Frontmatter, unique names, local links and required fixture coverage |
| Evaluate actual agent behavior | [Verification](verification.md) | An authorized non-author exercises the intended user journey against a frozen revision and records the result |
| Plan main features and extensions | [Execution plan](execution-plan.md); [template](../templates/execution-plan.md) | Full inventory, ordered prerequisites, literal acceptance/rejection and independent plan verdict |
| Accept bounded work and final integration | Coordinate/Verify; [execution plan](execution-plan.md) | M/VM and W/V assignments, finite correction evidence and final verdict on combined bytes |
| Check formal obligations | [Formal verification](formal-verification.md) | Reviewed specification/assumptions, pinned source/toolchain, checked result and trust/runtime boundaries |
| Review a Pele diagram | [Diagrams](diagrams.md) | Source, pinned renderer/options, rendered artifact and stated structural/pixel inspection |
| Compare models or harnesses | [Benchmarks](benchmarks.md) | Fixed variable/denominator, private held-out fixtures, versioned grader, raw execution and independent verdict |

The CLI never performs the action it assesses. The primary regression suite calls its public subprocess interface with literal expected decisions and uses temporary Git histories to test duplicate incorporation. These fixtures are synthetic reproductions of observed failure classes, not replays of private conversations.

Plan review, role independence, proof tools, diagram rendering and benchmark execution are workflow guidance. The CLI does not dispatch these roles, authenticate their evidence or enforce the checklist fields. Structural checks and behavioral exercises must be reported separately.
