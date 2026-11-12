# Project Manager Notes - Limit Order Book

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Does a trade print at the resting order's price, or the incoming order's limit?
- Within one price level, which order has priority: oldest or newest?
- Should a marketable order sweep successive price levels until it is filled?
- What happens to the unfilled remainder of a marketable order?
- Can the resting book ever be crossed, and which invariant prevents it?
- Should cancelling a filled or already-cancelled order raise, or be a no-op?
- Are prices integer cents and quantities integer shares, with no floating point?
