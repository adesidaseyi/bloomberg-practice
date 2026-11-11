import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest

from app.db import Database
from app.notifications import email
from app.repositories import attendees, workshops


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    conn = database.connect()
    for i in range(1, 7):
        attendees.add(conn, f"a{i}", f"Attendee {i}", f"a{i}@example.com")
    workshops.add(conn, "w1", "Intro to Rust", 2, 2_000_000_000.0)
    conn.commit()
    conn.close()
    email.reset()
    return database
