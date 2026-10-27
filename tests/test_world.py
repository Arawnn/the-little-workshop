from dataclasses import replace

import pytest

from workshop.vec3 import distance
from workshop.world import REACH, Diagnostic, World, diagnose


def test_worlds_are_different():
    w1 = World()
    w2 = World()
    w1.robot.position = replace(w1.robot.position, x=5)
    assert w2.robot.position.x == 0
    assert w1.robot is not w2.robot

@pytest.mark.parametrize("wear, expected", [
    (0, Diagnostic.JAMMED_GEAR),
    (69, Diagnostic.JAMMED_GEAR),
    (70, Diagnostic.OVERHEATED),
    (89, Diagnostic.OVERHEATED),
    (90, Diagnostic.WORN_BELT),
    (100, Diagnostic.WORN_BELT),
])
def test_diagnose_thresholds(wear, expected):
    assert diagnose(wear) == expected

@pytest.mark.parametrize("wear", [-1, 101])
def test_diagnose_rejects_out_of_range(wear):
    with pytest.raises(ValueError):
        diagnose(wear)

def test_poi_distance_less_than_reach_to_machine():
    world = World()
    
    assert distance(world.machine.poi, world.machine.position) < REACH

def test_robot_distance_sup_reach_machine():
    world = World()

    assert distance(world.robot.position, world.machine.position) > REACH
