import pathlib
import sqlite3

SCHEMA = pathlib.Path(__file__).with_name("schema.sql")


class Database:
    """Thin wrapper over a SQLite file. Each caller opens its own connection."""

    def __init__(self, path: str) -> None:
        self.path = path
        conn = self.connect()
        conn.executescript(SCHEMA.read_text())
        conn.commit()
        conn.close()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
