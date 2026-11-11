from app.repositories import signups, workshops


def roster(db, workshop_id):
    conn = db.connect()
    try:
        return [r["attendee_id"] for r in signups.list_active(conn, workshop_id)]
    finally:
        conn.close()


def fill_rate(db, workshop_id):
    conn = db.connect()
    try:
        w = workshops.get(conn, workshop_id)
        return signups.count_active(conn, workshop_id) / w["capacity"]
    finally:
        conn.close()
