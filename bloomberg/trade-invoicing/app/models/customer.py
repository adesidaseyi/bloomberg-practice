from dataclasses import dataclass


@dataclass
class Customer:
    customer_id: str
    name: str
    base_currency: str
