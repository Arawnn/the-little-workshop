import uuid

from workshop.events import Event, EventType
from workshop.robot_fsm import Reject
from workshop.simulator import Simulator
from workshop.vec3 import Vec3
from workshop.world import MachineState, RobotState


def test_simulator_scenario_nominal(make_world):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))

    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())

    assert world.robot.position == world.machine.poi
    assert world.robot.current_action_id is None
    assert world.machine.wear == 0
    assert world.machine.state == MachineState.RUNNING
    assert len(sim.events) == 0
    assert len(sim.pending_actions) == 0
    assert len(traces) == 4
    assert [(e.before, e.after) for e in traces] == [
        (RobotState.IDLE, RobotState.MOVING),
        (RobotState.MOVING, RobotState.INSPECTING),
        (RobotState.INSPECTING, RobotState.REPAIRING),
        (RobotState.REPAIRING, RobotState.IDLE),
    ]
    assert world.robot.state == RobotState.IDLE
    assert world.machine.diagnostic is None


def test_simulator_scenario_robot_near(make_world):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(3.5, 0, 0))

    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())
    assert len(traces) == 3
    assert [(e.before, e.after) for e in traces] == [
        (RobotState.IDLE, RobotState.INSPECTING),
        (RobotState.INSPECTING, RobotState.REPAIRING),
        (RobotState.REPAIRING, RobotState.IDLE),
    ]


def test_simulator_scenario_specific_wear(make_world):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(3.5, 0, 0))
    world.machine.wear = 75
    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())

    assert len(traces) == 3
    repairing = [e for e in traces if e.after == RobotState.REPAIRING]
    assert len(repairing) == 1
    assert "OVERHEATED" in repairing[0].outcome.reason


def test_simulator_scenario_unknown_action(make_world):
    world = make_world(robot_state=RobotState.MOVING, action_id=uuid.uuid4())
    sim = Simulator(world)
    trace = sim.run(Event(EventType.ACTION_COMPLETED, world.machine.id, uuid.uuid4()))

    assert len(trace) == 1
    assert isinstance(trace[0].outcome, Reject)

    assert world.robot.state == RobotState.MOVING


def test_simulator_pull_lever(make_world):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)
    sim = Simulator(world)
    event = sim.pull_lever()

    assert world.machine.state == MachineState.BROKEN

    assert event.type == EventType.MACHINE_BROKE
    assert event.machine_id == world.machine.id
