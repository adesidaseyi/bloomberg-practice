# Self-review guide - Trade Settlement

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the observations
that lead you to one.

Strong candidates often notice:

- `settle` ignores `settle_on` and settles a trade early
- `fail` has no terminal-state guard, so a settled trade can become failed
- `pending_notional` sums every trade for the account instead of only pending ones
- `settle_on` is inclusive: a trade may settle at `now == settle_on`
- `SETTLED` and `FAILED` are terminal
- pending notional covers only `PENDING` trades and uses `qty * price_cents`
- all money is integer cents; no floats in settlement

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
