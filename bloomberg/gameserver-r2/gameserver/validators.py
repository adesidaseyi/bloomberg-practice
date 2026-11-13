from .config import MAX_PAGE_SIZE, MAX_SKILL
from .errors import ValidationError


def validate_player_id(player_id: str) -> str:
    if not isinstance(player_id, str) or not player_id.strip():
        raise ValidationError("player_id must be a non-empty string")
    if len(player_id) > 64:
        raise ValidationError("player_id too long")
    return player_id


def validate_skill(skill: int) -> int:
    if isinstance(skill, bool) or not isinstance(skill, int):
        raise ValidationError("skill must be an int")
    if not 0 <= skill <= MAX_SKILL:
        raise ValidationError("skill out of range")
    return skill


def validate_limit(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValidationError("limit must be an int")
    if not 1 <= limit <= MAX_PAGE_SIZE:
        raise ValidationError("limit out of range")
    return limit
