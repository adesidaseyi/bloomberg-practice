OUTBOX: list[dict] = []


def send(to: str, subject: str) -> dict:
    msg = {"to": to, "subject": subject}
    OUTBOX.append(msg)
    return msg


def reset() -> None:
    OUTBOX.clear()
