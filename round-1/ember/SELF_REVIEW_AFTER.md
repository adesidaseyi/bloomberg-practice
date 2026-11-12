# Self-review guide - Circuit Breaker

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the observations
that lead you to one.

Strong candidates often notice:

- `allow` admits every call while `HALF_OPEN` instead of a single probe
- a success while `CLOSED` does not clear the consecutive-failure count, so intermittent failures accumulate
- `reset()` clears the state and timestamp but leaves the failure count, so one more failure can reopen the breaker
- `OPEN` becomes `HALF_OPEN` only once `now - opened_at >= cooldown_seconds`
- a successful probe closes the breaker and clears the failure and probe counters
- a failed probe reopens the breaker and restarts the cooldown
- while `CLOSED`, the consecutive-failure count stays below the threshold

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
