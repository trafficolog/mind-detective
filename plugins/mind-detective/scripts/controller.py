from __future__ import annotations

from dataclasses import replace

from .case import Case, CaseError, CaseLifecycle
from .feedback import ActionFeedback
from .journal import InteractionMode, JournalEntry
from .planner import CandidateCheck, select_next_action
from .search_log import SearchCheck, find_duplicate_checks
from .statements import Statement
from .timeline import Timeline


_TERMINAL = {
    CaseLifecycle.CLOSED_FOUND,
    CaseLifecycle.CLOSED_UNRESOLVED,
    CaseLifecycle.DELETED,
}


class CaseController:
    def create_case(self, case_id: str, item_label: str, now: str) -> Case:
        return Case(
            schema="mind-detective-case/v2",
            case_id=case_id,
            item_label=item_label,
            created_at=now,
            updated_at=now,
            lifecycle=CaseLifecycle.ACTIVE,
            statements=(),
            timeline=None,
            search_checks=(),
            candidates=(),
            next_action=None,
            constraints=(),
            outcome=None,
            current_mode=InteractionMode.UNSELECTED,
            interaction_journal=(),
            action_feedback=(),
        )

    def _ensure_mutable(self, case: Case) -> None:
        if case.lifecycle in _TERMINAL:
            raise CaseError("MD_CASE_TERMINAL", f"case is terminal: {case.lifecycle.value}")

    def set_mode(self, case: Case, mode: InteractionMode, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, current_mode=mode, updated_at=now)

    def append_journal_entry(self, case: Case, entry: JournalEntry, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(
            case,
            interaction_journal=case.interaction_journal + (entry,),
            updated_at=now,
        )

    def record_action_feedback(self, case: Case, feedback: ActionFeedback, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(
            case,
            action_feedback=case.action_feedback + (feedback,),
            updated_at=now,
        )

    def add_statement(self, case: Case, statement: Statement, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, statements=case.statements + (statement,), updated_at=now)

    def set_timeline(self, case: Case, timeline: Timeline, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, timeline=timeline, updated_at=now)

    def record_search_check(self, case: Case, check: SearchCheck, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, search_checks=case.search_checks + (check,), updated_at=now)

    def find_duplicate_search_checks(self, case: Case, target: str) -> tuple[SearchCheck, ...]:
        return find_duplicate_checks(case.search_checks, target)

    def replace_candidates(
        self,
        case: Case,
        candidates: tuple[CandidateCheck, ...],
        now: str,
    ) -> Case:
        self._ensure_mutable(case)
        return replace(case, candidates=tuple(candidates), updated_at=now)

    def refresh_next_action(self, case: Case, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, next_action=select_next_action(list(case.candidates)), updated_at=now)

    def set_constraints(self, case: Case, constraints: tuple[str, ...], now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, constraints=tuple(constraints), updated_at=now)

    def pause(self, case: Case, now: str) -> Case:
        self._ensure_mutable(case)
        if case.lifecycle is not CaseLifecycle.ACTIVE:
            raise CaseError("MD_CASE_STATE", "only active cases can be paused")
        return replace(case, lifecycle=CaseLifecycle.PAUSED, updated_at=now)

    def resume(self, case: Case, now: str) -> Case:
        self._ensure_mutable(case)
        if case.lifecycle is not CaseLifecycle.PAUSED:
            raise CaseError("MD_CASE_STATE", "only paused cases can be resumed")
        return replace(case, lifecycle=CaseLifecycle.ACTIVE, updated_at=now)

    def close_found(
        self,
        case: Case,
        now: str,
        outcome: dict[str, object] | None = None,
    ) -> Case:
        self._ensure_mutable(case)
        return replace(
            case,
            lifecycle=CaseLifecycle.CLOSED_FOUND,
            outcome=outcome,
            updated_at=now,
        )

    def close_unresolved(
        self,
        case: Case,
        now: str,
        outcome: dict[str, object] | None = None,
    ) -> Case:
        self._ensure_mutable(case)
        return replace(
            case,
            lifecycle=CaseLifecycle.CLOSED_UNRESOLVED,
            outcome=outcome,
            updated_at=now,
        )

    def mark_deleted(self, case: Case, now: str) -> Case:
        if case.lifecycle is CaseLifecycle.DELETED:
            raise CaseError("MD_CASE_TERMINAL", "case is already deleted")
        return replace(case, lifecycle=CaseLifecycle.DELETED, updated_at=now)
