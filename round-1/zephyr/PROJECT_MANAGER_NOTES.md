# Project Manager Notes - Subscription Entitlement

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- What are the valid source states for `activate`? Can a suspended subscription
  be activated directly, or must it be resumed?
- Can `activate` revive a cancelled or expired subscription?
- What should a second `cancel` do?
- Is `EXPIRED` a distinct state from `CANCELLED`?
- When exactly does a trial expire: at `now == expires_at`, or after it?
- Is expiry computed on read, or swept eagerly? Does a read change the stored
  status?
- Is a suspended subscription entitled?
- Can a `TRIAL` be suspended?
- Should a user be able to hold more than one live subscription?
- Is `is_entitled` safe if two threads read and expire the same subscription
  at once?
