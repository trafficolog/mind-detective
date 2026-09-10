from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def build_timeline(
    statements: list[Statement],
    events: list[TimelineEvent],
    last_supported_interaction_id: str | None,
    first_noticed_missing_id: str | None,
) -> Timeline:
    by_id = {statement.id: statement for statement in statements}
    unknown_intervals = tuple(
        f"statement:{statement.id}:{limitation}"
        for statement in statements
        if statement.event_time is None
        for limitation in statement.limitations
    )
    contradictions: list[str] = []

    if last_supported_interaction_id is not None and last_supported_interaction_id not in by_id:
        contradictions.append("MD_TIME_REFERENCE_MISSING")
    if first_noticed_missing_id is not None and first_noticed_missing_id not in by_id:
        contradictions.append("MD_TIME_REFERENCE_MISSING")

    if (
        last_supported_interaction_id in by_id
        and first_noticed_missing_id in by_id
        and last_supported_interaction_id is not None
        and first_noticed_missing_id is not None
    ):
        last = by_id[last_supported_interaction_id]
        missing = by_id[first_noticed_missing_id]
        if last.event_time is not None and missing.event_time is not None:
            try:
                if _parse_time(last.event_time) > _parse_time(missing.event_time):
                    contradictions.append("MD_TIME_ORDER_CONTRADICTION")
            except ValueError:
                contradictions.append("MD_TIME_INVALID_TIMESTAMP")

    return Timeline(
        last_supported_interaction_id=last_supported_interaction_id,
        first_noticed_missing_id=first_noticed_missing_id,
        events=tuple(events),
        unknown_intervals=unknown_intervals,
        contradictions=tuple(dict.fromkeys(contradictions)),
    )
