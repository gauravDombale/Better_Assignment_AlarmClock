"""Alarm scheduling decisions and the foreground runner."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path
import time as time_module

from .models import Alarm
from .storage import load_alarms, save_alarms


def due_alarms(alarms: Iterable[Alarm], now: datetime) -> list[Alarm]:
    """Return enabled alarms due at ``now`` and not fired on that date."""
    return [
        alarm
        for alarm in alarms
        if alarm.enabled and alarm.time <= now.time() and alarm.last_fired != now.date()
    ]


def run_loop(
    path: Path,
    *,
    now: Callable[[], datetime] = datetime.now,
    sleep: Callable[[float], None] = time_module.sleep,
    notify: Callable[[Alarm], None],
    load: Callable[[Path], list[Alarm]] = load_alarms,
    save: Callable[[Path, Iterable[Alarm]], None] = save_alarms,
    poll_interval: float = 1.0,
) -> None:
    """Poll storage and notify for due alarms until interrupted."""
    while True:
        current = now()
        alarms = load(path)
        due = due_alarms(alarms, current)
        if due:
            fired_date: date = current.date()
            for alarm in due:
                alarm.last_fired = fired_date
                notify(alarm)
            save(path, alarms)
        sleep(poll_interval)
