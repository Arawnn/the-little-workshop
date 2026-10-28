from fastapi import FastAPI
from pydantic import BaseModel, Field

from workshop.serialize import entry_to_dict
from workshop.simulator import Simulator
from workshop.vec3 import Vec3
from workshop.world import World

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class LeverOptions(BaseModel):
    wear: int = Field(default=0, ge=0, le=100)
    near: bool = False


@app.post("/lever")
def lever(options: LeverOptions) -> dict[str, list[dict[str, str | None]]]:
    world = World()
    if options.near:
        world.robot.position = Vec3(3.5, 0, 0)

    if options.wear:
        world.machine.wear = options.wear

    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())

    return {"trace": [entry_to_dict(e) for e in traces]}
