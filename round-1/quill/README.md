# quill - Timed Reserve Auction

`AuctionService` runs a single-item auction with a reserve price and a fixed
closing instant. The service is in-memory, single-process, and takes an injected
clock so closing behaviour is deterministic in tests.

## Domain model

An auction is configured with:

- `reserve_cents` - the minimum acceptable bid, a non-negative integer number of
  cents
- `closes_at` - the instant at which bidding ends



## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `OPEN` | clock | `CLOSED` |

## Pack files

- `README.md` - this specification
- `CANDIDATE_BRIEF.md` - the joining-late task and be-ready-to-explain list
- `PROJECT_MANAGER_NOTES.md` - questions to ask the interviewer
- `SETUP.md` - how to run the tests you write
- `SELF_REVIEW_AFTER.md` - read after the exercise

## Scope and time

In scope: find where the implementation deviates from this specification, write
a test that proves each deviation, fix the narrowest layer, and keep existing
correct behaviour working.

Out of scope: redesigning the component, changing the public API, or adding
features the specification does not describe.

Time budget: about 35 minutes.

This pack ships no tests. Read the spec, ask the interviewer about the edge
cases, then write your own tests.
