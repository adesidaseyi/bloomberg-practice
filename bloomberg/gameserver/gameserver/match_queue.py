import threading
from typing import Dict, List

from .models import QueueEntry


class MatchQueue:
    """Players waiting to be matched. Safe to call from multiple threads."""

    def __init__(self) -> None:
        self._entries: Dict[str, QueueEntry] = {}
        self._lock = threading.Lock()

    def enqueue(self, entry: QueueEntry) -> bool:
        with self._lock:
            if entry.player_id in self._entries:
                return False
            self._entries[entry.player_id] = entry
            return True

    def remove(self, player_id: str) -> bool:
        with self._lock:
            return self._entries.pop(player_id, None) is not None

    def snapshot(self) -> List[QueueEntry]:
        """Waiting players, earliest enqueued first."""
        with self._lock:
            return sorted(self._entries.values(), key=lambda e: e.enqueued_at)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
