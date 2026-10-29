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
- `web/` — browser client (Vite + TypeScript): a button pulls the lever, transitions stream in live

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

### Run the web client

The client needs the server running. Use two terminals:

```bash
# terminal 1
cd server
uv run uvicorn workshop.server:app --reload   # :8000

# terminal 2
cd web
npm install
npm run dev                                   # :5173
```

Open http://localhost:5173 and click **Pull the lever**: each transition appears as it is decided. Open a second tab to see both receive the same events.

In development, Vite proxies `/api/*` to `http://localhost:8000` (see `web/vite.config.ts`), so the browser talks to a single origin and no CORS setup is needed. The proxy only exists in `npm run dev`; production hosting is not decided yet.

## How it works

`idle → moving → inspecting → repairing → idle`

A state machine (state pattern) and an event-driven simulation: each action applies its effects to the world before the next decision.
