from __future__ import annotations

from dataclasses import replace

from .case import Case, CaseError, CaseLifecycle
from .feedback import ActionFeedback
from .journal import InteractionMode, JournalEntry
from .planner import CandidateCheck, select_next_action
from .portable_intrinsics import PortableKernelError
from .portable_kernel import (
    add_statement_json,
    append_journal_entry_json,
    close_found_json,
    close_unresolved_json,
    create_case,
    pause_json,
    record_action_feedback_json,
    record_search_check_json,
    refine_search_check_json,
    resume_json,
    set_mode_json,
)
from .search_log import SearchCheck, SearchLogError, SearchMethod, find_duplicate_checks
from .statements import Statement
from .store import case_from_dict, case_to_dict
from .timeline import Timeline


class CaseController:
    def _from_portable(self, payload: dict[str, object]) -> Case:
        return case_from_dict(payload)

    def _case_error(self, exc: PortableKernelError) -> CaseError:
        return CaseError(exc.code, str(exc))

    def create_case(self, case_id: str, item_label: str, now: str) -> Case:
        try:
            return self._from_portable(create_case(case_id, item_label, now))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def _ensure_mutable(self, case: Case) -> None:
        if case.lifecycle in {
            CaseLifecycle.CLOSED_FOUND,
            CaseLifecycle.CLOSED_UNRESOLVED,
            CaseLifecycle.DELETED,
        }:
            raise CaseError("MD_CASE_TERMINAL", f"case is terminal: {case.lifecycle.value}")

    def set_mode(self, case: Case, mode: InteractionMode, now: str) -> Case:
        try:
            return self._from_portable(set_mode_json(case_to_dict(case), mode.value, now))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def append_journal_entry(self, case: Case, entry: JournalEntry, now: str) -> Case:
        entry_payload: dict[str, object] = {
            "id": entry.id,
            "author": entry.author.value,
            "mode": entry.mode.value,
            "entry_type": entry.entry_type,
            "text": entry.text,
            "created_at": entry.created_at,
            "statement_ids": list(entry.statement_ids),
            "search_check_ids": list(entry.search_check_ids),
        }
        try:
            return self._from_portable(
                append_journal_entry_json(case_to_dict(case), entry_payload, now)
            )
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def record_action_feedback(self, case: Case, feedback: ActionFeedback, now: str) -> Case:
        feedback_payload: dict[str, object] = {
            "id": feedback.id,
            "candidate_id": feedback.candidate_id,
            "reason": feedback.reason.value,
            "recorded_at": feedback.recorded_at,
        }
        try:
            return self._from_portable(
                record_action_feedback_json(case_to_dict(case), feedback_payload, now)
            )
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def add_statement(self, case: Case, statement: Statement, now: str) -> Case:
        statement_payload: dict[str, object] = {
            "id": statement.id,
            "source": statement.source.value,
            "statement_type": statement.statement_type.value,
            "original_text": statement.original_text,
            "recorded_at": statement.recorded_at,
            "event_time": statement.event_time,
            "user_confirmation": statement.user_confirmation,
            "supporting_evidence_ids": list(statement.supporting_evidence_ids),
            "limitations": list(statement.limitations),
        }
        try:
            return self._from_portable(add_statement_json(case_to_dict(case), statement_payload, now))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def set_timeline(self, case: Case, timeline: Timeline, now: str) -> Case:
        self._ensure_mutable(case)
        return replace(case, timeline=timeline, updated_at=now)

    def record_search_check(self, case: Case, check: SearchCheck, now: str) -> Case:
        check_payload: dict[str, object] = {
            "id": check.id,
            "target": check.target,
            "method": check.method.value,
            "started_at": check.started_at,
            "completed_at": check.completed_at,
            "result": check.result.value,
            "inaccessible_parts": list(check.inaccessible_parts),
            "based_on": list(check.based_on),
            "notes": list(check.notes),
        }
        try:
            return self._from_portable(
                record_search_check_json(case_to_dict(case), check_payload, now)
            )
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def refine_search_check(
        self,
        case: Case,
        check_id: str,
        method: SearchMethod,
        inaccessible_parts: tuple[str, ...],
        now: str,
    ) -> Case:
        try:
            return self._from_portable(
                refine_search_check_json(
                    case_to_dict(case),
                    check_id,
                    method.value,
                    list(inaccessible_parts),
                    now,
                )
            )
        except PortableKernelError as exc:
            if exc.code in {"MD_SEARCH_METHOD_INVALID", "MD_SEARCH_CHECK_NOT_FOUND"}:
                raise SearchLogError(exc.code, str(exc)) from exc
            raise self._case_error(exc) from exc

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
        try:
            return self._from_portable(pause_json(case_to_dict(case), now))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def resume(self, case: Case, now: str) -> Case:
        try:
            return self._from_portable(resume_json(case_to_dict(case), now))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def close_found(
        self,
        case: Case,
        now: str,
        outcome: dict[str, object] | None = None,
    ) -> Case:
        try:
            return self._from_portable(close_found_json(case_to_dict(case), now, outcome))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def close_unresolved(
        self,
        case: Case,
        now: str,
        outcome: dict[str, object] | None = None,
    ) -> Case:
        try:
            return self._from_portable(close_unresolved_json(case_to_dict(case), now, outcome))
        except PortableKernelError as exc:
            raise self._case_error(exc) from exc

    def mark_deleted(self, case: Case, now: str) -> Case:
        if case.lifecycle is CaseLifecycle.DELETED:
            raise CaseError("MD_CASE_TERMINAL", "case is already deleted")
        return replace(case, lifecycle=CaseLifecycle.DELETED, updated_at=now)
