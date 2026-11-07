# Self-review guide - Rate Limiter

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- `allow` never rolls an elapsed window, so a key stays blocked forever after
  its first burst
- `remaining` ignores the elapsed window and reports a stale count
- `reset` does not actually clear the key's window
- a denied request still increments the counter, so `remaining` can go negative
- `remaining` reports `0` for a key that has never been seen, instead of the
  full limit
- the intended rules are: a window is over at `now - start >= window_seconds`,
  a denied request consumes nothing, an unseen key has the full limit, and
  `reset` affects only the addressed key

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
