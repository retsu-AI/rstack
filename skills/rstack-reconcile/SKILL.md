---
name: rstack-reconcile
description: Compare local engineering work with an existing branch or PR using files, trees, ancestry and patch evidence before duplicate integration.
---

# rstack-reconcile

Read [reconciliation](../../docs/reconciliation.md). Preserve dirty work and authorship, then use the read-only Git helper against exact existing refs and selected files.

Separate historical incorporation from current semantic acceptance. Return only the genuinely missing delta to the existing owner. No automatic cherry-pick, fetch, replacement PR, push or owner change follows from this skill.
