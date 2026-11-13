# Interviewer Guide - juniper

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
| J1 | `settle` ignores the settlement date |
| J2 | `fail` accepts a terminal trade |
| J3 | pending notional includes settled and failed trades |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the settlement boundary, terminal states, and which trades count toward pending notional? |
| 5-10 | Map the code | Can they point to the clock check, the status guards, and the notional filter? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Does a trade settle at exactly `settle_on`? | Yes. `now >= settle_on` is settleable. | J1 |
| Can a settled trade settle again? | No. Only `PENDING` can settle. | J2 |
| Can a failed trade be failed again? | No. `FAILED` is terminal. | J2 |
| Can a settled trade fail? | No. `SETTLED` is terminal. | J2 |
| Which trades count toward pending notional? | Only `PENDING` trades for the account. | J3 |
| Is notional `qty * price_cents`? | Yes, in integer cents. | J3 |
| Can a trade be booked with a past settlement date? | Yes. It is immediately settleable. | J1 |
| Is the clock injected and monotonic? | Injected for tests; the default is monotonic. | - |

## Bug inventory

### J1 - Trades settle before their date

- **Spec rule:** a trade settles only when `now >= settle_on`.
- **Location:** `python/settlement.py`, `SettlementService.settle`;
  `cpp/settlement.hpp`, `settle`; `java/Settlement.java`, `settle`.
- **Root cause:** the method checks the source state but never compares the
  injected clock with the trade's `settle_on`.
- **Minimal fix (Python):**

  ```python
  if self._clock() < trade.settle_on:
      raise ValueError("trade has not reached its settlement date")
  ```

- **Failing-test recipe:** book a trade with `settle_on=100` using a fake clock
  at `t=50`, assert `settle` raises and the status is still `PENDING`; advance
  to `t=100` and assert it settles.
- **Difficulty:** easy.
- **Hint ladder:** (1) "When may a trade settle?" (2) "Which clock does the
  service hold?" (3) "`settle` never reads it." (4) Show the date comparison.

### J2 - A settled trade can be failed

- **Spec rule:** only a `PENDING` trade can fail; `SETTLED` and `FAILED` are
  terminal.
- **Location:** `fail` in each language.
- **Root cause:** the method overwrites the status without checking it.
- **Minimal fix (Python):**

  ```python
  if trade.status is not TradeStatus.PENDING:
      raise ValueError("only pending trades can fail")
  ```

- **Failing-test recipe:** book a trade with `settle_on=0` and a fake clock at
  `t=0`, settle it, then assert `fail` raises and the status remains `SETTLED`.
- **Difficulty:** easy.
- **Hint ladder:** (1) "Which states may fail?" (2) "Does `fail` inspect the
  status?" (3) "It overwrites it." (4) Show the terminal-state guard.

### J3 - Pending notional never drops

- **Spec rule:** pending notional covers only `PENDING` trades.
- **Location:** `pending_notional` / `pendingNotional` in each language.
- **Root cause:** the sum filters by account but not by status.
- **Minimal fix (Python):**

  ```python
  return sum(
      trade.qty * trade.price_cents
      for trade in self._trades.values()
      if trade.account_id == account_id and trade.status is TradeStatus.PENDING
  )
  ```

- **Failing-test recipe:** book two trades for one account, settle one, and
  assert `pending_notional` equals only the other trade's `qty * price_cents`.
  Fail the remaining trade and assert pending notional becomes zero.
- **Difficulty:** easy.
- **Hint ladder:** (1) "What does pending mean?" (2) "Which trades does the sum
  include?" (3) "Every trade for the account." (4) Show the status filter.

## Acceptable alternative fixes

- Applying the date check before or after the source-state check, provided an
  invalid transition changes nothing.
- A shared `_require_pending(trade)` helper used by `settle` and `fail`.
- Filtering pending notional with a status compare rather than an enum identity;
  any correct expression is fine.

## Cross-language notes

The C++ and Java fixes are mechanical:

- in `settle`, compare `clock_()` / `clock.getAsDouble()` with `settle_on` and
  raise before changing state;
- in `fail`, reject anything that is not `PENDING`;
- in `pending_notional` / `pendingNotional`, add the `PENDING` filter.

Keep quantities and prices as integers, and keep the injected clock.

## Traps and wrong fixes

- Checking the settlement date only in `book` instead of in `settle`.
- Making `fail` a no-op for terminal trades when the spec says it raises.
- Including failed trades in pending notional because they "never settled".
- Using floating-point money or changing the public API.
- Letting an invalid settle or fail change state before raising.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1 defect | Finds 2 | Finds all three |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the exact settlement boundary, and state preservation after invalid transitions |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, transitions, complexity, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Map the trade lifecycle in this file. Do not suggest fixes yet."
- "Given this spec, what tests would prove the settlement date and notional rules?"
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
