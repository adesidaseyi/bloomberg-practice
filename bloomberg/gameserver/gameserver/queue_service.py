from .clock import Clock
from .events import EventLog
from .errors import PlayerAlreadyActiveError
from .match_queue import MatchQueue
from .models import PlayerStatus, QueueEntry
from .repos import PlayerRepository
from .validators import validate_player_id, validate_skill


class QueueService:
    def __init__(
        self,
        queue: MatchQueue,
        players: PlayerRepository,
        events: EventLog,
        clock: Clock,
    ) -> None:
        self._queue = queue
        self._players = players
        self._events = events
        self._clock = clock

    def join_queue(self, player_id: str, skill: int) -> None:
        validate_player_id(player_id)
        validate_skill(skill)

        existing = self._players.get(player_id)
        if existing is not None and existing.status != PlayerStatus.IDLE:
            raise PlayerAlreadyActiveError(player_id)

        self._players.upsert(player_id, skill)
        entry = QueueEntry(player_id=player_id, skill=skill, enqueued_at=self._clock.now())
        if not self._queue.enqueue(entry):
            raise PlayerAlreadyActiveError(player_id)
        self._players.set_status(player_id, PlayerStatus.QUEUED)
        self._events.emit("player_queued", player_id=player_id)

    def leave_queue(self, player_id: str) -> bool:
        raise NotImplementedError("TODO: implement leave_queue (see README)")
