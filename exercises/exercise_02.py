from dataclasses import dataclass



# TODO 1: Déclarer la dataclass Action
# Champs : id, type, machine_id, target (facultatif)
@dataclass(frozen=True)
class Action:
    id: str
    type: str
    machine_id: str
    target: str | None = None

# TODO 2: Déclarer la dataclass Event
# Champs : type, action_id, machine_id
@dataclass(frozen=True)
class Event:
    type: str
    action_id: str
    machine_id: str

# TODO 3: Créer une Action
# id = "fbd204a7-318e-4dd3-86e0-e6d524fc3f90"
# type = "move_to"
# machine_id = "fbd204a7-318e-4dd3-86e0-e6d524fc3f90"
# target = "POI-42"

action = Action(
    id='action-001', 
    type='move_to', 
    machine_id='machine-001', 
    target='POI-42'
)

inspect_action = Action(
    id="action-002",
    type="inspect",
    machine_id="machine-001"
)

# TODO 4: Créer un Event
# type = "action.completed"
# action_id = l'identifiant de l'action créée
# machine_id = l'identifiant de machine de l'action
event = Event(
    type="action.completed",
    action_id="action-001",
    machine_id="machine-001"
)

# TODO 5: Afficher les deux objets
print(action)
print(inspect_action)
print(event)
