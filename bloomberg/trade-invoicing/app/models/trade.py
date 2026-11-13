from dataclasses import dataclass


@dataclass
class Trade:
    trade_id: str
    customer_id: str
    symbol: str
    qty: int
    price: float
    currency: str
    executed_at: float  # epoch seconds (UTC)
