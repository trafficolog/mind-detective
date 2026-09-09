from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .planner import CandidateCheck, NextAction
from .search_log import SearchCheck
from .statements import Statement
from .timeline import Timeline


class CaseLifecycle(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED_FOUND = "closed_found"
    CLOSED_UNRESOLVED = "closed_unresolved"
    DELETED = "deleted"


class CaseError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class Case:
    schema: str
    case_id: str
    item_label: str
    created_at: str
    updated_at: str
    lifecycle: CaseLifecycle
    statements: tuple[Statement, ...]
    timeline: Timeline | None
    search_checks: tuple[SearchCheck, ...]
    candidates: tuple[CandidateCheck, ...]
    next_action: NextAction | None
    constraints: tuple[str, ...]
    outcome: dict[str, object] | None
