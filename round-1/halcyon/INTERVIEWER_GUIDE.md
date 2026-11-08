# Interviewer Guide - halcyon

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
| H1 | `fill` has no overfill guard |
| H2 | `fill` accepts terminal orders |
| H3 | `cancel` accepts terminal orders |
| H4 | `open_qty_for` counts cancelled orders |
| H5 | `remaining` ignores terminal status |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about fill-after-cancel, overfill, terminal cancels, and whether cancelled orders still count as open? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Can a cancelled order be filled? | No. Only `OPEN` or `PARTIAL` orders can be filled. | H2 |
| Can filled exceed qty? | No. A fill that would exceed the remaining quantity raises. | H1 |
| Is a second cancel allowed? | No. `FILLED` and `CANCELLED` are terminal. | H3 |
| Does `open_qty_for` include cancelled orders? | No. Only working orders count. | H4 |
| Does `remaining` return zero for a cancelled order? | Yes. Terminal orders have no open quantity. | H5 |

## Bug inventory

### H1 - `fill` can exceed the order quantity

- **Spec rule:** A fill may not exceed the remaining quantity.
- **Location:** `fill` in each language.
- **Root cause:** The new filled quantity is assigned without checking it against `qty`.
- **Minimal fix:**

```python
if order.filled + qty > order.qty:
    raise ValueError("fill exceeds order qty")
order.filled += qty
```
- **Failing-test recipe:** Place an order for 10, fill 8, then fill 3. The second fill should raise and the order should still have `filled == 8`.
- **Difficulty:** easy
- **Hint ladder:** (1) What invariant links filled and qty? (2) Where is the new filled total computed? (3) It is assigned without a bound check. (4) Show the guard.

### H2 - `fill` has no source-state guard

- **Spec rule:** Only `OPEN` and `PARTIAL` orders can be filled.
- **Location:** `fill` in each language.
- **Root cause:** The method never checks the order status before applying the execution.
- **Minimal fix:**

```python
if order.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
    raise ValueError("only working orders can be filled")
```
- **Failing-test recipe:** Cancel an order, then fill it. The fill should raise and the status should remain `CANCELLED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which states can accept a fill? (2) Does `fill` read the status? (3) It does not. (4) Show the guard.

### H3 - `cancel` has no terminal-state guard

- **Spec rule:** `FILLED` and `CANCELLED` are terminal; a second cancel raises.
- **Location:** `cancel` in each language.
- **Root cause:** The status is overwritten with `CANCELLED` without checking the source state.
- **Minimal fix:**

```python
if order.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
    raise ValueError("order is already terminal")
order.status = OrderStatus.CANCELLED
```
- **Failing-test recipe:** Cancel an order twice. The second call should raise and the status should remain `CANCELLED`.
- **Difficulty:** easy
- **Hint ladder:** (1) What does the spec say about terminal orders? (2) What does `cancel` check before writing status? (3) Nothing. (4) Show the guard.

### H4 - Open quantity includes terminal orders

- **Spec rule:** `open_qty_for` counts only `OPEN` and `PARTIAL` orders.
- **Location:** `open_qty_for` in each language.
- **Root cause:** The sum filters only by symbol, not by status.
- **Minimal fix:**

```python
return sum(
    o.qty - o.filled
    for o in self._orders.values()
    if o.symbol == symbol and o.status in (OrderStatus.OPEN, OrderStatus.PARTIAL)
)
```
- **Failing-test recipe:** Place an order for 10, cancel it, and assert `open_qty_for(symbol) == 0`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which orders consume open quantity? (2) What does the sum filter on? (3) It filters only by symbol. (4) Show the status filter.

### H5 - `remaining` reports open quantity for cancelled orders

- **Spec rule:** `remaining` is zero for `FILLED` and `CANCELLED`.
- **Location:** `remaining` in each language.
- **Root cause:** The method always returns `qty - filled` and never checks the status.
- **Minimal fix:**

```python
if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED):
    return 0
return order.qty - order.filled
```
- **Failing-test recipe:** Place an order for 10, fill 4, cancel it, and assert `remaining(id) == 0`.
- **Difficulty:** easy
- **Hint ladder:** (1) What should remaining mean for a cancelled order? (2) Does the method consult status? (3) It does not. (4) Show the terminal check.

## Acceptable alternative fixes

- A shared `_is_working(order)` helper used by `fill`, `cancel`, `remaining`, and `open_qty_for`.
- A transition table for order status instead of separate guards.
- Returning zero from `remaining` and filtering in `open_qty_for` are both required; one does not fix the other.

## Cross-language notes

- C++ and Java mirror the same guards and the same status filter in `open_qty_for`.
- Keep `filled` bounded in every fill path; do not clamp silently.

## Traps and wrong fixes

- Adding only an overfill guard and leaving fill-after-cancel possible.
- Making cancel idempotent when the spec says a terminal cancel raises.
- Fixing `open_qty_for` but leaving `remaining` stale for cancelled orders.
- Letting an invalid fill change `filled` before raising.

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
