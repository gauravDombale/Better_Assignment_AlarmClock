from datetime import time

import pytest

from alarmclock.timeparse import format_hhmm, parse_hhmm


@pytest.mark.parametrize(
    ("value", "expected"),
    [("00:00", time(0, 0)), ("09:05", time(9, 5)), ("23:59", time(23, 59))],
)
def test_parse_valid_hhmm(value: str, expected: time) -> None:
    assert parse_hhmm(value) == expected


@pytest.mark.parametrize("value", ["0:00", "00:0", "24:00", "12:60", "12.30", " noon"])
def test_parse_invalid_hhmm(value: str) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        parse_hhmm(value)


def test_format_hhmm() -> None:
    assert format_hhmm(time(7, 3)) == "07:03"
