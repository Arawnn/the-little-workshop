import asyncio

from fastapi import BackgroundTasks, FastAPI
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel, Field

from workshop.serialize import entry_to_dict
from workshop.simulator import Simulator
from workshop.vec3 import Vec3
from workshop.world import World

app = FastAPI()

client_queue = {}

TIME_SCALE = 1.0


async def broadcast(
    entries: list[dict[str, str | float | None]],
    queues: dict[int, asyncio.Queue],
    scale: float,
    sleep=asyncio.sleep,
) -> None:
    t_precedent = 0

    for entry in entries:
        delta = (entry["t"] - t_precedent) * scale
        await sleep(delta)
        for queue in queues.values():
            queue.put_nowait(entry)

        t_precedent = entry["t"]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/events", response_class=EventSourceResponse)
async def events():
    queue = asyncio.Queue()
    client_id = id(queue)
    client_queue[client_id] = queue
    try:
        while True:
            event = await queue.get()
            yield event
    finally:
        client_queue.pop(client_id)


class LeverOptions(BaseModel):
    wear: int = Field(default=0, ge=0, le=100)
    near: bool = False


@app.post("/lever")
async def lever(
    options: LeverOptions, background_tasks: BackgroundTasks
) -> dict[str, list[dict[str, str | float | None]]]:
    world = World()
    if options.near:
        world.robot.position = Vec3(3.5, 0, 0)

    if options.wear:
        world.machine.wear = options.wear

    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())

    entries = [entry_to_dict(e) for e in traces]

    background_tasks.add_task(broadcast, entries, client_queue, TIME_SCALE)

    return {"trace": entries}
