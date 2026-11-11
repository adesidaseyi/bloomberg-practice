from app import config
from app.repositories import signups
from app.util import clock


def change_tier(db, workshop_id, attendee_id, new_tier):
    """Move an attendee between tiers without ever leaving them unregistered."""
    if new_tier not in config.TIERS:
        raise ValueError("unknown tier")
    conn = db.connect()
    try:
        old = signups.find_active(conn, workshop_id, attendee_id)
        if old is None:
            raise ValueError("not signed up")
        signups.add(conn, workshop_id, attendee_id, new_tier, clock.now())
        signups.cancel(conn, old["id"])
        conn.commit()
    finally:
        conn.close()
