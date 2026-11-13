from app.storage import rates_repo

_cache = {}


def get_rate(from_ccy, to_ccy):
    key = (from_ccy, to_ccy)
    if key not in _cache:
        _cache[key] = rates_repo.get(from_ccy, to_ccy)
    return _cache[key]


def convert(amount, from_ccy, to_ccy):
    if from_ccy == to_ccy:
        return amount
    return round(amount * get_rate(from_ccy, to_ccy), 2)


def reset():
    _cache.clear()
