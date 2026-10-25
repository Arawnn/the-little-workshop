from dataclasses import dataclass
from collections import deque

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

events: deque[Event] = deque()
pending_actions: dict[str, Action] = {}

executor = ActionExecutor(events, pending_actions)

action = Action(
    id="action-001",
    type="move_to",
    machine_id="machine-001",
    target="POI-42"
)

executor.execute(action)

assert len(events) == 1
assert "action-001" in pending_actions
assert pending_actions["action-001"] is action

print("Executor test passed!")