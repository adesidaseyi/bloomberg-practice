from typing import List

from .clock import Clock
from .events import EventLog
from .lobby_service import LobbyService
from .match_queue import MatchQueue
from .models import Lobby, QueueEntry


class Matchmaker:
    """Greedy matchmaker: earliest-enqueued players anchor each lobby."""

    def __init__(
        self,
        queue: MatchQueue,
        lobby_service: LobbyService,
        clock: Clock,
        events: EventLog,
        lobby_size: int,
        skill_window: int,
    ) -> None:
        self._queue = queue
        self._lobby_service = lobby_service
        self._clock = clock
        self._events = events
        self._lobby_size = lobby_size
        self._skill_window = skill_window

    def tick(self) -> List[Lobby]:
        now = self._clock.now()
        entries = self._queue.snapshot()
        claimed = set()
        lobbies: List[Lobby] = []

        for anchor in entries:
            if anchor.player_id in claimed:
                continue
            group = [anchor]
            for candidate in entries:
                if len(group) == self._lobby_size:
                    break
                if candidate.player_id in claimed or candidate.player_id == anchor.player_id:
                    continue
                if abs(candidate.skill - anchor.skill) < self._skill_window:
                    group.append(candidate)

            if len(group) < self._lobby_size:
                continue
            claimed.update(e.player_id for e in group)
            lobbies.append(self._form_lobby(group, now))

        return lobbies

    def _form_lobby(self, group: List[QueueEntry], now: float) -> Lobby:
        lobby = self._lobby_service.create_lobby(self._lobby_size, now)
        for entry in group:
            self._queue.remove(entry.player_id)
            self._lobby_service.add_player(lobby.lobby_id, entry.player_id, paired_at=now)
        self._events.emit("lobby_formed", lobby_id=lobby.lobby_id, size=len(group))
        return lobby
