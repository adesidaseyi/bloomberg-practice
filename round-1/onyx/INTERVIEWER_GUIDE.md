# Interviewer Guide - onyx

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
| O1 | `validate` ignores expiry |
| O2 | `refresh` ignores expiry |
| O3 | `revoke` accepts already-revoked tokens |
| O4 | `revoke` accepts expired tokens |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the expiry boundary, refresh-after-expiry, second revoke, and revoke-after-expiry? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Does an expired token validate? | No. Validity requires `now < expires_at`. | O1 |
| Can an expired token be refreshed? | No. Refresh requires an unexpired token. | O2 |
| What should a second revoke do? | Raise. `REVOKED` is terminal. | O3 |
| Can an expired token be revoked? | No. It is already invalid. | O4 |
| Does refresh extend from now? | Yes, from the current clock time. | - |

## Bug inventory

### O1 - Expired tokens still validate

- **Spec rule:** A token is valid only while `ACTIVE` and `now < expires_at`.
- **Location:** `validate` in each language.
- **Root cause:** The method checks only the stored status, not the clock.
- **Minimal fix:**

```python
if tok is None or tok.status != TokenStatus.ACTIVE:
    return False
return self._clock() < tok.expires_at
```
- **Failing-test recipe:** Issue a token with a 10-second TTL, advance the clock to 10, and assert `validate` is `False`.
- **Difficulty:** easy
- **Hint ladder:** (1) What makes a token valid? (2) Does `validate` read the clock? (3) It only reads status. (4) Show the expiry check.

### O2 - Expired tokens can be revived

- **Spec rule:** Refresh is valid only for an active, unexpired token.
- **Location:** `refresh` in each language.
- **Root cause:** The guard checks only `ACTIVE`, so an expired token passes.
- **Minimal fix:**

```python
if tok.status != TokenStatus.ACTIVE or self._clock() >= tok.expires_at:
    raise ValueError("cannot refresh an expired or revoked token")
```
- **Failing-test recipe:** Issue a token with a 10-second TTL, advance to 10, then refresh. The refresh should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) Which tokens can be refreshed? (2) Does the guard consider expiry? (3) It only checks status. (4) Show the expiry condition.

### O3 - Revoke has no terminal-state guard

- **Spec rule:** `REVOKED` is terminal; a second revoke raises.
- **Location:** `revoke` in each language.
- **Root cause:** The method overwrites the status without checking it.
- **Minimal fix:**

```python
if tok.status != TokenStatus.ACTIVE:
    raise ValueError("cannot revoke a revoked token")
```
- **Failing-test recipe:** Issue a token, revoke it, then revoke it again. The second call should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) Is revoke idempotent? (2) What does `revoke` check? (3) Nothing. (4) Show the status guard.

### O4 - Expired tokens can be revoked

- **Spec rule:** Revoke is valid only for an active, unexpired token.
- **Location:** `revoke` in each language.
- **Root cause:** The method never checks the clock, so an expired token is treated as active.
- **Minimal fix:**

```python
if tok.status != TokenStatus.ACTIVE or self._clock() >= tok.expires_at:
    raise ValueError("cannot revoke an expired or revoked token")
```
- **Failing-test recipe:** Issue a token with a 10-second TTL, advance to 10, then revoke. The revoke should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) Can an expired token be revoked? (2) Does `revoke` read the clock? (3) It does not. (4) Show the expiry condition.

## Acceptable alternative fixes

- A shared `_valid(tok)` helper used by `validate`, `refresh`, and `revoke`.
- A stored `EXPIRED` status is acceptable if it is applied consistently; this pack keeps expiry logical.

## Cross-language notes

- C++ and Java mirror the same expiry checks in `validate`, `refresh`, and `revoke`.
- Use the injected clock everywhere; do not call the system clock directly.

## Traps and wrong fixes

- Fixing `validate` but leaving `refresh` able to revive an expired token.
- Guarding revoke against `REVOKED` but not against expiry.
- Making revoke idempotent when the spec says a second revoke raises.
- Using `<=` where the spec says `now < expires_at`.

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
