import itertools
import time
from typing import Dict

from ..config import SIMULATED_DB_LATENCY
from ..errors import LobbyNotFoundError
from ..models import Lobby


class LobbyRepository:
    """In-memory stand-in for a lobbies table.

    Every read/write that would hit the database sleeps briefly to simulate a
    network round trip.
    """

    def __init__(self, latency: float = SIMULATED_DB_LATENCY) -> None:
        self._lobbies: Dict[str, Lobby] = {}
        self._latency = latency
        self._ids = itertools.count(1)

    def _round_trip(self) -> None:
        if self._latency:
            time.sleep(self._latency)

    def create(self, capacity: int, created_at: float) -> Lobby:
        lobby = Lobby(
            lobby_id=f"lobby-{next(self._ids)}",
            capacity=capacity,
            created_at=created_at,
        )
        self._lobbies[lobby.lobby_id] = lobby
        return lobby

    def get(self, lobby_id: str) -> Lobby:
        lobby = self._lobbies.get(lobby_id)
        if lobby is None:
            raise LobbyNotFoundError(lobby_id)
        return lobby

    def is_member(self, lobby_id: str, player_id: str) -> bool:
        lobby = self.get(lobby_id)
        self._round_trip()
        return player_id in lobby.member_ids

    def member_count(self, lobby_id: str) -> int:
        lobby = self.get(lobby_id)
        self._round_trip()
        return len(lobby.member_ids)

    def add_member(self, lobby_id: str, player_id: str) -> None:
        lobby = self.get(lobby_id)
        self._round_trip()
        lobby.member_ids.append(player_id)

    def remove_member(self, lobby_id: str, player_id: str) -> None:
        lobby = self.get(lobby_id)
        self._round_trip()
        if player_id in lobby.member_ids:
            lobby.member_ids.remove(player_id)
