import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from workshop.actions import Action, ActionType
from workshop.events import Event, EventType
from workshop.vec3 import distance
from workshop.world import REACH, MachineState, RobotState, World


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
    def handle(self, world: World, event: Event) -> Transition | Reject | None: ...

    def _is_current_action(self, world: World, event: Event) -> bool:
        return world.robot.current_action_id == event.action_id

    def _start_inspection(self, world: World, event: Event, dist: float) -> Transition:
        action = Action(
            id=uuid.uuid4(),
            type=ActionType.INSPECT,
            machine_id=event.machine_id,
            target=world.machine.poi,
        )
        return Transition(
            target=RobotState.INSPECTING,
            action=action,
            reason=f"robot à {dist:.2f} m",
        )


class IdleState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.MACHINE_BROKE:
            return None

        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")

        d = distance(world.robot.position, world.machine.position)
        if d <= REACH:
            return self._start_inspection(world, event, d)

        action = Action(
            id=uuid.uuid4(),
            type=ActionType.MOVE_TO,
            machine_id=event.machine_id,
            target=world.machine.poi,
        )
        return Transition(
            target=RobotState.MOVING,
            action=action,
            reason=f"robot à {d:.2f} m",
        )


class MovingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.ACTION_COMPLETED:
            return None

        if not self._is_current_action(world, event):
            return Reject("L'action reçue ne correspond pas à l'action en cours du robot")

        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")

        d = distance(world.robot.position, world.machine.position)
        if d <= REACH:
            return self._start_inspection(world, event, d)

        # Pas encore de politique de reprise dans le scénario nominal
        return Reject(f"Le robot n'a pas atteint la machine, distance : {d:.2f} m")


class InspectingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.ACTION_COMPLETED:
            return None

        if not self._is_current_action(world, event):
            return Reject("L'action reçue ne correspond pas à l'action en cours du robot")

        if world.machine.state != MachineState.BROKEN:
            return Reject("La machine n'est pas cassée")

        d = distance(world.robot.position, world.machine.position)
        if d > REACH:
            return Reject(
                f"Réparation impossible : robot trop loin de la machine, distance : {d:.2f} m"
            )

        if world.machine.diagnostic is None:
            return Reject("Réparation impossible : aucun diagnostic connu pour la machine")

        action = Action(
            id=uuid.uuid4(),
            type=ActionType.REPAIR,
            machine_id=event.machine_id,
        )
        return Transition(
            target=RobotState.REPAIRING,
            action=action,
            reason=f"diagnostic : {world.machine.diagnostic.name}",
        )


class RepairingState(RobotStateHandler):
    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        if event.type != EventType.ACTION_COMPLETED:
            return None

        if not self._is_current_action(world, event):
            return Reject("L'action reçue ne correspond pas à l'action en cours du robot")

        if world.machine.state != MachineState.RUNNING:
            return Reject("Réparation échouée : la machine n'est pas en marche")

        return Transition(
            target=RobotState.IDLE,
            reason="machine réparée",
        )


class RobotStateMachine:
    def __init__(self) -> None:
        self.handlers: dict[RobotState, RobotStateHandler] = {
            RobotState.IDLE: IdleState(),
            RobotState.MOVING: MovingState(),
            RobotState.INSPECTING: InspectingState(),
            RobotState.REPAIRING: RepairingState(),
        }

    def handle(self, world: World, event: Event) -> Transition | Reject | None:
        handler = self.handlers[world.robot.state]
        result = handler.handle(world, event)
        if isinstance(result, Transition):
            world.robot.state = result.target
            world.robot.current_action_id = result.action.id if result.action is not None else None
        return result
