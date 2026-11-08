# Interviewer Guide - cobalt

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
| C1 | `authorize` checks balance, not available |
| C2 | `capture` has no status guard |
| C3 | `void` has no status guard |
| C4 | `capture` does not reduce the balance |
| C5 | Active holds includes terminal holds |

## Suggested 35-minute flow

| Time | Phase | What to look for |
| --- | --- | --- |
| 0-5 | Read the spec and ask questions | Does the candidate ask about available versus balance, capture settlement, and terminal hold states? |
| 5-10 | Map the code | Can they restate the invariants and point to where each transition is implemented? |
| 10-25 | Reproduce and fix | Do they write a failing test first? Do they isolate one defect at a time? |
| 25-30 | Run tests and explain | Do they keep valid behaviour green and explain why the fix belongs where it does? |
| 30-35 | Wrap-up | Idempotency, complexity, concurrency, distributed version. |

## Clarifying questions and recommended answers

The key question is whether the candidate asks before assuming. Give the
answers below when asked; do not volunteer them.

| Candidate question | Recommended answer | Unlocks |
| --- | --- | --- |
| Does authorize check available or balance? | Available. Reserved funds cannot be authorized again. | C1 |
| Can a voided hold be captured? | No. Only `HELD` can be captured. | C2 |
| Can a captured hold be voided? | No. Only `HELD` can be voided. | C3 |
| Does capture reduce the balance? | Yes, exactly once. | C4 |
| Do captured or voided holds still count against available? | No. Only `HELD` counts. | C5 |

## Bug inventory

### C1 - Reserved funds can be authorized again

- **Spec rule:** `authorize` must compare the amount to available funds.
- **Location:** `authorize` in each language.
- **Root cause:** The guard calls `balance` instead of `available`.
- **Minimal fix:**

```python
if self.available(account_id) < cents:
    raise ValueError("insufficient available funds")
```
- **Failing-test recipe:** Open an account with 1000 cents, authorize 700, then authorize 400. The second authorization should raise.
- **Difficulty:** easy
- **Hint ladder:** (1) What can be spent after a hold? (2) Which number does `authorize` compare against? (3) It uses the raw balance. (4) Show the `available` call.

### C2 - A voided or captured hold can be captured again

- **Spec rule:** Only a `HELD` authorization can be captured.
- **Location:** `capture` in each language.
- **Root cause:** The method overwrites the status without checking it.
- **Minimal fix:**

```python
if h.status != HoldStatus.HELD:
    raise ValueError(f"cannot capture a hold with status {h.status.value}")
```
- **Failing-test recipe:** Authorize a hold, void it, then capture it. The capture should raise and the status should remain `VOIDED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be captured? (2) Does `capture` inspect status? (3) It does not. (4) Show the guard.

### C3 - A captured or voided hold can be voided again

- **Spec rule:** Only a `HELD` authorization can be voided.
- **Location:** `void` in each language.
- **Root cause:** The method overwrites the status without checking it.
- **Minimal fix:**

```python
if h.status != HoldStatus.HELD:
    raise ValueError(f"cannot void a hold with status {h.status.value}")
```
- **Failing-test recipe:** Authorize a hold, capture it, then void it. The void should raise and the status should remain `CAPTURED`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which status can be voided? (2) Does `void` inspect status? (3) It does not. (4) Show the guard.

### C4 - Captured funds never settle

- **Spec rule:** Capture reduces the balance by the hold amount exactly once.
- **Location:** `capture` in each language.
- **Root cause:** The method changes the hold status but never debits the account.
- **Minimal fix:**

```python
self._balance[h.account_id] -= h.amount
h.status = HoldStatus.CAPTURED
```
- **Failing-test recipe:** Open with 1000, authorize 700, capture the hold, and assert `balance == 300`.
- **Difficulty:** easy
- **Hint ladder:** (1) What does capture mean for the ledger? (2) Does `capture` touch the balance? (3) It only changes status. (4) Show the debit.

### C5 - Voided and captured holds still reduce available

- **Spec rule:** Only `HELD` amounts reduce available.
- **Location:** `_active_holds` / `activeHolds` in each language.
- **Root cause:** The sum filters by account but not by `HELD` status.
- **Minimal fix:**

```python
return sum(
    h.amount for h in self._holds.values()
    if h.account_id == account_id and h.status == HoldStatus.HELD
)
```
- **Failing-test recipe:** Open with 1000, authorize 700, void the hold, and assert `available == 1000`.
- **Difficulty:** easy
- **Hint ladder:** (1) Which holds reserve funds? (2) What does the active-holds sum filter on? (3) It counts every hold for the account. (4) Show the status filter.

## Acceptable alternative fixes

- A helper such as `_active_holds(account)` used by both `available` and `authorize`.
- Computing available directly as `balance - active_holds` or maintaining a cached available count; both are valid if the invariant is maintained.

## Cross-language notes

- C++ and Java mirror the same `available`, capture, void, and active-hold changes.
- Keep all amounts as integer cents in every language.

## Traps and wrong fixes

- Fixing `available` but leaving `authorize` comparing against the raw balance.
- Adding capture guards but forgetting to debit the balance.
- Filtering active holds by account only, so voided holds still reserve funds.
- Letting an invalid capture or void change state before raising.

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
