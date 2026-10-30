import time
from typing import Protocol


class Clock(Protocol):
    def now(self) -> float: ...


class SystemClock(Clock):
    def now(self) -> float:
        return time.monotonic()
