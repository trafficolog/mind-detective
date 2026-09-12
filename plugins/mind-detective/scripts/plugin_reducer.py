from __future__ import annotations

from dataclasses import replace

from .case import Case, CaseError, CaseLifecycle
from .planner import CandidateCheck, select_next_action
from .portable_intrinsics import PortableKernelError
from .portable_kernel import set_timeline_json
from .store import case_from_dict, case_to_dict
from .timeline import Timeline


def _ensure_mutable(case: Case) -> None:
    if case.lifecycle in {
        CaseLifecycle.CLOSED_FOUND,
        CaseLifecycle.CLOSED_UNRESOLVED,
        CaseLifecycle.DELETED,
    }:
        raise CaseError("MD_CASE_TERMINAL", f"case is terminal: {case.lifecycle.value}")


def set_timeline(case: Case, timeline: Timeline, now: str) -> Case:
    """Compatibility adapter that delegates timeline truth to portable semantics."""
    event_payloads: list[dict[str, object]] = [
        {
            "id": event.id,
            "label": event.label,
            "statement_ids": list(event.statement_ids),
            "event_time": event.event_time,
            "time_precision": event.time_precision,
        }
        for event in timeline.events
    ]
    try:
        return case_from_dict(
            set_timeline_json(
                case_to_dict(case),
                event_payloads,
                timeline.last_supported_interaction_id,
                timeline.first_noticed_missing_id,
                now,
            )
        )
    except PortableKernelError as exc:
        raise CaseError(exc.code, str(exc)) from exc


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
