# AGENTS.md — Alarm Clock CLI

Instructions for the AI coding agent working in this repo. Read fully before doing anything.

## Context

This is a **30-minute, time-boxed build exercise** for a Senior Software Engineer role. The work is screen-recorded with live narration by the developer. Reviewers care about **engineering decisions, problem definition, how AI is directed, how output is reviewed, and how the result is validated** — not feature count.

So: be small, deliberate, and explicit about trade-offs. Explain *why* in one or two sentences before non-obvious choices, so the developer can narrate them.

## The task

Build an alarm clock as a **Python CLI application**.

- CLI only. No web UI, no React, no database, no network calls.
- No detailed spec exists. Scope is ours to decide (see "Scope" below).

## Hard constraints

- Python 3.11+, **standard library only** for runtime code (`argparse`, `json`, `datetime`, `pathlib`, `time`, `os`, `dataclasses`).
- `pytest` is the only allowed dev dependency.
- No audio libraries, no daemons, no OS notification APIs.
- Persistence is a single JSON file. Default `~/.alarmclock/alarms.json`; override with `--file` or the `ALARMCLOCK_FILE` env var.
- Everything must run with `python -m alarmclock ...` from the repo root.

## Workflow — follow these phases in order

Each phase ends with a **STOP**. Do not continue until the developer approves.

### Phase 0 — Refine requirements (target: ~3 min)
1. Restate the problem in 3-4 sentences.
2. Ask at most 5 clarifying questions that would change the design. Where a question has a sensible default, state the default and proceed unless told otherwise.
3. List explicit **assumptions**, **in-scope**, and **out-of-scope** items with a one-line reason for each cut.
4. **STOP.**

### Phase 1 — Design and implementation plan (target: ~4 min)
1. Propose module layout, data model, CLI surface, and error-handling approach.
2. Name the 2-3 riskiest design decisions and the alternatives considered (e.g. polling loop vs. sleep-until-next-alarm, `argparse` vs. a CLI framework).
3. Break implementation into small steps, each independently runnable and testable.
4. Write requirements, design, and plan to `docs/PLAN.md` and commit it as the first commit.
5. **STOP.**

### Phase 2 — Implement (target: ~15 min)
- One step at a time, in the order of the plan. After each step: run it, run tests, commit.
- Keep diffs small. Do not implement anything outside the approved plan. If something new seems necessary, propose it and wait.
- Write the test for pure logic *with* the code, not after.

### Phase 3 — Validate (target: ~5 min)
1. Run `pytest` and show results.
2. Run a real end-to-end demo: set an alarm one minute ahead, run `alarm run`, confirm it fires once.
3. Exercise at least three bad-input cases (bad time format, unknown id, corrupt JSON file).
4. Report honestly what is untested or known to be weak.
5. **STOP.**

### Phase 4 — Wrap up (target: ~3 min)
- Finish `README.md` (see below) and make the final commit.

## Scope

**In scope (must have)**
- `set HH:MM [--label TEXT]` — add an alarm (24-hour time)
- `list` — show all alarms with id, time, label, enabled state
- `remove ID` — delete an alarm
- `run` — foreground loop that fires due alarms (terminal bell `\a` plus a printed message) and exits cleanly on Ctrl+C
- JSON persistence with atomic writes
- Input validation with clear, single-line error messages

**Stretch (only if Phase 2 finishes early, and only with approval)**
- `--snooze MINUTES`
- `--repeat mon,wed,fri`

**Out of scope (state this in the README)**
- Audio playback, background daemon, system notifications, timezones, natural-language times ("in 5 minutes")

## Design guidance

Suggested layout (adjust in Phase 1 if there is a good reason):

```
alarmclock/
  __init__.py
  __main__.py      # calls cli.main()
  cli.py           # argparse wiring only; no business logic
  models.py        # Alarm dataclass
  timeparse.py     # parse_hhmm(str) -> datetime.time, raises ValueError
  storage.py       # load/save JSON, atomic write (tmp file + os.replace)
  scheduler.py     # due_alarms(alarms, now) pure function + run loop
tests/
  test_timeparse.py
  test_scheduler.py
  test_storage.py
docs/PLAN.md
README.md
```

Principles:
- **Pure core, thin shell.** Decision logic (`due_alarms`) is a pure function of `(alarms, now)`. I/O lives at the edges.
- **Inject the clock.** The run loop takes `now`, `sleep`, and `notify` as parameters so tests never wait on real time.
- **Fire once.** Track `last_fired` (date) per alarm so an alarm does not re-fire throughout its minute or on every poll.
- **Reload from disk each tick** so an alarm added from a second terminal is picked up by a running `run`.
- **Never destroy data on error.** A corrupt or unreadable JSON file produces an error and exit code 1; do not overwrite it.
- Exit codes: `0` success, `1` user/data error, `2` usage error (argparse default).

## Code standards

- Type hints on all function signatures; dataclasses for models.
- Small functions, descriptive names, docstrings only where intent isn't obvious.
- Errors: raise specific exceptions in library code; `cli.py` catches them and prints `error: <message>` to stderr.
- No dead code, no commented-out code, no TODOs left behind.
- No speculative abstractions. If there is one alarm type, there is one class.

## Testing

- `pytest`, fast and deterministic. No `time.sleep` in tests.
- Minimum coverage: time parsing (valid, invalid, edge cases like `00:00` and `23:59`), `due_alarms` (due, not yet due, already fired today, disabled), storage round-trip, corrupt-file handling.

## Git

- Small commits, imperative messages (`Add time parsing with validation`).
- First commit: `docs/PLAN.md`. Then one commit per plan step.

## README.md must contain

1. What it is, in two sentences.
2. Quick start: install requirements, example commands, how to run tests.
3. **Design decisions** and the trade-offs behind them.
4. **What was cut and why.**
5. **How I used AI**: where it helped, what I corrected or rejected.
6. **What I'd do next** with more time.

## Rules of engagement

- Prefer the simplest thing that works, then say what the next-simplest upgrade would be.
- If a request is ambiguous, ask before building. If you disagree with the developer's direction, say so briefly with a reason, then follow their decision.
- Never claim something works without running it. Show the command and its output.
- Do not add features, dependencies, files, or refactors that weren't in the approved plan.
- Flag your own mistakes as soon as you notice them.

## Definition of done

- [ ] `python -m alarmclock set/list/remove/run` all work end to end
- [ ] `pytest` passes
- [ ] Bad inputs produce clear errors, never tracebacks
- [ ] `docs/PLAN.md` and `README.md` are complete
- [ ] Git history shows the plan first, then incremental steps