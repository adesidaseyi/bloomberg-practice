from gameserver.models import PlayerStatus


def _queue(server, clock, players):
    for pid, skill in players:
        server.api.join_queue(pid, skill)
        clock.advance(1)


def test_no_lobby_until_enough_players(make_server, clock):
    server = make_server(lobby_size=3)
    _queue(server, clock, [("a", 1000), ("b", 1000)])
    assert server.api.run_matchmaking() == []
    assert len(server.queue) == 2


def test_matched_players_leave_queue_and_enter_lobby(server, clock):
    _queue(server, clock, [("a", 1000), ("b", 1010)])
    lobby_ids = server.api.run_matchmaking()
    assert len(lobby_ids) == 1
    assert len(server.queue) == 0
    assert set(server.lobbies.get(lobby_ids[0]).member_ids) == {"a", "b"}
    assert server.players.get("a").status == PlayerStatus.IN_LOBBY


def test_far_apart_skills_do_not_match(server, clock):
    _queue(server, clock, [("a", 1000), ("b", 1500)])
    assert server.api.run_matchmaking() == []


def test_earliest_enqueued_players_are_matched_first(server, clock):
    _queue(server, clock, [("a", 1000), ("b", 1000), ("c", 1000)])
    lobby_ids = server.api.run_matchmaking()
    assert len(lobby_ids) == 1
    assert set(server.lobbies.get(lobby_ids[0]).member_ids) == {"a", "b"}
    assert server.players.get("c").status == PlayerStatus.QUEUED


# ---- skill window rules (see README: "Matchmaking rules") ----

def test_players_exactly_at_skill_window_edge_are_matched(server, clock):
    _queue(server, clock, [("a", 1000), ("b", 1100)])  # window = 100, inclusive
    assert len(server.api.run_matchmaking()) == 1


def test_every_pair_in_a_lobby_is_within_the_skill_window(make_server, clock):
    server = make_server(lobby_size=3, skill_window=100)
    _queue(server, clock, [("A", 1000), ("B", 1060), ("C", 940), ("D", 1000)])
    lobby_ids = server.api.run_matchmaking()
    assert len(lobby_ids) == 1
    members = set(server.lobbies.get(lobby_ids[0]).member_ids)
    # B (1060) and C (940) differ by 120, so they can never share a lobby.
    assert members == {"A", "B", "D"}
    assert server.players.get("C").status == PlayerStatus.QUEUED
