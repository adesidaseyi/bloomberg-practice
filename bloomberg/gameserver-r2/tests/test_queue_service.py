import pytest

from gameserver.errors import PlayerAlreadyActiveError, ValidationError
from gameserver.models import PlayerStatus


def test_join_queue_marks_player_queued(server):
    server.api.join_queue("alice", 1000)
    assert server.players.get("alice").status == PlayerStatus.QUEUED
    assert len(server.queue) == 1


def test_join_queue_twice_is_rejected(server):
    server.api.join_queue("alice", 1000)
    with pytest.raises(PlayerAlreadyActiveError):
        server.api.join_queue("alice", 1000)
    assert len(server.queue) == 1


def test_cannot_join_queue_while_in_lobby(server, pair_up):
    pair_up(server, ["alice", "bob"])
    with pytest.raises(PlayerAlreadyActiveError):
        server.api.join_queue("alice", 1000)


def test_join_queue_validates_input(server):
    with pytest.raises(ValidationError):
        server.api.join_queue("", 1000)
    with pytest.raises(ValidationError):
        server.api.join_queue("alice", -5)


# ---- leave_queue (feature to implement) ----

def test_leave_queue_removes_player_and_resets_status(server):
    server.api.join_queue("alice", 1000)
    assert server.api.leave_queue("alice") == {"player_id": "alice", "left": True}
    assert len(server.queue) == 0
    assert server.players.get("alice").status == PlayerStatus.IDLE


def test_leave_queue_unknown_or_not_queued_returns_false(server):
    assert server.api.leave_queue("ghost")["left"] is False
    server.api.join_queue("alice", 1000)
    server.api.leave_queue("alice")
    assert server.api.leave_queue("alice")["left"] is False  # idempotent


def test_leave_queue_does_not_touch_players_already_in_lobby(server, pair_up):
    pair_up(server, ["alice", "bob"])
    assert server.api.leave_queue("alice")["left"] is False
    assert server.players.get("alice").status == PlayerStatus.IN_LOBBY


def test_player_who_left_is_not_matched_and_can_rejoin(server, clock):
    server.api.join_queue("alice", 1000)
    server.api.join_queue("bob", 1000)
    server.api.leave_queue("bob")
    assert server.api.run_matchmaking() == []
    server.api.join_queue("bob", 1000)
    clock.advance(1)
    assert len(server.api.run_matchmaking()) == 1
