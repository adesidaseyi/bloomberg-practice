# Self-review guide - Timed Reserve Auction

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the observations
that lead you to one.

Strong candidates often notice:

- `bid` accepts bids after `closes_at`
- `bid` accepts an amount below the reserve
- `bid` accepts a lower amount and replaces the leading bid
- the auction closes at `now >= closes_at`
- an accepted bid is at least the reserve and strictly above the current highest
- the leading bid is the highest accepted bid, not simply the latest
- `winner()` is `None` while the auction is `OPEN` and `None` when no bid exists

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
