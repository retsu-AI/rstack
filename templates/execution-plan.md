# Bounded execution plan

- Existing outcome/register and its writer:
- Original request, latest steering and exclusions:
- Manager M and independent manager verifier VM:
- Source/base/revision and preserved dirty work:
- User journey, design, shared contracts and deliberate omissions:
- Permissions, existing owner/operation lookup and duplicate suppression:
- Retry/time budget, integration reserve, dependency stop and resumption trigger:

## Feature inventory

| ID | Main feature or extension of | Required/optional/deferred | Acceptance IDs | Literal expected result and rejecting conditions | Evidence method |
|---|---|---|---|---|---|
| F1 | Main feature | Required | A1 | Fill from the actual request | Public workflow and relevant failure checks |
| F1.E1 | Extension of F1 | Resolve from request | A2 | Fill from the actual request | Name the supported check |

## Ordered checklist

| Order | Feature/check | Prerequisites | W / independent V | Owned paths | Implemented revision | Worker checks | Independent verdict/evidence | Integrated revision | Final VM acceptance |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Plan and rejecting conditions | Inventory/contracts | M / VM | Canonical plan | Record subject | Plan reviewed | Pending actual verdict | Not applicable | Plan gate only |
| 1 | F1 / A1 | Accepted plan | W1 / V1 | Assign disjoint paths | Pending | NOT RUN | Pending | Pending | Pending |
| 2 | F1.E1 / A2 | Name actual prerequisite | W2 / V2 | Assign disjoint paths | Pending | NOT RUN | Pending | Pending | Pending |
| 3 | Combined required scope | All required parts integrated | M / VM | Integrated subject | Exact revision | Relevant combined checks | Pending | Exact revision | Pending |

Replace the illustrative rows with the full requested inventory. Keep implementation and verification marks separate. For every nonpassing check retain the actual observation, responsible owner, budget remaining and next trigger. Record omitted or inaccessible evidence explicitly; do not infer PASS from a completed agent turn.
