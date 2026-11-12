from __future__ import annotations
from enum import Enum
from typing import Callable
import time


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Guards calls to a downstream service. While CLOSED, consecutive failures
    are counted; at the threshold the breaker OPENS. After a cooldown it becomes
    HALF_OPEN and admits a single probe. A successful probe closes the breaker, a
    failed probe opens it again."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 30.0,
                 clock: Callable[[], float] = time.monotonic) -> None:
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be non-negative")
        self._threshold = failure_threshold
        self._cooldown = cooldown_seconds
        self._clock = clock
        self._state = BreakerState.CLOSED
        self._failures = 0
        self._opened_at: float | None = None
        self._probes = 0

    def allow(self) -> bool:
        self._refresh()
        if self._state is BreakerState.OPEN:
            return False
        if self._state is BreakerState.HALF_OPEN:
            return True
        return True

    def record_success(self) -> None:
        if self._state is BreakerState.HALF_OPEN:
            self._state = BreakerState.CLOSED
            self._opened_at = None
            self._failures = 0
        self._probes = 0

    def record_failure(self) -> None:
        if self._state is BreakerState.HALF_OPEN:
            self._state = BreakerState.OPEN
            self._opened_at = self._clock()
            self._probes = 0
            return
        if self._state is BreakerState.OPEN:
            return
        self._failures += 1
        if self._failures >= self._threshold:
            self._state = BreakerState.OPEN
            self._opened_at = self._clock()

    def state(self) -> BreakerState:
        self._refresh()
        return self._state

    def failure_count(self) -> int:
        return self._failures

    def reset(self) -> None:
        self._state = BreakerState.CLOSED
        self._opened_at = None
        self._probes = 0

    def _refresh(self) -> None:
        if self._state is BreakerState.OPEN and self._opened_at is not None:
            if self._clock() - self._opened_at >= self._cooldown:
                self._state = BreakerState.HALF_OPEN
                self._probes = 0
