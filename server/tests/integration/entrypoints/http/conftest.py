import pytest

from workshop.entrypoints.http import server


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr(server, "TIME_SCALE", 0)


@pytest.fixture(autouse=True)
def server_clock(monkeypatch, fake_clock):
    monkeypatch.setattr(server, "clock", fake_clock())
