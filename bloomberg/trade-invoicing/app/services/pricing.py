from app import config


def notional(trade):
    return trade.qty * trade.price


def fee(trade):
    """Fee for one trade, in the trade's currency, rounded to cents."""
    return round(notional(trade) * config.FEE_RATE, 2)
