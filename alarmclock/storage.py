"""Persistent JSON storage for alarms."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Iterable

from .models import Alarm


DEFAULT_PATH = Path.home() / ".alarmclock" / "alarms.json"


class StorageError(Exception):
    """Raised when the alarm file cannot be read or written safely."""


def resolve_path(explicit: str | Path | None = None) -> Path:
    """Resolve the configured alarm file path."""
    if explicit is not None:
        return Path(explicit).expanduser()
    environment_path = os.environ.get("ALARMCLOCK_FILE")
    if environment_path:
        return Path(environment_path).expanduser()
    return DEFAULT_PATH


def load_alarms(path: Path) -> list[Alarm]:
    """Load alarms from JSON, treating a missing file as empty storage."""
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            raw_alarms = json.load(file)
        if not isinstance(raw_alarms, list):
            raise ValueError("root value is not a list")
        return [Alarm.from_dict(item) for item in raw_alarms]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise StorageError(f"cannot read alarm file: {error}") from error


def save_alarms(path: Path, alarms: Iterable[Alarm]) -> None:
    """Atomically replace the alarm file with the supplied alarms."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = file.name
            json.dump([alarm.to_dict() for alarm in alarms], file, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, TypeError, ValueError) as error:
        raise StorageError(f"cannot write alarm file: {error}") from error
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass
