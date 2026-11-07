from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable
import time


class SubStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Subscription:
    sub_id: str
    user_id: str
    status: SubStatus
    expires_at: float | None


class SubscriptionService:
    """Entitlement lifecycle for a SaaS product. A subscription starts as a TRIAL
    with a TTL, is ACTIVE once paid, can be SUSPENDED and resumed, and can be
    CANCELLED. An unpaid trial that runs out of time EXPIRES."""

    def __init__(self, trial_ttl_seconds: int = 60, clock: Callable[[], float] = time.time) -> None:
        self._subs: dict[str, Subscription] = {}
        self._ttl = trial_ttl_seconds
        self._clock = clock
        self._seq = 0

    def start_trial(self, user_id: str) -> Subscription:
        self._seq += 1
        sid = f"S{self._seq}"
        sub = Subscription(sid, user_id, SubStatus.TRIAL, self._clock() + self._ttl)
        self._subs[sid] = sub
        return sub

    def activate(self, sub_id: str) -> Subscription:
        sub = self._get(sub_id)
        sub.status = SubStatus.ACTIVE
        sub.expires_at = None
        return sub

    def suspend(self, sub_id: str) -> Subscription:
        sub = self._get(sub_id)
        if sub.status not in (SubStatus.TRIAL, SubStatus.ACTIVE):
            raise ValueError("only active subscriptions can be suspended")
        sub.status = SubStatus.SUSPENDED
        return sub

    def resume(self, sub_id: str) -> Subscription:
        sub = self._get(sub_id)
        if sub.status != SubStatus.SUSPENDED:
            raise ValueError("only suspended subscriptions can be resumed")
        sub.status = SubStatus.ACTIVE
        return sub

    def cancel(self, sub_id: str) -> Subscription:
        sub = self._get(sub_id)
        sub.status = SubStatus.CANCELLED
        sub.expires_at = None
        return sub

    def is_entitled(self, sub_id: str) -> bool:
        sub = self._get(sub_id)
        if sub.status == SubStatus.ACTIVE:
            return True
        if sub.status == SubStatus.SUSPENDED:
            return True
        if sub.status == SubStatus.TRIAL:
            return True
        return False

    def _get(self, sub_id: str) -> Subscription:
        sub = self._subs.get(sub_id)
        if sub is None:
            raise ValueError("subscription not found")
        return sub

    def _cleanup_expired(self) -> None:
        now = self._clock()
        for sub in self._subs.values():
            if sub.status == SubStatus.TRIAL and sub.expires_at is not None and sub.expires_at <= now:
                sub.status = SubStatus.EXPIRED
