---
name: rstack-checkpoint
description: Answer progress questions from fresh evidence and diagnose stale engineering work using previous/current timestamps and concrete deltas.
---

# rstack-checkpoint

Read [checkpoints](../../docs/checkpoints.md). Compare prior/current UTC times and actual progress, at most 15 minutes apart during an authorized active run. Use the checkpoint helper for elapsed minutes; it creates no schedule.

Answer the user's check-in directly, then continue the current authorized unit. Diagnose a stale interval from evidence without interrupting or replacing active owners. Stop unchanged polling with a concrete resumption trigger.
