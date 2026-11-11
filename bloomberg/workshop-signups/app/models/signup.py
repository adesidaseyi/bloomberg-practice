from dataclasses import dataclass


@dataclass
class Signup:
    id: int
    workshop_id: str
    attendee_id: str
    tier: str
    status: str
    created_at: float
