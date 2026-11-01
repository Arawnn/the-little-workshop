from typing import Protocol

from workshop.domain.trace_entry import TraceEntry


class EventStreamPublisher(Protocol):
    def publish(self, entries: list[TraceEntry]) -> None: ...
