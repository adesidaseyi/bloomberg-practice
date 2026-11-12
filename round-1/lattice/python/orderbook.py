from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Order:
    order_id: str
    side: Side
    price_cents: int
    qty: int
    remaining: int
    status: OrderStatus
    seq: int


@dataclass
class Trade:
    trade_id: str
    price_cents: int
    qty: int
    buy_order_id: str
    sell_order_id: str


class OrderBook:
    """A single-symbol limit order book with price-time priority. A marketable
    order executes against resting liquidity, best price first and oldest order
    first within a price level, until it is filled or the next level no longer
    crosses. Trades print at the resting order's price; any remainder rests."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._bids: dict[str, Order] = {}
        self._asks: dict[str, Order] = {}
        self._seq = 0
        self._trade_seq = 0

    def submit(self, side: str, price_cents: int, qty: int) -> list[Trade]:
        if side not in ("buy", "sell"):
            raise ValueError("side must be buy or sell")
        if price_cents <= 0:
            raise ValueError("price must be positive")
        if qty <= 0:
            raise ValueError("qty must be positive")
        s = Side(side)

        self._seq += 1
        incoming = Order(f"O{self._seq}", s, price_cents, qty, qty,
                         OrderStatus.OPEN, self._seq)
        self._orders[incoming.order_id] = incoming
        trades: list[Trade] = []

        resting = self._best_opposite(s)
        if resting is not None and self._crosses(incoming, resting):
            level = resting.price_cents
            while incoming.remaining > 0:
                resting = self._best_opposite(s)
                if resting is None or resting.price_cents != level:
                    break
                if not self._crosses(incoming, resting):
                    break
                self._execute(incoming, resting, trades)

        if incoming.remaining == 0:
            incoming.status = OrderStatus.FILLED
        else:
            if incoming.remaining < incoming.qty:
                incoming.status = OrderStatus.PARTIAL
            self._book(s)[incoming.order_id] = incoming
        return trades

    def cancel(self, order_id: str) -> Order:
        order = self.order(order_id)
        if order.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
            raise ValueError("only open or partially filled orders can be cancelled")
        order.status = OrderStatus.CANCELLED
        self._bids.pop(order_id, None)
        self._asks.pop(order_id, None)
        return order

    def order(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError("order not found")
        return order

    def best_bid(self) -> int | None:
        if not self._bids:
            return None
        return max(o.price_cents for o in self._bids.values())

    def best_ask(self) -> int | None:
        if not self._asks:
            return None
        return min(o.price_cents for o in self._asks.values())

    def _execute(self, incoming: Order, resting: Order, trades: list[Trade]) -> None:
        take = min(incoming.remaining, resting.remaining)
        self._trade_seq += 1
        if incoming.side is Side.BUY:
            buy_id, sell_id = incoming.order_id, resting.order_id
        else:
            buy_id, sell_id = resting.order_id, incoming.order_id
        trades.append(Trade(f"T{self._trade_seq}", incoming.price_cents, take,
                            buy_id, sell_id))
        incoming.remaining -= take
        resting.remaining -= take
        if incoming.remaining == 0:
            incoming.status = OrderStatus.FILLED
        else:
            incoming.status = OrderStatus.PARTIAL
        if resting.remaining == 0:
            resting.status = OrderStatus.FILLED
            self._book(resting.side).pop(resting.order_id, None)
        else:
            resting.status = OrderStatus.PARTIAL

    def _best_opposite(self, side: Side) -> Order | None:
        book = self._asks if side is Side.BUY else self._bids
        if not book:
            return None
        if side is Side.BUY:
            return min(book.values(), key=lambda o: (o.price_cents, -o.seq))
        return min(book.values(), key=lambda o: (-o.price_cents, -o.seq))

    @staticmethod
    def _crosses(incoming: Order, resting: Order) -> bool:
        if incoming.side is Side.BUY:
            return resting.price_cents <= incoming.price_cents
        return resting.price_cents >= incoming.price_cents

    def _book(self, side: Side) -> dict[str, Order]:
        return self._bids if side is Side.BUY else self._asks
