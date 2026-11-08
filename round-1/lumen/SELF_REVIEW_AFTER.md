# Self-review guide - Job State Machine

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- start has no state guard, so a running or finished job can be started again
- complete has no state guard, so a non-running job can be completed
- fail has no state guard, so a queued or finished job can fail
- fail is off by one and allows one retry past the attempt budget
- attempts increments on start; the budget check must use < not <=
- DONE and FAILED should be terminal

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
