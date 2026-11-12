# Project Manager Notes - Circuit Breaker

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Are failures counted consecutively, or over the breaker's whole lifetime?
- How many probe calls may a half-open breaker admit at once?
- Does a success while CLOSED clear the failure count?
- Should `reset()` clear the state only, or every counter and timestamp too?
- When does the cooldown start, and does a failed probe restart it?
- What should happen to a result recorded while the breaker is OPEN?
- Is the clock injected for tests, and is it monotonic?
