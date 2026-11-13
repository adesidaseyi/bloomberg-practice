from app import config
from app.storage import trades_repo
from app.util import dates

PER_LINE_TOLERANCE = 0.01


def check(invoice):
    """Independent check: do the invoice's fees match the day's trades?"""
    trades = [
        t for t in trades_repo.for_customer(invoice.customer_id)
        if dates.business_date(t.executed_at) == invoice.business_date
    ]
    expected = sum(t.qty * t.price * config.FEE_RATE for t in trades)
    tolerance = PER_LINE_TOLERANCE * max(1, len(trades))
    return abs(invoice.total_fees - expected) <= tolerance
