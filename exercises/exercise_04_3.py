from dataclasses import dataclass

@dataclass(frozen=True)
class Action:
    id: str
    type: str
    machine_id: str
    target: str | None = None

@dataclass
class World:
    robot_position: str = "BASE"
    diagnosis: str | None = None
    repaired: bool = False


def apply_effect(action: Action, world: World) -> None:
    # TODO 1: Si action.type == "move_to"
    # Vérifier que target n'est pas None
    # Modifier world.robot_position
    if action.type == "move_to":
        if action.target is None:
            raise ValueError("Target is required if action equals move_to")
        world.robot_position = action.target

    # TODO 2: Si action.type == "inspect"
    # Modifier world.diagnosis
    elif action.type == "inspect":
        world.diagnosis = "fault_detected"
    # TODO 3: Si action.type == "repair"
    # Modifier world.repaired
    elif action.type == "repair":
        world.repaired = True



# --- TEST ---
world = World()

actions = [
    Action(
        id="action-001",
        type="move_to",
        machine_id="machine-001",
        target="POI-42",
    ),
    Action(
        id="action-002",
        type="inspect",
        machine_id="machine-001",
    ),
    Action(
        id="action-003",
        type="repair",
        machine_id="machine-001",
    ),
]

print("Initial:", world)

for action in actions:
    apply_effect(action, world)
    print(f"After {action.type}:", world)


# Test supplémentaire
world = World()

action = Action(
    id="action-004",
    type="move_to",
    machine_id="machine-001",
    target="POI-99"
)

apply_effect(action, world)

assert world.robot_position == "POI-99"

print("Move test passed!")