from dataclasses import dataclass
from typing import Optional

from .api import GameServerAPI
from .clock import Clock
from .config import DEFAULT_LOBBY_SIZE, DEFAULT_SKILL_WINDOW, SIMULATED_DB_LATENCY
from .events import EventLog
from .lobby_service import LobbyService
from .match_queue import MatchQueue
from .matchmaker import Matchmaker
from .queue_service import QueueService
from .repos import LobbyRepository, PairingRepository, PlayerRepository


@dataclass
class GameServer:
    clock: Clock
    events: EventLog
    players: PlayerRepository
    lobbies: LobbyRepository
    pairings: PairingRepository
    queue: MatchQueue
    queue_service: QueueService
    lobby_service: LobbyService
    matchmaker: Matchmaker
    api: GameServerAPI


def build_server(
    clock: Optional[Clock] = None,
    lobby_size: int = DEFAULT_LOBBY_SIZE,
    skill_window: int = DEFAULT_SKILL_WINDOW,
    db_latency: float = SIMULATED_DB_LATENCY,
) -> GameServer:
    clock = clock or Clock()
    events = EventLog()
    players = PlayerRepository()
    lobbies = LobbyRepository(latency=db_latency)
    pairings = PairingRepository()
    queue = MatchQueue()
    queue_service = QueueService(queue, players, events, clock)
    lobby_service = LobbyService(lobbies, players, pairings, events, clock)
    matchmaker = Matchmaker(queue, lobby_service, clock, events, lobby_size, skill_window)
    api = GameServerAPI(queue_service, lobby_service, matchmaker)
    return GameServer(
        clock=clock,
        events=events,
        players=players,
        lobbies=lobbies,
        pairings=pairings,
        queue=queue,
        queue_service=queue_service,
        lobby_service=lobby_service,
        matchmaker=matchmaker,
        api=api,
    )
