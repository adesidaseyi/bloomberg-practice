import threading
from typing import Dict, Optional

from ..errors import PlayerNotFoundError
from ..models import Player, PlayerStatus


class PlayerRepository:
    def __init__(self) -> None:
        self._players: Dict[str, Player] = {}
        self._lock = threading.Lock()

    def get(self, player_id: str) -> Optional[Player]:
        with self._lock:
            return self._players.get(player_id)

    def require(self, player_id: str) -> Player:
        player = self.get(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        return player

    def upsert(self, player_id: str, skill: int) -> Player:
        with self._lock:
            player = self._players.get(player_id)
            if player is None:
                player = Player(player_id=player_id, skill=skill)
                self._players[player_id] = player
            else:
                player.skill = skill
            return player

    def set_status(self, player_id: str, status: PlayerStatus) -> None:
        with self._lock:
            self._players[player_id].status = status
