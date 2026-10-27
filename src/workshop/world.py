from enum import Enum, auto
from dataclasses import dataclass, field
import uuid
from workshop.vec3 import Vec3

REACH = 1.5

class RobotState(Enum):
    IDLE = auto()
    MOVING = auto()
    INSPECTING = auto()
    REPAIRING = auto()

class MachineState(Enum):
    RUNNING = auto()
    BROKEN = auto()
    REPAIRING = auto()

class Diagnostic(Enum):
    JAMMED_GEAR = auto()
    OVERHEATED = auto()
    WORN_BELT = auto()

@dataclass
class Machine:
    id: uuid.UUID
    position: Vec3
    poi: Vec3
    wear: int
    state: MachineState
    diagnostic: Diagnostic | None = None

@dataclass
class Robot:
    id: uuid.UUID
    position: Vec3
    state: RobotState
    target_machine_id: uuid.UUID | None = None
    current_action_id: uuid.UUID | None = None

@dataclass
class World:
    robot: Robot = field(default_factory=lambda: Robot(
        id=uuid.uuid4(),
        position= Vec3(0,0,0),
        state=RobotState.IDLE
    ))
    machine: Machine = field(default_factory=lambda: Machine(
        id=uuid.uuid4(),
        position=Vec3(4,0,0),
        poi=Vec3(3,0,0),
        wear=0,
        state=MachineState.RUNNING
    ))

def diagnose(wear: int) -> Diagnostic:
    if wear > 100:
        raise ValueError("L'usure ne peut pas être supérieur à 100")
    if wear < 0: 
        raise ValueError("L'usure ne peut pas être inférieur à 0")
    if wear >= 90:
        return Diagnostic.WORN_BELT
    elif wear >= 70:
        return Diagnostic.OVERHEATED
    
    return Diagnostic.JAMMED_GEAR

