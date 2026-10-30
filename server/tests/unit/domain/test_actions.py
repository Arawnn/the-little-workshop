from workshop.domain.actions import ACTION_DURATIONS, ActionType


def test_action_type_has_positive_duration():

    for action in ActionType:
        if action in ACTION_DURATIONS:
            assert ACTION_DURATIONS[action] > 0
        else:
            raise ValueError(f"{action} has no duration: add it to ACTION_DURATIONS.")


def test_action_type_has_specific_values():

    assert ACTION_DURATIONS[ActionType.MOVE_TO] == 2

    assert ACTION_DURATIONS[ActionType.INSPECT] == 1

    assert ACTION_DURATIONS[ActionType.REPAIR] == 3
