# Self-review guide - Subscription Entitlement

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- `activate` accepts any current status, so cancelled and expired
  subscriptions can be revived, and suspended ones bypass `resume`
- `cancel` accepts terminal states, so a second cancel succeeds
- `_cleanup_expired` exists but is never called, so an expired trial stays
  `TRIAL` and still reads as entitled
- `is_entitled` treats `SUSPENDED` as entitled
- `suspend` accepts a `TRIAL`
- the intended rules are: `ACTIVE` and an unexpired `TRIAL` are entitled;
  expiry applies at `now >= expires_at`; invalid transitions raise and leave
  the subscription unchanged

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
