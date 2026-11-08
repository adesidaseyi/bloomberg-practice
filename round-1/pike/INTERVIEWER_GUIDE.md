# Interviewer Guide - pike

> **INTERVIEWER ONLY.** This file is the answer key. Do not give it to the
> candidate, and do not leave it open on a shared screen.

## Pack at a glance

- Round 1: one stateful service, 35 minutes.
- Candidate-facing spec: `README.md`.
- Candidate-facing framing: `CANDIDATE_BRIEF.md`.
- Clarifying questions: `PROJECT_MANAGER_NOTES.md` (candidate should ask these).
- Languages: `python/`, `cpp/`, `java/`; the same defects exist in each.
- Candidate deliverable: a failing test per defect, a narrow fix, and an
  explanation of the invariant each fix protects.

| ID | Defect |
| --- | --- |
| P1 | `approve` has no source-state guard |
| P2 | `reject` has no source-state guard |
| P3 | `withdraw` has no source-state guard |
| P4 | `pending_count` counts every document |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask whether all three decisions are guarded and whether the pending count filters by status? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Can a rejected document be approved? | No. Only `PENDING` can be approved. | P1 |
| Can an approved document be rejected? | No. Only `PENDING` can be rejected. | P2 |
| Can a decided document be withdrawn? | No. Only `PENDING` can be withdrawn. | P3 |
| Does pending_count include decided documents? | No. Only `PENDING` documents. | P4 |

## Bug inventory

### P1 - A decided document can be approved

- **Spec rule:** Only `PENDING` documents can be approved.
- **Location:** `approve` in each language.
- **Root cause:** The status is overwritten with `APPROVED` without checking the source state.
- **Minimal fix:**

```python
if doc.status != DocStatus.PENDING:
    raise ValueError("only pending documents can be approved")
doc.status = DocStatus.APPROVED
```
- **Failing-test recipe:** Submit a document, reject it, then approve it. The approve should raise and the status should remain `REJECTED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be approved? (2) Does `approve` inspect status? (3) It does not. (4) Show the guard.

### P2 - A decided document can be rejected

- **Spec rule:** Only `PENDING` documents can be rejected.
- **Location:** `reject` in each language.
- **Root cause:** The status is overwritten with `REJECTED` without checking the source state.
- **Minimal fix:**

```python
if doc.status != DocStatus.PENDING:
    raise ValueError("only pending documents can be rejected")
doc.status = DocStatus.REJECTED
```
- **Failing-test recipe:** Submit a document, approve it, then reject it. The reject should raise and the status should remain `APPROVED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be rejected? (2) Does `reject` inspect status? (3) It does not. (4) Show the guard.

### P3 - A decided document can be withdrawn

- **Spec rule:** Only `PENDING` documents can be withdrawn.
- **Location:** `withdraw` in each language.
- **Root cause:** The status is overwritten with `WITHDRAWN` without checking the source state.
- **Minimal fix:**

```python
if doc.status != DocStatus.PENDING:
    raise ValueError("only pending documents can be withdrawn")
doc.status = DocStatus.WITHDRAWN
```
- **Failing-test recipe:** Submit a document, approve it, then withdraw it. The withdraw should raise and the status should remain `APPROVED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be withdrawn? (2) Does `withdraw` inspect status? (3) It does not. (4) Show the guard.

### P4 - Pending count never goes down

- **Spec rule:** `pending_count` counts only `PENDING` documents.
- **Location:** `pending_count` / `pendingCount` in each language.
- **Root cause:** The method returns the size of the whole document map.
- **Minimal fix:**

```python
return sum(1 for d in self._docs.values() if d.status == DocStatus.PENDING)
```
- **Failing-test recipe:** Submit two documents, approve one, and assert `pending_count() == 1`.
- **Difficulty:** easy
- **Hint ladder:** (1) What does 'pending' mean? (2) What does the count use? (3) It counts the entire document map. (4) Show the status filter.

## Acceptable alternative fixes

- A shared `_require_pending(doc)` helper used by all three decisions.
- A transition table for document status instead of separate guards.

## Cross-language notes

- C++ and Java mirror the same PENDING guards and the same status filter in the pending count.

## Traps and wrong fixes

- Guarding approve but leaving reject or withdraw unguarded.
- Counting all documents in `pending_count` because the map size looks convenient.
- Letting an invalid transition change status before raising.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1-2 defects | Finds 3-4 | Finds all |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the exact boundary where relevant, and state-preservation after invalid transitions |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, transitions, complexity, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Map the state machine in this file. Do not suggest fixes yet."
- "Given this spec, what tests would prove each rule?"
- "Review this diff against the spec and tell me which rule it protects."

Watch for: "Just make the tests pass", accepting a diff without reading it, or
letting the assistant invent behaviour the spec does not describe.

## Pre-interview checklist

- [ ] No `test_*.py`, `test.cpp`, or `Check.java` files are present in the pack.
- [ ] Python imports cleanly; C++ compiles with `-std=c++17`; Java compiles with
  JDK 11+.
- [ ] `README.md` is open, not this guide.
- [ ] A private holdout (outside the repo) is available if you want to verify
  your own fixes.
