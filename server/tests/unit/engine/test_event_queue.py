import uuid

from workshop.domain.events import Event, EventType
from workshop.engine.event_queue import PriorityEventQueue


def test_priority_queue_in_chronological_order():
    event_1 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    event_2 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    event_3 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, event_1)
    queue.push(0.0, event_2)
    queue.push(3.0, event_3)

    events = []
    while queue:
        _, event = queue.pop()
        events.append(event)

    assert events[0].machine_id == event_2.machine_id
    assert events[1].machine_id == event_1.machine_id
    assert events[2].machine_id == event_3.machine_id


def test_queue_len_before_after_pop():
    event_1 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    event_2 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    event_3 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, event_1)
    queue.push(0.0, event_2)
    queue.push(3.0, event_3)

    assert len(queue) == 3
    queue.pop()
    assert len(queue) == 2


def test_queue_current_time():
    event_1 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    event_2 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    event_3 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, event_1)
    queue.push(1.0, event_2)
    queue.push(5.0, event_3)

    assert queue.current_time() == 0.0
    queue.pop()
    assert queue.current_time() == 1.0
