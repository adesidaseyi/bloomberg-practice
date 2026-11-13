from dataclasses import dataclass, field


@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    business_date: str          # YYYY-MM-DD
    currency: str
    lines: list = field(default_factory=list)
    total_fees: float = 0.0
    total_notional: float = 0.0
    created_at: float = 0.0
