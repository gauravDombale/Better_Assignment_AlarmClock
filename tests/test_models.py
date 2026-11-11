from datetime import date, time

from alarmclock.models import Alarm


def test_alarm_round_trip() -> None:
    alarm = Alarm(4, time(6, 30), "Morning", last_fired=date(2026, 11, 11))

    restored = Alarm.from_dict(alarm.to_dict())

    assert restored == alarm
