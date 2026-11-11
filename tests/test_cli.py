from pathlib import Path

from alarmclock import cli


def test_set_list_and_remove_commands(tmp_path, capsys) -> None:
    path = tmp_path / "alarms.json"

    assert cli.main(["set", "07:05", "--label", "Wake", "--file", str(path)]) == 0
    assert "created alarm 1" in capsys.readouterr().out

    assert cli.main(["list", "--file", str(path)]) == 0
    assert "1: 07:05 Wake [enabled]" in capsys.readouterr().out

    assert cli.main(["remove", "1", "--file", str(path)]) == 0
    assert "removed alarm 1" in capsys.readouterr().out


def test_bad_time_returns_error(tmp_path, capsys) -> None:
    result = cli.main(["set", "25:00", "--file", str(tmp_path / "alarms.json")])

    captured = capsys.readouterr()
    assert result == 1
    assert captured.err.startswith("error: ")


def test_unknown_id_returns_error(tmp_path, capsys) -> None:
    result = cli.main(["remove", "99", "--file", str(tmp_path / "alarms.json")])

    captured = capsys.readouterr()
    assert result == 1
    assert "alarm ID 99 not found" in captured.err


def test_corrupt_file_returns_error(tmp_path, capsys) -> None:
    path = Path(tmp_path / "alarms.json")
    path.write_text("not json", encoding="utf-8")

    result = cli.main(["list", "--file", str(path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "cannot read alarm file" in captured.err


def test_run_handles_keyboard_interrupt(monkeypatch, tmp_path, capsys) -> None:
    def interrupt(*args, **kwargs) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "run_loop", interrupt)

    assert cli.main(["run", "--file", str(tmp_path / "alarms.json")]) == 0
    assert "stopped" in capsys.readouterr().out
