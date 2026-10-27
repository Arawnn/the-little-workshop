from dataclasses import dataclass

import uuid
from workshop.events import Action, ActionType, Event, EventType
from workshop.vec3 import distance
from workshop.world import REACH, MachineState, RobotState, World
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class Transition:
    target: RobotState
    action: Action | None
    reason: str
    
@dataclass(frozen=True)
class Reject:
    reason: str


class RobotStateHandler(ABC):
    @abstractmethod
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        ...


class IdleState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.MACHINE_BROKE:
            return None

        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")
        
        d = distance(world.robot.position, world.machine.position)
        if d <= REACH:
            action = Action(
                id=uuid.uuid4(),
                type=ActionType.INSPECT,
                machine_id=event.machine_id,
                target=world.machine.poi
            )
            return Transition(
                target=RobotState.INSPECTING,
                action=action,
                reason=f"robot at {d:.2f}m"
            )
        else:
            action = Action(
                id=uuid.uuid4(),
                type=ActionType.MOVE_TO,
                machine_id=event.machine_id,
                target=world.machine.poi
            )
            return Transition(
                RobotState.MOVING,
                action,
                f"robot at {d:.2f}m"
            )


class RobotStateMachine:
    def __init__(self) -> None:
        self.handlers: dict[RobotState, RobotStateHandler] = {
            RobotState.IDLE: IdleState()
        }
    
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        state = world.robot.state
        handler = self.handlers[state]
        result = handler.handle(world, event)
        if isinstance(result, Transition):
            world.robot.state = result.target
            if result.action is not None:
                world.robot.current_action_id = result.action.id
            else:
                world.robot.current_action_id = None
        return result

        

        
            
