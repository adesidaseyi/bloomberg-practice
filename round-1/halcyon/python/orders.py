from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str
    qty: int
    filled: int
    status: OrderStatus


class OrderService:
    """Tracks working orders for a trading desk. Orders are placed OPEN, filled in
    one or more executions, and may be cancelled while they still have open quantity."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._seq = 0

    def place(self, symbol: str, side: str, qty: int) -> Order:
        if side not in ("buy", "sell"):
            raise ValueError("side must be buy or sell")
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._seq += 1
        oid = f"O{self._seq}"
        order = Order(oid, symbol, side, qty, 0, OrderStatus.OPEN)
        self._orders[oid] = order
        return order

    def fill(self, order_id: str, qty: int) -> Order:
        order = self._get(order_id)
        if qty <= 0:
            raise ValueError("fill qty must be positive")
        order.filled += qty
        if order.filled == order.qty:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL
        return order

    def cancel(self, order_id: str) -> Order:
        order = self._get(order_id)
        order.status = OrderStatus.CANCELLED
        return order

    def remaining(self, order_id: str) -> int:
        order = self._get(order_id)
        return order.qty - order.filled

    def open_qty_for(self, symbol: str) -> int:
        return sum(o.qty - o.filled for o in self._orders.values() if o.symbol == symbol)

    def _get(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError("order not found")
        return order
