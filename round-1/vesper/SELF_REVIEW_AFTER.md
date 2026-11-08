# Self-review guide - Connection Pool

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- acquire does not check whether the pool is closed
- acquire does not enforce capacity, so the pool can exceed its size
- release has no status guard, so an idle connection can be released again
- release ignores the closed flag, so a closed pool still accepts releases
- the invariant in-use + idle <= capacity should always hold
- a double release inflates the idle count above capacity

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
