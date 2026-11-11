from dataclasses import dataclass


@dataclass
class WaitlistEntry:
    id: int
    workshop_id: str
    attendee_id: str
    joined_at: float
