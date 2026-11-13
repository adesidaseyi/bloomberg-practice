import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest

from app.models.customer import Customer
from app.services import fx
from app.storage import customers_repo, invoices_repo, rates_repo, trades_repo


@pytest.fixture(autouse=True)
def clean_state():
    for mod in (customers_repo, invoices_repo, rates_repo, trades_repo, fx):
        mod.reset()
    customers_repo.add(Customer("c1", "Acme Capital", "USD"))
    customers_repo.add(Customer("c2", "Euro Funds", "EUR"))
    yield
