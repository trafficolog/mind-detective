from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from .portable_kernel import derive_timeline_json
from .statements import Statement


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    id: str
    label: str
    statement_ids: tuple[str, ...]
    event_time: str | None
    time_precision: str


@dataclass(frozen=True, slots=True)
class Timeline:
    last_supported_interaction_id: str | None
    first_noticed_missing_id: str | None
    events: tuple[TimelineEvent, ...]
    unknown_intervals: tuple[str, ...]
    contradictions: tuple[str, ...]


def build_timeline(
    statements: list[Statement],
    events: list[TimelineEvent],
    last_supported_interaction_id: str | None,
    first_noticed_missing_id: str | None,
) -> Timeline:
    statement_payloads: list[object] = [
        {
            "id": statement.id,
            "event_time": statement.event_time,
            "limitations": list(statement.limitations),
        }
        for statement in statements
    ]
    event_payloads = [
        {
            "id": event.id,
            "label": event.label,
            "statement_ids": list(event.statement_ids),
            "event_time": event.event_time,
            "time_precision": event.time_precision,
        }
        for event in events
    ]
    canonical = derive_timeline_json(
        statement_payloads,
        event_payloads,
        last_supported_interaction_id,
        first_noticed_missing_id,
    )
    unknown_intervals = cast(list[str], canonical["unknown_intervals"])
    contradictions = cast(list[str], canonical["contradictions"])
    return Timeline(
        last_supported_interaction_id=last_supported_interaction_id,
        first_noticed_missing_id=first_noticed_missing_id,
        events=tuple(events),
        unknown_intervals=tuple(unknown_intervals),
        contradictions=tuple(contradictions),
    )
