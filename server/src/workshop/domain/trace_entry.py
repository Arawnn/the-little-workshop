from dataclasses import dataclass

from workshop.domain.events import EventType
from workshop.domain.robot_fsm import Reject, Transition
from workshop.domain.world import RobotState


@dataclass(frozen=True)
class TraceEntry:
    before: RobotState
    event_type: EventType
    outcome: Transition | Reject | None
    after: RobotState
    t: float
