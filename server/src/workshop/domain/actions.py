import uuid
from dataclasses import dataclass
from enum import Enum, auto

from workshop.domain.vec3 import Vec3


class ActionType(Enum):
    MOVE_TO = auto()
    INSPECT = auto()
    REPAIR = auto()


ACTION_DURATIONS: dict[ActionType, float] = {
    ActionType.MOVE_TO: 2.0,
    ActionType.INSPECT: 1.0,
    ActionType.REPAIR: 3.0,
}


@dataclass(frozen=True)
class Action:
    id: uuid.UUID
    type: ActionType
    machine_id: uuid.UUID
    target: Vec3 | None = None
