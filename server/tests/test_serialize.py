import json

from workshop.events import EventType
from workshop.robot_fsm import Reject, Transition
from workshop.serialize import entry_to_dict
from workshop.simulator import TraceEntry
from workshop.world import RobotState


def test_entry_to_dict_transition():
    entry = TraceEntry(
        before=RobotState.IDLE,
        event_type=EventType.MACHINE_BROKE,
        outcome=Transition(target=RobotState.MOVING, reason="robot at 4.0m"),
        after=RobotState.MOVING,
        t=0.0,
    )
    res = json.dumps(entry_to_dict(entry))

    assert json.loads(res) == {
        "before": "idle",
        "after": "moving",
        "event": "machine.broke",
        "outcome": "transition",
        "reason": "robot at 4.0m",
        "t": 0.0,
    }


def test_entry_to_dict_ignore():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.MACHINE_BROKE,
        outcome=None,
        after=RobotState.MOVING,
        t=0.0,
    )
    res = json.dumps(entry_to_dict(entry))

    assert json.loads(res) == {
        "before": "moving",
        "after": "moving",
        "event": "machine.broke",
        "outcome": "ignored",
        "reason": None,
        "t": 0.0,
    }


def test_entry_to_dict_reject():
    entry = TraceEntry(
        before=RobotState.MOVING,
        event_type=EventType.ACTION_COMPLETED,
        outcome=Reject(reason="robot too far"),
        after=RobotState.MOVING,
        t=0.0,
    )
    res = json.dumps(entry_to_dict(entry))

    assert json.loads(res) == {
        "before": "moving",
        "after": "moving",
        "event": "action.completed",
        "outcome": "reject",
        "reason": "robot too far",
        "t": 0.0,
    }
