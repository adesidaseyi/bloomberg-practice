from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import time


@dataclass
class _Window:
    start: float
    count: int


class RateLimiter:
    """A fixed-window per-key rate limiter. Each key may be allowed up to `limit`
    times per `window_seconds`. When the window elapses the count resets."""

    def __init__(self, limit: int, window_seconds: float,
                 clock: Callable[[], float] = time.time) -> None:
        self._limit = limit
        self._window = window_seconds
        self._clock = clock
        self._state: dict[str, _Window] = {}

    def allow(self, key: str) -> bool:
        now = self._clock()
        st = self._state.get(key)
        if st is None:
            st = _Window(now, 0)
            self._state[key] = st
        st.count += 1
        if st.count <= self._limit:
            return True
        return False

    def remaining(self, key: str) -> int:
        st = self._state.get(key)
        if st is None:
            return 0
        return self._limit - st.count

    def reset(self, key: str) -> None:
        pass
