# Project Manager Notes - Rate Limiter

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Is this a fixed window or a sliding window?
- When exactly does the count reset: at `now - start == window`, or only after
  it?
- What should `remaining` report once the window has elapsed?
- Does a denied request consume quota?
- Should `reset` take effect immediately on the next call?
- What should `remaining` report for a key that has never been seen?
- Does `reset` affect only the addressed key, or all keys?
- Is `allow` safe if two threads call it for the same key at once?
