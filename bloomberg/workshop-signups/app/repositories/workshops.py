def add(conn, workshop_id, title, capacity, starts_at):
    conn.execute(
        "INSERT INTO workshops (id, title, capacity, starts_at) VALUES (?, ?, ?, ?)",
        (workshop_id, title, capacity, starts_at),
    )


def get(conn, workshop_id):
    return conn.execute("SELECT * FROM workshops WHERE id = ?", (workshop_id,)).fetchone()
