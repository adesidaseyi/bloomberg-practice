from datetime import datetime, timezone


def business_date(ts: float) -> str:
    """The business day (YYYY-MM-DD) a timestamp belongs to."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
