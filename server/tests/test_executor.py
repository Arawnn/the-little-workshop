import uuid

from workshop.actions import ACTION_DURATIONS, Action, ActionType
from workshop.event_queue import PriorityEventQueue
from workshop.events import EventType
from workshop.executor import ActionExecutor
from workshop.world import MachineState


def test_executor_execute_repair_action(make_world):
    world = make_world()
    action = Action(id=uuid.uuid4(), type=ActionType.REPAIR, machine_id=world.machine.id)
    executor = ActionExecutor(queue=PriorityEventQueue(), pending_actions={}, world=world)

    executor.execute(action)

    assert world.machine.state == MachineState.REPAIRING

    assert executor.pending_actions[action.id] is action

    t, event = executor.queue.pop()

    assert t == ACTION_DURATIONS[ActionType.REPAIR]
    assert event.type == EventType.ACTION_COMPLETED
    assert event.action_id == action.id
    assert len(executor.queue) == 0
