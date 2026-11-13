# Candidate Brief - Trade Settlement

You are joining an existing project late in development.

Start with `README.md`. It is the product specification for `SettlementService`:
the states, the settlement date rule, the public API, and the invariants the
service is supposed to protect.

The implementation is in place but has not been validated against that spec.
Your job is to:

- clarify the edge cases with the interviewer before changing behaviour;
- read the implementation and form a hypothesis about where it deviates;
- write a test that proves each deviation;
- fix the narrowest layer, keeping every test you write green.

This pack ships no tests. Use `SETUP.md` to run the tests you write in Python,
C++, or Java.

## Where the code lives

The same system is implemented three times, once per language:

`python/settlement.py` (`SettlementService`, `Trade`), `cpp/settlement.hpp`, and
`java/Settlement.java`.

## Be ready to explain

- your invariants
- the state transitions
- why a bug occurs, and why your fix belongs where you put it
- whether each operation should be idempotent
- the time and space complexity
- what changes in a concurrent or distributed version
