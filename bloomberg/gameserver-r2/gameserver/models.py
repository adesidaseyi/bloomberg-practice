from dataclasses import dataclass, field
from enum import Enum
from typing import List


class PlayerStatus(str, Enum):
    IDLE = "idle"
    QUEUED = "queued"
    IN_LOBBY = "in_lobby"


@dataclass
class Player:
    player_id: str
    skill: int
    status: PlayerStatus = PlayerStatus.IDLE


@dataclass(frozen=True)
class QueueEntry:
    player_id: str
    skill: int
    enqueued_at: float


@dataclass
class Lobby:
    lobby_id: str
    capacity: int
    created_at: float
    member_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Pairing:
    """Records that a player is currently paired into a lobby."""

    player_id: str
    lobby_id: str
    paired_at: float
