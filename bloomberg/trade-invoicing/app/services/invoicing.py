from app.models.invoice import Invoice
from app.services import fx, pricing
from app.storage import customers_repo, invoices_repo, trades_repo
from app.util import clock, dates, ids


class CustomerNotFound(Exception):
    pass


def generate_invoice(customer_id, business_date):
    """Build and store the invoice for one customer and business day."""
    customer = customers_repo.get(customer_id)
    if customer is None:
        raise CustomerNotFound(customer_id)

    day_trades = [
        t for t in trades_repo.for_customer(customer_id)
        if dates.business_date(t.executed_at) == business_date
    ]
    lines = []
    for t in sorted(day_trades, key=lambda t: t.executed_at):
        lines.append({
            "trade_id": t.trade_id,
            "symbol": t.symbol,
            "notional": fx.convert(pricing.notional(t), t.currency, customer.base_currency),
            "fee": fx.convert(pricing.fee(t), t.currency, customer.base_currency),
        })
    invoice = Invoice(
        invoice_id=ids.new_id("INV"),
        customer_id=customer_id,
        business_date=business_date,
        currency=customer.base_currency,
        lines=lines,
        total_fees=round(sum(l["fee"] for l in lines), 2),
        total_notional=round(sum(l["notional"] for l in lines), 2),
        created_at=clock.now(),
    )
    invoices_repo.add(invoice)
    return invoice
