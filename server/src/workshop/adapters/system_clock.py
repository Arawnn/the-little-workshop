import time

from workshop.domain.clock import Clock


class SystemClock(Clock):
    def now(self) -> float:
        return time.monotonic()
