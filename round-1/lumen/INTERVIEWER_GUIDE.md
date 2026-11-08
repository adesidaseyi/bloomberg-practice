# Interviewer Guide - lumen

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
| L1 | `start` has no source-state guard |
| L2 | `complete` has no source-state guard |
| L3 | `fail` has no source-state guard |
| L4 | `fail` retries one time too many |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask whether all three transitions are guarded and where the attempt budget boundary sits? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Can a running or done job be started? | No. Only `QUEUED`. | L1 |
| Can a queued job be completed? | No. Only `RUNNING`. | L2 |
| Can a queued or done job fail? | No. Only `RUNNING`. | L3 |
| After how many failures does a job become FAILED? | When attempts reach `max_attempts`, using `<` for the retry branch. | L4 |

## Bug inventory

### L1 - A running or finished job can be started again

- **Spec rule:** Only a `QUEUED` job can start.
- **Location:** `start` in each language.
- **Root cause:** The status is overwritten with `RUNNING` without checking the source state.
- **Minimal fix:**

```python
if job.status != JobStatus.QUEUED:
    raise ValueError("only queued jobs can start")
```
- **Failing-test recipe:** Start a job twice. The second start should raise and the status should remain `RUNNING`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can start? (2) Does `start` inspect status? (3) It does not. (4) Show the guard.

### L2 - A non-running job can be completed

- **Spec rule:** Only a `RUNNING` job can complete.
- **Location:** `complete` in each language.
- **Root cause:** The status is overwritten with `DONE` without checking the source state.
- **Minimal fix:**

```python
if job.status != JobStatus.RUNNING:
    raise ValueError("only running jobs can complete")
```
- **Failing-test recipe:** Enqueue a job and complete it without starting it. The complete should raise and the status should remain `QUEUED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can complete? (2) Does `complete` inspect status? (3) It does not. (4) Show the guard.

### L3 - A non-running job can fail

- **Spec rule:** Only a `RUNNING` job can fail.
- **Location:** `fail` in each language.
- **Root cause:** The method applies retry logic without checking the current status.
- **Minimal fix:**

```python
if job.status != JobStatus.RUNNING:
    raise ValueError("only running jobs can fail")
```
- **Failing-test recipe:** Enqueue a job and fail it without starting it. The fail should raise and the status should remain `QUEUED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can fail? (2) Does `fail` inspect status? (3) It does not. (4) Show the guard.

### L4 - Attempt budget is off by one

- **Spec rule:** A failure retries only while `attempts < max_attempts`; otherwise it becomes `FAILED`.
- **Location:** `fail` in each language.
- **Root cause:** The retry branch uses `attempts <= max_attempts` instead of `attempts < max_attempts`.
- **Minimal fix:**

```python
if job.attempts < self._max:
    job.status = JobStatus.QUEUED
else:
    job.status = JobStatus.FAILED
```
- **Failing-test recipe:** With `max_attempts=2`, start and fail twice. After the second failure the job should be `FAILED`, not `QUEUED`.
- **Difficulty:** medium
- **Hint ladder:** (1) How many starts are allowed? (2) When does a failure stop retrying? (3) The branch uses `<=`. (4) Show the `<` comparison.

## Acceptable alternative fixes

- A transition table for job status instead of separate guards.
- Checking both status and attempt budget inside `start`; both checks are valid and may be combined.

## Cross-language notes

- C++ and Java mirror the same QUEUED/RUNNING guards and the same `<` boundary in `fail`.

## Traps and wrong fixes

- Guarding start/complete but leaving fail unguarded.
- Using `<=` in the retry branch and allowing one extra attempt.
- Letting an invalid transition change status before raising.
- Treating `FAILED` as restartable when the spec says it is terminal.

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
