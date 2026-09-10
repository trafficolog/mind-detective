from __future__ import annotations

from collections.abc import Mapping

from .portable_contract import SUPPORTED_COMMAND_TYPES
from .portable_intrinsics import (
    PortableKernelError,
    clone_json,
    portable_error,
    split_python_whitespace,
    unicode_casefold,
)

_CASE_SCHEMA = "mind-detective-case/v2"
_TERMINAL_LIFECYCLES = frozenset({"closed_found", "closed_unresolved", "deleted"})
_INTERACTION_MODES = frozenset({"unselected", "reconstruction", "search"})
_STATEMENT_TYPES = frozenset(
    {"recollection", "habit", "observation", "hypothesis", "search_suggestion"}
)
_SEARCH_METHODS = frozenset(
    {"reported_check", "glance", "visual_systematic", "empty_and_check", "tactile"}
)
_SEARCH_RESULTS = frozenset({"found", "not_found", "partial", "inaccessible"})
_FEEDBACK_REASONS = frozenset(
    {"already_checked", "impossible_now", "irrelevant", "unsafe_or_uncomfortable", "other"}
)
_FORBIDDEN_KEYS = frozenset(
    {"probability", "pod", "belief_weight", "posterior", "prior_probability"}
)
_ALLOWED_PAYLOAD_KEYS: dict[str, frozenset[str]] = {
    "set_mode": frozenset({"mode"}),
    "add_statement": frozenset(
        {
            "statement_id",
            "source",
            "statement_type",
            "original_text",
            "event_time",
            "user_confirmation",
            "supporting_evidence_ids",
            "limitations",
        }
    ),
    "record_search_check": frozenset(
        {
            "check_id",
            "target",
            "method",
            "started_at",
            "completed_at",
            "result",
            "inaccessible_parts",
            "based_on",
            "notes",
        }
    ),
    "refine_search_check": frozenset({"check_id", "method", "inaccessible_parts"}),
    "reject_next_action": frozenset({"feedback_id", "candidate_id", "reason"}),
    "pause": frozenset(),
    "resume": frozenset(),
    "close_found": frozenset({"outcome"}),
    "close_unresolved": frozenset({"outcome"}),
}


def create_case(case_id: str, item_label: str, now: str) -> dict[str, object]:
    if not case_id:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "case_id must be a non-empty string")
    if not item_label:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "item_label must be a non-empty string")
    if not now:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "now must be a non-empty string")
    return {
        "schema": _CASE_SCHEMA,
        "case_id": case_id,
        "item_label": item_label,
        "created_at": now,
        "updated_at": now,
        "lifecycle": "active",
        "statements": [],
        "timeline": None,
        "search_checks": [],
        "candidates": [],
        "next_action": None,
        "constraints": [],
        "outcome": None,
        "current_mode": "unselected",
        "interaction_journal": [],
        "action_feedback": [],
    }


