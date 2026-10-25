from re import A
from workshop.world import World, diagnose, Diagnostic, REACH
from workshop.vec3 import distance
import pytest
from dataclasses import replace

def test_worlds_are_different():
    w1 = World()
    w2 = World()
    w1.robot.position = replace(w1.robot.position, x=5)
    assert w2.robot.position.x == 0
    assert w1.robot is not w2.robot

def test_threshold_diagnose():
    assert diagnose(70) == Diagnostic.OVERHEATED
    assert diagnose(90) == Diagnostic.WORN_BELT
    assert diagnose(0) == Diagnostic.JAMMED_GEAR
    assert diagnose(100) == Diagnostic.WORN_BELT
    with pytest.raises(ValueError):
        diagnose(101)
    with pytest.raises(ValueError):
        diagnose(-1)

def test_poi_distance_less_than_reach_to_machine():
    world = World()
    
    assert distance(world.machine.poi, world.machine.position) < REACH

def test_robot_distance_sup_reach_machine():
    world = World()

    assert distance(world.robot.position, world.machine.position) > REACH
