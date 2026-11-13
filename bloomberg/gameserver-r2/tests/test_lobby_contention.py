import threading

from gameserver.errors import LobbyFullError


def run_concurrently(n, fn):
    """Run fn(i) on n threads released at the same moment; collect results/exceptions."""
    barrier = threading.Barrier(n)
    results = [None] * n

    def worker(i):
        barrier.wait()
        try:
            results[i] = fn(i)
        except Exception as exc:  # noqa: BLE001 - tests inspect the exception
            results[i] = exc

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_sequential_duplicate_join_is_a_noop(server):
    server.players.upsert("p1", 1000)
    lobby = server.lobby_service.create_lobby(capacity=4)
    assert server.api.join_lobby(lobby.lobby_id, "p1")["added"] is True
    assert server.api.join_lobby(lobby.lobby_id, "p1")["added"] is False
    assert server.lobbies.get(lobby.lobby_id).member_ids == ["p1"]


def test_same_player_joining_concurrently_is_added_exactly_once(server):
    server.players.upsert("p1", 1000)
    lobby = server.lobby_service.create_lobby(capacity=4)

    results = run_concurrently(8, lambda i: server.api.join_lobby(lobby.lobby_id, "p1"))

    members = server.lobbies.get(lobby.lobby_id).member_ids
    assert members.count("p1") == 1
    assert sum(1 for r in results if isinstance(r, dict) and r["added"]) == 1
    assert len(server.pairings.newest_first()) == 1


def test_lobby_never_exceeds_capacity_under_concurrent_joins(server):
    for i in range(12):
        server.players.upsert(f"p{i}", 1000)
    lobby = server.lobby_service.create_lobby(capacity=4)

    results = run_concurrently(12, lambda i: server.api.join_lobby(lobby.lobby_id, f"p{i}"))

    assert len(server.lobbies.get(lobby.lobby_id).member_ids) == 4
    assert sum(isinstance(r, LobbyFullError) for r in results) == 8
