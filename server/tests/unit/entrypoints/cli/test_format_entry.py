from workshop.domain.events import EventType
from workshop.domain.robot_fsm import Reject, Transition
from workshop.domain.world import RobotState
from workshop.engine.simulator import TraceEntry
from workshop.entrypoints.cli.pull_lever import format_entry

# --- format_entry ---


def test_format_entry():
    entry = TraceEntry(
        before=RobotState.IDLE,
        event_type=EventType.MACHINE_BROKE,
        outcome=Transition(target=RobotState.MOVING, reason="robot at 4.0m"),
        after=RobotState.MOVING,
        t=0.0,
    )

    row = format_entry(entry)

    assert row == "idle   --machine.broke-->   moving   (robot at 4.0m)"


def test_format_entry_reject():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.ACTION_COMPLETED,
        outcome=Reject(reason="robot too far"),
        after=RobotState.MOVING,
        t=0.0,
    )

    row = format_entry(entry)

    assert row == "moving   --action.completed--x   rejected: robot too far"


def test_format_entry_ignored():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.MACHINE_BROKE,
        outcome=None,
        after=RobotState.MOVING,
        t=0.0,
    )

    row = format_entry(entry)

    assert row == "moving   --machine.broke--   ignored"
