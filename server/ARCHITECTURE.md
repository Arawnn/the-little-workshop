# Server architecture

The `workshop` package follows a ports-and-adapters (hexagonal) layout. Dependencies point inward: `entrypoints` and `adapters` depend on `engine` and `domain`, never the reverse.

```text
src/workshop/
├── domain/        the world and its rules — no I/O, no framework
│                  world, actions, events, vec3, robot_fsm, effects, clock (Clock port)
├── engine/        moves simulated time forward and chains decisions
│                  simulator, executor, event_queue
├── adapters/      driven side: what the core calls through a port
│                  system_clock (SystemClock implements Clock)
└── entrypoints/   driving side: what calls the core
    ├── http/      FastAPI app (HTTP + SSE), JSON serialization
    └── cli/       pull-lever command
```

## Rules

- `domain` imports nothing from the other layers.
- `engine` imports `domain` only.
- A port is a `typing.Protocol` that lives next to the code that needs it (`domain/clock.py`). Its implementations live in `adapters/`.
- Entrypoints are the composition root: they pick the concrete adapters (for example, `SystemClock()` in `entrypoints/http/server.py`) and pass them to the engine.

## Tests

Tests are grouped by type, and each type mirrors the `src/workshop/` tree:

```text
tests/
├── conftest.py          shared fixtures (make_world, fake_clock)
├── unit/                one module at a time, no HTTP, no process boundary
│   ├── domain/
│   ├── engine/
│   └── entrypoints/
└── integration/         an entrypoint driven end to end (TestClient, CLI main)
    └── entrypoints/
```

Fixtures that only make sense for one layer live in a `conftest.py` inside that folder (for example, `integration/entrypoints/http/conftest.py` replaces the server clock and time scale).

```bash
uv run pytest tests/unit          # fast feedback
uv run pytest tests/integration
```
