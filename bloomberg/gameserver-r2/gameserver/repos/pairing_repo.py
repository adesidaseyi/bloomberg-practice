import threading
from typing import List, Optional

from ..models import Pairing


class PairingRepository:
    """Which players are currently paired, ordered newest first.

    Ordering key is (paired_at DESC, player_id ASC). Every member of a lobby
    formed in the same matchmaking tick shares the same paired_at.
    """

    def __init__(self) -> None:
        self._pairings: List[Pairing] = []
        self._lock = threading.Lock()

    @staticmethod
    def sort_key(pairing: Pairing):
        return (-pairing.paired_at, pairing.player_id)

    def record(self, pairing: Pairing) -> None:
        with self._lock:
            self._pairings.append(pairing)
            self._pairings.sort(key=self.sort_key)

    def remove_player(self, player_id: str) -> Optional[Pairing]:
        with self._lock:
            for i, pairing in enumerate(self._pairings):
                if pairing.player_id == player_id:
                    return self._pairings.pop(i)
            return None

    def newest_first(self) -> List[Pairing]:
        with self._lock:
            return list(self._pairings)
