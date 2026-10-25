from dataclasses import dataclass
import math 

@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def get_point(self):
        return (self.x, self.y, self.z)


def distance(a: Vec3, b: Vec3) -> float:
    return math.dist(a.get_point(), b.get_point())