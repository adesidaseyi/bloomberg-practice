# Interviewer Guide - ember

> **INTERVIEWER ONLY.** This file is the answer key. Do not give it to the
> candidate, and do not leave it open on a shared screen.

## Pack at a glance

- Round 1: one stateful service, 35 minutes.
- Candidate-facing spec: `README.md`.
- Candidate-facing framing: `CANDIDATE_BRIEF.md`.
- Clarifying questions: `PROJECT_MANAGER_NOTES.md` (candidate should ask these).
- Languages: `python/`, `cpp/`, `java/`; the same three defects exist in each.
- Candidate deliverable: a failing test per defect, a narrow fix, and an
  explanation of the invariant each fix protects.

| ID | Defect |
| --- | --- |
| E1 | `allow` admits every call while `HALF_OPEN` |
| E2 | a success while `CLOSED` does not clear the failure count |
| E3 | `reset` leaves the failure count behind |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about consecutive failures, the single probe, reset, and the cooldown boundary before coding? |
| 5-10 | Map the code | Can they name the state fields and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Are failures counted consecutively, or over the breaker's lifetime? | Consecutive. A success while `CLOSED` clears the run. | E2 |
| How many calls may `HALF_OPEN` admit? | Exactly one probe until its result is recorded. | E1 |
| Does `allow()` apply the cooldown transition? | Yes, and `state()` does too. | E1 |
| Does a failed probe restart the cooldown? | Yes. The breaker reopens at that instant. | - |
| What does `reset()` clear? | The state, failure count, open timestamp, and probe count. | E3 |
| Is a result recorded while `OPEN` meaningful? | No. It is ignored and the breaker stays `OPEN`. | - |
| Is the clock injected and monotonic? | Injected for tests; the default is monotonic. | - |
| Are calls admitted before the breaker opened still recorded? | Treat their results as ignored while `OPEN`. | - |

## Bug inventory

### E1 - A half-open breaker admits every call

- **Spec rule:** `HALF_OPEN` admits exactly one probe until the result is
  recorded.
- **Location:** `python/breaker.py`, `CircuitBreaker.allow`; `cpp/breaker.hpp`,
  `allow`; `java/Breaker.java`, `allow`.
- **Root cause:** the `HALF_OPEN` branch returns `True` without consulting or
  incrementing the probe counter.
- **Minimal fix (Python):**

  ```python
  if self._state is BreakerState.HALF_OPEN:
      if self._probes >= 1:
          return False
      self._probes += 1
      return True
  ```

- **Failing-test recipe:** with a fake clock, drive the breaker to `OPEN`, advance
  past the cooldown, then assert `allow()` is `True` once and `False` on the next
  call. Record a probe result to leave the state clean.
- **Difficulty:** easy.
- **Hint ladder:** (1) "How many probes should half-open admit?" (2) "Does
  `allow` track the probes it admits?" (3) "It returns true every time." (4) Show
  the counter guard.

### E2 - Intermittent failures accumulate across successes

- **Spec rule:** a success while `CLOSED` clears the consecutive-failure count.
- **Location:** `record_success` in each language.
- **Root cause:** the failure count is reset only inside the `HALF_OPEN` branch,
  so the `CLOSED` path leaves it untouched.
- **Minimal fix (Python):** reset the count on every success, not only a probe:

  ```python
  def record_success(self) -> None:
      if self._state is BreakerState.HALF_OPEN:
          self._state = BreakerState.CLOSED
          self._opened_at = None
      if self._state is BreakerState.CLOSED:
          self._failures = 0
      self._probes = 0
  ```

- **Failing-test recipe:** with `failure_threshold=3`, record failure, success,
  failure, success, failure. Assert the breaker is still `CLOSED` and
  `failure_count() == 1`.
- **Difficulty:** medium.
- **Hint ladder:** (1) "What does 'consecutive' mean?" (2) "Which method should
  clear the run?" (3) "It only clears it on the half-open path." (4) Show the
  unconditional reset for the closed path.

### E3 - `reset` leaves the breaker primed to open

- **Spec rule:** `reset()` returns to `CLOSED` and clears the failure count, the
  open timestamp, and the probe count.
- **Location:** `reset` in each language.
- **Root cause:** the method clears the state, timestamp, and probes but not the
  failure count. One more failure can immediately reach the threshold.
- **Minimal fix (Python):**

  ```python
  def reset(self) -> None:
      self._state = BreakerState.CLOSED
      self._failures = 0
      self._opened_at = None
      self._probes = 0
  ```

- **Failing-test recipe:** open the breaker, call `reset()`, and assert
  `failure_count() == 0`. Then record one failure and assert the breaker is still
  `CLOSED`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What does the spec say reset clears?" (2) "Which fields
  does `reset` touch?" (3) "It leaves the failure count." (4) Show the missing
  assignment.

## Acceptable alternative fixes

- A shared `_open()` / `_close()` helper that sets the state and counters in one
  place.
- Tracking only the current run and deriving `failure_count()` from it; any
  representation is valid if the reported values match the spec.
- Applying the cooldown transition through a `_refresh()` helper called by both
  `allow()` and `state()`.

## Cross-language notes

The C++ and Java fixes are mechanical:

- add the probe-count guard to `allow` in each language;
- clear the failure count on a successful call in `record_success` /
  `recordSuccess` when the state is not `OPEN`;
- clear `failures_` / `failures` in `reset`.

Keep the injected clock and the default threshold and cooldown. Do not rename
public methods.

## Traps and wrong fixes

- Fixing `reset` but leaving the `CLOSED` success path.
- Letting `allow()` enter `HALF_OPEN` but returning `False` on the same call; the
  first half-open call is the probe and returns `True`.
- Treating `failure_count()` as lifetime failures rather than the current run.
- Admitting a probe without consuming the single slot.
- Changing the cooldown on success instead of on a failed probe.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1 defect | Finds 2 | Finds all three |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the cooldown boundary, and state preservation after invalid results |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, transitions, complexity, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Map the state machine in this file. Do not suggest fixes yet."
- "Given this spec, what tests would prove each transition rule?"
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
