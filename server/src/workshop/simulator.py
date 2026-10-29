import uuid
from dataclasses import dataclass

from workshop.actions import Action
from workshop.effects import apply_completion_effect
from workshop.event_queue import PriorityEventQueue
from workshop.events import Event, EventType
from workshop.executor import ActionExecutor
from workshop.robot_fsm import Reject, RobotStateMachine, Transition
from workshop.world import MachineState, RobotState, World


@dataclass(frozen=True)
class TraceEntry:
    before: RobotState
    event_type: EventType
    outcome: Transition | Reject | None
    after: RobotState
    t: float


class Simulator:
    def __init__(self, world: World) -> None:
        self.world = world
        self.events: PriorityEventQueue = PriorityEventQueue()
        self.pending_actions: dict[uuid.UUID, Action] = {}
        self.executor = ActionExecutor(self.events, self.pending_actions, self.world)
        self.robot_fsm = RobotStateMachine()

    def run(self, first_event: Event) -> list[TraceEntry]:
        trace: list[TraceEntry] = []
        self.events.push(0.0, first_event)

        while self.events:
            t, event = self.events.pop()

            if event.type == EventType.ACTION_COMPLETED:
                completed_action = self.pending_actions.pop(event.action_id, None)
                if completed_action is not None:
                    apply_completion_effect(completed_action, self.world)

            before = self.world.robot.state
            outcome = self.robot_fsm.handle(self.world, event)
            after = self.world.robot.state

            trace.append(
                TraceEntry(before=before, event_type=event.type, outcome=outcome, after=after, t=t)
            )
            if isinstance(outcome, Transition) and outcome.action is not None:
                self.executor.execute(outcome.action)

        return trace

    def pull_lever(self) -> Event:
        self.world.machine.state = MachineState.BROKEN
        return Event(type=EventType.MACHINE_BROKE, machine_id=self.world.machine.id)
