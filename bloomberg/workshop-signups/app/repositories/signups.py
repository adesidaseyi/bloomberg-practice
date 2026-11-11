def add(conn, workshop_id, attendee_id, tier, created_at):
    cur = conn.execute(
        "INSERT INTO signups (workshop_id, attendee_id, tier, status, created_at) "
        "VALUES (?, ?, ?, 'active', ?)",
        (workshop_id, attendee_id, tier, created_at),
    )
    return cur.lastrowid


def find_active(conn, workshop_id, attendee_id):
    return conn.execute(
        "SELECT * FROM signups WHERE workshop_id = ? AND attendee_id = ? AND status = 'active'",
        (workshop_id, attendee_id),
    ).fetchone()


def count_active(conn, workshop_id):
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM signups WHERE workshop_id = ? AND status = 'active'",
        (workshop_id,),
    ).fetchone()
    return row["n"]


def cancel(conn, signup_id):
    conn.execute("UPDATE signups SET status = 'cancelled' WHERE id = ?", (signup_id,))


def list_active(conn, workshop_id):
    return conn.execute(
        "SELECT * FROM signups WHERE workshop_id = ? AND status = 'active' ORDER BY id",
        (workshop_id,),
    ).fetchall()


def for_reminders(conn, window_start, window_end):
    return conn.execute(
        "SELECT s.id, s.workshop_id, s.attendee_id, a.email, w.title "
        "FROM signups s "
        "JOIN attendees a ON a.id = s.attendee_id "
        "JOIN workshops w ON w.id = s.workshop_id "
        "WHERE w.starts_at >= ? AND w.starts_at < ?",
        (window_start, window_end),
    ).fetchall()
