# Matchmaking Game Server (Round-2 practice, Python)

Players join a queue; a matchmaker groups them into lobbies of `lobby_size`.
The "database" is in-memory but each lobby read/write sleeps ~0.5 ms to simulate a network round trip.

Run tests: `pip install pytest && python -m pytest -q`
Starting state: **10 failing, 11 passing**. Don't edit the tests to make them pass.

## Layout
```
gameserver/
  api.py            request handlers (join_queue, leave_queue, join_lobby, run_matchmaking, list_pairs)
  queue_service.py  join/leave queue, player status transitions
  matchmaker.py     tick(): forms lobbies from the queue
  lobby_service.py  create lobby, add/remove players, list paired players
  match_queue.py    thread-safe waiting list
  repos/            player, lobby, pairing repositories
  pagination.py     cursor helpers
  server.py         wiring (build_server)
tests/
```

## Spec
**Player state:** `idle -> queued -> in_lobby`. A player is in at most one state.

**join_queue:** rejects (PlayerAlreadyActiveError) if the player is already queued or in a lobby.

**Lobbies:**
- A player appears in a lobby's `member_ids` at most once and has at most one pairing record.
- A lobby never holds more than `capacity` players.
- `add_player` returns `False` if the player is already a member, and raises `LobbyFullError` when full.
- These hold even when requests arrive concurrently (e.g. a reconnect via `join_lobby` racing another request).

**Matchmaking rules:**
- Earliest-enqueued player anchors each lobby; lobbies have exactly `lobby_size` players.
- Skill window is **inclusive**, and **every pair** of players in a lobby must be within `skill_window` of each other.

**list_pairs(cursor, limit):** currently paired players, newest first. A client that follows `next_cursor` until it is `None` must:
- never see the same player twice, and
- never miss a player who was paired for the whole traversal,
even if pairings are added or removed between page requests. Treat `cursor` as opaque to clients.

**leave_queue(player_id) -> bool** (not implemented yet):
- Queued player: remove from queue, set status `idle`, emit `player_left_queue`, return `True`.
- Unknown player, not queued, or already in a lobby: return `False`, change nothing. Never raises for these.

## Your tasks
1. Get all tests green with minimal, well-explained changes.
2. Add tests for anything you fix that the suite doesn't cover.
3. Be ready to explain the tradeoffs of each fix out loud.

## Things to think about
- Which operations in this codebase are check-then-act? What are the ways to make them atomic (lock, atomic repo method, unique constraint)? What does each cost?
- What does a lock held across a DB round trip do to throughput?
- Why does offset pagination break when the list changes? What does a keyset cursor need to contain for the sort order used here, and why is `paired_at` alone not enough?
- What happens if a player calls `leave_queue` between the matchmaker's snapshot and lobby creation?
- Hidden-test-style cases to expect: 50 threads joining the same lobby, a lobby of size 1, `limit` equal to the exact number of items, an empty list, a malformed cursor, two ticks in a row.

## Suggested timing (35 min)
Spec/assumptions 3 min -> skim + AI summary 5 -> hypotheses and verify failing tests 7 -> fixes + regression tests 15 -> wrap-up 5.
