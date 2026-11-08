from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Any
import time


@dataclass
class _Entry:
    value: Any
    expires_at: float


class LRUCache:
    """A capacity-bounded cache with per-entry TTL and least-recently-used
    eviction. A read counts as a use. Expired entries are not returned and do not
    count toward size."""

    def __init__(self, capacity: int, ttl_seconds: float,
                 clock: Callable[[], float] = time.time) -> None:
        self._cap = capacity
        self._ttl = ttl_seconds
        self._clock = clock
        self._data: "OrderedDict[str, _Entry]" = OrderedDict()

    def put(self, key: str, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key)
            return
        self._data[key] = _Entry(value, self._clock() + self._ttl)
        self._data.move_to_end(key)
        while len(self._data) > self._cap:
            self._data.popitem(last=False)   # evict the front (least recently used)

    def get(self, key: str) -> Any:
        e = self._data.get(key)
        if e is None:
            return None
        return e.value

    def size(self) -> int:
        return len(self._data)
