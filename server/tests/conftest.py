import uuid
from collections.abc import Callable

import pytest

from workshop.domain.clock import Clock
from workshop.domain.vec3 import Vec3
from workshop.domain.world import Diagnostic, MachineState, RobotState, World


@pytest.fixture
def make_world() -> Callable[..., World]:
    """Factory fixture: pytest injects the function, each test calls it with its own parameters."""

    def _make_world(
        robot_state: RobotState = RobotState.IDLE,
        position: Vec3 = Vec3(0, 0, 0),
        action_id: uuid.UUID | None = None,
        machine_state: MachineState = MachineState.BROKEN,
        diagnostic: Diagnostic | None = None,
    ) -> World:
        world = World()
        world.robot.state = robot_state
        world.robot.position = position
        world.robot.current_action_id = action_id
        world.machine.state = machine_state
        world.machine.diagnostic = diagnostic
        return world

    return _make_world


class FakeClock(Clock):
    def __init__(self, t: float = 10.0):
        self.t = t

    def now(self) -> float:
        return self.t


@pytest.fixture
def fake_clock() -> Callable[[], FakeClock]:
    def _fake_clock() -> FakeClock:
        return FakeClock()

    return _fake_clock
