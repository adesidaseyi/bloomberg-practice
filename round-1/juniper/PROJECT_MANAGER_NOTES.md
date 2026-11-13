# Project Manager Notes - Trade Settlement

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Does a trade settle at exactly `settle_on`, or only after it?
- What does `settle` do to a trade that is already settled or failed?
- What does `fail` do to a trade that is already terminal?
- Which statuses count toward pending notional?
- Is notional `qty * price_cents`, in integer cents?
- Can a trade be booked with a settlement date in the past?
- Does `pending_notional` change when a trade settles or fails?
- Is the clock injected for tests, and is it monotonic?
