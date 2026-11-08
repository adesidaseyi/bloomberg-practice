# Interviewer Guide - marlin

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
| M1 | `release` has no status guard |
| M2 | `commit` ignores expiry |
| M3 | `release` ignores expiry |
| M4 | `reserved_units` ignores expiry |
| M5 | `reserved_units` counts committed units |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about expiry before commit/release, double release, committed units, and what `reserved_units` means? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Can a committed or released reservation be released again? | No. Only `HELD` can be released. | M1 |
| Can an expired hold be committed? | No. Apply expiry before the commit guard. | M2 |
| Can an expired hold be released? | No. Expiry already releases it. | M3 |
| Should `reserved_units` apply expiry? | Yes. Expired holds are no longer reserved. | M4 |
| Do committed units count as reserved? | No. Only `HELD` units are reserved. | M5 |

## Bug inventory

### M1 - Release can return units twice

- **Spec rule:** Only a `HELD` reservation can be released.
- **Location:** `release` in each language.
- **Root cause:** The method adds the quantity back regardless of the reservation's current status.
- **Minimal fix:**

```python
if r.status != ResStatus.HELD:
    raise ValueError("only held reservations can be released")
self._available[r.sku] += r.qty
r.status = ResStatus.RELEASED
```
- **Failing-test recipe:** Reserve 5 units, release the reservation, then release it again. The second call should raise and available should be unchanged.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be released? (2) Does `release` inspect status? (3) It does not. (4) Show the guard.

### M2 - An expired hold can be committed

- **Spec rule:** Expiry is applied before a transition; an expired hold cannot be committed.
- **Location:** `commit` and the expiry helper in each language.
- **Root cause:** `commit` does not call the cleanup helper before checking `HELD`.
- **Minimal fix:**

```python
self._cleanup_expired()
if r.status != ResStatus.HELD:
    raise ValueError("only held reservations can be committed")
```
- **Failing-test recipe:** Reserve with a 10-second TTL, advance the clock to 10, then commit. The commit should raise and the reservation should be `RELEASED`.
- **Difficulty:** medium
- **Hint ladder:** (1) When does a hold expire? (2) Does `commit` apply expiry? (3) It reads the status without cleanup. (4) Show the cleanup call.

### M3 - An expired hold can be released

- **Spec rule:** Expiry is applied before a transition; an expired hold is already released.
- **Location:** `release` in each language.
- **Root cause:** `release` does not call the cleanup helper before the status guard.
- **Minimal fix:**

```python
self._cleanup_expired()
if r.status != ResStatus.HELD:
    raise ValueError("only held reservations can be released")
```
- **Failing-test recipe:** Reserve with a 10-second TTL, advance to 10, then release. The release should raise and available should already include the units.
- **Difficulty:** medium
- **Hint ladder:** (1) What happens to a hold at its TTL? (2) Does `release` apply expiry first? (3) It does not. (4) Show the cleanup call.

### M4 - Reserved units include expired holds

- **Spec rule:** `reserved_units` applies expiry and counts only live `HELD` units.
- **Location:** `reserved_units` in each language.
- **Root cause:** The read never runs cleanup, so expired holds still look reserved.
- **Minimal fix:**

```python
self._cleanup_expired()
return sum(
    r.qty for r in self._reservations.values()
    if r.sku == sku and r.status == ResStatus.HELD
)
```
- **Failing-test recipe:** Reserve 5 units, advance past the TTL, and assert `reserved_units(sku) == 0`.
- **Difficulty:** easy
- **Hint ladder:** (1) Should a read apply expiry? (2) Does `reserved_units` call cleanup? (3) It does not. (4) Show the cleanup call.

### M5 - Committed units still count as reserved

- **Spec rule:** Only `HELD` units are reserved; committed units have shipped.
- **Location:** `reserved_units` in each language.
- **Root cause:** The method returns `capacity - available`, which includes committed units because commit does not change available.
- **Minimal fix:**

```python
return sum(
    r.qty for r in self._reservations.values()
    if r.sku == sku and r.status == ResStatus.HELD
)
```
- **Failing-test recipe:** Reserve 5 units, commit the reservation, and assert `reserved_units(sku) == 0` while available is unchanged.
- **Difficulty:** medium
- **Hint ladder:** (1) What does 'reserved' mean after a commit? (2) How is `reserved_units` computed? (3) It uses capacity minus available, which still includes committed units. (4) Show the HELD-only sum.

## Acceptable alternative fixes

- A shared `_refresh(r)` helper that applies expiry to one reservation before a transition.
- Computing `reserved_units` from `HELD` records, or maintaining a separate held counter; both are valid if the invariant is clear.
- A distinct `EXPIRED` status is acceptable if the spec and status checks are updated consistently; this pack uses `RELEASED`.

## Cross-language notes

- C++ and Java have the same `cleanup()` helper; call it from `commit`, `release`, and `reserved_units`.
- Mirror the HELD-only sum in `reserved_units`, not `capacity - available`.

## Traps and wrong fixes

- Guarding `release` but not applying expiry first.
- Fixing `commit` expiry but leaving `release` able to act on an expired hold.
- Computing `reserved_units` from `capacity - available` after fixing only the expiry call.
- Returning units twice on a double release.

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
