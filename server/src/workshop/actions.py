import uuid
from dataclasses import dataclass
from enum import Enum, auto

from workshop.vec3 import Vec3


class ActionType(Enum):
    MOVE_TO = auto()
    INSPECT = auto()
    REPAIR = auto()


@dataclass(frozen=True)
class Action:
    id: uuid.UUID
    type: ActionType
    machine_id: uuid.UUID
    target: Vec3 | None = None
