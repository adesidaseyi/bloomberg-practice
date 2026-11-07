# Interviewer Guide - zephyr

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
| Z1 | `activate` has no source-state guard |
| Z2 | `cancel` accepts terminal states |
| Z3 | expiry is never applied |
| Z4 | suspended subscriptions read as entitled |
| Z5 | `suspend` accepts a trial |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the expiry boundary, terminal states, suspended entitlement, and suspend-from-trial before coding? |
| 5-10 | Map the code | Can they state the transition table and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Is the trial expired at exactly `expires_at`? | Yes. `now >= expires_at` is expired. | Z3 boundary test |
| Can `activate` be called on a suspended subscription? | No. Use `resume`. | Z1 |
| Can `activate` revive a cancelled or expired subscription? | No. Both are terminal. | Z1, Z3 |
| Is `cancel` idempotent? | No. A second cancel raises. | Z2 |
| Does `is_entitled` change the stored status? | Yes. Lazy expiry materialises `EXPIRED`. | Z3 |
| Is a suspended subscription entitled? | No. Suspension removes access. | Z4 |
| Can a trial be suspended? | No. Only `ACTIVE` can be suspended. | Z5 |
| Can one user hold multiple live subscriptions? | Treat this as out of scope unless the candidate raises it; the pack does not plant a duplicate-trial bug. | - |

## Bug inventory

### Z1 - `activate` accepts every state

- **Spec rule:** `activate` is valid only from an unexpired `TRIAL`.
- **Location:** `python/subscriptions.py`, `SubscriptionService.activate`;
  `cpp/subscriptions.hpp`, `activate`; `java/Subscriptions.java`, `activate`.
- **Root cause:** there is no source-state guard. Any status is overwritten with
  `ACTIVE`, so `CANCELLED` and `EXPIRED` can be revived, and `SUSPENDED` can
  bypass `resume`.
- **Minimal fix (Python):**

  ```python
  def activate(self, sub_id: str) -> Subscription:
      sub = self._get(sub_id)
      if sub.status != SubStatus.TRIAL:
          raise ValueError("only a trial can be activated")
      sub.status = SubStatus.ACTIVE
      sub.expires_at = None
      return sub
  ```

  If expiry is applied in `_get`, an expired trial has already become
  `EXPIRED` and the guard rejects it.
- **Failing-test recipe:**

  ```python
  sub = service.start_trial("u")
  service.cancel(sub.sub_id)
  with pytest.raises(ValueError):
      service.activate(sub.sub_id)
  assert sub.status == SubStatus.CANCELLED
  ```

  Also test `SUSPENDED` and `EXPIRED` sources if time allows.
- **Difficulty:** easy.
- **Hint ladder:** (1) "Which source states does the spec allow?" (2) "Where
  does `activate` check its input state?" (3) "It does not; any status becomes
  active." (4) Show the guard.

### Z2 - `cancel` accepts terminal states

- **Spec rule:** `CANCELLED` and `EXPIRED` are terminal; a second cancel raises
  and leaves state unchanged.
- **Location:** `cancel` in each language.
- **Root cause:** no terminal-state guard; the status is always overwritten with
  `CANCELLED`.
- **Minimal fix (Python):**

  ```python
  def cancel(self, sub_id: str) -> Subscription:
      sub = self._get(sub_id)
      if sub.status in (SubStatus.CANCELLED, SubStatus.EXPIRED):
          raise ValueError("subscription is already terminal")
      sub.status = SubStatus.CANCELLED
      sub.expires_at = None
      return sub
  ```

- **Failing-test recipe:** cancel once, then assert the second call raises and
  the status is still `CANCELLED`. Also check that cancelling an `EXPIRED`
  subscription raises.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What does the spec say about terminal states?" (2) "What
  does `cancel` do before changing status?" (3) "Nothing; it always overwrites."
  (4) Show the guard.

### Z3 - expiry is never applied

- **Spec rule:** any read or transition applies due expiry; at
  `now >= expires_at` the status is `EXPIRED` and the subscription is not
  entitled.
- **Location:** `_cleanup_expired` is defined but never called; `is_entitled`
  treats every `TRIAL` as entitled.
- **Root cause:** the expiry helper is dead code and the read path never checks
  the clock.
