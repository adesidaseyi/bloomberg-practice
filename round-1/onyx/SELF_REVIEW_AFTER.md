# Self-review guide - Access Token Store

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- validate ignores expiry, so an expired token still validates
- refresh does not check expiry, so an expired token can be revived
- revoke can run twice (no terminal-state guard)
- revoke accepts an expired token even though it is already invalid
- a valid token is `ACTIVE` and `now < expires_at`
- refresh should only extend a token that is still valid

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
