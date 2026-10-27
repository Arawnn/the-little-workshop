import uuid
from workshop.events import ActionType, Event, EventType
from workshop.robot_fsm import Reject, RobotStateMachine, Transition
from workshop.vec3 import Vec3
from workshop.world import MachineState, Robot, RobotState, World


def test_robot_far_machine():
    world = World()
    world.machine.state = MachineState.BROKEN
    
    event = Event(
        type=EventType.MACHINE_BROKE,
        machine_id=world.machine.id,
    )

    robot_fsm = RobotStateMachine()
    result = robot_fsm.handle(world, event)
    assert isinstance(result, Transition)
    assert result.target == RobotState.MOVING
    assert result.action.type == ActionType.MOVE_TO
    assert world.machine.poi == result.action.target
    assert world.robot.state == RobotState.MOVING
    assert world.robot.current_action_id == result.action.id


def test_robot_near_machine():
    robot = Robot(
        id=uuid.uuid4(),
        position=Vec3(3.5,0,0),
        state=RobotState.IDLE
    )
    world = World(robot=robot)
    world.machine.state = MachineState.BROKEN

    event = Event(
        type=EventType.MACHINE_BROKE,
        machine_id=world.machine.id,
    )

    robot_fsm = RobotStateMachine()
    result = robot_fsm.handle(world, event)

    assert isinstance(result, Transition)
    assert result.target == RobotState.INSPECTING
    assert result.action.type == ActionType.INSPECT
    assert result.action.machine_id == event.machine_id
    assert result.action.target == world.machine.poi
    assert world.robot.state == RobotState.INSPECTING

def test_robot_boundary_machine():
    robot = Robot(
        id=uuid.uuid4(),
        position=Vec3(5.5,0,0),
        state=RobotState.IDLE
    )
    world = World(robot=robot)
    world.machine.state = MachineState.BROKEN
    
    event = Event(
        type=EventType.MACHINE_BROKE,
        machine_id=world.machine.id,
    )

    robot_fsm = RobotStateMachine()
    result = robot_fsm.handle(world, event)

    assert isinstance(result, Transition)
    assert result.target == RobotState.INSPECTING
    assert result.action.type == ActionType.INSPECT
    assert result.action.machine_id == event.machine_id
    assert result.action.target == world.machine.poi
    assert world.robot.state == RobotState.INSPECTING


def test_fsm_reject_if_machine_not_broken():
    world = World()
    
    event = Event(
        type=EventType.MACHINE_BROKE,
        machine_id=world.machine.id,
    )

    robot_fsm = RobotStateMachine()
    result = robot_fsm.handle(world, event)

    assert isinstance(result, Reject)
    assert result.reason != ""
    assert world.robot.state == RobotState.IDLE
    assert world.robot.current_action_id is None

def test_fsm_ignore_event_not_idle():
    world = World()
    
    event = Event(
        type=EventType.ACTION_COMPLETED,
        machine_id=world.machine.id,
    )

    robot_fsm = RobotStateMachine()
    result = robot_fsm.handle(world, event)

    assert result is None
    assert world.robot.state == RobotState.IDLE
    assert world.robot.current_action_id is None