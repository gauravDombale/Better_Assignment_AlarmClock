"""Parsing and formatting for strict 24-hour alarm times."""

from datetime import time
import re


_HHMM = re.compile(r"^(\d{2}):(\d{2})$")


def parse_hhmm(value: str) -> time:
    """Parse an exact `HH:MM` value or raise ValueError."""
    match = _HHMM.fullmatch(value)
    if match is None:
        raise ValueError("time must use HH:MM in 24-hour format")

    hour, minute = (int(part) for part in match.groups())
    if hour > 23 or minute > 59:
        raise ValueError("time must use HH:MM in 24-hour format")
    return time(hour=hour, minute=minute)


def format_hhmm(value: time) -> str:
    """Format a time as `HH:MM`."""
    return value.strftime("%H:%M")
