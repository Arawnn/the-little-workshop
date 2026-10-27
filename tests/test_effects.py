import uuid

import pytest

from workshop.effects import apply_completion_effect, apply_start_effect
from workshop.events import Action, ActionType
from workshop.world import Diagnostic, MachineState


def test_apply_start_effect_repair_action(make_world):
    world = make_world()
    action = Action(id=uuid.uuid4(), type=ActionType.REPAIR, machine_id=world.machine.id)

    apply_start_effect(action=action, world=world)

    assert world.machine.state == MachineState.REPAIRING


def test_apply_completion_effect_move_to_action(make_world):
    world = make_world()
    action = Action(
        id=uuid.uuid4(),
        type=ActionType.MOVE_TO,
        machine_id=world.machine.id,
        target=world.machine.poi,
    )

    apply_completion_effect(action=action, world=world)

    assert world.robot.position == world.machine.poi


def test_apply_completion_effect_move_to_without_target(make_world):
    world = make_world()
    action = Action(id=uuid.uuid4(), type=ActionType.MOVE_TO, machine_id=world.machine.id)

    with pytest.raises(ValueError):
        apply_completion_effect(action=action, world=world)


def test_apply_completion_effect_inspect_action(make_world):
    world = make_world()
    action = Action(id=uuid.uuid4(), type=ActionType.INSPECT, machine_id=world.machine.id)

    assert world.machine.diagnostic is None

    apply_completion_effect(action=action, world=world)

    assert isinstance(world.machine.diagnostic, Diagnostic)
    assert world.machine.diagnostic == Diagnostic.JAMMED_GEAR
    world.machine.wear = 75
    apply_completion_effect(action=action, world=world)
    assert world.machine.diagnostic == Diagnostic.OVERHEATED
    world.machine.wear = 90
    apply_completion_effect(action=action, world=world)
    assert world.machine.diagnostic == Diagnostic.WORN_BELT


def test_apply_completion_effect_repair_action(make_world):
    world = make_world(machine_state=MachineState.REPAIRING, diagnostic=Diagnostic.JAMMED_GEAR)
    world.machine.wear = 75
    action = Action(id=uuid.uuid4(), type=ActionType.REPAIR, machine_id=world.machine.id)

    apply_completion_effect(action=action, world=world)

    assert world.machine.diagnostic is None
    assert world.machine.wear == 0
    assert world.machine.state == MachineState.RUNNING
