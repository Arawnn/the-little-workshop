import uuid

from workshop.domain.actions import ACTION_DURATIONS, Action
from workshop.domain.effects import apply_start_effect
from workshop.domain.events import Event, EventType
from workshop.domain.world import World
from workshop.engine.event_queue import PriorityEventQueue


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
