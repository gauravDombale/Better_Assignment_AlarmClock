from datetime import datetime, time

from alarmclock.models import Alarm
from alarmclock.scheduler import due_alarms, run_loop


def test_due_alarms_returns_due_enabled_alarms() -> None:
    now = datetime(2026, 11, 11, 10, 30)
    due = Alarm(1, time(10, 30))
    earlier = Alarm(2, time(9, 0))
    later = Alarm(3, time(10, 31))
    disabled = Alarm(4, time(8, 0), enabled=False)
    already_fired = Alarm(5, time(7, 0), last_fired=now.date())

    assert due_alarms([due, earlier, later, disabled, already_fired], now) == [due, earlier]


def test_due_alarms_does_not_fire_alarm_from_another_date() -> None:
    alarm = Alarm(1, time(9, 0), last_fired=datetime(2026, 11, 10).date())

    assert due_alarms([alarm], datetime(2026, 11, 11, 9, 1)) == [alarm]


def test_run_loop_reloads_and_fires_once() -> None:
    alarm = Alarm(1, time(10, 0), "Meeting")
    stored = [alarm]
    notifications: list[int] = []
    moments = iter([datetime(2026, 11, 11, 10, 0), datetime(2026, 11, 11, 10, 0)])

    def fake_now() -> datetime:
        return next(moments)

    def fake_sleep(_: float) -> None:
        if len(notifications) == 1:
            raise KeyboardInterrupt

    def fake_load(_path) -> list[Alarm]:
        return stored

    def fake_save(_path, alarms) -> None:
        assert list(alarms)[0].last_fired == datetime(2026, 11, 11).date()

    try:
        run_loop(
            path=None,
            now=fake_now,
            sleep=fake_sleep,
            notify=lambda item: notifications.append(item.id),
            load=fake_load,
            save=fake_save,
        )
    except KeyboardInterrupt:
        pass

    assert notifications == [1]
