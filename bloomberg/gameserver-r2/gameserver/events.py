import threading
from typing import Any, Dict, List


class EventLog:
    """Tiny in-memory event sink used for observability in tests."""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def emit(self, name: str, **fields: Any) -> None:
        with self._lock:
            self._events.append({"name": name, **fields})

    def all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._events)

    def count(self, name: str) -> int:
        return sum(1 for e in self.all() if e["name"] == name)
