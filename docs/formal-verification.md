# Formal proof evidence

Use formal verification for a bounded mathematical claim, invariant, or supported code component when it helps satisfy an acceptance criterion. Follow [exact-subject verification](verification.md) and retain the existing owner, worker/verifier pair and canonical record. Selecting a tool does not authorize installation, remote uploads, credentials or spending.

Before proving, have the independent verifier review the formal statement, definitions, assumptions and connection to the intended requirement. Record excluded behavior and any implementation-to-model correspondence still to establish. A checked proof establishes its formal claim under its assumptions; it does not establish specification correctness or arbitrary runtime behavior.

## Lean

Keep the project's pinned toolchain and dependencies. Name the theorem and module or build target that cover the criterion, then retain the invocation and full result. A default build that omits that target supplies no evidence for it. Use the existing project's [Lake configuration](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/) rather than creating an unrelated proof environment.

Inspect `#print axioms theoremName`, including dependencies. `sorryAx` leaves the claim incomplete. Report custom axioms and native-evaluation trust for explicit review. Where supported and appropriate, recheck the relevant module with `lean4checker --fresh`. For higher-risk unreviewed generated proofs, consider a trusted challenge and sandboxed `lake comparator` with external checking. Preserve unavailable checks as not run. These checks still depend on the meaning of the formal statement and the stated trust boundary. See the [official proof-validation guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## Verus for supported Rust

Choose components expressible in the supported Rust subset. State `requires`, `ensures`, invariants and the functions being checked. Record Verus, Rust/toolchain and solver versions, source revision, invocation, checked scope and result. Verus performs static verification, adds no runtime checks, and does not support every Rust feature/library or verify Rust/LLVM. Keep ordinary runtime and integration checks for the surrounding system. See the [Verus overview](https://verus-lang.github.io/verus/guide/).

The verifier inspects admission mechanisms, `assume`, external specifications and `#[verifier::external_body]`. An external body assumes its contract without proving its implementation; list that boundary and its supporting evidence. See [calling unverified code](https://verus-lang.github.io/verus/guide/calling-unverified-from-verified.html). Where supported, `--no-cheating` disallows `assume`; it does not replace specification review. See the [Verus reference](https://verus-lang.github.io/verus/guide/print.html).

Check how unverified callers uphold preconditions. Where relevant and supported, use `-V check-safe-api` or verified wrappers that check preconditions dynamically. See [calling verified code](https://verus-lang.github.io/verus/guide/calling-verified-from-unverified.html).

## Optional Aristotle

Aristotle is disabled unless selected for the task. Confirm the installed SDK version and documented language support before choosing an API or command. The [3.0.0 changelog](https://raw.githubusercontent.com/harmonic-ai/aristotle/main/CHANGELOG.md) removes `aristotle formalize` and ask mode. Do not infer a current Lean or Rust workflow from an older example. Consult the [official SDK](https://github.com/harmonic-ai/aristotle).

The user may supply an existing `ARISTOTLE_API_KEY` through their process environment or secret manager. Never request a pasted key, print it, store it in skill files, logs or a committed environment file, or pass it as a command argument. Do not run `aristotle login`, create an account/key, or request a grant. Key configuration does not authorize a run.

Before a separately authorized remote run, confirm the upload scope, requested properties, budget and stop conditions. Review the actual upload manifest; filename exclusions alone cannot detect secrets inside source files. When available in the installed version, `submit --dry-run` inspects without uploading or requiring a key. Retain project/task IDs and check uncertain outcomes before resubmission. Preserve each property's proved, refuted, in-progress, unresolved, unchecked or unknown state. Exit success alone does not establish proof acceptance. See the [CLI reference](https://raw.githubusercontent.com/harmonic-ai/aristotle/main/docs/cli-reference.md).

Independently validate returned artifacts before relying on them and account for consumed credits. See the [service terms](https://www.harmonic.fun/legal/terms/). These instructions contain no credentials and make no remote call.

## Acceptance and correction

For each acceptance ID, retain the exact subject, formal statement, tool/dependency versions, command and receipt, status, assumptions/admissions, independent verdict and unproved boundary. Distinguish source inventory, an earlier proof receipt and a fresh checked run. A timeout, missing tool, unchecked output or failed proof remains visible. Return corrections to the author within the existing attempt/time budget, then rerun affected checks and independent review on the changed revision. Worker proof acceptance does not close final integration or delivery.

Use [the bounded architecture/state-machine example](formal-architecture-example.md) when the criterion involves stale asynchronous work. It links editable Pele input, a small Lean model and explicit implementation correspondence gaps. Apply actual tool receipts and independent acceptance; illustrative source alone remains unobserved.
