# Alarm Clock CLI Plan

## Requirements

Build a Python 3.11+ command-line alarm clock with no runtime dependencies beyond the standard library. It must support creating, listing, and removing alarms, plus a foreground runner that notifies when alarms are due. Alarm data is persisted in one JSON file, with a default path of `~/.alarmclock/alarms.json` and overrides through `--file` or `ALARMCLOCK_FILE`.

The application must be runnable from the repository root with `python -m alarmclock ...`. It must validate input, report user and data errors as concise messages, avoid destroying corrupt data, fire an alarm only once per day, reload storage on every runner tick, and exit cleanly on Ctrl+C. Tests must be fast and deterministic.

## Design

### Module layout

```text
alarmclock/
  __init__.py
  __main__.py
  cli.py
  models.py
  timeparse.py
  storage.py
  scheduler.py
tests/
  test_timeparse.py
  test_scheduler.py
  test_storage.py
docs/
  PLAN.md
README.md
```

- `models.py` contains the `Alarm` dataclass and JSON serialization helpers.
- `timeparse.py` parses strict 24-hour `HH:MM` values into `datetime.time`.
- `storage.py` loads and saves alarms, resolves the configured path, and performs atomic writes with a temporary file followed by `os.replace`.
- `scheduler.py` contains the pure `due_alarms(alarms, now)` decision function and the injectable foreground loop.
- `cli.py` owns `argparse` wiring, command handlers, and conversion of library exceptions into one-line errors.
- `__main__.py` delegates to `cli.main()`.

### Data model

Each alarm has:

- `id: int`
- `time: str` in `HH:MM` form
- `label: str`
- `enabled: bool`
- `last_fired: str | None` containing an ISO date

IDs are sequential integers assigned from the highest existing ID. Duplicate times are allowed. `last_fired` prevents repeated notifications during the same local calendar date without disabling the alarm.

### CLI surface

- `python -m alarmclock set HH:MM [--label TEXT] [--file PATH]`
- `python -m alarmclock list [--file PATH]`
- `python -m alarmclock remove ID [--file PATH]`
- `python -m alarmclock run [--file PATH]`

The environment variable is used when `--file` is absent. Successful commands return `0`; user/data errors return `1`; `argparse` usage errors retain exit code `2`.

### Error handling

Library code raises specific exceptions or `ValueError`; the CLI catches expected errors and prints `error: <message>` to stderr. JSON decoding failures and unreadable files are reported without overwriting the source file. Missing storage is treated as an empty alarm list.

## Risky decisions and alternatives

1. **Polling loop versus sleeping until the next alarm:** use one-second polling so alarms added from another terminal are picked up on the next tick. The trade-off is small periodic work in exchange for simple behavior and reliable external updates.
2. **JSON format versus a database:** use one human-readable JSON file because the assignment requires single-file persistence and the data volume is tiny. Atomic replacement protects the file during writes.
3. **Argparse versus a CLI framework:** use `argparse` because it is in the standard library, provides help and usage errors, and keeps the dependency footprint at zero.

## Implementation steps

1. Add package scaffolding, the `Alarm` model, strict time parsing, and focused unit tests.
2. Add JSON storage, path resolution, atomic writes, corrupt-file handling, and storage tests.
3. Add the pure scheduler logic and injectable runner, with deterministic scheduler tests.
4. Add CLI parsing and command handlers, then test command behavior and error output.
5. Run the full test suite and perform the required end-to-end and bad-input demonstrations.
6. Complete the README with usage, decisions, cuts, AI usage, and next steps; make the final commit.

## Validation criteria

- `python -m alarmclock set/list/remove/run` work end to end.
- `pytest` passes without tests waiting on real time.
- Invalid times, unknown IDs, and corrupt JSON produce clear errors without tracebacks or data loss.
- The runner emits one notification per alarm per day and exits cleanly on Ctrl+C.
