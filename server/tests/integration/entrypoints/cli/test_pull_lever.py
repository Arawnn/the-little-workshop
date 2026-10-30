import pytest

from workshop.entrypoints.cli.pull_lever import main

# --- format_entry ---


def test_main_default(capsys):
    main([])

    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 4
    assert lines[0].startswith("idle   --machine.broke-->   moving")
    assert lines[-1].startswith("repairing   --action.completed-->   idle")


def test_main_near(capsys):
    main(["--near"])

    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 3
    assert lines[0].startswith("idle   --machine.broke-->   inspecting")
    assert not any("moving" in line for line in lines)


def test_main_wear(capsys):
    main(["--wear", "75"])

    out = capsys.readouterr().out

    assert "OVERHEATED" in out


@pytest.mark.parametrize("wear", ["-1", "101", "150"])
def test_main_rejects_invalid_wear(wear, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--wear", wear])

    assert exc.value.code == 2
    assert "--wear must be between 0 and 100" in capsys.readouterr().err
