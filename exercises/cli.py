from dataclasses import dataclass
from typing import Callable

REACH = 1.5

Guard = Callable[[World, Event], bool]    # la précondition
Action = Callable[[World, Event], None]   # l'action, qui ajoute à la file son action.completed

@dataclass(frozen=True)
class Transition:
    source: RobotState
    event_type: str
    guard: Guard
    action: Action
    target: RobotState

# --- préconditions : petites fonctions pures, testables seules
def robot_far(world, event) -> bool:
    return distance(world.robot.position, world.machine.position) > REACH

def robot_near(world, event) -> bool:
    return not robot_far(world, event)   # règle aussi le cas de 1,5 m pile

# --- la table = les tableaux de la spec
TRANSITIONS = [
    Transition(RobotState.IDLE, "machine.broke", robot_far,  start_move_to_poi, RobotState.MOVING),
    Transition(RobotState.IDLE, "machine.broke", robot_near, start_inspection,  RobotState.INSPECTING),
    # moving -> inspecting, inspecting -> repairing, repairing -> idle : à toi
]

def dispatch(world, event) -> None:
    current = world.robot.state
    candidates = [t for t in TRANSITIONS
                if t.source == current and t.event_type == event.type]
    if not candidates:
        print(f"ignoré : {current} ne réagit pas à {event.type}")
        return
    for t in candidates:
        if t.guard(world, event):
            t.action(world, event)
            world.robot.state = t.target
            print(f"{current} --{event.type}--> {t.target}  ({t.guard.__name__} -> {t.action.__name__})")
            return
    print(f"précondition échouée : {current} --{event.type}-->, aucune précondition vraie")

