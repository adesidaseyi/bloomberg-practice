# Self-review guide - Wallet Authorization Holds

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- authorize checks the raw balance instead of available, so reserved funds can be authorized again
- a voided hold can still be captured (capture has no status guard)
- a captured hold can still be voided (void has no status guard)
- capture does not reduce the balance, so funds never settle
- active holds includes captured and voided holds, so releasing a hold does not free available
- available should always equal balance minus the sum of HELD amounts
- capture settles out of the balance exactly once

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
