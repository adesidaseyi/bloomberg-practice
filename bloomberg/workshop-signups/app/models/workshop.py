from dataclasses import dataclass


@dataclass
class Workshop:
    id: str
    title: str
    capacity: int
    starts_at: float
