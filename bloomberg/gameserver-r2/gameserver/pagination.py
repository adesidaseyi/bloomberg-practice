from typing import Optional

from .errors import ValidationError


def encode_offset_cursor(offset: int) -> str:
    return str(offset)


def decode_offset_cursor(cursor: Optional[str]) -> int:
    if cursor is None:
        return 0
    try:
        offset = int(cursor)
    except (TypeError, ValueError):
        raise ValidationError("invalid cursor")
    if offset < 0:
        raise ValidationError("invalid cursor")
    return offset
