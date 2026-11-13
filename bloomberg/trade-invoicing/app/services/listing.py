from app import config
from app.storage import invoices_repo


def list_invoices(customer_id, page=1):
    """One page of a customer's invoices, oldest first. Pages start at 1."""
    items = sorted(invoices_repo.for_customer(customer_id), key=lambda i: i.created_at)
    start = (page - 1) * config.PAGE_SIZE
    end = start + config.PAGE_SIZE - 1
    return items[start:end]
