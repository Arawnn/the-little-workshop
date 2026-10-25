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


action = Action(
    id="action-001",
    type="move_to",
    machine_id="machine-001",
    target="POI-42"
)

event = Event(
    type="action.completed",
    action_id="action-001",
    machine_id="machine-001"
)

# TODO 1: Créer pending_actions
# Type : dict[str, Action]
pending_actions: dict[str, Action] = {}

# TODO 2: Enregistrer l'action
# Utiliser action.id comme clé
pending_actions[action.id] = action

# TODO 3: Retrouver puis supprimer l'action
# Utiliser pop() avec event.action_id
action = pending_actions.pop(event.action_id)


# TODO 4: Afficher l'action récupérée
print(action)

# TODO 5: Afficher le dictionnaire
# Il doit être vide à la fin
print(pending_actions)