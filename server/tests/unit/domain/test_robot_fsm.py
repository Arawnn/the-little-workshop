import uuid

from workshop.domain.actions import ActionType
from workshop.domain.events import Event, EventType
from workshop.domain.robot_fsm import Reject, RobotStateMachine, Transition
from workshop.domain.vec3 import Vec3
from workshop.domain.world import Diagnostic, MachineState, RobotState, World


def machine_broke(world: World) -> Event:
    return Event(type=EventType.MACHINE_BROKE, machine_id=world.machine.id)


def action_completed(world: World, action_id: uuid.UUID | None) -> Event:
    return Event(type=EventType.ACTION_COMPLETED, machine_id=world.machine.id, action_id=action_id)


# --- idle ---


def test_fsm_idle_state_robot_far(make_world):
    world = make_world()

    result = RobotStateMachine().handle(world, machine_broke(world))

    assert isinstance(result, Transition)
    assert result.target == RobotState.MOVING
    assert result.action.type == ActionType.MOVE_TO
    assert result.action.target == world.machine.poi
    assert world.robot.state == RobotState.MOVING
    assert world.robot.current_action_id == result.action.id


def test_fsm_idle_state_robot_near(make_world):
    world = make_world(position=Vec3(3.5, 0, 0))
    event = machine_broke(world)

    result = RobotStateMachine().handle(world, event)

    assert isinstance(result, Transition)
    assert result.target == RobotState.INSPECTING
    assert result.action.type == ActionType.INSPECT
    assert result.action.machine_id == event.machine_id
    assert result.action.target == world.machine.poi
    assert world.robot.state == RobotState.INSPECTING


def test_fsm_idle_state_robot_boundary(make_world):
    world = make_world(position=Vec3(5.5, 0, 0))
    event = machine_broke(world)

    result = RobotStateMachine().handle(world, event)

    assert isinstance(result, Transition)
    assert result.target == RobotState.INSPECTING
    assert result.action.type == ActionType.INSPECT
    assert result.action.machine_id == event.machine_id
    assert result.action.target == world.machine.poi
    assert world.robot.state == RobotState.INSPECTING


def test_fsm_idle_state_reject_if_machine_not_broken(make_world):
    world = make_world(machine_state=MachineState.RUNNING)

    result = RobotStateMachine().handle(world, machine_broke(world))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.IDLE
    assert world.robot.current_action_id is None


def test_fsm_idle_state_ignore_action_completed(make_world):
    world = make_world()

    result = RobotStateMachine().handle(world, action_completed(world, None))

    assert result is None
    assert world.robot.state == RobotState.IDLE
    assert world.robot.current_action_id is None


# --- moving ---


def test_fsm_moving_state(make_world):
    action_id = uuid.uuid4()
    world = make_world(RobotState.MOVING, position=Vec3(5, 0, 0), action_id=action_id)

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Transition)
    assert world.robot.state == RobotState.INSPECTING
    assert world.robot.current_action_id == result.action.id


def test_fsm_moving_state_ignore_machine_broke(make_world):
    world = make_world(RobotState.MOVING)

    result = RobotStateMachine().handle(world, machine_broke(world))

    assert result is None
    assert world.robot.state == RobotState.MOVING
    assert world.robot.current_action_id is None


def test_fsm_moving_state_reject_if_action_id_not_correspond(make_world):
    current_id = uuid.uuid4()
    world = make_world(RobotState.MOVING, action_id=current_id)

    result = RobotStateMachine().handle(world, action_completed(world, uuid.uuid4()))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.MOVING
    assert world.robot.current_action_id == current_id


def test_fsm_moving_state_reject_if_robot_too_far(make_world):
    action_id = uuid.uuid4()
    world = make_world(RobotState.MOVING, position=Vec3(9, 0, 0), action_id=action_id)

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.MOVING
    assert world.robot.current_action_id == action_id


# --- inspecting ---


def test_fsm_inspecting_state(make_world):
    action_id = uuid.uuid4()
    world = make_world(
        RobotState.INSPECTING,
        position=Vec3(5, 0, 0),
        action_id=action_id,
        diagnostic=Diagnostic.JAMMED_GEAR,
    )

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Transition)
    assert result.action.type == ActionType.REPAIR
    assert world.robot.state == RobotState.REPAIRING
    assert world.robot.current_action_id == result.action.id


def test_fsm_inspecting_state_robot_boundary(make_world):
    action_id = uuid.uuid4()
    world = make_world(
        RobotState.INSPECTING,
        position=Vec3(5.5, 0, 0),
        action_id=action_id,
        diagnostic=Diagnostic.JAMMED_GEAR,
    )

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Transition)
    assert world.robot.state == RobotState.REPAIRING
    assert world.robot.current_action_id == result.action.id


def test_fsm_inspecting_state_reject_if_action_id_not_correspond(make_world):
    current_id = uuid.uuid4()
    world = make_world(RobotState.INSPECTING, action_id=current_id)

    result = RobotStateMachine().handle(world, action_completed(world, uuid.uuid4()))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.INSPECTING
    assert world.robot.current_action_id == current_id


def test_fsm_inspecting_state_reject_if_robot_too_far(make_world):
    action_id = uuid.uuid4()
    world = make_world(
        RobotState.INSPECTING,
        position=Vec3(9, 0, 0),
        action_id=action_id,
        diagnostic=Diagnostic.JAMMED_GEAR,
    )

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.INSPECTING
    assert world.robot.current_action_id == action_id


def test_fsm_inspecting_state_reject_if_diagnostic_is_none(make_world):
    action_id = uuid.uuid4()
    world = make_world(RobotState.INSPECTING, position=Vec3(5, 0, 0), action_id=action_id)

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.INSPECTING
    assert world.robot.current_action_id == action_id


# --- repairing ---


def test_fsm_repairing_state(make_world):
    action_id = uuid.uuid4()
    world = make_world(
        RobotState.REPAIRING,
        position=Vec3(5, 0, 0),
        action_id=action_id,
        machine_state=MachineState.RUNNING,
    )

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Transition)
    assert result.action is None
    assert world.robot.state == RobotState.IDLE
    assert world.robot.current_action_id is None


def test_fsm_repairing_state_reject_if_machine_not_running(make_world):
    action_id = uuid.uuid4()
    world = make_world(RobotState.REPAIRING, position=Vec3(5, 0, 0), action_id=action_id)

    result = RobotStateMachine().handle(world, action_completed(world, action_id))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.REPAIRING
    assert world.robot.current_action_id == action_id


def test_fsm_repairing_state_reject_if_action_id_not_correspond(make_world):
    current_id = uuid.uuid4()
    world = make_world(RobotState.REPAIRING, action_id=current_id)

    result = RobotStateMachine().handle(world, action_completed(world, uuid.uuid4()))

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.REPAIRING
    assert world.robot.current_action_id == current_id
