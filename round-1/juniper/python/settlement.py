from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable
import time


class TradeStatus(str, Enum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"


@dataclass
class Trade:
    trade_id: str
    account_id: str
    symbol: str
    qty: int
    price_cents: int
    settle_on: float
    status: TradeStatus


class SettlementService:
    """Tracks executed trades until they settle on or after their settlement
    date, or fail. Pending notional is the sum of qty * price_cents over pending
    trades."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._trades: dict[str, Trade] = {}
        self._seq = 0

    def book(self, account_id: str, symbol: str, qty: int, price_cents: int,
             settle_on: float) -> Trade:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if price_cents <= 0:
            raise ValueError("price must be positive")
        self._seq += 1
        trade = Trade(f"S{self._seq}", account_id, symbol, qty, price_cents,
                      settle_on, TradeStatus.PENDING)
        self._trades[trade.trade_id] = trade
        return trade

    def settle(self, trade_id: str) -> Trade:
        trade = self._get(trade_id)
        if trade.status is not TradeStatus.PENDING:
            raise ValueError("only pending trades can settle")
        trade.status = TradeStatus.SETTLED
        return trade

    def fail(self, trade_id: str) -> Trade:
        trade = self._get(trade_id)
        trade.status = TradeStatus.FAILED
        return trade

    def pending_notional(self, account_id: str) -> int:
        return sum(trade.qty * trade.price_cents
                   for trade in self._trades.values()
                   if trade.account_id == account_id)

    def trade(self, trade_id: str) -> Trade:
        return self._get(trade_id)

    def _get(self, trade_id: str) -> Trade:
        trade = self._trades.get(trade_id)
        if trade is None:
            raise ValueError("trade not found")
        return trade
