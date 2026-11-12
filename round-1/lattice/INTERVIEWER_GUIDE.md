# Interviewer Guide - lattice

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
| L1 | trades print at the incoming limit instead of the resting price |
| L2 | the newest order wins within a price level |
| L3 | the sweep stops at the first price level |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about the execution price, time priority, level sweeping, the remainder, and the crossed-book invariant? |
| 5-10 | Map the code | Can they explain how the book is stored, how the best opposite order is chosen, and where status changes? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Price levels, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Does a trade print at the resting order's price or the incoming limit? | The resting order's price. | L1 |
| Within one price level, which order has priority? | The oldest order, by arrival sequence. | L2 |
| Must a marketable order sweep successive price levels? | Yes, while it still crosses. | L3 |
| What happens to the unfilled remainder? | It rests at the incoming limit price. | - |
| Can the resting book ever be crossed? | No. `best_bid < best_ask` whenever both sides are present. | L3 |
| Is cancel idempotent? | No. A second cancel, or cancelling a filled order, raises. | - |
| Are prices and quantities integers? | Integer cents and integer shares; no floats. | - |
| Is a partial fill allowed? | Yes. Both orders' `remaining` quantities decrease. | - |
| Does the whole best price level fill before the next level? | Yes, in time order, then the next level. | L2, L3 |

## Bug inventory

### L1 - Executions print at the aggressor's limit

- **Spec rule:** a trade prints at the resting order's price.
- **Location:** `python/orderbook.py`, `OrderBook._execute`;
  `cpp/orderbook.hpp`, `execute`; `java/OrderBook.java`, `execute`.
- **Root cause:** the `Trade` is built with the incoming order's `price_cents`
  instead of the resting order's `price_cents`.
- **Minimal fix (Python):**

  ```python
  trades.append(Trade(f"T{self._trade_seq}", resting.price_cents, take,
                      buy_id, sell_id))
  ```

- **Failing-test recipe:** rest a sell for 10 shares at 100 cents, then submit a
  buy for 10 shares at 105 cents. Assert one trade exists and its price is 100.
- **Difficulty:** easy.
- **Hint ladder:** (1) "Which side was already resting?" (2) "Whose price does
  an execution normally use?" (3) "The code uses the incoming limit." (4) Show
  the `resting.price_cents` line.

### L2 - The newest order wins at a price

- **Spec rule:** within a price level, the oldest order has priority.
- **Location:** `_best_opposite` / `bestOpposite` in each language.
- **Root cause:** the tie-break compares `seq` in the wrong direction, so the
  largest sequence number (the newest order) wins.
- **Minimal fix (Python):**

  ```python
  if side is Side.BUY:
      return min(book.values(), key=lambda o: (o.price_cents, o.seq))
  return min(book.values(), key=lambda o: (-o.price_cents, o.seq))
  ```

- **Failing-test recipe:** rest two sells for 5 shares at 100 cents, one after
  the other (`O1` then `O2`), then buy 5 shares at 100. Assert the trade's
  `sell_order_id` is `O1` and `O2` still has 5 shares remaining.
- **Difficulty:** easy.
- **Hint ladder:** (1) "At the same price, what decides priority?" (2) "Which
  way does the tie-break compare `seq`?" (3) "It prefers the larger `seq`." (4)
  Show the corrected keys.

### L3 - The sweep stops at the first level

- **Spec rule:** a marketable order continues into the next price level while it
  still crosses.
- **Location:** `submit` in each language.
- **Root cause:** the loop pins the first opposite price as `level` and breaks
  as soon as the best opposite order has a different price. The incoming
  remainder then rests, which can leave the book crossed.
- **Minimal fix (Python):**

  ```python
  while incoming.remaining > 0:
      resting = self._best_opposite(s)
      if resting is None or not self._crosses(incoming, resting):
          break
      self._execute(incoming, resting, trades)
  ```

- **Failing-test recipe:** rest 5 shares at 100 and 5 shares at 101, then submit
  a buy for 10 shares at 101. Assert two trades with quantities 5 and 5, the
  incoming order is `FILLED`, no bid remains, and `best_bid()` and `best_ask()`
  are both `None`. A second test can assert the book is never crossed after any
  submission.
- **Difficulty:** medium.
- **Hint ladder:** (1) "What should happen when the best level is exhausted?" (2)
  "What ends the matching loop?" (3) "It stops when the price changes." (4) Show
  the loop that uses only the crossing condition.

## Acceptable alternative fixes

- Sorting the opposite book once per submission and walking it, or repeatedly
  selecting the best order. Both are fine if price and time priority hold.
- Grouping orders by price level, provided time priority is preserved within a
  level.
- A dedicated `_match` helper called from `submit`.
- Removing the `level` gate and comparing each candidate directly with the
  incoming limit.

## Cross-language notes

The C++ and Java fixes are mechanical:

- use the resting order's price when constructing the `Trade`;
- change the `seq` tie-break from newest-first to oldest-first;
- remove the pinned price level from `submit`, or replace the loop with one that
  stops only when the next order no longer crosses.

Keep prices and quantities as integers, and remove a resting order from the book
when its `remaining` reaches zero.

## Traps and wrong fixes

- Fixing the trade price but leaving the priority order wrong.
- Continuing the sweep past a price that no longer crosses the limit.
- Forgetting to decrease the resting order's remaining quantity on a partial
  fill.
- Resting the full incoming quantity instead of only the unfilled remainder.
- Leaving fully filled resting orders in the book so they can match again.
- Changing the public API or introducing floating-point prices.

## Rubric

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Discovery | Finds 1 defect | Finds 2 | Finds all three |
| Tests | Tests only happy paths | One test per defect | Tests each defect, the crossed-book invariant, and partial-fill state |
| Fixes | Broad rewrites | Narrow fixes | Narrow fixes in the right layer, with no regression |
| Explanation | Describes symptoms | Names the invariant | Explains invariant, matching rules, complexity, and concurrency |
| AI collaboration | Asks the assistant to fix it | Uses it to explain code | Uses it to map the code and review hypotheses, owns the fix and the tests |

## AI-assistant notes

Good prompts to hear from the candidate:

- "Map the matching path in this file. Do not suggest fixes yet."
- "Given this spec, what tests would prove price and time priority?"
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
