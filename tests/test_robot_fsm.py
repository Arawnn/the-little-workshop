

from workshop.events import ActionType, Event, EventType
from workshop.robot_fsm import RobotStateMachine, Transition
from workshop.world import MachineState, RobotState, World


def test_robot_at_4m():
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
    assert world.robot.current_action_id == result.action.id
