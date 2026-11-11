from datetime import date, time
import json

import pytest

from alarmclock.models import Alarm
from alarmclock.storage import StorageError, load_alarms, resolve_path, save_alarms


def test_storage_round_trip(tmp_path) -> None:
    path = tmp_path / "nested" / "alarms.json"
    alarms = [Alarm(1, time(8, 15), "Breakfast", last_fired=date(2026, 11, 11))]

    save_alarms(path, alarms)

    assert load_alarms(path) == alarms


def test_missing_storage_is_empty(tmp_path) -> None:
    assert load_alarms(tmp_path / "missing.json") == []


def test_corrupt_storage_raises_without_overwriting(tmp_path) -> None:
    path = tmp_path / "alarms.json"
    original = "{not valid json"
    path.write_text(original, encoding="utf-8")

    with pytest.raises(StorageError, match="cannot read alarm file"):
        load_alarms(path)

    assert path.read_text(encoding="utf-8") == original


def test_non_list_storage_is_rejected(tmp_path) -> None:
    path = tmp_path / "alarms.json"
    path.write_text(json.dumps({"alarms": []}), encoding="utf-8")

    with pytest.raises(StorageError, match="cannot read alarm file"):
        load_alarms(path)


def test_explicit_path_takes_precedence(tmp_path, monkeypatch) -> None:
    environment_path = tmp_path / "environment.json"
    explicit_path = tmp_path / "explicit.json"
    monkeypatch.setenv("ALARMCLOCK_FILE", str(environment_path))

    assert resolve_path(explicit_path) == explicit_path
    assert resolve_path() == environment_path
