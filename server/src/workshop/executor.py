import uuid

from workshop.actions import ACTION_DURATIONS, Action
from workshop.effects import apply_start_effect
from workshop.event_queue import PriorityEventQueue
from workshop.events import Event, EventType
from workshop.world import World


class ActionExecutor:
    def __init__(
        self, queue: PriorityEventQueue, pending_actions: dict[uuid.UUID, Action], world: World
    ) -> None:
        self.queue = queue
        self.pending_actions = pending_actions
        self.world = world

    def execute(self, action: Action) -> None:

        self.pending_actions[action.id] = action

        apply_start_effect(action, self.world)

        event = Event(
            type=EventType.ACTION_COMPLETED, action_id=action.id, machine_id=action.machine_id
        )

        self.queue.push(self.queue.current_time() + ACTION_DURATIONS[action.type], event)
