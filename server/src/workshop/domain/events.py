import uuid
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    MACHINE_BROKE = "machine.broke"
    ACTION_COMPLETED = "action.completed"


@dataclass(frozen=True)
class Event:
    type: EventType
    machine_id: uuid.UUID
    action_id: uuid.UUID | None = None
