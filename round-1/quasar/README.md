# quasar - Rate Limiter

`RateLimiter` enforces a per-key request quota using fixed windows. The service
is in-memory, single-process, and takes an injected clock so window behaviour is
deterministic in tests.

## Domain model

For each key the limiter stores:

- the start of the current window
- the number of requests allowed in that window

Windows are independent per key.

## Public API

### `allow(key) -> bool`

Consumes one unit of quota and returns `True` when the request is allowed.
Returns `False` when the window's quota is exhausted.

### `remaining(key) -> int`

Reports how much quota is left in the key's current window.

### `reset(key) -> None`

Discards the key's current window.

## Repository map

```text
python/ratelimit.py   RateLimiter
cpp/ratelimit.hpp     header-only equivalent
java/RateLimit.java   equivalent
python/conftest.py    import path for your Python tests
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
