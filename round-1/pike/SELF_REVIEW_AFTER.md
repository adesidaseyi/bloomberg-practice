# Self-review guide - Document Approval Workflow

This file is for AFTER the exercise. It lists what strong candidates tend to
notice. It is not a patch: there is no corrected code here, only the
observations that lead you to one.

Strong candidates often notice:

- approve has no state guard, so a rejected or already-approved document can be approved
- reject has no state guard, so a decided document can be rejected
- withdraw has no state guard, so a decided document can be withdrawn
- pending_count counts every document, not only the pending ones
- PENDING is the only non-terminal state
- every transition should start from PENDING

If you reproduced each issue with a test you wrote, fixed it, and can explain
each fix in terms of the invariant it protects, you did the exercise well.