def _required_str(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        portable_error("MD_WEB_COMMAND_PAYLOAD", f"{key} must be a non-empty string")
    return value


def _optional_str(data: dict[str, object], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", f"{key} must be a string or null")
    return value


def _as_dict(value: object, key: str) -> dict[str, object]:
    if not isinstance(value, dict):
        portable_error("MD_WEB_COMMAND_PAYLOAD", f"{key} must be an object")
    return value


def _as_list(value: object, key: str) -> list[object]:
    if not isinstance(value, list):
        portable_error("MD_WEB_COMMAND_PAYLOAD", f"{key} must be an array")
    return value


def _string_list(data: dict[str, object], key: str) -> list[str]:
    value = data.get(key, [])
    items = _as_list(value, key)
    result: list[str] = []
    for item in items:
        if not isinstance(item, str):
            portable_error("MD_WEB_COMMAND_PAYLOAD", f"{key} must be an array of strings")
        result.append(item)
    return result


def _outcome(data: dict[str, object]) -> dict[str, object] | None:
    value = data.get("outcome")
    if value is None:
        return None
    return clone_json(_as_dict(value, "outcome"))


def _reject_forbidden_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if unicode_casefold(str(key)) in _FORBIDDEN_KEYS:
                portable_error("MD_WEB_FORBIDDEN_FIELD", f"forbidden command field: {key}")
            _reject_forbidden_keys(nested)
        return
    if isinstance(value, list):
        for nested in value:
            _reject_forbidden_keys(nested)
        return
    if isinstance(value, float):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "floating-point values are not portable")


def _validate_payload(command_type: str, payload: dict[str, object]) -> None:
    _reject_forbidden_keys(payload)
    allowed = _ALLOWED_PAYLOAD_KEYS.get(command_type)
    if allowed is None:
        portable_error("MD_WEB_COMMAND_TYPE", f"unsupported command: {command_type}")
    unexpected = sorted(set(payload) - allowed)
    if unexpected:
        portable_error(
            "MD_WEB_COMMAND_PAYLOAD",
            "unexpected command fields: " + ",".join(unexpected),
        )


def _ensure_case_shape(case: dict[str, object]) -> None:
    if case.get("schema") != _CASE_SCHEMA:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "unsupported case schema")
    _required_str(case, "case_id")
    _required_str(case, "updated_at")
    lifecycle = _required_str(case, "lifecycle")
    if lifecycle not in {"active", "paused", "closed_found", "closed_unresolved", "deleted"}:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid lifecycle")
    current_mode = _required_str(case, "current_mode")
    if current_mode not in _INTERACTION_MODES:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid current_mode")
    _as_list(case.get("statements"), "statements")
    _as_list(case.get("search_checks"), "search_checks")
    _as_list(case.get("candidates"), "candidates")
    _as_list(case.get("constraints"), "constraints")
    _as_list(case.get("interaction_journal"), "interaction_journal")
    _as_list(case.get("action_feedback"), "action_feedback")


def _ensure_mutable(case: dict[str, object]) -> None:
    lifecycle = _required_str(case, "lifecycle")
    if lifecycle in _TERMINAL_LIFECYCLES:
        portable_error("MD_CASE_TERMINAL", f"case is terminal: {lifecycle}")


def _journal_mode(case: dict[str, object]) -> str:
    mode = _required_str(case, "current_mode")
    if mode in {"reconstruction", "search"}:
        return mode
    portable_error("MD_WEB_MODE_REQUIRED", "select an interaction mode before recording journal activity")


def _normalize_candidate_target(value: str) -> str:
    folded = unicode_casefold(value).replace("ё", "е")
    return " ".join(split_python_whitespace(folded))


def _append_search_candidate(
    case: dict[str, object],
    *,
    statement_id: str,
    target: str,
) -> None:
    candidates = _as_list(case["candidates"], "candidates")
    normalized = _normalize_candidate_target(target)
    for raw in candidates:
        candidate = _as_dict(raw, "candidate")
        existing_target = _required_str(candidate, "target")
        if _normalize_candidate_target(existing_target) == normalized:
            return
    candidates.append(
        {
            "id": f"candidate-{statement_id}",
            "target": target,
            "route_relation": "none",
            "check_state": "unchecked",
            "effort": "low",
            "safety": "caution",
            "urgency_relevance": "normal",
            "basis": "episode",
            "based_on": [statement_id],
            "rationale": ["MD_PLAN_USER_SUPPORTED"],
        }
    )


def _append_journal(
    case: dict[str, object],
    *,
    command_id: str,
    mode: str,
    entry_type: str,
    text: str,
    now: str,
    statement_ids: list[str] | None = None,
    search_check_ids: list[str] | None = None,
) -> None:
    journal = _as_list(case["interaction_journal"], "interaction_journal")
    journal.append(
        {
            "id": f"journal-{command_id}",
            "author": "user",
            "mode": mode,
            "entry_type": entry_type,
            "text": text,
            "created_at": now,
            "statement_ids": statement_ids or [],
            "search_check_ids": search_check_ids or [],
        }
    )


