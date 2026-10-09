# Reconcile local work with the existing change

Before a cherry-pick, replacement PR or lost-work claim, preserve the worktree, branch, base/head, dirty status, source author, known existing PR and original outcome. Missing tracking refs, a missing old worktree or a completed local report do not establish unpublished or lost work.

Use the read-only command with the exact already-present refs and relevant paths:

```sh
python3 -B scripts/rstack.py reconcile --repo /path/to/repository --candidate candidate-ref --target existing-pr-ref --paths src/feature tests/feature
```

It resolves commit identities, checks ancestry, whole-tree identity, selected file identity and stable patch IDs against target history. It reports dirty files without altering them. It never fetches, checks out, cherry-picks, commits, pushes or creates a PR. For uncommitted work, preserve its owned diff/file hashes separately and compare it explicitly; the command's committed result does not cover that delta. Deleted paths are valid when present in either revision; paths missing from both are input errors.

An ancestor proves historical inclusion, not survival after a later revert. Same selected files can coexist with differences elsewhere. Patch equality can conceal later changes and cannot prove semantic compatibility. Combine these facts with current relevant files, base/current tree, exact existing PR metadata and the requested behavior. Patch equality alone never authorizes review carry-over to a changed final revision.

If incorporation exists, return that receipt and the genuinely missing delta to the existing owner. Do not duplicate the cherry-pick or open a replacement draft. If uncertain, identify the exact missing ref/source or authorized remote read needed. Keep source incorporation, PR publication, hosted CI, merge, release and runtime/customer acceptance distinct.
