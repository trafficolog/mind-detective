from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StatementSource(str, Enum):
    USER = "user"
    FILE = "file"
    ASSISTANT = "assistant"


class StatementType(str, Enum):
    RECOLLECTION = "recollection"
    HABIT = "habit"
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    SEARCH_SUGGESTION = "search_suggestion"


ALLOWED_TYPES: dict[StatementSource, frozenset[StatementType]] = {
    StatementSource.USER: frozenset(StatementType),
    StatementSource.FILE: frozenset({StatementType.OBSERVATION}),
    StatementSource.ASSISTANT: frozenset(
        {StatementType.HYPOTHESIS, StatementType.SEARCH_SUGGESTION}
    ),
}


class StatementError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class Statement:
    id: str
    source: StatementSource
    statement_type: StatementType
    original_text: str
    recorded_at: str
    event_time: str | None
    user_confirmation: bool
    supporting_evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]


def create_statement(
    *,
    statement_id: str,
    source: StatementSource,
    statement_type: StatementType,
    original_text: str,
    recorded_at: str,
    event_time: str | None,
    user_confirmation: bool,
    supporting_evidence_ids: tuple[str, ...],
    limitations: tuple[str, ...],
) -> Statement:
    if statement_type not in ALLOWED_TYPES[source]:
        code = (
            "MD_STMT_ASSISTANT_ORIGIN"
            if source is StatementSource.ASSISTANT
            and statement_type
            in {
                StatementType.RECOLLECTION,
                StatementType.HABIT,
                StatementType.OBSERVATION,
            }
            else "MD_STMT_SOURCE_TYPE"
        )
        raise StatementError(code, f"{source.value} cannot originate {statement_type.value}")

    return Statement(
        id=statement_id,
        source=source,
        statement_type=statement_type,
        original_text=original_text,
        recorded_at=recorded_at,
        event_time=event_time,
        user_confirmation=user_confirmation,
        supporting_evidence_ids=tuple(supporting_evidence_ids),
        limitations=tuple(limitations),
    )
