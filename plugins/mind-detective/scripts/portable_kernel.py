from __future__ import annotations

from collections.abc import Mapping

from .portable_contract import SUPPORTED_COMMAND_TYPES
from .portable_intrinsics import (
    PortableKernelError,
    clone_json,
    compare_python_strings,
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


def _primitive_copy(case: dict[str, object], now: str) -> dict[str, object]:
    _ensure_case_shape(case)
    _ensure_mutable(case)
    if not now:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "now must be a non-empty string")
    result = clone_json(case)
    result["updated_at"] = now
    return result


def set_mode_json(case: dict[str, object], mode: str, now: str) -> dict[str, object]:
    result = _primitive_copy(case, now)
    if mode not in _INTERACTION_MODES:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid interaction mode")
    result["current_mode"] = mode
    return result


def append_journal_entry_json(
    case: dict[str, object],
    entry: dict[str, object],
    now: str,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    journal = _as_list(result["interaction_journal"], "interaction_journal")
    journal.append(clone_json(entry))
    return result


def record_action_feedback_json(
    case: dict[str, object],
    feedback: dict[str, object],
    now: str,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    items = _as_list(result["action_feedback"], "action_feedback")
    items.append(clone_json(feedback))
    return result


def add_statement_json(
    case: dict[str, object],
    statement: dict[str, object],
    now: str,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    statements = _as_list(result["statements"], "statements")
    statements.append(clone_json(statement))
    return result


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
        if _required_str(candidate, "id") in based_on:
            candidate["check_state"] = state


def record_search_check_json(
    case: dict[str, object],
    check: dict[str, object],
    now: str,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    checks = _as_list(result["search_checks"], "search_checks")
    copied_check = clone_json(check)
    checks.append(copied_check)
    _apply_check_to_candidates(result, copied_check)
    return result


def refine_search_check_json(
    case: dict[str, object],
    check_id: str,
    method: str,
    inaccessible_parts: list[str],
    now: str,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    if method == "inaccessible":
        portable_error(
            "MD_SEARCH_METHOD_INVALID",
            "inaccessible is a legacy compatibility value, not a refinement method",
        )
    if method not in _SEARCH_METHODS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search method")
    checks = _as_list(result["search_checks"], "search_checks")
    found: dict[str, object] | None = None
    for raw in checks:
        check = _as_dict(raw, "search_check")
        if _required_str(check, "id") == check_id:
            check["method"] = method
            check["inaccessible_parts"] = clone_json(inaccessible_parts)
            found = check
            break
    if found is None:
        portable_error("MD_SEARCH_CHECK_NOT_FOUND", f"search check not found: {check_id}")
    _apply_check_to_candidates(result, found)
    return result


def pause_json(case: dict[str, object], now: str) -> dict[str, object]:
    result = _primitive_copy(case, now)
    if _required_str(case, "lifecycle") != "active":
        portable_error("MD_CASE_STATE", "only active cases can be paused")
    result["lifecycle"] = "paused"
    return result


def resume_json(case: dict[str, object], now: str) -> dict[str, object]:
    result = _primitive_copy(case, now)
    if _required_str(case, "lifecycle") != "paused":
        portable_error("MD_CASE_STATE", "only paused cases can be resumed")
    result["lifecycle"] = "active"
    return result


def close_found_json(
    case: dict[str, object],
    now: str,
    outcome: dict[str, object] | None = None,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    result["lifecycle"] = "closed_found"
    result["outcome"] = clone_json(outcome)
    return result


def close_unresolved_json(
    case: dict[str, object],
    now: str,
    outcome: dict[str, object] | None = None,
) -> dict[str, object]:
    result = _primitive_copy(case, now)
    result["lifecycle"] = "closed_unresolved"
    result["outcome"] = clone_json(outcome)
    return result


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
) -> dict[str, object]:
    result = clone_json(case)
    candidates = _as_list(result["candidates"], "candidates")
    normalized = _normalize_candidate_target(target)
    for raw in candidates:
        candidate = _as_dict(raw, "candidate")
        if _normalize_candidate_target(_required_str(candidate, "target")) == normalized:
            return result
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
    return result


def _web_journal_entry(
    *,
    command_id: str,
    mode: str,
    entry_type: str,
    text: str,
    now: str,
    statement_ids: list[str] | None = None,
    search_check_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": f"journal-{command_id}",
        "author": "user",
        "mode": mode,
        "entry_type": entry_type,
        "text": text,
        "created_at": now,
        "statement_ids": statement_ids or [],
        "search_check_ids": search_check_ids or [],
    }


def _statement_from_payload(payload: dict[str, object], now: str) -> dict[str, object]:
    source = _required_str(payload, "source")
    if source != "user":
        portable_error("MD_WEB_STATEMENT_SOURCE", "Web statement commands must be user-originated")
    statement_type = _required_str(payload, "statement_type")
    if statement_type not in _STATEMENT_TYPES:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid statement_type")
    return {
        "id": _required_str(payload, "statement_id"),
        "source": source,
        "statement_type": statement_type,
        "original_text": _required_str(payload, "original_text"),
        "recorded_at": now,
        "event_time": _optional_str(payload, "event_time"),
        "user_confirmation": bool(payload.get("user_confirmation", False)),
        "supporting_evidence_ids": _string_list(payload, "supporting_evidence_ids"),
        "limitations": _string_list(payload, "limitations"),
    }


def _check_from_payload(payload: dict[str, object], now: str) -> dict[str, object]:
    method = payload.get("method", "reported_check")
    if not isinstance(method, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "method must be a string")
    if method == "inaccessible":
        portable_error("MD_SEARCH_METHOD_INVALID", "inaccessible is not a Web check method")
    if method not in _SEARCH_METHODS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search method")
    search_result = payload.get("result", "not_found")
    if not isinstance(search_result, str) or search_result not in _SEARCH_RESULTS:
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid search result")
    started_at = payload.get("started_at", now)
    completed_at = payload.get("completed_at", now)
    if not isinstance(started_at, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "started_at must be a string")
    if completed_at is not None and not isinstance(completed_at, str):
        portable_error("MD_WEB_COMMAND_PAYLOAD", "completed_at must be a string or null")
    return {
        "id": _required_str(payload, "check_id"),
        "target": _required_str(payload, "target"),
        "method": method,
        "started_at": started_at,
        "completed_at": completed_at,
        "result": search_result,
        "inaccessible_parts": _string_list(payload, "inaccessible_parts"),
        "based_on": _string_list(payload, "based_on"),
        "notes": _string_list(payload, "notes"),
    }


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

    if command_type == "set_mode":
        return set_mode_json(case, _required_str(payload, "mode"), now)
    if command_type == "add_statement":
        mode = _journal_mode(case)
        statement = _statement_from_payload(payload, now)
        result = add_statement_json(case, statement, now)
        if mode == "search" and statement["statement_type"] == "search_suggestion":
            result = _append_search_candidate(
                result,
                statement_id=_required_str(statement, "id"),
                target=_required_str(statement, "original_text"),
            )
        return append_journal_entry_json(
            result,
            _web_journal_entry(
                command_id=command_id,
                mode=mode,
                entry_type="statement",
                text=_required_str(statement, "original_text"),
                now=now,
                statement_ids=[_required_str(statement, "id")],
            ),
            now,
        )
    if command_type == "record_search_check":
        mode = _journal_mode(case)
        check = _check_from_payload(payload, now)
        result = record_search_check_json(case, check, now)
        return append_journal_entry_json(
            result,
            _web_journal_entry(
                command_id=command_id,
                mode=mode,
                entry_type="search_check",
                text=_required_str(check, "target"),
                now=now,
                search_check_ids=[_required_str(check, "id")],
            ),
            now,
        )
    if command_type == "refine_search_check":
        return refine_search_check_json(
            case,
            _required_str(payload, "check_id"),
            _required_str(payload, "method"),
            _string_list(payload, "inaccessible_parts"),
            now,
        )
    if command_type == "reject_next_action":
        reason = _required_str(payload, "reason")
        if reason not in _FEEDBACK_REASONS:
            portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid action feedback reason")
        feedback: dict[str, object] = {
            "id": _required_str(payload, "feedback_id"),
            "candidate_id": _required_str(payload, "candidate_id"),
            "reason": reason,
            "recorded_at": now,
        }
        return record_action_feedback_json(case, feedback, now)
    if command_type == "pause":
        return pause_json(case, now)
    if command_type == "resume":
        return resume_json(case, now)
    if command_type == "close_found":
        return close_found_json(case, now, _outcome(payload))
    if command_type == "close_unresolved":
        return close_unresolved_json(case, now, _outcome(payload))
    portable_error("MD_WEB_COMMAND_TYPE", f"unsupported command: {command_type}")


_URGENCY_ORDER = ("high", "normal")
_BASIS_ORDER = ("episode", "habit", "generic")
_ROUTE_ORDER = ("direct", "indirect", "none")
_CHECK_STATE_ORDER = ("unchecked", "partial", "checked")
_EFFORT_ORDER = ("low", "medium", "high")


def _candidate_field(candidate: dict[str, object], field: str) -> str:
    value = _required_str(candidate, field)
    return value


def _keep_best_candidates(
    candidates: list[dict[str, object]],
    field: str,
    order: tuple[str, ...],
) -> list[dict[str, object]]:
    for preferred in order:
        matched: list[dict[str, object]] = []
        for candidate in candidates:
            if _candidate_field(candidate, field) == preferred:
                matched.append(candidate)
        if matched:
            return matched
    return candidates


def select_next_action_json(candidates: list[object]) -> dict[str, object] | None:
    pool: list[dict[str, object]] = []
    for raw in candidates:
        candidate = _as_dict(raw, "candidate")
        if _candidate_field(candidate, "safety") != "unsafe":
            pool.append(candidate)
    if not pool:
        return None

    pool = _keep_best_candidates(pool, "urgency_relevance", _URGENCY_ORDER)
    pool = _keep_best_candidates(pool, "basis", _BASIS_ORDER)
    pool = _keep_best_candidates(pool, "route_relation", _ROUTE_ORDER)
    pool = _keep_best_candidates(pool, "check_state", _CHECK_STATE_ORDER)
    pool = _keep_best_candidates(pool, "effort", _EFFORT_ORDER)

    chosen = pool[0]
    for candidate in pool[1:]:
        if compare_python_strings(
            _candidate_field(candidate, "id"),
            _candidate_field(chosen, "id"),
        ) < 0:
            chosen = candidate

    urgency = _candidate_field(chosen, "urgency_relevance")
    basis = _candidate_field(chosen, "basis")
    route = _candidate_field(chosen, "route_relation")
    check_state = _candidate_field(chosen, "check_state")
    effort = _candidate_field(chosen, "effort")
    safety = _candidate_field(chosen, "safety")
    codes: list[str] = []
    if urgency == "high":
        codes.append("MD_PLAN_URGENT")
    codes.append(f"MD_PLAN_BASIS_{basis.upper()}")
    codes.append(f"MD_PLAN_{route.upper()}_ROUTE")
    codes.append(f"MD_PLAN_{check_state.upper()}")
    codes.append(f"MD_PLAN_{effort.upper()}_EFFORT")
    if safety == "caution":
        codes.append("MD_PLAN_CAUTION")

    return {
        "candidate_id": _candidate_field(chosen, "id"),
        "target": _candidate_field(chosen, "target"),
        "rationale_codes": codes,
    }


def _proposal(
    kind: str,
    copy_key: str,
    *,
    candidate_id: str | None = None,
    target: str | None = None,
    rationale_codes: list[str] | None = None,
    related_statement_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "kind": kind,
        "candidate_id": candidate_id,
        "target": target,
        "copy_key": copy_key,
        "rationale_codes": rationale_codes or [],
        "related_statement_ids": related_statement_ids or [],
    }


def build_checklist_proposal_json(case: dict[str, object], mode: str) -> dict[str, object]:
    _ensure_case_shape(case)
    if mode == "reconstruction":
        statements = _as_list(case["statements"], "statements")
        related: list[str] = []
        for raw in statements[-3:]:
            statement = _as_dict(raw, "statement")
            related.append(_required_str(statement, "id"))
        return _proposal(
            "clarification",
            "reconstruction.clarify_supported_sequence",
            related_statement_ids=related,
        )
    if mode != "search":
        portable_error("MD_WEB_COMMAND_PAYLOAD", "invalid proposal mode")

    rejected: set[str] = set()
    for raw in _as_list(case["action_feedback"], "action_feedback"):
        feedback = _as_dict(raw, "action_feedback")
        rejected.add(_required_str(feedback, "candidate_id"))
    available: list[object] = []
    for raw in _as_list(case["candidates"], "candidates"):
        candidate = _as_dict(raw, "candidate")
        if _required_str(candidate, "id") not in rejected:
            available.append(candidate)
    action = select_next_action_json(available)
    if action is not None:
        rationale = _as_list(action["rationale_codes"], "rationale_codes")
        rationale_codes: list[str] = []
        for value in rationale:
            if not isinstance(value, str):
                portable_error("MD_WEB_COMMAND_PAYLOAD", "rationale code must be a string")
            rationale_codes.append(value)
        return _proposal(
            "next_action",
            "next_action.check_target",
            candidate_id=_required_str(action, "candidate_id"),
            target=_required_str(action, "target"),
            rationale_codes=rationale_codes,
        )

    checks = _as_list(case["search_checks"], "search_checks")
    for raw in checks[::-1]:
        check = _as_dict(raw, "search_check")
        result = _required_str(check, "result")
        inaccessible = _as_list(check.get("inaccessible_parts", []), "inaccessible_parts")
        if result in {"partial", "inaccessible"} or inaccessible:
            return _proposal(
                "clarification",
                "empty.resolve_partial_check",
                target=_required_str(check, "target"),
            )

    return _proposal("need_more_information", "empty.add_supported_place_or_reconstruct")


__all__ = [
    "PortableKernelError",
    "add_statement_json",
    "append_journal_entry_json",
    "apply_command",
    "build_checklist_proposal_json",
    "close_found_json",
    "close_unresolved_json",
    "create_case",
    "pause_json",
    "record_action_feedback_json",
    "record_search_check_json",
    "refine_search_check_json",
    "resume_json",
    "select_next_action_json",
    "set_mode_json",
]
