"""Command-line interface for the alarm clock."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import datetime
import sys

from .models import Alarm
from .scheduler import run_loop
from .storage import StorageError, load_alarms, resolve_path, save_alarms
from .timeparse import format_hhmm, parse_hhmm


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description="Manage and run terminal alarms.")
    commands = parser.add_subparsers(dest="command", required=True)

    set_parser = commands.add_parser("set", help="create an alarm")
    set_parser.add_argument("time", help="alarm time in HH:MM format")
    set_parser.add_argument("--label", default="", help="optional alarm label")
    _add_file_argument(set_parser)

    list_parser = commands.add_parser("list", help="list alarms")
    _add_file_argument(list_parser)

    remove_parser = commands.add_parser("remove", help="remove an alarm")
    remove_parser.add_argument("id", type=int, help="alarm ID")
    _add_file_argument(remove_parser)

    run_parser = commands.add_parser("run", help="run the foreground alarm loop")
    _add_file_argument(run_parser)

    return parser


def _add_file_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", help="alarm JSON file path")


def _handle_set(args: argparse.Namespace) -> int:
    alarm_time = parse_hhmm(args.time)
    path = resolve_path(args.file)
    alarms = load_alarms(path)
    next_id = max((alarm.id for alarm in alarms), default=0) + 1
    alarm = Alarm(next_id, alarm_time, args.label)
    save_alarms(path, [*alarms, alarm])
    print(f"created alarm {alarm.id} at {format_hhmm(alarm.time)}")
    return 0


def _handle_list(args: argparse.Namespace) -> int:
    alarms = load_alarms(resolve_path(args.file))
    if not alarms:
        print("no alarms")
        return 0
    for alarm in alarms:
        state = "enabled" if alarm.enabled else "disabled"
        label = f" {alarm.label}" if alarm.label else ""
        print(f"{alarm.id}: {format_hhmm(alarm.time)}{label} [{state}]")
    return 0


def _handle_remove(args: argparse.Namespace) -> int:
    path = resolve_path(args.file)
    alarms = load_alarms(path)
    remaining = [alarm for alarm in alarms if alarm.id != args.id]
    if len(remaining) == len(alarms):
        raise ValueError(f"alarm ID {args.id} not found")
    save_alarms(path, remaining)
    print(f"removed alarm {args.id}")
    return 0


def _notify(alarm: Alarm) -> None:
    label = alarm.label or format_hhmm(alarm.time)
    print(f"\aalarm {alarm.id}: {label}", flush=True)


def _handle_run(args: argparse.Namespace) -> int:
    try:
        run_loop(resolve_path(args.file), notify=_notify)
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "set": _handle_set,
        "list": _handle_list,
        "remove": _handle_remove,
        "run": _handle_run,
    }
    try:
        return handlers[args.command](args)
    except (StorageError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
