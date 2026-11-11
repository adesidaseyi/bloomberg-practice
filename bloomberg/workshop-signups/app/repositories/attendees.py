def add(conn, attendee_id, name, email):
    conn.execute("INSERT INTO attendees (id, name, email) VALUES (?, ?, ?)", (attendee_id, name, email))


def get(conn, attendee_id):
    return conn.execute("SELECT * FROM attendees WHERE id = ?", (attendee_id,)).fetchone()
