# Project Manager Notes - Timed Reserve Auction

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- When exactly does bidding close: at `now == closes_at`, or after it?
- Is a bid equal to the reserve acceptable?
- Must a bid strictly exceed the current highest?
- What should a bid after the close do?
- Does `status()` change the stored state when the closing instant has passed?
- Does `winner()` return the highest bid or only the latest one?
- Is `winner()` ever non-`None` while the auction is `OPEN`?
- Is the clock injected for tests, and is it monotonic?
