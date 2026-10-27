from dataclasses import dataclass

import uuid
from workshop.events import Action, ActionType, Event, EventType
from workshop.vec3 import distance
from workshop.world import REACH, MachineState, Robot, RobotState, World, diagnose
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class Transition:
    target: RobotState
    reason: str
    action: Action | None = None
    
    
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
                target=RobotState.MOVING,
                action=action,
                reason=f"robot at {d:.2f}m"
            )

class MovingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        # ignore si l'action n'est pas completed
        if event.type != EventType.ACTION_COMPLETED:
            return None
        if event.action_id != world.robot.current_action_id:
            return Reject("L'action reçu ne correspond pas à l'action courante du robot.")
        # reject si la machine n'est pas broken
        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")

        d = distance(world.robot.position, world.machine.position)
        # si le robot est a 1,5m ou moins alors lancer une action 
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
            # Pas encore de politique de reprise pour le scénario nominal
            return Reject(f"Le roboto n'a pas réussi à atteindre la machine, distance: {d:.2f}m")
        
    
class InspectingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.ACTION_COMPLETED:
            return None

        if event.action_id != world.robot.current_action_id:
            return Reject("L'action reçu ne correspond pas à l'action courante du robot.")

        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")

        d = distance(world.robot.position, world.machine.position)
        if d > REACH:
            return Reject(f"Impossible de lancer le repair. Le robot est trop loin de la machine, distance: {d:.2f}")

        if world.machine.diagnostic is None:
            return Reject("Impossible de lancer le repair. Aucun diagnostic connu n'a été détecté sur la machine")
            
        action = Action(
            id=uuid.uuid4(),
            type=ActionType.REPAIR,
            machine_id=event.machine_id
        )
        return Transition(
            target=RobotState.REPAIRING,
            action=action,
            reason=f"diagnostic: {world.machine.diagnostic}"
        )
        
class RepairingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.ACTION_COMPLETED:
            return None

        if event.action_id != world.robot.current_action_id:
            return Reject("L'action reçu ne correspond pas à l'action courante du robot.")
        if world.machine.state != MachineState.RUNNING:
            return Reject("La machine n'est pas en marche")
        

        return Transition(
            target=RobotState.IDLE,
            reason="machine réparée"
        )



class RobotStateMachine:
    def __init__(self) -> None:
        self.handlers: dict[RobotState, RobotStateHandler] = {
            RobotState.IDLE: IdleState(),
            RobotState.MOVING: MovingState(),
            RobotState.INSPECTING: InspectingState(),
            RobotState.REPAIRING: RepairingState()
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

        

        
            
