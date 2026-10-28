import uuid
from collections import deque

from workshop.actions import Action, ActionType
from workshop.events import EventType
from workshop.executor import ActionExecutor
from workshop.world import MachineState


def test_executor_execute_repair_action(make_world):
    world = make_world()
    action = Action(id=uuid.uuid4(), type=ActionType.REPAIR, machine_id=world.machine.id)
    executor = ActionExecutor(events=deque(), pending_actions={}, world=world)

    executor.execute(action)

    assert world.machine.state == MachineState.REPAIRING

    assert executor.pending_actions[action.id] is action

    event_in_queue = executor.events.popleft()
    assert event_in_queue.type == EventType.ACTION_COMPLETED
    assert event_in_queue.action_id == action.id
    assert len(executor.events) == 0
