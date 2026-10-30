import uuid

from workshop.domain.events import Event, EventType
from workshop.engine.event_queue import PriorityEventQueue


def test_priority_queue_in_chronological_order():
    first_at_3 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    at_0 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    second_at_3 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, first_at_3)
    queue.push(0.0, at_0)
    queue.push(3.0, second_at_3)

    events = []
    while queue:
        _, event = queue.pop()
        events.append(event)

    assert events[0].machine_id == at_0.machine_id
    assert events[1].machine_id == first_at_3.machine_id
    assert events[2].machine_id == second_at_3.machine_id


def test_queue_len_before_after_pop():
    first_at_3 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    at_0 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    second_at_3 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, first_at_3)
    queue.push(0.0, at_0)
    queue.push(3.0, second_at_3)

    assert len(queue) == 3
    queue.pop()
    assert len(queue) == 2


def test_queue_current_time():
    at_3 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    at_1 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    at_5 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, at_3)
    queue.push(1.0, at_1)
    queue.push(5.0, at_5)

    assert queue.current_time() == 0.0
    queue.pop()
    assert queue.current_time() == 1.0


def test_peek():
    at_3 = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    earliest = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())
    at_5 = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(3.0, at_3)
    queue.push(1.0, earliest)

    queue.push(5.0, at_5)

    t, head_event = queue.peek()

    assert t == 1.0
    assert head_event == earliest


def test_peek_with_two_event_with_same_time():

    pushed_first = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    pushed_second = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(1.0, pushed_first)
    queue.push(1.0, pushed_second)

    t, head_event = queue.peek()

    assert t == 1.0
    assert head_event == pushed_first


def test_peek_with_empty_queue():
    queue = PriorityEventQueue()

    assert queue.peek() is None


def test_peek_does_not_remove_head():
    pushed_first = Event(type=EventType.ACTION_COMPLETED, machine_id=uuid.uuid4())
    pushed_second = Event(type=EventType.MACHINE_BROKE, machine_id=uuid.uuid4())

    queue = PriorityEventQueue()

    queue.push(1.0, pushed_first)
    queue.push(1.0, pushed_second)

    _, _ = queue.peek()

    assert len(queue) == 2
    assert queue.current_time() == 0.0
