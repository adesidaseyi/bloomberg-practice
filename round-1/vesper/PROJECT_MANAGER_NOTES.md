# Project Manager Notes - Connection Pool

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- What should acquiring from a closed pool do?
- Can the pool ever exceed its capacity?
- What should releasing an already-idle connection do?
- Should release work after close?
- What invariant holds for in-use plus idle versus capacity?
- Should close drain or forcibly close in-use connections?
- Is acquire/release safe under concurrent callers?
