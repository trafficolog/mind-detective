from __future__ import annotations

from dataclasses import replace

from .case import Case, CaseError, CaseLifecycle
from .planner import CandidateCheck, select_next_action
from .timeline import Timeline


def _ensure_mutable(case: Case) -> None:
    if case.lifecycle in {
        CaseLifecycle.CLOSED_FOUND,
        CaseLifecycle.CLOSED_UNRESOLVED,
        CaseLifecycle.DELETED,
    }:
        raise CaseError("MD_CASE_TERMINAL", f"case is terminal: {case.lifecycle.value}")


def set_timeline(case: Case, timeline: Timeline, now: str) -> Case:
    """Apply plugin-only reconstruction timeline state outside the portable Web contract."""
    _ensure_mutable(case)
    return replace(case, timeline=timeline, updated_at=now)


def replace_candidates(
    case: Case,
    candidates: tuple[CandidateCheck, ...],
    now: str,
) -> Case:
    """Replace plugin-produced candidate state without extending the portable command surface."""
    _ensure_mutable(case)
    return replace(case, candidates=tuple(candidates), updated_at=now)


def refresh_next_action(case: Case, now: str) -> Case:
    """Recompute the plugin next action from canonical candidate state."""
    _ensure_mutable(case)
    return replace(case, next_action=select_next_action(list(case.candidates)), updated_at=now)


def set_constraints(case: Case, constraints: tuple[str, ...], now: str) -> Case:
    """Apply plugin-only constraints without pretending they are portable Web commands."""
    _ensure_mutable(case)
    return replace(case, constraints=tuple(constraints), updated_at=now)


def mark_deleted(case: Case, now: str) -> Case:
    """Preserve the existing plugin deletion semantics behind the explicit plugin boundary."""
    if case.lifecycle is CaseLifecycle.DELETED:
        raise CaseError("MD_CASE_TERMINAL", "case is already deleted")
    return replace(case, lifecycle=CaseLifecycle.DELETED, updated_at=now)
