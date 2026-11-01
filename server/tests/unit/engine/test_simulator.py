import uuid

from workshop.domain.events import Event, EventType
from workshop.domain.robot_fsm import Reject
from workshop.domain.vec3 import Vec3
from workshop.domain.world import MachineState, RobotState
from workshop.engine.simulator import Simulator


def test_simulator_scenario_nominal(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))

    clock = fake_clock()
    sim = Simulator(world, clock)
    sim.pull_lever()

    traces = []
    for now in [10.0, 12.0, 13.0, 16.0]:
        clock.t = now
        due = sim.step()
        assert len(due) == 1
        traces += due

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

    clock = fake_clock()
    sim = Simulator(world, clock)
    sim.pull_lever()
    clock.t = 14.0
    traces = sim.step()
    assert len(traces) == 3
    assert [(e.before, e.after) for e in traces] == [
        (RobotState.IDLE, RobotState.INSPECTING),
        (RobotState.INSPECTING, RobotState.REPAIRING),
        (RobotState.REPAIRING, RobotState.IDLE),
    ]


def test_simulator_scenario_specific_wear(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(3.5, 0, 0))
    world.machine.wear = 75
    clock = fake_clock()
    sim = Simulator(world, clock)
    sim.pull_lever()
    clock.t = 14.0
    traces = sim.step()

    assert len(traces) == 3
    repairing = [e for e in traces if e.after == RobotState.REPAIRING]
    assert len(repairing) == 1
    if repairing[0].outcome:
        assert "OVERHEATED" in repairing[0].outcome.reason


def test_simulator_scenario_unknown_action(make_world, fake_clock):
    world = make_world(robot_state=RobotState.MOVING, action_id=uuid.uuid4())
    sim = Simulator(world, fake_clock())
    sim.schedule(Event(EventType.ACTION_COMPLETED, world.machine.id, uuid.uuid4()))
    trace = sim.step()

    assert len(trace) == 1
    assert isinstance(trace[0].outcome, Reject)

    assert world.robot.state == RobotState.MOVING


def test_simulator_pull_lever(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)
    sim = Simulator(world, fake_clock())
    event = sim.pull_lever()

    assert world.machine.state == MachineState.BROKEN

    if isinstance(event, Event):
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

    clock = fake_clock()
    sim = Simulator(world, clock)
    sim.pull_lever()
    clock.t = 16.0
    sim.step()

    event = sim.pull_lever()
    clock.t = 22.0
    sim.step()
    assert isinstance(event, Event)
    assert event.type == EventType.MACHINE_BROKE
    assert len(sim.events) == 0


def test_simulator_step_with_empty_queue(make_world, sequence_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)

    sim = Simulator(world, sequence_clock([0.0]))

    assert sim.step() == []
    assert len(sim.events) == 0
    assert world.robot.state == RobotState.IDLE
    assert world.machine.state == MachineState.RUNNING


def test_simulator_step_with_no_due_event(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)
    sim = Simulator(world, fake_clock())
    event = Event(EventType.ACTION_COMPLETED, uuid.uuid4(), action_id=uuid.uuid4())
    sim.events.push(16.0, event)

    assert sim.step() == []
    item = sim.events.peek()
    if item is not None:
        t, e = item
        assert e is event
        assert t == 16.0


def test_simulator_step_with_inclusive_with_boundary_clock(make_world, fake_clock):
    world = make_world(robot_state=RobotState.IDLE, machine_state=MachineState.RUNNING)
    sim = Simulator(world, fake_clock())

    event = Event(EventType.MACHINE_BROKE, uuid.uuid4())
    sim.events.push(10.0, event)

    traces = sim.step()

    assert traces[0].t == 10.0
    assert len(traces) == 1
    assert len(sim.events) == 0


def test_simulator_step_with_nominal_scenario_at_15(make_world, sequence_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))

    sim = Simulator(world, sequence_clock([10.0, 15.0]))
    sim.pull_lever()
    traces = sim.step()

    assert len(sim.events) == 1
    assert len(sim.pending_actions) == 1
    assert len(traces) == 3
    assert [(e.before, e.after) for e in traces] == [
        (RobotState.IDLE, RobotState.MOVING),
        (RobotState.MOVING, RobotState.INSPECTING),
        (RobotState.INSPECTING, RobotState.REPAIRING),
    ]
    assert [e.t for e in traces] == [10.0, 12.0, 13.0]
    item = sim.events.peek()
    if item is not None:
        t, _ = item
        assert t == 16.0


def test_simulator_step_with_two_successive_call_at_different_t(make_world, fake_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))
    clock = fake_clock()
    sim = Simulator(world, clock)
    sim.pull_lever()
    clock.t = 15.0
    traces = sim.step()
    assert len(traces) == 3
    clock.t = 20.0
    traces = sim.step()

    assert len(traces) == 1
    assert traces[0].t == 16.0
    assert len(sim.events) == 0


def test_simulator_step_reads_clock_once(make_world, sequence_clock):
    world = make_world(machine_state=MachineState.RUNNING, position=Vec3(9, 0, 0))

    sim = Simulator(world, sequence_clock([10.0, 15.0]))
    sim.pull_lever()
    traces = sim.step()

    assert [e.t for e in traces] == [10.0, 12.0, 13.0]
