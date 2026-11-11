from app import config
from app.notifications import email
from app.repositories import signups
from app.util import clock


def due_reminders(db, now=None):
    now = clock.now() if now is None else now
    conn = db.connect()
    try:
        return signups.for_reminders(conn, now, now + config.REMINDER_WINDOW_SECONDS)
    finally:
        conn.close()


def send_reminders(db, now=None):
    sent = 0
    for row in due_reminders(db, now):
        email.send(row["email"], f"Reminder: {row['title']} starts soon")
        sent += 1
    return sent
