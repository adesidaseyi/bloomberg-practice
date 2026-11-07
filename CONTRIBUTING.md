# Contributing

Thanks for adding to the question bank. Each "pack" is a self-contained practice codebase
with deliberately planted bugs and **no tests**. The candidate writes the tests; you ship
the broken code and the story around it. Keep that contract and new packs will fit right in.

## The two round shapes

- `round-1/<codename>/` — one stateful domain object with a clear lifecycle and **3 to 5
  planted bugs**. Target ~35 minutes.
- `round-2/<codename>/` — a larger multi-module microservice with more bugs and a ticket
  backlog. Target ~45 minutes.

Use a **codename** that reveals nothing about the domain (for example `halcyon`, `kestrel`).
The documents tell the story; the folder name does not.

## No shipped tests

Packs do not ship tests. This is deliberate: confirming a bug with a test you wrote is the
skill being practised. What a pack ships instead:

- the implementation, with the bugs in it, one folder per language;
- a `conftest.py` in each `python/` so a candidate's own `test_*.py` imports the module;
- the story: round 1 ships `README.md` with the product spec and
  `CANDIDATE_BRIEF.md` with the joining-late framing; round 2 ships `tickets/`
  with one reported problem each.

Candidate-facing packs contain **no solution file** and **no test file**. An
optional `INTERVIEWER_GUIDE.md` may be added as an interviewer-only answer key;
it must be clearly marked and kept out of the candidate's view. You still verify
the pack with a private holdout suite (next section) that you keep out of the
candidate-facing material.

## Languages and layout

A pack is implemented three times with the **same bugs**, one folder per language.

```text
round-1/<codename>/                       round-2/<codename>/
  README.md                                 README.md
  CANDIDATE_BRIEF.md                        SETUP.md
  PROJECT_MANAGER_NOTES.md                  tickets/
  SELF_REVIEW_AFTER.md                      python/  cpp/  java/
  SETUP.md
  INTERVIEWER_GUIDE.md  (optional, interviewer-only)
  python/  cpp/  java/
```

- **python/** — the module(s) plus a `conftest.py` that puts the pack on the path. No tests.
- **cpp/** — a header-only implementation (`.hpp`). No test file and no Makefile; a candidate
  writes `test.cpp`.
- **java/** — the classes only. No `Tests.java`; a candidate writes `Check.java`.

## Verify with a private holdout (do not commit it)

Write a full acceptance suite while you build the pack, in all three languages, and use it to
prove two things: every planted bug is independently reproducible with a failing test, and
applying the intended fix turns the whole suite green. Then delete it, or keep it somewhere
outside the repo. It is your answer key, not part of the pack.

## The rules (please keep these)

1. **Bugs that a written test can catch.** Each planted bug must be reproducible by a small,
   obvious test a candidate could write from the symptom. If you cannot write that test, the
   bug is too obscure.
2. **Fixable cleanly.** The intended fix is the narrowest change that restores the invariant,
   in all three languages.
3. **Realistic lifecycle bugs.** Missing state guards, idempotency gaps, off-by-ones at a
   boundary, stale reads that skip expiry cleanup, broken invariants. No syntax errors and no
   giveaway comments in the code.
4. **No external dependencies, services, API keys, or network calls.** Standard library only.
5. **Integer money.** If a pack handles money, use integer cents; no floats in a ledger.
6. **Determinism.** Anything time-based takes an injected clock, so a candidate's expiry tests
   are exact.
7. **Shipped code must compile and import on its own**, with no test files present.

## Round 1 document set

- `README.md` — the product specification: the system, the domain model, the lifecycle,
  the public API, the agreed rules, the points to confirm with the interviewer, the
  repository map, and the scope/time budget. It does not enumerate symptoms or bug
  locations.
- `CANDIDATE_BRIEF.md` — "You are joining an existing project late in development", the
  task framing (clarify, reproduce, fix), where the code lives, and a be-ready-to-explain
  list (invariants, state transitions, idempotency, complexity, the concurrent/distributed
  version).
- `PROJECT_MANAGER_NOTES.md` — the clarifying questions a strong candidate asks. The
  interviewer plays the project manager, so some answers are judgement calls.
- `SELF_REVIEW_AFTER.md` — what strong candidates notice, read after the exercise.
  Observations, not a patch.
- `SETUP.md` — how to run the tests the candidate writes, in each language.
- `INTERVIEWER_GUIDE.md` — optional, interviewer-only answer key: recommended answers,
  bug inventory, intended fixes, test recipes, hint ladder, and rubric.

## Round 2 document set

- `README.md` — "Welcome to the team that ...", a repository map, the product rules as
  bullets, and a note that the candidate writes the tests.
- `tickets/` — one `.md` per reported problem: a Report, Acceptance criteria, and a scope
  boundary. The tickets are the symptoms; they do not name the buggy line.
- `SETUP.md` — how to run the tests the candidate writes, in each language.

## Opening a change

Create a branch, add your pack (or language port), and open a pull request. In the PR
description (not in the repo), list the codename, the round, the languages, the planted bugs,
and confirm that your private holdout went red-to-green in all three. Keep the holdout and any
solution out of the repository.
