import uuid

from workshop.events import Event, EventType
from workshop.robot_fsm import Reject
from workshop.simulator import Simulator
from workshop.vec3 import Vec3
from workshop.world import MachineState, RobotState


def test_simulator_scenario_nominal(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))

    sim = Simulator(world, fake_clock())
    sim.pull_lever()
    traces = sim.run()

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
    assert [e.t for e in traces] == [10.0, 12.0, 13.0, 16.0]
    assert world.robot.state == RobotState.IDLE
    assert world.machine.diagnostic is None


def test_simulator_scenario_robot_near(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(3.5, 0, 0))

    sim = Simulator(world, fake_clock())
    sim.pull_lever()
    traces = sim.run()
    assert len(traces) == 3
    assert [(e.before, e.after) for e in traces] == [
        (RobotState.IDLE, RobotState.INSPECTING),
        (RobotState.INSPECTING, RobotState.REPAIRING),
        (RobotState.REPAIRING, RobotState.IDLE),
    ]


def test_simulator_scenario_specific_wear(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(3.5, 0, 0))
    world.machine.wear = 75
    sim = Simulator(world, fake_clock())
    sim.pull_lever()
    traces = sim.run()

    assert len(traces) == 3
    repairing = [e for e in traces if e.after == RobotState.REPAIRING]
    assert len(repairing) == 1
    assert "OVERHEATED" in repairing[0].outcome.reason


def test_simulator_scenario_unknown_action(make_world, fake_clock):
    world = make_world(robot_state=RobotState.MOVING, action_id=uuid.uuid4())
    sim = Simulator(world, fake_clock())
    sim.schedule(Event(EventType.ACTION_COMPLETED, world.machine.id, uuid.uuid4()))
    trace = sim.run()

    assert len(trace) == 1
    assert isinstance(trace[0].outcome, Reject)

    assert world.robot.state == RobotState.MOVING


def test_simulator_pull_lever(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)
    sim = Simulator(world, fake_clock())
    event = sim.pull_lever()

    assert world.machine.state == MachineState.BROKEN

    assert event.type == EventType.MACHINE_BROKE
    assert event.machine_id == world.machine.id


def test_simulator_pull_lever_success(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)

    sim = Simulator(world, fake_clock())

    result = sim.pull_lever()

    assert isinstance(result, Event)

    t, event = sim.events.pop()
    assert t == 10.0
    assert event.type == EventType.MACHINE_BROKE


def test_simulator_reject_pull_lever(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.BROKEN)

    sim = Simulator(world, fake_clock())

    result = sim.pull_lever()

    assert isinstance(result, Reject)

    assert result.reason != ""


def test_simulator_reject_does_not_affect_state(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.BROKEN)

    sim = Simulator(world, fake_clock())
    robot_state = world.robot.state
    machine_state = world.machine.state
    result = sim.pull_lever()

    assert isinstance(result, Reject)
    assert world.robot.state == robot_state
    assert world.machine.state == machine_state
    assert len(sim.events) == 0


def test_simulator_accept_new_pull_lever_when_queue_is_empty(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)

    sim = Simulator(world, fake_clock())
    sim.pull_lever()

    sim.run()
    event = sim.pull_lever()
    sim.run()
    assert isinstance(event, Event)
    assert event.type == EventType.MACHINE_BROKE
    assert len(sim.events) == 0
