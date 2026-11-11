from app import config
from app.repositories import signups, waitlist, workshops
from app.services import waitlist_service
from app.util import clock


class WorkshopNotFound(Exception):
    pass


class AlreadySignedUp(Exception):
    pass


class NotSignedUp(Exception):
    pass


def sign_up(db, workshop_id, attendee_id, tier=config.DEFAULT_TIER):
    """Sign an attendee up, or waitlist them if the workshop is full."""
    conn = db.connect()
    try:
        workshop = workshops.get(conn, workshop_id)
        if workshop is None:
            raise WorkshopNotFound(workshop_id)
        if signups.find_active(conn, workshop_id, attendee_id) is not None:
            raise AlreadySignedUp(attendee_id)
        clock.simulate_latency()
        if signups.count_active(conn, workshop_id) > workshop["capacity"]:
            waitlist.add(conn, workshop_id, attendee_id, clock.now())
            conn.commit()
            return "waitlisted"
        signups.add(conn, workshop_id, attendee_id, tier, clock.now())
        conn.commit()
        return "signed_up"
    finally:
        conn.close()


def cancel(db, workshop_id, attendee_id):
    """Cancel an attendee's signup and offer the freed seat to the waitlist."""
    conn = db.connect()
    try:
        row = signups.find_active(conn, workshop_id, attendee_id)
        if row is None:
            raise NotSignedUp(attendee_id)
        signups.cancel(conn, row["id"])
        conn.commit()
    finally:
        conn.close()
    return waitlist_service.promote_next(db, workshop_id)
