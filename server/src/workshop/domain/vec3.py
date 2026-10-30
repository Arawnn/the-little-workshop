import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def as_tuple(self) -> tuple(float, float, float):
        return (self.x, self.y, self.z)


def distance(a: Vec3, b: Vec3) -> float:
    return math.dist(a.as_tuple(), b.as_tuple())
