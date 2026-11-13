import dataclasses
import json


def to_json(invoice):
    """Serialise an invoice for the billing system (money as JSON numbers)."""
    return json.dumps(dataclasses.asdict(invoice), sort_keys=True)