def _candidate_state_for_check(check: dict[str, object]) -> str:
    result = _required_str(check, "result")
    inaccessible_parts = _as_list(check.get("inaccessible_parts", []), "inaccessible_parts")
    if result in {"partial", "inaccessible"} or inaccessible_parts:
        return "partial"
    return "checked"


def _apply_check_to_candidates(case: dict[str, object], check: dict[str, object]) -> None:
    based_on = set(_string_list(check, "based_on"))
    if not based_on:
        return
    state = _candidate_state_for_check(check)
    candidates = _as_list(case["candidates"], "candidates")
    for raw in candidates:
        candidate = _as_dict(raw, "candidate")
        candidate_id = _required_str(candidate, "id")
        if candidate_id in based_on:
            candidate["check_state"] = state


def _apply_set_mode(case: dict[str, object], payload: dict[str, object]) -> None:
    mode = _required_str(payload, "mode")
    if mode not in _INTERACTION_MODES:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid interaction mode")
    case["current_mode"] = mode


def _apply_add_statement(
    case: dict[str, object],
    payload: dict[str, object],
    command_id: str,
    now: str,
) -> None:
    mode = _journal_mode(case)
    source = _required_str(payload, "source")
    if source != "user":
        portable_error("MD_WEB_STATEMENT_SOURCE", "Web statement commands must be user-originated")
    statement_type = _required_str(payload, "statement_type")
    if statement_type not in _STATEMENT_TYPES:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid statement_type")
    statement_id = _required_str(payload, "statement_id")
    original_text = _required_str(payload, "original_text")
    statement = {
        "id": statement_id,
        "source": source,
        "statement_type": statement_type,
        "original_text": original_text,
        "recorded_at": now,
        "event_time": _optional_str(payload, "event_time"),
        "user_confirmation": bool(payload.get("user_confirmation", False)),
        "supporting_evidence_ids": _string_list(payload, "supporting_evidence_ids"),
        "limitations": _string_list(payload, "limitations"),
    }
    statements = _as_list(case["statements"], "statements")
    statements.append(statement)
    if mode == "search" and statement_type == "search_suggestion":
        _append_search_candidate(case, statement_id=statement_id, target=original_text)
    _append_journal(
        case,
        command_id=command_id,
        mode=mode,
        entry_type="statement",
        text=original_text,
        now=now,
        statement_ids=[statement_id],
    )


def _apply_record_search_check(
    case: dict[str, object],
    payload: dict[str, object],
    command_id: str,
    now: str,
) -> None:
    mode = _journal_mode(case)
    method_raw = payload.get("method", "reported_check")
    if not isinstance(method_raw, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "method must be a string")
    if method_raw == "inaccessible":
        portable_error("MD_SEARCH_METHOD_INVALID", "inaccessible is not a Web check method")
    if method_raw not in _SEARCH_METHODS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search method")
    result_raw = payload.get("result", "not_found")
    if not isinstance(result_raw, str) or result_raw not in _SEARCH_RESULTS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search result")
    started_at = payload.get("started_at", now)
    completed_at = payload.get("completed_at", now)
    if not isinstance(started_at, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "started_at must be a string")
    if completed_at is not None and not isinstance(completed_at, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "completed_at must be a string or null")
    check_id = _required_str(payload, "check_id")
    target = _required_str(payload, "target")
    check: dict[str, object] = {
        "id": check_id,
        "target": target,
        "method": method_raw,
        "started_at": started_at,
        "completed_at": completed_at,
        "result": result_raw,
        "inaccessible_parts": _string_list(payload, "inaccessible_parts"),
        "based_on": _string_list(payload, "based_on"),
        "notes": _string_list(payload, "notes"),
    }
    checks = _as_list(case["search_checks"], "search_checks")
    checks.append(check)
    _apply_check_to_candidates(case, check)
    _append_journal(
        case,
        command_id=command_id,
        mode=mode,
        entry_type="search_check",
        text=target,
        now=now,
        search_check_ids=[check_id],
    )


