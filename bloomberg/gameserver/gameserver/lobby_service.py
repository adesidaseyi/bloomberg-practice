from typing import List, Optional

from .clock import Clock
from .errors import LobbyFullError
from .events import EventLog
from .models import Lobby, Pairing, PlayerStatus
from .repos import LobbyRepository, PairingRepository, PlayerRepository


class LobbyService:
    def __init__(
        self,
        lobbies: LobbyRepository,
        players: PlayerRepository,
        pairings: PairingRepository,
        events: EventLog,
        clock: Clock,
    ) -> None:
        self._lobbies = lobbies
        self._players = players
        self._pairings = pairings
        self._events = events
        self._clock = clock

    def create_lobby(self, capacity: int, now: Optional[float] = None) -> Lobby:
        created_at = self._clock.now() if now is None else now
        return self._lobbies.create(capacity, created_at)

    def add_player(
        self, lobby_id: str, player_id: str, paired_at: Optional[float] = None
    ) -> bool:
        """Add a player to a lobby. Returns False if they were already a member."""
        self._players.require(player_id)
        lobby = self._lobbies.get(lobby_id)

        if self._lobbies.is_member(lobby_id, player_id):
            return False
        if self._lobbies.member_count(lobby_id) >= lobby.capacity:
            raise LobbyFullError(lobby_id)

        self._lobbies.add_member(lobby_id, player_id)
        self._players.set_status(player_id, PlayerStatus.IN_LOBBY)
        when = self._clock.now() if paired_at is None else paired_at
        self._pairings.record(Pairing(player_id=player_id, lobby_id=lobby_id, paired_at=when))
        self._events.emit("player_paired", player_id=player_id, lobby_id=lobby_id)
        return True

    def unpair(self, player_id: str) -> bool:
        """Remove a player from whatever lobby they are in."""
        pairing = self._pairings.remove_player(player_id)
        if pairing is None:
            return False
        self._lobbies.remove_member(pairing.lobby_id, player_id)
        self._players.set_status(player_id, PlayerStatus.IDLE)
        self._events.emit("player_unpaired", player_id=player_id, lobby_id=pairing.lobby_id)
        return True

    def list_paired(self, offset: int, limit: int) -> List[Pairing]:
        """Currently paired players, newest pairing first."""
        return self._pairings.newest_first()[offset : offset + limit]
