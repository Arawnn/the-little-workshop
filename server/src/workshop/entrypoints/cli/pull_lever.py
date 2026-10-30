import argparse

from workshop.adapters.system_clock import SystemClock
from workshop.domain.robot_fsm import Reject, Transition
from workshop.domain.vec3 import Vec3
from workshop.domain.world import World
from workshop.engine.simulator import Simulator, TraceEntry


def format_entry(entry: TraceEntry) -> str:
    before = entry.before.name.lower()
    event = entry.event_type.value

    if isinstance(entry.outcome, Transition):
        return f"{before}   --{event}-->   {entry.after.name.lower()}   ({entry.outcome.reason})"
    if isinstance(entry.outcome, Reject):
        return f"{before}   --{event}--x   rejected: {entry.outcome.reason}"
    return f"{before}   --{event}--   ignored"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pull-lever",
        description="Pull the lever and print the robot's decisions.",
    )
    parser.add_argument("--near", action="store_true", help="place the robot near the machine")
    parser.add_argument("--wear", type=int, default=0, help="machine wear, from 0 to 100")
    args = parser.parse_args(argv)
    if not 0 <= args.wear <= 100:
        parser.error("--wear must be between 0 and 100")
    return args


def main(argv=None):
    args = parse_args(argv)
    world = World()
    if args.near:
        world.robot.position = Vec3(3.5, 0, 0)

    if args.wear:
        world.machine.wear = args.wear

    sim = Simulator(world, SystemClock())
    sim.pull_lever()
    traces = sim.run()
    for trace in traces:
        print(format_entry(trace))
