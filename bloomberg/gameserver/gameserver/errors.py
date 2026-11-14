class GameServerError(Exception):
    """Base class for all domain errors."""


class ValidationError(GameServerError):
    pass


class PlayerNotFoundError(GameServerError):
    pass


class PlayerAlreadyActiveError(GameServerError):
    """Player is already queued or already in a lobby."""


class LobbyNotFoundError(GameServerError):
    pass


class LobbyFullError(GameServerError):
    pass
