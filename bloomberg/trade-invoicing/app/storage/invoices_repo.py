_invoices = []


def add(invoice):
    _invoices.append(invoice)


def for_customer(customer_id):
    return [i for i in _invoices if i.customer_id == customer_id]


def reset():
    _invoices.clear()
