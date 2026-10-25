from collections import deque
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

@dataclass
class World:
    robot_position: str = "BASE"
    diagnosis: str | None = None
    repaired: bool = False

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


class ActionExecutor:
    def __init__(
        self,
        events: deque[Event],
        pending_actions: dict[str, Action]
    ) -> None:
        self.events = events

        # TODO 1: Stocker pending_actions
        self.pending_actions = pending_actions

    def execute(self, action: Action) -> None:
        print(f"Starting action: {action.type}")

        # TODO 2: Enregistrer l'action
        # dans pending_actions
        self.pending_actions[action.id] = action

        # TODO 3: Créer un Event
        # de type action.completed
        event = Event(
            type="action.completed",
            action_id=action.id,
            machine_id=action.machine_id
        )
        # TODO 4: Ajouter l'événement
        # dans la deque
        self.events.append(event)


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


# --- SIMULATION ---

events: deque[Event] = deque()
pending_actions: dict[str, Action] = {}

world = World()
machine = RobotStateMachine()
executor = ActionExecutor(events, pending_actions)

initial_action = Action(
    id="action-001",
    type="move_to",
    machine_id="machine-001",
    target="POI-42"
)

# TODO 1: Démarrer initial_action
# Indice : utiliser executor
executor.execute(initial_action)

# TODO 2: Créer une boucle while
# Elle doit continuer tant qu'il reste des événements
while events:

    # TODO 3: Récupérer le premier événement
    event = events.popleft()

    # TODO 4: Retrouver et supprimer l'action
    # associée à cet événement
    # Indice : pending_actions
    
    completed_action = pending_actions.pop(event.action_id)
    
    # TODO 5: Appliquer les effets sur world
    apply_effect(completed_action, world)

    # TODO 6: Sauvegarder l'état actuel de la machine
    # pour pouvoir afficher la transition
    state = machine.state

    # TODO 7: Transmettre l'événement à la FSM
    # et récupérer la prochaine action
    next_action = machine.handle(event)

    # TODO 8: Afficher la transition
    # Exemple : MOVING -> INSPECTING
    print(f"{state} -> {machine.state}")

    # TODO 9: Si une nouvelle action existe,
    # la transmettre à ActionExecutor
    if next_action is not None:
        executor.execute(next_action)


# TODO 10: Afficher l'état final du monde
print("Final world:", world)

# TODO 11: Afficher l'état final de la FSM
print("Final state:", machine.state.name)

assert world.robot_position == "POI-42"
assert world.diagnosis == "fault_detected"
assert world.repaired is True
assert machine.state == State.DONE

assert len(events) == 0
assert len(pending_actions) == 0