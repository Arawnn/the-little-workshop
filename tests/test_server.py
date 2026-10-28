from fastapi.testclient import TestClient

from workshop.server import app

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
            },
            {
                "before": "moving",
                "after": "inspecting",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "robot at 1.00 m",
            },
            {
                "before": "inspecting",
                "after": "repairing",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "diagnostic: JAMMED_GEAR",
            },
            {
                "before": "repairing",
                "after": "idle",
                "event": "action.completed",
                "outcome": "transition",
                "reason": "machine repaired",
            },
        ]
    }


def test_lever_rejects_wear_above_100():
    r = client.post("/lever", json={"wear": 150})

    assert r.status_code == 422
