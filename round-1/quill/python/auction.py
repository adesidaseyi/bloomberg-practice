from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable
import time


class AuctionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Bid:
    bid_id: str
    bidder_id: str
    amount_cents: int


class AuctionService:
    """A single-item auction with a reserve price and a fixed closing instant.
    Bids are accepted only while the auction is open, at or above the reserve,
    and strictly above the current highest bid. The highest bid wins at close."""

    def __init__(self, reserve_cents: int, closes_at: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        if reserve_cents < 0:
            raise ValueError("reserve must be non-negative")
        self._reserve = reserve_cents
        self._closes_at = closes_at
        self._clock = clock
        self._status = AuctionStatus.OPEN
        self._highest: Bid | None = None
        self._seq = 0

    def bid(self, bidder_id: str, cents: int) -> Bid:
        if cents <= 0:
            raise ValueError("bid amount must be positive")
        self._seq += 1
        bid = Bid(f"B{self._seq}", bidder_id, cents)
        self._highest = bid
        return bid

    def status(self) -> AuctionStatus:
        self._refresh()
        return self._status

    def highest_bid(self) -> Bid | None:
        return self._highest

    def winner(self) -> Bid | None:
        self._refresh()
        if self._status is AuctionStatus.OPEN:
            return None
        return self._highest

    def _refresh(self) -> None:
        if self._status is AuctionStatus.OPEN and self._clock() >= self._closes_at:
            self._status = AuctionStatus.CLOSED
