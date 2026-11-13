from app.models.trade import Trade
from app.services import invoicing
from app.storage import trades_repo


def test_simple_invoice():
    # 2026-11-10 15:00 UTC, well inside the business day
    trades_repo.add(Trade("t1", "c1", "AAPL", 100, 200.0, "USD", 1_794_322_800.0))
    inv = invoicing.generate_invoice("c1", "2026-11-10")
    assert len(inv.lines) == 1
    assert inv.total_fees == 25.0


def test_late_tuesday_trade_is_in_tuesday_invoice():
    # 2026-11-10 23:00 UTC-5 is 2026-11-11 04:00 UTC.
    trades_repo.add(Trade("t2", "c1", "AAPL", 100, 200.0, "USD", 1_794_369_600.0))
    inv = invoicing.generate_invoice("c1", "2026-11-10")
    assert any(line["trade_id"] == "t2" for line in inv.lines)
