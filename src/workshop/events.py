from dataclasses import dataclass
from enum import Enum, auto
import uuid

from workshop.vec3 import Vec3

@dataclass(frozen=True)
class Event:
    type: str
    machine_id: str
    action_id: uuid.UUID | None = None

@dataclass(frozen=True)
class Action:
    id: uuid.UUID
    type: ActionType
    machine_id: str
    target: Vec3


class ActionType(Enum):
    MOVE_TO = auto()
    INSPECT = auto()
    REPAIR = auto()


