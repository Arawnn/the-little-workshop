from dataclasses import dataclass
from enum import Enum, auto

@dataclass(frozen=True)
class Action:
    id: str
    type: str
    machine_id: str
    target: str | None = None

@dataclass(frozen=True)
class Event:
    type: str
    action_id: str
    machine_id: str

class State(Enum):
    IDLE = auto()
    MOVING = auto()
    INSPECTING = auto()
    REPAIRING = auto()
    DONE = auto()

class RobotStateMachine:
    def __init__(self):
        self.state = State.MOVING

    def handle(self, event: Event) -> Action | None:
        # TODO 1: Ignorer les événements
        # différents de "action.completed"
        if event.type != "action.completed":
            return None
        # TODO 2: MOVING -> INSPECTING
        # Retourner une action inspect
        if self.state == State.MOVING:
            self.state = State.INSPECTING
            return Action(
                id="action-002",
                type="inspect",
                machine_id=event.machine_id,
                target="POI-42"
            )
        # TODO 3: INSPECTING -> REPAIRING
        # Retourner une action repair
        if self.state == State.INSPECTING:
            self.state = State.REPAIRING
            return Action(
                id="action-003",
                type="repair",
                machine_id=event.machine_id,
                target="POI-42"
            )
        # TODO 4: REPAIRING -> DONE
        # Ne retourner aucune action
        if self.state == State.REPAIRING:
            self.state = State.DONE
            return None
        return None


robot = RobotStateMachine()

event = Event(
    type="action.completed",
    action_id="action-001",
    machine_id="machine-001"
)

print("Initial:", robot.state.name)

action = robot.handle(event)
print("After first event:", robot.state.name)
print("Next action:", action)

action = robot.handle(event)
print("After second event:", robot.state.name)
print("Next action:", action)

action = robot.handle(event)
print("After third event:", robot.state.name)
print("Next action:", action)