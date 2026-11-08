# Self-review guide - Order Lifecycle

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- a cancelled order can still be filled (fill has no status guard)
- a fill can push filled past the original quantity (no overfill guard)
- cancel can run twice on the same order (no terminal-state guard)
- open-quantity for a symbol still counts cancelled orders
- remaining keeps reporting open quantity for a cancelled order
- the invariant `0 <= filled <= qty` should always hold

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
