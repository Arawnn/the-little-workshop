# The Little Workshop

**A world where agents make decisions.**

![The robot repairs the machine](assets/pull-lever.gif)

A visitor pulls a lever and the machine breaks. The robot then decides what to do: move, inspect, run a diagnosis, repair. Every decision is traced, including the ones it rejects.

## Project status

- [x] The robot loop in the terminal
- [x] The lever over HTTP, with live events (SSE)
- [ ] The 3D scene in the browser
- [ ] An LLM proposes the action, the engine validates it

## Repository organization

- `server/` — Python engine: state machine, simulation, `pull-lever` CLI and FastAPI server (HTTP + SSE)
- `web/` — browser client (Vite + TypeScript, coming next)

## Try it

```bash
cd server
uv sync
uv run pull-lever             # robot 4 m away: it moves first
uv run pull-lever --near      # robot nearby: it inspects right away
uv run pull-lever --wear 95   # high wear: different diagnosis
uv run pytest
uv run uvicorn workshop.server:app --reload   # HTTP + SSE server on :8000
```

## How it works

`idle → moving → inspecting → repairing → idle`

A state machine (state pattern) and an event-driven simulation: each action applies its effects to the world before the next decision.
