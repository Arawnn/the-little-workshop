import asyncio

from fastapi.testclient import TestClient

from workshop.server import app, broadcast

client = TestClient(app)


def test_health():
    r = client.get("/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_lever_without_options():
    r = client.post("/lever", json={})

    assert r.status_code == 200
    assert r.json() == {
        "trace": [
            {
                "before": "idle",
                "after": "moving",
                "event": "machine.broke",
                "outcome": "transition",
                "reason": "robot at 4.00 m",
                "t": 0.0,
            },
            {
                "before": "moving",
                "after": "inspecting",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "robot at 1.00 m",
                "t": 2.0,
            },
            {
                "before": "inspecting",
                "after": "repairing",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "diagnostic: JAMMED_GEAR",
                "t": 3.0,
            },
            {
                "before": "repairing",
                "after": "idle",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "machine repaired",
                "t": 6.0,
            },
        ]
    }


def test_lever_rejects_wear_above_100():
    r = client.post("/lever", json={"wear": 150})

    assert r.status_code == 422


def test_broadcast_waits_delta_time_scale():
    delays = []

    async def fake_sleep(seconds: float) -> None:
        delays.append(seconds)

    entries = [{"t": 0.0}, {"t": 2.0}, {"t": 3.0}, {"t": 6.0}]

    asyncio.run(broadcast(entries, {}, 1, fake_sleep))

    assert delays == [0.0, 2.0, 1.0, 3.0]


def test_broadcast_waits_delta_time_half_scale():

    delays = []

    async def fake_sleep(seconds: float) -> None:
        delays.append(seconds)

    entries = [{"t": 0.0}, {"t": 2.0}, {"t": 3.0}, {"t": 6.0}]

    asyncio.run(broadcast(entries, {}, 0.5, fake_sleep))

    assert delays == [0.0, 1.0, 0.5, 1.5]


def test_broadcast_pushes_entries_to_subscribers():
    queue = asyncio.Queue()
    queues = {1: queue}

    async def fake_sleep(seconds: float) -> None:
        pass

    entries = [{"t": 0.0}, {"t": 2.0}, {"t": 3.0}, {"t": 6.0}]

    asyncio.run(broadcast(entries, queues, 1, fake_sleep))

    assert len(entries) == queue.qsize()

    received = []
    while queue.qsize() > 0:
        received.append(queue.get_nowait())
    assert received == entries
