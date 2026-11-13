# Interviewer Guide - quill

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
| Q1 | `bid` accepts bids after `closes_at` |
| Q2 | `bid` accepts an amount below the reserve |
| Q3 | a lower bid replaces the leading bid |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the closing boundary, reserve equality, strict improvement, and lazy close before coding? |
| 5-10 | Map the code | Can they point to the bid validation, the leading bid, and the close transition? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Is the auction closed at exactly `closes_at`? | Yes. `now >= closes_at` is closed. | Q1 |
| Is a bid equal to the reserve acceptable? | Yes. The bid must be at least the reserve. | Q2 |
| Must a bid strictly exceed the current highest? | Yes. An equal or lower bid is rejected. | Q3 |
| What should a bid after the close do? | Raise `ValueError` and leave the auction unchanged. | Q1 |
| Does `status()` apply the close? | Yes. `bid()` and `winner()` apply it too. | Q1 |
| Is `winner()` ever non-`None` while `OPEN`? | No. It is `None` until the auction closes. | - |
| What is the winner when no bid was accepted? | `None`. | - |
| Is the clock injected and monotonic? | Injected for tests; the default is monotonic. | - |

## Bug inventory

### Q1 - Late bids are accepted

- **Spec rule:** a bid is accepted only while the auction is `OPEN`, and the
  auction is closed once `now >= closes_at`.
- **Location:** `python/auction.py`, `AuctionService.bid`; `cpp/auction.hpp`,
  `bid`; `java/Auction.java`, `bid`.
- **Root cause:** `bid` never applies or checks the closing transition, so it
  accepts bids after the deadline.
- **Minimal fix (Python):**

  ```python
  if self.status() is AuctionStatus.CLOSED:
      raise ValueError("auction is closed")
  ```

- **Failing-test recipe:** with `closes_at=10` and a fake clock at `t=10`,
  assert `status()` is `CLOSED`, then assert `bid` raises. With no bid before
  the close, `winner()` must stay `None`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What ends the auction?" (2) "Does `bid` check the
  clock?" (3) "It does not; it only validates the amount." (4) Show the status
  guard.

### Q2 - Bids below the reserve are accepted

- **Spec rule:** an accepted bid is at least the reserve.
- **Location:** `bid` in each language.
- **Root cause:** the method validates that the amount is positive but never
  compares it with `reserve_cents`.
- **Minimal fix (Python):**

  ```python
  if cents < self._reserve:
      raise ValueError("bid is below the reserve")
  ```

- **Failing-test recipe:** with a reserve of 100, assert a bid of 99 raises and
  leaves `highest_bid()` unchanged; assert a bid of 100 is accepted.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What is the reserve for?" (2) "Which bid amount is
  acceptable?" (3) "The code never reads the reserve." (4) Show the comparison.

### Q3 - A lower bid replaces the leader

- **Spec rule:** a new bid must be strictly greater than the current highest.
- **Location:** `bid` in each language.
- **Root cause:** the highest bid is overwritten unconditionally, and there is
  no comparison with the current highest bid.
- **Minimal fix (Python):**

  ```python
  if self._highest is not None and cents <= self._highest.amount_cents:
      raise ValueError("bid must exceed the current highest")
  ```

  The later assignment to `_highest` is then safe.
- **Failing-test recipe:** bid 100, then bid 90. The second bid should raise,
  and `highest_bid().amount_cents` should remain 100.
- **Difficulty:** medium.
- **Hint ladder:** (1) "How does a new bid compare with the leader?" (2) "Which
  bid does the code keep?" (3) "It keeps the latest bid." (4) Show the
  strict-greater guard.

## Acceptable alternative fixes

- Checking the deadline directly with `now < closes_at` instead of calling
  `status()`.
- Validating the reserve and the current highest in either order, as long as a
  rejected bid changes nothing.
- Keeping the highest bid by comparing amounts on assignment instead of
  rejecting lower bids. The spec requires the lower bid to raise, so a pure
  max-update without a guard is not sufficient.

## Cross-language notes

The C++ and Java fixes are mechanical:

- apply the close in `bid` / `bid` and reject the bid;
- compare the amount with the reserve;
- compare the amount with the current highest and reject equal or lower bids.

Keep bid amounts as integer cents and preserve the injected clock.

## Traps and wrong fixes

- Allowing a bid equal to the current highest instead of requiring a strict
  increase.
- Requiring a bid to be strictly above the reserve instead of at least the
  reserve.
- Checking the deadline in `status()` but not in `bid()`.
- Taking a snapshot of the winner at close and then letting a late bid change
  the reported winner; the spec closes bidding, so late bids must raise.
- Forgetting to leave the leading bid unchanged after a rejected bid.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1 defect | Finds 2 | Finds all three |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the exact closing boundary, and state preservation after rejection |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, transitions, complexity, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Map the bidding lifecycle in this file. Do not suggest fixes yet."
- "Given this spec, what tests would prove the reserve and time rules?"
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
