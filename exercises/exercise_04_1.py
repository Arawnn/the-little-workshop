from collections import deque
from dataclasses import dataclass

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


# TODO 1: Déclarer la classe ActionExecutor
class ActionExecutor:
# TODO 2: Créer le constructeur __init__
# Il reçoit une deque et la stocke dans self.events
    def __init__(self, events: deque[Event]) -> None:
        self.events = events
# TODO 3: Créer execute(self, action: Action) -> None
# Afficher "Starting action: <type>"
    def execute(self, action: Action) -> None:
        print(f"Starting action: {action.type}")
# TODO 4: Créer un Event avec les données de l'action
        event = Event(
            type="action.completed",
            action_id=action.id,
            machine_id=action.machine_id
        )
# TODO 5: Ajouter l'événement à self.events
        self.events.append(event)

# --- TEST ---
events: deque[Event] = deque()
executor = ActionExecutor(events)

action = Action(
    id="action-001",
    type="move_to",
    machine_id="machine-001",
    target="POI-42"
)

executor.execute(action)

print("Number of events:", len(events))
print("First event:", events[0])