- **Minimal fix (Python):** apply expiry before doing the operation's work. A
  clean central place is `_get`, because every public operation uses it:

  ```python
  def _get(self, sub_id: str) -> Subscription:
      sub = self._subs.get(sub_id)
      if sub is None:
          raise ValueError("subscription not found")
      self._cleanup_expired()
      return sub
  ```

  An equally acceptable fix is a per-subscription `_refresh(sub)` called at the
  start of each public method. The key requirement is that `is_entitled`
  returns `False` and the stored status becomes `EXPIRED`.
- **Failing-test recipe:**

  ```python
  clock = FakeClock()
  service = SubscriptionService(trial_ttl_seconds=10, clock=clock)
  sub = service.start_trial("u")
  clock.now = 10
  assert service.is_entitled(sub.sub_id) is False
  assert sub.status == SubStatus.EXPIRED
  ```

- **Difficulty:** medium. The candidate must decide where lazy expiry belongs
  without changing the public API.
- **Hint ladder:** (1) "When is expiry supposed to happen?" (2) "Find the
  expiry helper. Who calls it?" (3) "Nobody; it is dead code, and the read path
  ignores the clock." (4) Show the `_get`/`_refresh` placement.
- **Notes:** `_cleanup_expired` already uses `<=`, so the exact boundary works
  once it is called. Do not accept a fix that only checks `expires_at` inside
  `is_entitled` but leaves `activate`/`cancel` able to act on a stale `TRIAL`;
  the spec says all reads and transitions apply expiry.

### Z4 - suspended subscriptions read as entitled

- **Spec rule:** only `ACTIVE` and an unexpired `TRIAL` are entitled.
- **Location:** `is_entitled` in each language.
- **Root cause:** `SUSPENDED` is included in the true branch.
- **Minimal fix (Python):** remove the `SUSPENDED` branch and keep `ACTIVE`
  plus unexpired `TRIAL`.
- **Failing-test recipe:** start a trial, activate it, suspend it, then assert
  `is_entitled` is `False`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "Does suspension remove access?" (2) "Which statuses does
  `is_entitled` return true for?" (3) "It includes `SUSPENDED`." (4) Show the
  corrected conditions.

### Z5 - `suspend` accepts a trial

- **Spec rule:** only `ACTIVE` can be suspended.
- **Location:** `suspend` in each language.
- **Root cause:** the guard allows `TRIAL` as well as `ACTIVE`.
- **Minimal fix (Python):**

  ```python
  if sub.status != SubStatus.ACTIVE:
      raise ValueError("only active subscriptions can be suspended")
  ```

- **Failing-test recipe:** start a trial, assert `suspend` raises, and assert
  the status is still `TRIAL`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What is the source state for suspension?" (2) "Which
  states does the guard accept?" (3) "It accepts `TRIAL` too." (4) Show the
  single-state guard.

## Acceptable alternative fixes

- Applying expiry in `_get` versus a dedicated `_refresh` in every public
  method. Both are fine if every read and transition observes expiry.
- A transition table/dict instead of separate guards, provided invalid
  transitions raise and leave state unchanged.
- `_cleanup_expired` sweeping every subscription versus refreshing only the
  addressed one. The sweep is O(n) per call; accept it for this exercise if the
  candidate can state the trade-off.

## Traps and wrong fixes

- Wrapping `activate` in `try/except` instead of adding a source-state guard.
- Making `cancel` idempotent when the spec says a second cancel raises.
- Fixing `is_entitled` but leaving `activate` and `cancel` able to act on an
  expired `TRIAL`.
- Changing the public API, adding a new status, or redesigning the service.
- Letting an invalid transition change state before raising.

## Cross-language notes

The C++ and Java fixes are mechanical:

- call the existing `cleanup()` from `get()` (or from each public method) to apply
  expiry;
- guard `activate` with `status == TRIAL`;
- guard `cancel` against `CANCELLED` and `EXPIRED`;
- guard `suspend` with `status == ACTIVE`;
- remove `SUSPENDED` from the true branches in `is_entitled`/`isEntitled`.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1-2 defects | Finds 3-4 | Finds all 5 |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the exact boundary, and state-preservation after invalid transitions |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, transition table, complexity, and concurrency |
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
