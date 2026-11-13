_customers = {}


def add(customer):
    _customers[customer.customer_id] = customer


def get(customer_id):
    return _customers.get(customer_id)


def reset():
    _customers.clear()
