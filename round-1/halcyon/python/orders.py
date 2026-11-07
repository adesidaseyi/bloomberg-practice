from __future__ import annotations
import unittest
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
        # Keep the active order objects in a map keyed by their generated order_id.
        self._orders: dict[str, Order] = {}
        self._seq = 0

    def place(self, symbol: str, side: str, qty: int) -> Order:
        # Create a new Order object for the requested symbol/side/quantity and store it.
        if side not in ("buy", "sell"):
            raise ValueError("side must be buy or sell")
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._seq += 1
        oid = f"O{self._seq}"
        order = Order(oid, symbol, side, qty, 0, OrderStatus.OPEN)
        self._orders[oid] = order
        return order

    # report orders that over-fill
    def fill(self, order_id: str, qty: int) -> Order:
        # Update the matching Order object to reflect a trade execution against its open quantity.
        order = self._get(order_id)
        if qty <= 0:
            raise ValueError("fill qty must be positive")
        if order.filled + qty > order.qty:
            raise ValueError("fill exceeds order qty")
        order.filled += qty
        if order.filled == order.qty:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL
        return order

    def cancel(self, order_id: str) -> Order:
        # Mark the selected Order as cancelled so it is no longer active in the order book.
        order = self._get(order_id)
        order.status = OrderStatus.CANCELLED
        return order

    def remaining(self, order_id: str) -> int:
        # Return how much of the Order is still unfilled based on its filled amount.
        order = self._get(order_id)
        return order.qty - order.filled

    def open_qty_for(self, symbol: str) -> int:
        # Sum the remaining quantity across all Order objects for a given symbol.
        return sum(o.qty - o.filled for o in self._orders.values() if o.symbol == symbol)

    def _get(self, order_id: str) -> Order:
        # Fetch the tracked Order object by its id, raising if it is not present.
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError("order not found")
        return order


if __name__ == "__main__":
    class OrderServiceTests(unittest.TestCase):
        def test_partial_fill_sets_partial_status(self):
            service = OrderService()
            order = service.place("AAPL", "buy", 10)

            service.fill(order.order_id, 4)

            self.assertEqual(order.status, OrderStatus.PARTIAL)

        def test_overfill_detected(self):
            service = OrderService()
            order = service.place("AAPL", "buy", 10)

            service.fill(order.order_id, 8)
            service.fill(order.order_id, 3)

            self.assertLessEqual(order.filled, order.qty)

    unittest.main()