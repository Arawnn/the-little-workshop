from workshop.actions import Action, ActionType
from workshop.world import MachineState, World, diagnose


def apply_start_effect(action: Action, world: World) -> None:
    match action.type:
        case ActionType.REPAIR:
            world.machine.state = MachineState.REPAIRING


def apply_completion_effect(action: Action, world: World) -> None:
    match action.type:
        case ActionType.MOVE_TO:
            if action.target is None:
                raise ValueError("Une destination est nécessaire pour déplacer le robot")
            world.robot.position = action.target
        case ActionType.INSPECT:
            world.machine.diagnostic = diagnose(world.machine.wear)
        case ActionType.REPAIR:
            world.machine.state = MachineState.RUNNING
            world.machine.diagnostic = None
            world.machine.wear = 0
