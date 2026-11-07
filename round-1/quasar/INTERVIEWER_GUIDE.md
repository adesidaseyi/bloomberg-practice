# Interviewer Guide - quasar

> **INTERVIEWER ONLY.** This file is the answer key. Do not give it to the
> candidate, and do not leave it open on a shared screen.

## Pack at a glance

- Round 1: one stateful service, 35 minutes.
- Candidate-facing spec: `README.md`.
- Candidate-facing framing: `CANDIDATE_BRIEF.md`.
- Clarifying questions: `PROJECT_MANAGER_NOTES.md` (candidate should ask these).
- Languages: `python/`, `cpp/`, `java/`; the same five defects exist in each.
- Candidate deliverable: a failing test per defect, a narrow fix, and an
  explanation of the invariant each fix protects.

| ID | Defect |
| --- | --- |
| Q1 | `allow` never rolls an elapsed window |
| Q2 | `remaining` ignores an elapsed window |
| Q3 | `reset` is a no-op |
| Q4 | denied requests consume quota |
| Q5 | unseen keys report zero remaining |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the exact boundary, denied requests, `reset`, and unseen keys before coding? |
| 5-10 | Map the code | Can they explain what the `_Window` state contains and which methods read it? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Sliding versus fixed window, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Is this fixed-window or sliding-window? | Fixed-window. A sliding window would need per-request timestamps. | Q1, Q2 |
| Is the window over at exactly `window_seconds`? | Yes. `now - start >= window_seconds` starts a fresh window. | Q1 |
| What should `remaining` report after the window has elapsed? | The full `limit`. | Q2 |
| Does a denied request consume quota? | No. A denial changes nothing. | Q4 |
| Does `reset` start a new window immediately? | It discards the key's window; the next request opens a fresh one at that instant. | Q3 |
| What does `remaining` report for an unseen key? | The full `limit`. | Q5 |
| Does `reset` affect one key or all keys? | Only the addressed key. | Q3 |
| Is thread safety required? | Not in this exercise, but the candidate should be able to explain the race. | - |

## Bug inventory

### Q1 - `allow` never rolls an elapsed window

- **Spec rule:** a window is over at `now - start >= window_seconds`; the next
  request opens a fresh window.
- **Location:** `python/ratelimit.py`, `RateLimiter.allow`;
  `cpp/ratelimit.hpp`, `allow`; `java/RateLimit.java`, `allow`.
- **Root cause:** `allow` reads the count but never compares the clock to the
  stored window start, so the count only ever rises.
- **Minimal fix (Python):**

  ```python
  def allow(self, key: str) -> bool:
      now = self._clock()
      st = self._state.get(key)
      if st is None or now - st.start >= self._window:
          st = _Window(now, 0)
          self._state[key] = st
      if st.count < self._limit:
          st.count += 1
          return True
      return False
  ```

- **Failing-test recipe:** with `limit=1, window=10`, allow at `t=0`, advance
  the clock to `t=10`, and assert `allow` is `True` again.
- **Difficulty:** medium.
- **Hint ladder:** (1) "What ends a window?" (2) "Where does `allow` compare
  `now` to the window start?" (3) "It never does; the count only rises." (4)
  Show the rollover branch.

### Q2 - `remaining` ignores an elapsed window

- **Spec rule:** an elapsed window reports the full `limit`.
- **Location:** `remaining` in each language.
- **Root cause:** the method returns `limit - count` without checking whether the
  stored window is still current.
- **Minimal fix (Python):**

  ```python
  def remaining(self, key: str) -> int:
      st = self._state.get(key)
      if st is None:
          return self._limit
      if self._clock() - st.start >= self._window:
          return self._limit
      return self._limit - st.count
  ```

- **Failing-test recipe:** with `limit=3`, allow once, advance the clock by
  `window_seconds`, and assert `remaining` is `3`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What should remaining say after a window ends?" (2)
  "Does `remaining` know when the window started?" (3) "It reads the count but
  not the clock." (4) Show the elapsed-window branch.

### Q3 - `reset` is a no-op

- **Spec rule:** `reset(key)` discards only that key's window.
- **Location:** `reset` in each language.
- **Root cause:** the body is empty.
- **Minimal fix (Python):**

  ```python
  def reset(self, key: str) -> None:
      self._state.pop(key, None)
  ```

  Setting `count = 0` and `start = now` is also acceptable if the candidate
  explains that the next request gets a full fresh window.
- **Failing-test recipe:** exhaust a key's quota, call `reset`, then assert
  `allow` is `True` and `remaining` is `limit - 1`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What is `reset` supposed to change?" (2) "Read the body
  of `reset`." (3) "It does nothing." (4) Show the pop/reset.

### Q4 - denied requests consume quota

- **Spec rule:** a denied request consumes nothing.
- **Location:** `allow` in each language.
- **Root cause:** the counter is incremented before the limit check, so a denied
  request still raises the count. `remaining` can go negative.
- **Minimal fix (Python):** check `st.count < self._limit` first, then increment
  only on the allowed path.
- **Failing-test recipe:** with `limit=2`, call `allow` twice (true, true), then
  once more (false), and assert `remaining` is `0`, not `-1`. Call `allow` again
  and assert it is still `False` and `remaining` is still `0`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "Does a denied request change the state?" (2) "When is the
  counter incremented?" (3) "Before the check, so denials consume quota." (4)
  Show the check-then-increment order.

### Q5 - unseen keys report zero remaining

- **Spec rule:** an unseen key has the full `limit`.
- **Location:** `remaining` in each language.
- **Root cause:** the missing-key branch returns `0` instead of `limit`.
- **Minimal fix (Python):** return `self._limit` when the key has no state.
- **Failing-test recipe:** create a new limiter and assert
  `remaining("never-seen") == limit`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What should an unseen key report?" (2) "What does
  `remaining` return when the key is absent?" (3) "It returns zero." (4) Show
  the corrected branch.

## Acceptable alternative fixes

- Storing a window object versus two parallel dicts; either is fine.
- `reset` removing the key versus resetting `count=0` and `start=now`. Both
  satisfy "the next request gets a fresh window"; ask the candidate to explain
  the difference.
- A helper such as `_window_for(key)` that both `allow` and `remaining` use to
  detect rollover. This is a good design answer.
- A sliding-window implementation is out of scope; accept a discussion of it,
  not a rewrite.

## Traps and wrong fixes

- Fixing only `allow` and leaving `remaining` stale.
- Fixing only `remaining` and leaving `allow` blocked forever.
- Making `reset` clear every key instead of one.
- Clamping `remaining` to zero instead of preventing denied requests from
  incrementing the count.
- Using `>` instead of `>=` at the boundary.
- Treating a denied request as consuming quota because "the request happened".

## Cross-language notes

The C++ and Java fixes are mechanical:

- in `allow`, roll when `now - window.start >= window` and check the limit before
  incrementing;
- in `remaining`, return the full limit when the key is absent or the window has
  elapsed;
- in `reset`, erase the key (`state_.erase(key)` / `state.remove(key)`) or reset
  its count and start.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1-2 defects | Finds 3-4 | Finds all 5 |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the exact boundary, and that denials do not consume quota |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, complexity, fixed versus sliding windows, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Explain the window state in this limiter. Do not suggest fixes yet."
- "Given this spec, what tests would prove the boundary and the denial rule?"
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
