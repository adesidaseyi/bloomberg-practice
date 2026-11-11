def add(conn, workshop_id, attendee_id, joined_at):
    conn.execute(
        "INSERT INTO waitlist (workshop_id, attendee_id, joined_at) VALUES (?, ?, ?)",
        (workshop_id, attendee_id, joined_at),
    )


def next_in_line(conn, workshop_id):
    return conn.execute(
        "SELECT * FROM waitlist WHERE workshop_id = ? ORDER BY joined_at DESC LIMIT 1",
        (workshop_id,),
    ).fetchone()


def remove(conn, entry_id):
    conn.execute("DELETE FROM waitlist WHERE id = ?", (entry_id,))


def list_all(conn, workshop_id):
    return conn.execute(
        "SELECT * FROM waitlist WHERE workshop_id = ? ORDER BY joined_at", (workshop_id,)
    ).fetchall()
