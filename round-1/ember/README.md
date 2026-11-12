# ember - Circuit Breaker

`CircuitBreaker` guards calls to a downstream quote feed. The service is
in-memory, single-process, and takes an injected clock so cooldown behaviour is
deterministic in tests.

## Domain model

A breaker is configured with:

- `failure_threshold` - a positive number of consecutive failures
- `cooldown_seconds` - a non-negative cooldown period

A breaker has:

- `state` - one of `CLOSED`, `OPEN`, `HALF_OPEN`
- `failures` - the current run of consecutive failures
- `opened_at` - the instant the breaker most recently opened
- `probes` - the number of probe calls admitted in the current half-open period


## Lifecycle

| From | Event | To |
| --- | --- | --- |
| `CLOSED` | failure count reaches the threshold | `OPEN` |
| `OPEN` | cooldown elapsed | `HALF_OPEN` |
| `HALF_OPEN` | probe succeeds | `CLOSED` |
| `HALF_OPEN` | probe fails | `OPEN` |

## Repository map

```text
python/breaker.py   CircuitBreaker
cpp/breaker.hpp     header-only equivalent
java/Breaker.java   equivalent
python/conftest.py  import path for your Python tests
```

The same behaviour is implemented in all three languages. Pick one.

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
