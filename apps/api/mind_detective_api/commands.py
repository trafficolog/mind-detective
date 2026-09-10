from __future__ import annotations

from collections.abc import Mapping

from .contracts import CommandEnvelope
from .core_bridge import validate_or_migrate_case_payload

from scripts.controller import CaseController
from scripts.feedback import ActionFeedback, ActionFeedbackReason
from scripts.journal import InteractionMode, JournalAuthor, JournalEntry, JournalMode
from scripts.search_log import SearchCheck, SearchMethod, SearchResult
from scripts.statements import StatementSource, StatementType, create_statement
from scripts.store import case_from_dict, case_to_dict


class CommandError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


_FORBIDDEN_KEYS = {"probability", "pod", "belief_weight", "posterior", "prior_probability"}

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


def _reject_forbidden_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).casefold() in _FORBIDDEN_KEYS:
                raise CommandError("MD_WEB_FORBIDDEN_FIELD", f"forbidden command field: {key}")
            _reject_forbidden_keys(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _reject_forbidden_keys(nested)


def _require_allowed_payload(envelope: CommandEnvelope) -> None:
    _reject_forbidden_keys(envelope.payload)
    allowed = _ALLOWED_PAYLOAD_KEYS[envelope.command_type]
    unexpected = sorted(set(envelope.payload) - allowed)
    if unexpected:
        raise CommandError(
            "MD_WEB_COMMAND_PAYLOAD",
            "unexpected command fields: " + ",".join(unexpected),
        )


def _required_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise CommandError("MD_WEB_COMMAND_PAYLOAD", f"{key} must be a non-empty string")
    return value


def _optional_str(payload: dict[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise CommandError("MD_WEB_COMMAND_PAYLOAD", f"{key} must be a string or null")
    return value


def _string_tuple(payload: dict[str, object], key: str) -> tuple[str, ...]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise CommandError("MD_WEB_COMMAND_PAYLOAD", f"{key} must be an array of strings")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise CommandError("MD_WEB_COMMAND_PAYLOAD", f"{key} must be an array of strings")
        result.append(item)
    return tuple(result)


def _outcome(payload: dict[str, object]) -> dict[str, object] | None:
    value = payload.get("outcome")
    if value is None:
        return None
    if not isinstance(value, dict):
        raise CommandError("MD_WEB_COMMAND_PAYLOAD", "outcome must be an object or null")
    return value


def _journal_mode(mode: InteractionMode) -> JournalMode:
    if mode is InteractionMode.RECONSTRUCTION:
        return JournalMode.RECONSTRUCTION
    if mode is InteractionMode.SEARCH:
        return JournalMode.SEARCH
    raise CommandError("MD_WEB_MODE_REQUIRED", "select an interaction mode before recording journal activity")


def _append_statement_journal(
    controller: CaseController,
    case: object,
    envelope: CommandEnvelope,
    statement_id: str,
    text: str,
) -> object:
    # `case` is deliberately kept internal to execute_command; the typed helper is
    # inlined through controller calls below so Web never supplies journal provenance.
    raise AssertionError("unreachable")


def execute_command(
    case_payload: dict[str, object],
    envelope: CommandEnvelope,
) -> dict[str, object]:
    canonical_payload = validate_or_migrate_case_payload(case_payload)
    case = case_from_dict(canonical_payload)
    if case.updated_at != envelope.expected_updated_at:
        raise CommandError(
            "MD_WEB_STALE_COMMAND",
            "command was created for an older case state",
        )
    _require_allowed_payload(envelope)

    controller = CaseController()
    payload = envelope.payload
    command_type = envelope.command_type

    if command_type == "set_mode":
        case = controller.set_mode(
            case,
            InteractionMode(_required_str(payload, "mode")),
            envelope.now,
        )
    elif command_type == "add_statement":
        mode = _journal_mode(case.current_mode)
        source = StatementSource(_required_str(payload, "source"))
        if source is not StatementSource.USER:
            raise CommandError("MD_WEB_STATEMENT_SOURCE", "Web statement commands must be user-originated")
        statement_id = _required_str(payload, "statement_id")
        original_text = _required_str(payload, "original_text")
        statement = create_statement(
            statement_id=statement_id,
            source=source,
            statement_type=StatementType(_required_str(payload, "statement_type")),
            original_text=original_text,
            recorded_at=envelope.now,
            event_time=_optional_str(payload, "event_time"),
            user_confirmation=bool(payload.get("user_confirmation", False)),
            supporting_evidence_ids=_string_tuple(payload, "supporting_evidence_ids"),
            limitations=_string_tuple(payload, "limitations"),
        )
        case = controller.add_statement(case, statement, envelope.now)
        case = controller.append_journal_entry(
            case,
            JournalEntry(
                id=f"journal-{envelope.command_id}",
                author=JournalAuthor.USER,
                mode=mode,
                entry_type="statement",
                text=original_text,
                created_at=envelope.now,
                statement_ids=(statement_id,),
            ),
            envelope.now,
        )
    elif command_type == "record_search_check":
        mode = _journal_mode(case.current_mode)
        method_raw = payload.get("method", SearchMethod.REPORTED_CHECK.value)
        if not isinstance(method_raw, str):
            raise CommandError("MD_WEB_COMMAND_PAYLOAD", "method must be a string")
        if method_raw == SearchMethod.INACCESSIBLE.value:
            raise CommandError(
                "MD_SEARCH_METHOD_INVALID",
                "inaccessible is not a Web check method",
            )
        result_raw = payload.get("result", SearchResult.NOT_FOUND.value)
        if not isinstance(result_raw, str):
            raise CommandError("MD_WEB_COMMAND_PAYLOAD", "result must be a string")
        started_at = payload.get("started_at", envelope.now)
        completed_at = payload.get("completed_at", envelope.now)
        if not isinstance(started_at, str):
            raise CommandError("MD_WEB_COMMAND_PAYLOAD", "started_at must be a string")
        if completed_at is not None and not isinstance(completed_at, str):
            raise CommandError("MD_WEB_COMMAND_PAYLOAD", "completed_at must be a string or null")
        check_id = _required_str(payload, "check_id")
        target = _required_str(payload, "target")
        check = SearchCheck(
            id=check_id,
            target=target,
            method=SearchMethod(method_raw),
            started_at=started_at,
            completed_at=completed_at,
            result=SearchResult(result_raw),
            inaccessible_parts=_string_tuple(payload, "inaccessible_parts"),
            based_on=_string_tuple(payload, "based_on"),
            notes=_string_tuple(payload, "notes"),
        )
        case = controller.record_search_check(case, check, envelope.now)
        case = controller.append_journal_entry(
            case,
            JournalEntry(
                id=f"journal-{envelope.command_id}",
                author=JournalAuthor.USER,
                mode=mode,
                entry_type="search_check",
                text=target,
                created_at=envelope.now,
                search_check_ids=(check_id,),
            ),
            envelope.now,
        )
    elif command_type == "refine_search_check":
        case = controller.refine_search_check(
            case,
            _required_str(payload, "check_id"),
            SearchMethod(_required_str(payload, "method")),
            _string_tuple(payload, "inaccessible_parts"),
            envelope.now,
        )
    elif command_type == "reject_next_action":
        feedback = ActionFeedback(
            id=_required_str(payload, "feedback_id"),
            candidate_id=_required_str(payload, "candidate_id"),
            reason=ActionFeedbackReason(_required_str(payload, "reason")),
            recorded_at=envelope.now,
        )
        case = controller.record_action_feedback(case, feedback, envelope.now)
    elif command_type == "pause":
        case = controller.pause(case, envelope.now)
    elif command_type == "resume":
        case = controller.resume(case, envelope.now)
    elif command_type == "close_found":
        case = controller.close_found(case, envelope.now, _outcome(payload))
    elif command_type == "close_unresolved":
        case = controller.close_unresolved(case, envelope.now, _outcome(payload))
    else:
        raise CommandError("MD_WEB_COMMAND_TYPE", f"unsupported command: {command_type}")

    return case_to_dict(case)
