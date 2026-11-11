# Alarm Clock CLI

Alarm Clock CLI is a small Python 3.11+ terminal application for creating, listing, removing, and running local-time alarms. Alarms persist in a single JSON file and notify through a terminal bell and printed message.

## Quick start

Runtime code uses only the Python standard library. Install the test dependency if needed:

```bash
python3 -m pip install pytest
```

Create and inspect an alarm:

```bash
python -m alarmclock set 07:30 --label "Start work"
python -m alarmclock list
python -m alarmclock remove 1
```

Run the foreground scheduler:

```bash
python -m alarmclock run
```

The default file is `~/.alarmclock/alarms.json`. Use `--file PATH` on any command or set `ALARMCLOCK_FILE` to use another file. Run the tests with:

```bash
python3 -m pytest
```

## Design decisions

- The core scheduler is a pure `due_alarms(alarms, now)` function, while file and terminal I/O stay at the edges. This keeps the important behavior easy to test.
- The runner polls once per second and reloads the JSON file every tick. This is simple and lets another terminal add an alarm while the runner is active.
- JSON was chosen because the assignment requires one local file and the data set is small. Writes use a temporary file and `os.replace` to avoid leaving a partially written file.
- The run loop accepts injected clock, sleep, notification, load, and save functions, so tests never wait for real time.
- `last_fired` stores the local calendar date of the last notification, preventing an alarm from firing repeatedly during the same minute or day.
- `argparse` provides standard-library help and usage errors without adding a CLI dependency.

## What was cut

Audio playback, background daemon behavior, desktop notifications, timezones, and natural-language times are out of scope because the exercise explicitly excludes them and they would add platform-specific complexity. Snooze and repeating alarms were left as stretch features because the required single-time alarm workflow was complete and tested first.

## How I used AI

AI helped break the assignment into small commits, draft the module boundaries, generate initial test cases, and review edge cases around time parsing, atomic writes, and once-per-day firing. I kept the implementation deliberately small, checked every generated behavior with tests or a real CLI command, and rejected unnecessary abstractions and stretch features during the time-boxed build.

## What I would do next

I would add optional repeating schedules and snooze behavior behind explicit data-model fields, then add stronger migration/version handling for future JSON format changes. I would also add subprocess-level tests for exit codes and a longer-running integration test around alarms added from a second terminal.
