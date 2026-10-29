import pytest

from workshop.events import EventType
from workshop.pull_lever import format_entry, main
from workshop.robot_fsm import Reject, Transition
from workshop.simulator import TraceEntry
from workshop.world import RobotState

# --- format_entry ---


def test_format_entry():
    entry = TraceEntry(
        before=RobotState.IDLE,
        event_type=EventType.MACHINE_BROKE,
        outcome=Transition(target=RobotState.MOVING, reason="robot at 4.0m"),
        after=RobotState.MOVING,
    )

    row = format_entry(entry)

    assert row == "idle   --machine.broke-->   moving   (robot at 4.0m)"


def test_format_entry_reject():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.ACTION_COMPLETED,
        outcome=Reject(reason="robot too far"),
        after=RobotState.MOVING,
    )

    row = format_entry(entry)

    assert row == "moving   --action.completed--x   rejected: robot too far"


def test_format_entry_ignored():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.MACHINE_BROKE,
        outcome=None,
        after=RobotState.MOVING,
    )

    row = format_entry(entry)

    assert row == "moving   --machine.broke--   ignored"


# --- main ---


def test_main_default(capsys):
    main([])

    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 4
    assert lines[0].startswith("idle   --machine.broke-->   moving")
    assert lines[-1].startswith("repairing   --action.completed-->   idle")


def test_main_near(capsys):
    main(["--near"])

    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 3
    assert lines[0].startswith("idle   --machine.broke-->   inspecting")
    assert not any("moving" in line for line in lines)


def test_main_wear(capsys):
    main(["--wear", "75"])

    out = capsys.readouterr().out

    assert "OVERHEATED" in out


@pytest.mark.parametrize("wear", ["-1", "101", "150"])
def test_main_rejects_invalid_wear(wear, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--wear", wear])

    assert exc.value.code == 2
    assert "--wear must be between 0 and 100" in capsys.readouterr().err
