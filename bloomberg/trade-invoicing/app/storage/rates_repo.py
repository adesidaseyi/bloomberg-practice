_rates = {}


def set_rate(from_ccy, to_ccy, rate):
    _rates[(from_ccy, to_ccy)] = rate


def get(from_ccy, to_ccy):
    return _rates[(from_ccy, to_ccy)]


def reset():
    _rates.clear()
