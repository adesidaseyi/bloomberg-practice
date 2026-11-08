# Project Manager Notes - Wallet Authorization Holds

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Does authorizing reduce the balance, or only the available funds?
- Can a voided hold be captured?
- What should a second void on the same hold do?
- What invariant relates balance, available, and active holds?
- Does capture settle out of the balance exactly once?
- Should captured or voided holds still reduce available?
- Are all amounts integer cents, with no floating point?
