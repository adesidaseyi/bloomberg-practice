_trades = []


def add(trade):
    _trades.append(trade)


def for_customer(customer_id):
    return [t for t in _trades if t.customer_id == customer_id]


def reset():
    _trades.clear()
