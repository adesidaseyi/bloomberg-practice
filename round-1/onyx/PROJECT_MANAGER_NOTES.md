# Project Manager Notes - Access Token Store

Read this after your first pass. It is a checklist of the questions a strong
candidate asks before and during the fix. The interviewer is playing the
project manager, so some answers are judgement calls, not facts in the code.

- Should an expired token pass validation?
- Can an expired token be refreshed back to life?
- What should a second revoke do?
- Can an expired token be revoked?
- Does refresh extend from now, or from the original expiry?
- Should validation force cleanup of expired tokens, or just report them invalid?
- Is revoke idempotent, or an error the second time?
