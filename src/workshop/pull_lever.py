import argparse

from workshop.robot_fsm import Reject, Transition
from workshop.simulator import Simulator, TraceEntry
from workshop.vec3 import Vec3
from workshop.world import World


def format_entry(entry: TraceEntry) -> str:
    before = entry.before.name.lower()
    event = entry.event_type.value

    if isinstance(entry.outcome, Transition):
        return f"{before}   --{event}-->   {entry.after.name.lower()}   ({entry.outcome.reason})"
    if isinstance(entry.outcome, Reject):
        return f"{before}   --{event}--x   rejeté : {entry.outcome.reason}"
    return f"{before}   --{event}--   ignoré"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pull-lever",
        description="Tire le levier et affiche les décisions du Bricoleur.",
    )
    parser.add_argument("--near", action="store_true", help="place le robot près de la machine")
    parser.add_argument("--wear", type=int, default=0, help="usure de la machine, de 0 à 100")
    args = parser.parse_args(argv)
    if not 0 <= args.wear <= 100:
        parser.error("--wear doit être compris entre 0 et 100")
    return args


def main(argv=None):
    args = parse_args(argv)
    world = World()
    if args.near:
        world.robot.position = Vec3(3.5, 0, 0)

    if args.wear:
        world.machine.wear = args.wear

    sim = Simulator(world)

    traces = sim.run(sim.pull_lever())
    for trace in traces:
        print(format_entry(trace))
