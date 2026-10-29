import heapq
import itertools

from workshop.events import Event


class PriorityEventQueue:
    def __init__(self) -> None:
        self._heap: list[tuple[float, int, Event]] = []
        self._counter = itertools.count()
        self._current_time = 0.0

    def push(self, time: float, event: Event) -> None:
        heapq.heappush(self._heap, (time, next(self._counter), event))

    def pop(self) -> tuple[float, Event]:
        simulated_time, _, event = heapq.heappop(self._heap)
        self._current_time = simulated_time
        return (simulated_time, event)

    def current_time(self) -> float:

        return self._current_time

    def __len__(self) -> int:
        return len(self._heap)
