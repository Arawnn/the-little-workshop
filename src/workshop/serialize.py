from workshop.robot_fsm import Reject, Transition
from workshop.simulator import TraceEntry


def entry_to_dict(entry: TraceEntry) -> dict:
    return {
        "before": entry.before.name.lower(),
        "after": entry.after.name.lower(),
        "event": entry.event_type.value,
        "outcome": match_outcome(entry),
        "reason": entry.outcome.reason if entry.outcome is not None else None,
    }


def match_outcome(entry: TraceEntry) -> str:
    match entry.outcome:
        case Transition():
            return "transition"
        case Reject():
            return "reject"
        case None:
            return "ignored"
        case _:
            raise ValueError(f"unknown outcome: {entry.outcome!r}")
