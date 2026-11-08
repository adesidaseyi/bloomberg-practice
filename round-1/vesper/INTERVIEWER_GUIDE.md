# Interviewer Guide - vesper

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
| V1 | `acquire` ignores the closed flag |
| V2 | `acquire` ignores capacity |
| V3 | `release` has no status guard |
| V4 | `release` ignores the closed flag |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about closed-pool behaviour, capacity exhaustion, and double release? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Can acquire work after close? | No. A closed pool raises. | V1 |
| Can the pool exceed capacity? | No. Acquire raises when exhausted. | V2 |
| Can an idle connection be released again? | No. Only `IN_USE` can be released. | V3 |
| Can release work after close? | No in this model. | V4 |

## Bug inventory

### V1 - A closed pool still hands out connections

- **Spec rule:** `acquire` from a closed pool raises.
- **Location:** `acquire` in each language.
- **Root cause:** The method never checks `_closed`.
- **Minimal fix:**

```python
if self._closed:
    raise ValueError("pool is closed")
```
- **Failing-test recipe:** Acquire a connection, close the pool, then acquire again. The second acquire should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) What does close mean? (2) Does `acquire` read the closed flag? (3) It does not. (4) Show the guard.

### V2 - The pool can grow past its capacity

- **Spec rule:** `size <= capacity` always holds.
- **Location:** `acquire` in each language.
- **Root cause:** When no idle connection exists, the method creates a new one without checking the current size.
- **Minimal fix:**

```python
if len(self._conns) >= self._capacity:
    raise ValueError("pool exhausted")
```
- **Failing-test recipe:** Create a pool of capacity 1, acquire one connection, then acquire again. The second acquire should raise and `size()` should remain 1.
- **Difficulty:** easy
- **Hint ladder:** (1) What bounds the pool? (2) When is a new connection created? (3) It is created unconditionally after the idle scan. (4) Show the capacity guard.

### V3 - A connection can be released twice

- **Spec rule:** Only an `IN_USE` connection can be released.
- **Location:** `release` in each language.
- **Root cause:** The method sets the status to `IDLE` without checking the current status.
- **Minimal fix:**

```python
if c.status != ConnStatus.IN_USE:
    raise ValueError("connection is not in use")
c.status = ConnStatus.IDLE
```
- **Failing-test recipe:** Acquire a connection, release it, then release it again. The second release should raise and the idle count should stay at 1.
- **Difficulty:** easy
- **Hint ladder:** (1) Which connections can be released? (2) Does `release` inspect status? (3) It does not. (4) Show the guard.

### V4 - A closed pool still accepts releases

- **Spec rule:** `release` from a closed pool raises.
- **Location:** `release` in each language.
- **Root cause:** The method never checks `_closed`.
- **Minimal fix:**

```python
if self._closed:
    raise ValueError("pool is closed")
```
- **Failing-test recipe:** Acquire a connection, close the pool, then release it. The release should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) What does close mean for the pool? (2) Does `release` read the closed flag? (3) It does not. (4) Show the guard.

## Acceptable alternative fixes

- Checking closed and capacity in a shared `_check_open()` helper.
- Maintaining an explicit size counter instead of `len(conns)`; both are valid if the invariant holds.

## Cross-language notes

- C++ and Java mirror the same closed and capacity guards in `acquire` and `release`.

## Traps and wrong fixes

- Checking capacity only when creating a connection but not when reusing idle ones (reuse is fine, but the invariant still matters).
- Guarding acquire for close but leaving release unguarded.
- Making double release idempotent when the spec says it raises.
- Letting an invalid acquire create a connection before raising.

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
