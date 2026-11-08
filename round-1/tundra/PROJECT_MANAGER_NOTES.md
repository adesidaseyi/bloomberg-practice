# Project Manager Notes - LRU Cache with TTL

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Should a read return an entry that has expired?
- Does a read count as a use for LRU ordering?
- Should size count entries that have expired but not been purged?
- Does put update the value and TTL of an existing key?
- Which entry is evicted first when capacity is exceeded?
- Is get expected to be O(1)?
