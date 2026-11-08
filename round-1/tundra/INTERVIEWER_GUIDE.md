# Interviewer Guide - tundra

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
| T1 | `get` ignores expiry |
| T2 | `get` does not mark the key as used |
| T3 | `size` counts expired entries |
| T4 | `put` ignores updates to an existing key |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about expiry on read, read-recency, size semantics, and put-update behaviour? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Should get return an expired entry? | No. Treat it as missing. | T1 |
| Does get count as a use? | Yes. Move the key to most-recently-used. | T2 |
| Should size count expired entries? | No. Count live entries only. | T3 |
| Does put update an existing key? | Yes. Update the value and reset the TTL. | T4 |

## Bug inventory

### T1 - Expired values are still served

- **Spec rule:** `get` returns `None` for an expired entry.
- **Location:** `get` in each language.
- **Root cause:** The method returns the stored value without comparing the clock to `expires_at`.
- **Minimal fix:**

```python
if self._clock() >= e.expires_at:
    del self._data[key]
    return None
return e.value
```
- **Failing-test recipe:** Put a key with a 10-second TTL, advance the clock to 10, and assert `get` returns `None`.
- **Difficulty:** easy
- **Hint ladder:** (1) What makes an entry live? (2) Does `get` read `expires_at`? (3) It does not. (4) Show the expiry check.

### T2 - LRU eviction picks the wrong key

- **Spec rule:** A successful read marks the entry most-recently-used.
- **Location:** `get` in each language.
- **Root cause:** The method returns the value without moving the key to the most-recently-used end.
- **Minimal fix:**

```python
self._data.move_to_end(key)
return e.value
```
- **Failing-test recipe:** With capacity 2, put `a`, put `b`, get `a`, then put `c`. `a` should still be present and `b` should be evicted.
- **Difficulty:** medium
- **Hint ladder:** (1) What does a read mean for LRU order? (2) Does `get` update order? (3) It does not. (4) Show the move-to-end.

### T3 - Dead entries inflate the size

- **Spec rule:** `size` counts live entries only.
- **Location:** `size` in each language.
- **Root cause:** The method returns the raw container size without purging expired entries.
- **Minimal fix:**

```python
now = self._clock()
return sum(1 for e in self._data.values() if e.expires_at > now)
```
- **Failing-test recipe:** Put two keys with a 10-second TTL, advance to 10, and assert `size() == 0`.
- **Difficulty:** easy
- **Hint ladder:** (1) Should expired entries count? (2) What does `size` return? (3) The raw map length. (4) Show the live-entry count.

### T4 - Updating a key has no effect

- **Spec rule:** `put` updates the value and resets the TTL for an existing key.
- **Location:** `put` in each language.
- **Root cause:** When the key already exists, the method moves it to the end and returns without writing the new value or expiry.
- **Minimal fix:**

```python
self._data[key] = _Entry(value, self._clock() + self._ttl)
self._data.move_to_end(key)
```
- **Failing-test recipe:** Put `k = 1`, then put `k = 2`, and assert `get(k) == 2`. Advance past the original TTL and assert the updated entry is still live.
- **Difficulty:** easy
- **Hint ladder:** (1) What should put do to an existing key? (2) What does the existing-key branch do? (3) It only reorders and returns. (4) Show the update.

## Acceptable alternative fixes

- Purging expired entries eagerly on every operation versus lazily on read; both are valid if size and eviction see only live entries.
- Using an ordered map plus a secondary structure is fine; keep get/put O(1) on average.

## Cross-language notes

- C++ uses a list plus index map; mirror the expiry check, move-to-back on get, live-size count, and update on put.
- Java uses a LinkedHashMap; mirror the same order and expiry semantics.

## Traps and wrong fixes

- Deleting expired entries only in `get` but leaving `size` stale.
- Updating recency on `put` but not on `get`.
- Treating an expired entry as a hit because the value is still in the map.
- Evicting the most-recently-used entry instead of the least-recently-used one.

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
