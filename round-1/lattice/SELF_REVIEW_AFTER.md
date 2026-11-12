# Self-review guide - Limit Order Book

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the observations
that lead you to one.

Strong candidates often notice:

- trades print at the incoming limit instead of the resting order's price
- within a price level, the newest order fills before the oldest
- the sweep stops at the first price level, so a large order can finish partially filled and leave the book crossed
- a marketable order should continue while the next level still crosses its limit
- each execution reduces both orders' remaining quantity; a resting order at zero leaves the book
- the unfilled remainder of an incoming order rests at its limit
- `best_bid` is below `best_ask` whenever both sides are present
- prices are integer cents; no floats in the book

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
