from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .case import Case, CaseLifecycle
from .planner import (
    CandidateBasis,
    CandidateCheck,
    CheckState,
    Effort,
    NextAction,
    RouteRelation,
    Safety,
    UrgencyRelevance,
)
from .schemas import CASE_SCHEMA, SchemaError, validate_case_payload
from .search_log import SearchCheck, SearchMethod, SearchResult
from .statements import StatementSource, StatementType, create_statement
from .timeline import Timeline, TimelineEvent


class StoreError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _safe_case_id(case_id: str) -> str:
    if not case_id or case_id in {".", ".."} or "/" in case_id or "\\" in case_id:
        raise StoreError("MD_STORE_CASE_ID", "unsafe case id")
    return case_id


def _statement_to_dict(statement: Any) -> dict[str, object]:
    return {
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


def _timeline_to_dict(timeline: Timeline | None) -> dict[str, object] | None:
    if timeline is None:
        return None
    return {
        "last_supported_interaction_id": timeline.last_supported_interaction_id,
        "first_noticed_missing_id": timeline.first_noticed_missing_id,
        "events": [
            {
                "id": event.id,
                "label": event.label,
                "statement_ids": list(event.statement_ids),
                "event_time": event.event_time,
                "time_precision": event.time_precision,
            }
            for event in timeline.events
        ],
        "unknown_intervals": list(timeline.unknown_intervals),
        "contradictions": list(timeline.contradictions),
    }


def _check_to_dict(check: SearchCheck) -> dict[str, object]:
    return {
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


def _candidate_to_dict(candidate: CandidateCheck) -> dict[str, object]:
    return {
        "id": candidate.id,
        "target": candidate.target,
        "route_relation": candidate.route_relation.value,
        "check_state": candidate.check_state.value,
        "effort": candidate.effort.value,
        "safety": candidate.safety.value,
        "urgency_relevance": candidate.urgency_relevance.value,
        "basis": candidate.basis.value,
        "based_on": list(candidate.based_on),
        "rationale": list(candidate.rationale),
    }


def _next_action_to_dict(action: NextAction | None) -> dict[str, object] | None:
    if action is None:
        return None
    return {
        "candidate_id": action.candidate_id,
        "target": action.target,
        "rationale_codes": list(action.rationale_codes),
    }


def case_to_dict(case: Case) -> dict[str, object]:
    return {
        "schema": CASE_SCHEMA,
        "case_id": case.case_id,
        "item_label": case.item_label,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "lifecycle": case.lifecycle.value,
        "statements": [_statement_to_dict(item) for item in case.statements],
        "timeline": _timeline_to_dict(case.timeline),
        "search_checks": [_check_to_dict(item) for item in case.search_checks],
        "candidates": [_candidate_to_dict(item) for item in case.candidates],
        "next_action": _next_action_to_dict(case.next_action),
        "constraints": list(case.constraints),
        "outcome": case.outcome,
    }


def _as_dict(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise StoreError("MD_STORE_SCHEMA_INVALID", f"{field} must be an object")
    return value


def _as_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise StoreError("MD_STORE_SCHEMA_INVALID", f"{field} must be an array")
    return value


def _tuple_str(value: object, field: str) -> tuple[str, ...]:
    items = _as_list(value, field)
    if not all(isinstance(item, str) for item in items):
        raise StoreError("MD_STORE_SCHEMA_INVALID", f"{field} must contain strings")
    return tuple(items)


def _required_str(data: dict[str, object], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str):
        raise StoreError("MD_STORE_SCHEMA_INVALID", f"{field} must be a string")
    return value


def case_from_dict(data: dict[str, object]) -> Case:
    try:
        validate_case_payload(data)
    except SchemaError as exc:
        raise StoreError(exc.code, str(exc)) from exc

    statements = []
    for raw in _as_list(data["statements"], "statements"):
        item = _as_dict(raw, "statement")
        statements.append(
            create_statement(
                statement_id=_required_str(item, "id"),
                source=StatementSource(_required_str(item, "source")),
                statement_type=StatementType(_required_str(item, "statement_type")),
                original_text=_required_str(item, "original_text"),
                recorded_at=_required_str(item, "recorded_at"),
                event_time=item.get("event_time") if isinstance(item.get("event_time"), str) else None,
                user_confirmation=bool(item.get("user_confirmation", False)),
                supporting_evidence_ids=_tuple_str(
                    item.get("supporting_evidence_ids", []), "supporting_evidence_ids"
                ),
                limitations=_tuple_str(item.get("limitations", []), "limitations"),
            )
        )

    timeline_raw = data["timeline"]
    timeline: Timeline | None = None
    if timeline_raw is not None:
        item = _as_dict(timeline_raw, "timeline")
        events = []
        for raw_event in _as_list(item.get("events", []), "events"):
            event = _as_dict(raw_event, "event")
            event_time = event.get("event_time")
            events.append(
                TimelineEvent(
                    id=_required_str(event, "id"),
                    label=_required_str(event, "label"),
                    statement_ids=_tuple_str(event.get("statement_ids", []), "statement_ids"),
                    event_time=event_time if isinstance(event_time, str) else None,
                    time_precision=_required_str(event, "time_precision"),
                )
            )
        last_id = item.get("last_supported_interaction_id")
        missing_id = item.get("first_noticed_missing_id")
        timeline = Timeline(
            last_supported_interaction_id=last_id if isinstance(last_id, str) else None,
            first_noticed_missing_id=missing_id if isinstance(missing_id, str) else None,
            events=tuple(events),
            unknown_intervals=_tuple_str(item.get("unknown_intervals", []), "unknown_intervals"),
            contradictions=_tuple_str(item.get("contradictions", []), "contradictions"),
        )

    checks = []
    for raw in _as_list(data["search_checks"], "search_checks"):
        item = _as_dict(raw, "search_check")
        completed_at = item.get("completed_at")
        checks.append(
            SearchCheck(
                id=_required_str(item, "id"),
                target=_required_str(item, "target"),
                method=SearchMethod(_required_str(item, "method")),
                started_at=_required_str(item, "started_at"),
                completed_at=completed_at if isinstance(completed_at, str) else None,
                result=SearchResult(_required_str(item, "result")),
                inaccessible_parts=_tuple_str(item.get("inaccessible_parts", []), "inaccessible_parts"),
                based_on=_tuple_str(item.get("based_on", []), "based_on"),
                notes=_tuple_str(item.get("notes", []), "notes"),
            )
        )

    candidates = []
    for raw in _as_list(data["candidates"], "candidates"):
        item = _as_dict(raw, "candidate")
        candidates.append(
            CandidateCheck(
                id=_required_str(item, "id"),
                target=_required_str(item, "target"),
                route_relation=RouteRelation(_required_str(item, "route_relation")),
                check_state=CheckState(_required_str(item, "check_state")),
                effort=Effort(_required_str(item, "effort")),
                safety=Safety(_required_str(item, "safety")),
                urgency_relevance=UrgencyRelevance(_required_str(item, "urgency_relevance")),
                basis=CandidateBasis(_required_str(item, "basis")),
                based_on=_tuple_str(item.get("based_on", []), "based_on"),
                rationale=_tuple_str(item.get("rationale", []), "rationale"),
            )
        )

    next_action_raw = data["next_action"]
    next_action = None
    if next_action_raw is not None:
        item = _as_dict(next_action_raw, "next_action")
        next_action = NextAction(
            candidate_id=_required_str(item, "candidate_id"),
            target=_required_str(item, "target"),
            rationale_codes=_tuple_str(item.get("rationale_codes", []), "rationale_codes"),
        )

    outcome = data["outcome"]
    if outcome is not None and not isinstance(outcome, dict):
        raise StoreError("MD_STORE_SCHEMA_INVALID", "outcome must be an object or null")

    try:
        lifecycle = CaseLifecycle(_required_str(data, "lifecycle"))
    except ValueError as exc:
        raise StoreError("MD_STORE_SCHEMA_INVALID", "invalid lifecycle") from exc

    return Case(
        schema=CASE_SCHEMA,
        case_id=_required_str(data, "case_id"),
        item_label=_required_str(data, "item_label"),
        created_at=_required_str(data, "created_at"),
        updated_at=_required_str(data, "updated_at"),
        lifecycle=lifecycle,
        statements=tuple(statements),
        timeline=timeline,
        search_checks=tuple(checks),
        candidates=tuple(candidates),
        next_action=next_action,
        constraints=_tuple_str(data["constraints"], "constraints"),
        outcome=outcome,
    )


def _case_path(case_id: str, root: Path) -> Path:
    safe_id = _safe_case_id(case_id)
    return root / ".mind-detective" / "cases" / safe_id / "case.json"


def save_case(case: Case, root: Path) -> Path:
    path = _case_path(case.case_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("case.json.tmp")
    payload = json.dumps(case_to_dict(case), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    return path


def load_case(case_id: str, root: Path) -> Case:
    path = _case_path(case_id, root)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StoreError("MD_STORE_NOT_FOUND", f"case not found: {case_id}") from exc
    except json.JSONDecodeError as exc:
        raise StoreError("MD_STORE_JSON", "case file contains invalid JSON") from exc
    if not isinstance(raw, dict):
        raise StoreError("MD_STORE_SCHEMA_INVALID", "case payload must be an object")
    return case_from_dict(raw)


def delete_case(case_id: str, root: Path) -> bool:
    path = _case_path(case_id, root)
    case_dir = path.parent
    if not case_dir.exists():
        return False
    shutil.rmtree(case_dir)
    return True
