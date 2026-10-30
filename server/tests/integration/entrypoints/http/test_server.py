import asyncio

from fastapi.testclient import TestClient

from workshop.entrypoints.http.server import app, client_queue

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
                "t": 10.0,
            },
            {
                "before": "moving",
                "after": "inspecting",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "robot at 1.00 m",
                "t": 12.0,
            },
            {
                "before": "inspecting",
                "after": "repairing",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "diagnostic: JAMMED_GEAR",
                "t": 13.0,
            },
            {
                "before": "repairing",
                "after": "idle",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "machine repaired",
                "t": 16.0,
            },
        ]
    }


def test_lever_rejects_wear_above_100():
    r = client.post("/lever", json={"wear": 150})

    assert r.status_code == 422


def test_lever_broadcasts_trace_to_subscribers():
    queue = asyncio.Queue()
    client_id = id(queue)
    client_queue[client_id] = queue

    try:
        r = client.post("/lever", json={})
        received = []
        while queue.qsize():
            received.append(queue.get_nowait())
        assert received == r.json()["trace"]

    finally:
        del client_queue[client_id]