def _apply_refine_search_check(
    case: dict[str, object],
    payload: dict[str, object],
) -> None:
    check_id = _required_str(payload, "check_id")
    method = _required_str(payload, "method")
    if method == "inaccessible":
        portable_error(
            "MD_SEARCH_METHOD_INVALID",
            "inaccessible is a legacy compatibility value, not a refinement method",
        )
    if method not in _SEARCH_METHODS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search method")
    inaccessible_parts = _string_list(payload, "inaccessible_parts")
    checks = _as_list(case["search_checks"], "search_checks")
    found: dict[str, object] | None = None
    for raw in checks:
        check = _as_dict(raw, "search_check")
        if _required_str(check, "id") == check_id:
            check["method"] = method
            check["inaccessible_parts"] = inaccessible_parts
            found = check
            break
    if found is None:
        portable_error("MD_SEARCH_CHECK_NOT_FOUND", f"search check not found: {check_id}")
    _apply_check_to_candidates(case, found)


def _apply_reject_next_action(
    case: dict[str, object],
    payload: dict[str, object],
    now: str,
) -> None:
    reason = _required_str(payload, "reason")
    if reason not in _FEEDBACK_REASONS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid action feedback reason")
    feedback = _as_list(case["action_feedback"], "action_feedback")
    feedback.append(
        {
            "id": _required_str(payload, "feedback_id"),
            "candidate_id": _required_str(payload, "candidate_id"),
            "reason": reason,
            "recorded_at": now,
        }
    )


def _apply_lifecycle(case: dict[str, object], command_type: str, payload: dict[str, object]) -> None:
    lifecycle = _required_str(case, "lifecycle")
    if command_type == "pause":
        if lifecycle != "active":
            portable_error("MD_CASE_STATE", "only active cases can be paused")
        case["lifecycle"] = "paused"
        return
    if command_type == "resume":
        if lifecycle != "paused":
            portable_error("MD_CASE_STATE", "only paused cases can be resumed")
        case["lifecycle"] = "active"
        return
    if command_type == "close_found":
        case["lifecycle"] = "closed_found"
        case["outcome"] = _outcome(payload)
        return
    if command_type == "close_unresolved":
        case["lifecycle"] = "closed_unresolved"
        case["outcome"] = _outcome(payload)
        return
    portable_error("MD_WEB_COMMAND_TYPE", f"unsupported lifecycle command: {command_type}")


def apply_command(
    case: dict[str, object],
    command: dict[str, object],
) -> dict[str, object]:
    _ensure_case_shape(case)
    command_type = _required_str(command, "command_type")
    if command_type not in SUPPORTED_COMMAND_TYPES:
        portable_error("MD_WEB_COMMAND_TYPE", f"unsupported command: {command_type}")
    expected_updated_at = _required_str(command, "expected_updated_at")
    now = _required_str(command, "now")
    command_id = _required_str(command, "command_id")
    payload = _as_dict(command.get("payload", {}), "payload")
    if _required_str(case, "updated_at") != expected_updated_at:
        portable_error("MD_WEB_STALE_COMMAND", "command was created for an older case state")
    _validate_payload(command_type, payload)
    _ensure_mutable(case)

    result = clone_json(case)
    if command_type == "set_mode":
        _apply_set_mode(result, payload)
    elif command_type == "add_statement":
        _apply_add_statement(result, payload, command_id, now)
    elif command_type == "record_search_check":
        _apply_record_search_check(result, payload, command_id, now)
    elif command_type == "refine_search_check":
        _apply_refine_search_check(result, payload)
    elif command_type == "reject_next_action":
        _apply_reject_next_action(result, payload, now)
    elif command_type in {"pause", "resume", "close_found", "close_unresolved"}:
        _apply_lifecycle(result, command_type, payload)
    else:
        portable_error("MD_WEB_COMMAND_TYPE", f"unsupported command: {command_type}")
    result["updated_at"] = now
    return result


__all__ = ["PortableKernelError", "apply_command", "create_case"]
