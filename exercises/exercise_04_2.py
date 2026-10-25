from dataclasses import dataclass

# TODO 1: Déclarer une dataclass World
# Attention : nous voulons pouvoir modifier ses attributs !
# robot_position: str = "BASE"
# diagnosis: str | None = None
# repaired: bool = False
@dataclass
class World:
    robot_position: str = "BASE"
    diagnosis: str | None = None
    repaired: bool = False


# TODO 2: Instancier World sans argument
world = World()

# TODO 3: Afficher son état initial
print(world)

# TODO 4: Déplacer le robot vers POI-42
world.robot_position = "POI-42"

# TODO 5: Définir le diagnostic "fault_detected"
world.diagnosis = "fault_detected"

# TODO 6: Marquer la réparation comme terminée
world.repaired = True

# TODO 7: Afficher son état final
print(world)