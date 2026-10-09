# Provenance and source relationship

Rstack's original workflow text and Python implementation were developed for Retsu with Codex. Its operating practices came from the repository owner's engineering guidance. This public repository is a sanitized export of the local source snapshot `8a7910b209315020195872d3546d3bc81bbd8ade`; it starts a separate public Git history. The original development history is preserved privately, rather than represented as public ancestry.

The offline Python implementation, example record, regression tests and synthetic fixtures are retained from that snapshot. Public documentation removes internal audit, task and review context, replaces an internal integration patch with portable setup instructions, and adjusts the two skill entrypoints that referred to that context. Historical author review reports and private delivery receipts are not part of the public package. Earlier review of the source does not automatically accept the changed public package.

## Pstack

Lauren Tan / poteto's pstack informed the engineering workflow. The inspected installation declared version `0.15.15`, upstream repository [cursor/plugins](https://github.com/cursor/plugins), directory `pstack`, commit `9f451cf875ad1239912762f67741e8e5ba6ac0f1`, with an MIT license and copyright 2026 Lauren Tan. This identifies the inspected snapshot, not the latest upstream release.

The installed pstack-codex adapter, poteto-mode router, skill-authoring and feature playbooks, and the Model the Domain, Test Behavior Not Implementation and Prove It Works principles informed structure and verification. Codex skill-creator informed the concise entrypoints and progressive references. Their implementation and complete playbook text are not copied here. Pstack is neither bundled nor renamed; consumers use their own installed host adapter when available.

The [pstack MIT notice](../licenses/pstack-MIT.txt) is retained for attribution. It applies to pstack, not to the research brief or rstack's original implementation. See [NOTICE](../NOTICE.md) for the distinctions.

## Secondary research coverage

A user-supplied 13-page research brief about Lauren Tan's engineering practices informed the [page-to-practice adoption matrix](pdf-adoption.md). All 472 extracted text lines were read, including diagram labels. Page pixels and video were not inspected, and the brief's throughput anecdotes and source links were not independently verified. The matrix is a paraphrase of text-supported practices, not a transcript or a claim of visual coverage.

No brief bytes, extracted full text, screenshots, account paths, private conversation, startup audit or source receipts are distributed here. The fixture records are synthetic examples of engineering state and do not authenticate actual work, permissions or deliveries.
