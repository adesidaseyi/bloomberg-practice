import time

from app import config


def now() -> float:
    return time.time()


def simulate_latency() -> None:
    time.sleep(config.LATENCY_SECONDS)
