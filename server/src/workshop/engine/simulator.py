import uuid
from dataclasses import dataclass

from workshop.domain.actions import Action
from workshop.domain.clock import Clock
from workshop.domain.effects import apply_completion_effect
from workshop.domain.events import Event, EventType
from workshop.domain.robot_fsm import Reject, RobotStateMachine, Transition
from workshop.domain.world import MachineState, RobotState, World
from workshop.engine.event_queue import PriorityEventQueue
from workshop.engine.executor import ActionExecutor


@dataclass(frozen=True)
class TraceEntry:
    before: RobotState
    event_type: EventType
    outcome: Transition | Reject | None
    after: RobotState
    t: float


class Simulator:
    def __init__(self, world: World, clock: Clock) -> None:
        self.world = world
        self.clock = clock
        self.events: PriorityEventQueue = PriorityEventQueue()
        self.pending_actions: dict[uuid.UUID, Action] = {}
        self.executor = ActionExecutor(self.events, self.pending_actions, self.world)
        self.robot_fsm = RobotStateMachine()

    def run(self) -> list[TraceEntry]:
        trace: list[TraceEntry] = []

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

    def pull_lever(self) -> Event | Reject:
        if self.world.machine.state != MachineState.RUNNING:
            return Reject("Machine is not running!")
        self.world.machine.state = MachineState.BROKEN

        event = Event(type=EventType.MACHINE_BROKE, machine_id=self.world.machine.id)
        self.schedule(event)

        return event

    def schedule(self, event: Event):
        t = self.clock.now()
        self.events.push(t, event)
