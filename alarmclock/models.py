"""Core alarm data model."""

from dataclasses import dataclass
from datetime import date, time
from typing import Any

from .timeparse import format_hhmm, parse_hhmm


@dataclass
class Alarm:
    """A single local-time alarm."""

    id: int
    time: time
    label: str = ""
    enabled: bool = True
    last_fired: date | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the JSON-compatible representation of this alarm."""
        return {
            "id": self.id,
            "time": format_hhmm(self.time),
            "label": self.label,
            "enabled": self.enabled,
            "last_fired": self.last_fired.isoformat() if self.last_fired else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Alarm":
        """Construct an alarm from its persisted representation."""
        last_fired_value = data.get("last_fired")
        last_fired = date.fromisoformat(last_fired_value) if last_fired_value else None
        return cls(
            id=int(data["id"]),
            time=parse_hhmm(str(data["time"])),
            label=str(data.get("label", "")),
            enabled=bool(data.get("enabled", True)),
            last_fired=last_fired,
        )
