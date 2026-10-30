import asyncio

from fastapi.testclient import TestClient

from workshop.entrypoints.http.server import app, broadcast

client = TestClient(app)


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
