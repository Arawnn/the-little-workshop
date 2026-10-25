from workshop.vec3 import Vec3, distance
import pytest
from dataclasses import FrozenInstanceError

def test_distance_equal_5():
    a = Vec3(0,0,0)
    b = Vec3(3,4,0)

    d = distance(a,b)
    assert d == pytest.approx(5.0)

def test_distance_with_same_point():
    a = Vec3(5,0,0)
    
    d = distance(a, a)
    assert d == 0.0

def test_distance_param_interchangeable():
    a = Vec3(0,0,0)
    b = Vec3(3,4,0)

    assert distance(a,b) == distance(b,a)

def test_vec3_frozen_class():
    a = Vec3(3,0,0)
    with pytest.raises(FrozenInstanceError):
        a.x = 1
