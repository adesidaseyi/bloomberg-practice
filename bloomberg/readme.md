# Workshop Signups Service

Backend module for a conference's workshop registration. Attendees sign up for
workshops with limited seats. When a workshop is full, attendees join a
waitlist. When someone cancels, the next waitlisted attendee is promoted.
Attendees can upgrade or downgrade their ticket tier, and receive a reminder
email shortly before their workshop starts.

## Layout

```
app/
  config.py                  tunables (tiers, reminder window, simulated latency)
  db.py                      SQLite wrapper; each caller opens its own connection
  schema.sql                 table definitions and indexes
  models/                    plain dataclasses mirroring the tables
  repositories/              one module per table; only place that writes SQL
  services/
    signup_service.py        sign_up, cancel
    waitlist_service.py      promote_next
    tier_service.py          change_tier
    reminder_service.py      due_reminders, send_reminders
  notifications/email.py     fake email sender with an in-memory OUTBOX
  reports/attendance.py      roster, fill_rate
  util/                      clock helpers, id generator
tests/                       pytest; fixture builds a fresh database per test
```

## Concepts

- **Workshop:** a session with a `capacity` (number of seats) and a start time.
- **Signup:** a row in `signups`. Its status is `active` or `cancelled`. Rows are
  never deleted, so history is kept. Only `active` rows hold a seat.
- **Waitlist entry:** a row in `waitlist` for someone who tried to join a full
  workshop. Entries are removed when promoted.
- **Tier:** `standard` or `vip`, stored on the signup row.

## Behaviour

1. An attendee can hold at most one active signup per workshop.
2. A workshop can never hold more active signups than its capacity.
3. If a workshop is full, a new request joins the waitlist instead.
4. The waitlist is first come, first served.
5. When an active signup is cancelled, the freed seat goes to the waitlist.
6. Changing tier keeps the attendee registered; they must never appear
   unregistered, even briefly.
7. Reminder emails go to attendees whose workshop starts in the next 24 hours.
   Cancelled attendees are not contacted.
8. Reports always reflect the current state of active signups.

## Running

```
pip install pytest
pytest -q tests
```

Services open their own connection from the `Database` object and commit before
returning. `config.LATENCY_SECONDS` simulates the latency of the auth and
payment lookups that happen in production between steps of a request.

## Notes from the team

- Production runs several app instances behind a load balancer, all sharing
  one database.
- Mobile clients retry requests on flaky connections.
- Other teams read the `signups` table directly for finance reporting.