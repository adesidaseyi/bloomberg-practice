from app import config
from app.repositories import signups, waitlist, workshops
from app.util import clock


def promote_next(db, workshop_id):
    """Move the next waitlisted attendee into the workshop if a seat is free."""
    conn = db.connect()
    try:
        workshop = workshops.get(conn, workshop_id)
        if signups.count_active(conn, workshop_id) >= workshop["capacity"]:
            return None
        entry = waitlist.next_in_line(conn, workshop_id)
        if entry is None:
            return None
        signups.add(conn, workshop_id, entry["attendee_id"], config.DEFAULT_TIER, clock.now())
        waitlist.remove(conn, entry["id"])
        conn.commit()
        return entry["attendee_id"]
    finally:
        conn.close()
