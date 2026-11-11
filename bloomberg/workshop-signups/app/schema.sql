CREATE TABLE attendees (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL
);
CREATE TABLE workshops (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, capacity INTEGER NOT NULL, starts_at REAL NOT NULL
);
CREATE TABLE signups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workshop_id TEXT NOT NULL, attendee_id TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'standard',
    status TEXT NOT NULL DEFAULT 'active',   -- active | cancelled
    created_at REAL NOT NULL
);
CREATE TABLE waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workshop_id TEXT NOT NULL, attendee_id TEXT NOT NULL, joined_at REAL NOT NULL
);
CREATE INDEX idx_signups_workshop ON signups (workshop_id, status);
CREATE INDEX idx_waitlist_workshop ON waitlist (workshop_id, joined_at);
