import pytest

from gameserver.server import build_server


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self._now = start

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def make_server(clock):
    def _make(**kwargs):
        kwargs.setdefault("clock", clock)
        return build_server(**kwargs)

    return _make


@pytest.fixture
def server(make_server):
    """Server with 2-player lobbies."""
    return make_server(lobby_size=2)


@pytest.fixture
def pair_up(clock):
    """Queue the given players (same skill), advance time, run one matchmaking tick."""

    def _pair_up(server, player_ids, skill=1000):
        for pid in player_ids:
            server.api.join_queue(pid, skill)
            clock.advance(0.001)
        clock.advance(1)
        return server.api.run_matchmaking()

    return _pair_up
