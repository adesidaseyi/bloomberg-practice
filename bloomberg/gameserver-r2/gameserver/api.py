from typing import Any, Dict, List, Optional

from .config import DEFAULT_PAGE_SIZE
from .lobby_service import LobbyService
from .matchmaker import Matchmaker
from .pagination import decode_offset_cursor, encode_offset_cursor
from .queue_service import QueueService
from .validators import validate_limit, validate_player_id


class GameServerAPI:
    """Thin request-handler layer. Returns plain dicts, like a JSON API would."""

    def __init__(
        self,
        queue_service: QueueService,
        lobby_service: LobbyService,
        matchmaker: Matchmaker,
    ) -> None:
        self._queue_service = queue_service
        self._lobby_service = lobby_service
        self._matchmaker = matchmaker

    def join_queue(self, player_id: str, skill: int) -> Dict[str, Any]:
        self._queue_service.join_queue(player_id, skill)
        return {"player_id": player_id, "status": "queued"}

    def leave_queue(self, player_id: str) -> Dict[str, Any]:
        return {"player_id": player_id, "left": self._queue_service.leave_queue(player_id)}

    def join_lobby(self, lobby_id: str, player_id: str) -> Dict[str, Any]:
        """Used for reconnects: put a known player back into a specific lobby."""
        validate_player_id(player_id)
        added = self._lobby_service.add_player(lobby_id, player_id)
        return {"lobby_id": lobby_id, "player_id": player_id, "added": added}

    def run_matchmaking(self) -> List[str]:
        return [lobby.lobby_id for lobby in self._matchmaker.tick()]

    def list_pairs(
        self, cursor: Optional[str] = None, limit: int = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        """List currently paired players, newest first.

        Clients follow `next_cursor` until it is None.
        """
        limit = validate_limit(limit)
        offset = decode_offset_cursor(cursor)
        pairings = self._lobby_service.list_paired(offset=offset, limit=limit)
        next_cursor = encode_offset_cursor(offset + limit) if len(pairings) == limit else None
        return {
            "items": [
                {"player_id": p.player_id, "lobby_id": p.lobby_id, "paired_at": p.paired_at}
                for p in pairings
            ],
            "next_cursor": next_cursor,
        }
