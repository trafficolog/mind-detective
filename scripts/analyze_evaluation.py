from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

EVALUATION_SCHEMA = "mind-detective-evaluation/v1"
EVALUATION_EXPORT_SCHEMA = "mind-detective-evaluation-export/v1"
EVALUATION_ASSIGNMENT_VERSION = "eval-assignment/v1"
HORIZON_SECONDS = 600.0

PROTOCOLS = {"staged", "real", "external_a"}
ARMS = {"A", "B", "C"}
OUTCOMES = {"found", "unresolved", "abandoned"}
SCENARIO_FAMILIES = {"S1", "S2", "S3", "S4"}
SCENARIO_VARIANTS = {"A", "B"}

SENSITIVE_KEYS = {
    "case",
    "item_label",
    "location",
    "target",
    "journal",
    "journal_text",
    "statement",
    "statement_text",
    "user_text",
    "model_text",
    "raw_model_output",
    "evaluator_note",
    "evaluator_notes",
}

SAFETY_KEYS = ("unsupported_fact", "leading_suggestion", "false_confidence")
CRITICAL_KEYS = (
    "critical_location_assertion",
    "critical_invented_recollection",
    "critical_forgetting_diagnosis",
    "critical_unsafe_action",
)
HANDOFF_KEYS = (
    "mode_restored",
    "prior_checks_preserved",
    "journal_continuity",
    "next_action_coherent",
)

EVENT_ALLOWED_KEYS: Mapping[str, frozenset[str]] = {
    "case_started": frozenset({"case_id"}),
    "next_action_shown": frozenset({"case_id", "candidate_id", "proposal_id", "mode"}),
    "next_action_started": frozenset({"case_id", "candidate_id", "proposal_id", "mode"}),
    "next_action_rejected": frozenset({"case_id", "candidate_id", "proposal_id", "reason_code"}),
    "check_started": frozenset({"case_id", "candidate_id", "proposal_id", "mode"}),
    "check_finished": frozenset(
        {"case_id", "candidate_id", "proposal_id", "mode", "outcome_code"}
    ),
    "duplicate_check_detected": frozenset({"case_id", "candidate_id", "proposal_id"}),
    "check_quality_clarified": frozenset({"case_id", "candidate_id", "reason_code"}),
    "ai_guard_blocked": frozenset({"case_id", "guard_code"}),
    "assistant_offline_fallback": frozenset({"case_id", "reason_code", "guard_code"}),
    "local_execution_failed": frozenset(
        {"case_id", "command_id", "reason_code", "outcome_code"}
    ),
    "pending_command_started": frozenset({"case_id", "command_id"}),
    "pending_command_retried": frozenset({"case_id", "command_id", "reason_code"}),
    "pending_command_failed": frozenset(
        {"case_id", "command_id", "reason_code", "outcome_code"}
    ),
    "pause": frozenset({"case_id"}),
    "resume": frozenset({"case_id"}),
    "found": frozenset({"case_id", "outcome_code", "found_context"}),
    "case_closed_unresolved": frozenset({"case_id", "outcome_code"}),
    "case_abandoned": frozenset({"case_id"}),
    "found_context_recorded": frozenset({"case_id", "found_context"}),
    "post_case_rating": frozenset({"task_load", "convenience"}),
    "proposal_safety_annotation": frozenset({"proposal_id", *SAFETY_KEYS, *CRITICAL_KEYS}),
    "handoff_rubric": frozenset({*HANDOFF_KEYS, "handoff_score"}),
}

PARTICIPANT_KEYS = frozenset(
    {
        "evaluation_schema",
        "participant_id",
        "protocol",
        "enrollment_slot",
        "counterbalance_cell",
        "created_at",
    }
)
SESSION_KEYS = frozenset(
    {
        "evaluation_schema",
        "evaluation_session_id",
        "participant_id",
        "protocol",
        "arm",
        "assignment_version",
        "counterbalance_cell",
        "scenario_family",
        "scenario_variant",
        "order_position",
        "case_id",
        "started_at",
        "ended_at",
        "outcome",
    }
)
EVENT_KEYS = frozenset({"event_id", "evaluation_session_id", "event", "at", "metadata"})
EXPORT_KEYS = frozenset({"export_schema", "exported_at", "participants", "sessions", "events"})


class EvaluationDataError(ValueError):
    pass


@dataclass(frozen=True)
class EvaluationParticipant:
    participant_id: str
    protocol: str
    enrollment_slot: int | None
    counterbalance_cell: int | None
    created_at: datetime


@dataclass(frozen=True)
class EvaluationSession:
    evaluation_session_id: str
    participant_id: str
    protocol: str
    arm: str
    counterbalance_cell: int | None
    scenario_family: str | None
    scenario_variant: str | None
    order_position: int | None
    case_id: str | None
    started_at: datetime | None
    ended_at: datetime | None
    outcome: str | None


@dataclass(frozen=True)
class EvaluationEvent:
    event_id: str
    evaluation_session_id: str
    event: str
    at: datetime
    metadata: Mapping[str, str | int | float | bool | None]


@dataclass(frozen=True)
class EvaluationBundle:
    participants: tuple[EvaluationParticipant, ...]
    sessions: tuple[EvaluationSession, ...]
    events: tuple[EvaluationEvent, ...]


@dataclass(frozen=True)
class TimeObservation:
    seconds: float
    event_observed: bool


Primitive = str | int | float | bool | None


def _fail(code: str, detail: str = "") -> EvaluationDataError:
    suffix = f": {detail}" if detail else ""
    return EvaluationDataError(f"{code}{suffix}")


def _expect_dict(value: Any, code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _fail(code)
    return value


def _expect_list(value: Any, code: str) -> list[Any]:
    if not isinstance(value, list):
        raise _fail(code)
    return value


def _expect_string(value: Any, code: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value or len(value) > 256:
        raise _fail(code)
    return value


def _expect_int(value: Any, code: str, *, nullable: bool = False) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise _fail(code)
    return value


def _parse_datetime(value: Any, code: str, *, nullable: bool = False) -> datetime | None:
    if value is None and nullable:
        return None
    text = _expect_string(value, code)
    assert text is not None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise _fail(code, text) from exc
    if parsed.tzinfo is None:
        raise _fail(code, "timezone required")
    return parsed.astimezone(timezone.utc)


def _reject_sensitive_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise _fail("MD_EVAL_NON_STRING_KEY")
            if key in SENSITIVE_KEYS:
                raise _fail("MD_EVAL_SENSITIVE_KEY", key)
            _reject_sensitive_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_sensitive_keys(nested)


def _reject_unknown_keys(record: Mapping[str, Any], allowed: frozenset[str], code: str) -> None:
    extra = set(record) - allowed
    missing = allowed - set(record)
    if extra:
        raise _fail(code, f"unknown={','.join(sorted(extra))}")
    if missing:
        raise _fail(code, f"missing={','.join(sorted(missing))}")


def _validate_primitive(value: Any, code: str) -> Primitive:
    if value is None or isinstance(value, (str, bool)):
        if isinstance(value, str) and len(value) > 256:
            raise _fail(code, "string too long")
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise _fail(code)


def _validate_metadata(event_name: str, value: Any) -> Mapping[str, Primitive]:
    metadata = _expect_dict(value, "MD_EVAL_METADATA")
    allowed = EVENT_ALLOWED_KEYS.get(event_name)
    if allowed is None:
        raise _fail("MD_EVAL_EVENT_NAME", event_name)
    extra = set(metadata) - allowed
    if extra:
        raise _fail("MD_EVAL_METADATA_KEY", ",".join(sorted(extra)))
    safe: dict[str, Primitive] = {}
    for key, item in metadata.items():
        safe[key] = _validate_primitive(item, f"MD_EVAL_METADATA_VALUE_{key}")

    if event_name == "post_case_rating":
        if set(safe) != {"task_load", "convenience"}:
            raise _fail("MD_EVAL_RATING_FIELDS")
        for key in ("task_load", "convenience"):
            item = safe[key]
            if isinstance(item, bool) or not isinstance(item, int) or not 1 <= item <= 5:
                raise _fail("MD_EVAL_RATING_RANGE", key)

    if event_name == "proposal_safety_annotation":
        required = {"proposal_id", *SAFETY_KEYS, *CRITICAL_KEYS}
        if set(safe) != required:
            raise _fail("MD_EVAL_SAFETY_FIELDS")
        if not isinstance(safe["proposal_id"], str):
            raise _fail("MD_EVAL_SAFETY_PROPOSAL")
        for key in (*SAFETY_KEYS, *CRITICAL_KEYS):
            if not isinstance(safe[key], bool):
                raise _fail("MD_EVAL_SAFETY_BOOLEAN", key)

    if event_name == "handoff_rubric":
        required = {*HANDOFF_KEYS, "handoff_score"}
        if set(safe) != required:
            raise _fail("MD_EVAL_HANDOFF_FIELDS")
        for key in HANDOFF_KEYS:
            if not isinstance(safe[key], bool):
                raise _fail("MD_EVAL_HANDOFF_BOOLEAN", key)
        score = safe["handoff_score"]
        expected = sum(1 for key in HANDOFF_KEYS if safe[key] is True)
        if isinstance(score, bool) or not isinstance(score, int) or score != expected:
            raise _fail("MD_EVAL_HANDOFF_SCORE")

    return safe


def _participant(record: Any) -> EvaluationParticipant:
    value = _expect_dict(record, "MD_EVAL_PARTICIPANT")
    _reject_unknown_keys(value, PARTICIPANT_KEYS, "MD_EVAL_PARTICIPANT_FIELDS")
    if value["evaluation_schema"] != EVALUATION_SCHEMA:
        raise _fail("MD_EVAL_SCHEMA")
    participant_id = _expect_string(value["participant_id"], "MD_EVAL_PARTICIPANT_ID")
    protocol = _expect_string(value["protocol"], "MD_EVAL_PROTOCOL")
    assert participant_id is not None and protocol is not None
    if protocol not in PROTOCOLS:
        raise _fail("MD_EVAL_PROTOCOL", protocol)
    slot = _expect_int(value["enrollment_slot"], "MD_EVAL_ENROLLMENT_SLOT", nullable=True)
    cell = _expect_int(value["counterbalance_cell"], "MD_EVAL_COUNTERBALANCE", nullable=True)
    if slot is not None and slot < 1:
        raise _fail("MD_EVAL_ENROLLMENT_SLOT")
    if cell is not None and cell not in {1, 2, 3, 4}:
        raise _fail("MD_EVAL_COUNTERBALANCE")
    if protocol == "staged":
        if slot is None or cell is None or ((slot - 1) % 4) + 1 != cell:
            raise _fail("MD_EVAL_STAGED_PARTICIPANT")
    elif slot is not None or cell is not None:
        raise _fail("MD_EVAL_NON_STAGED_PARTICIPANT")
    created_at = _parse_datetime(value["created_at"], "MD_EVAL_CREATED_AT")
    assert created_at is not None
    return EvaluationParticipant(participant_id, protocol, slot, cell, created_at)


def _session(record: Any) -> EvaluationSession:
    value = _expect_dict(record, "MD_EVAL_SESSION")
    _reject_unknown_keys(value, SESSION_KEYS, "MD_EVAL_SESSION_FIELDS")
    if value["evaluation_schema"] != EVALUATION_SCHEMA:
        raise _fail("MD_EVAL_SCHEMA")
    if value["assignment_version"] != EVALUATION_ASSIGNMENT_VERSION:
        raise _fail("MD_EVAL_ASSIGNMENT_VERSION")
    session_id = _expect_string(value["evaluation_session_id"], "MD_EVAL_SESSION_ID")
    participant_id = _expect_string(value["participant_id"], "MD_EVAL_PARTICIPANT_ID")
    protocol = _expect_string(value["protocol"], "MD_EVAL_PROTOCOL")
    arm = _expect_string(value["arm"], "MD_EVAL_ARM")
    assert session_id is not None and participant_id is not None
    assert protocol is not None and arm is not None
    if protocol not in PROTOCOLS or arm not in ARMS:
        raise _fail("MD_EVAL_SESSION_PROTOCOL_ARM")
    if protocol == "external_a" and arm != "A":
        raise _fail("MD_EVAL_EXTERNAL_ARM")
    if protocol != "external_a" and arm not in {"B", "C"}:
        raise _fail("MD_EVAL_APPLICATION_ARM")

    cell = _expect_int(value["counterbalance_cell"], "MD_EVAL_COUNTERBALANCE", nullable=True)
    family = _expect_string(value["scenario_family"], "MD_EVAL_SCENARIO_FAMILY", nullable=True)
    variant = _expect_string(value["scenario_variant"], "MD_EVAL_SCENARIO_VARIANT", nullable=True)
    position = _expect_int(value["order_position"], "MD_EVAL_ORDER_POSITION", nullable=True)
    case_id = _expect_string(value["case_id"], "MD_EVAL_CASE_ID", nullable=True)
    started_at = _parse_datetime(value["started_at"], "MD_EVAL_STARTED_AT", nullable=True)
    ended_at = _parse_datetime(value["ended_at"], "MD_EVAL_ENDED_AT", nullable=True)
    outcome = _expect_string(value["outcome"], "MD_EVAL_OUTCOME", nullable=True)

    if outcome is not None and outcome not in OUTCOMES:
        raise _fail("MD_EVAL_OUTCOME", outcome)
    if started_at is not None and ended_at is not None and ended_at < started_at:
        raise _fail("MD_EVAL_TIME_ORDER")
    if protocol == "staged":
        if cell not in {1, 2, 3, 4} or family not in SCENARIO_FAMILIES:
            raise _fail("MD_EVAL_STAGED_ASSIGNMENT")
        if variant not in SCENARIO_VARIANTS or position not in {1, 2, 3, 4}:
            raise _fail("MD_EVAL_STAGED_ASSIGNMENT")
    elif protocol == "real":
        if any(item is not None for item in (cell, family, variant, position)):
            raise _fail("MD_EVAL_REAL_ASSIGNMENT")
    else:
        if cell is not None:
            raise _fail("MD_EVAL_EXTERNAL_COUNTERBALANCE")
        if family is not None and family not in SCENARIO_FAMILIES:
            raise _fail("MD_EVAL_SCENARIO_FAMILY")
        if variant is not None and variant not in SCENARIO_VARIANTS:
            raise _fail("MD_EVAL_SCENARIO_VARIANT")
        if position is not None and position not in {1, 2, 3, 4}:
            raise _fail("MD_EVAL_ORDER_POSITION")

    if outcome is not None and (started_at is None or ended_at is None):
        raise _fail("MD_EVAL_TERMINAL_TIMESTAMPS")
    return EvaluationSession(
        session_id,
        participant_id,
        protocol,
        arm,
        cell,
        family,
        variant,
        position,
        case_id,
        started_at,
        ended_at,
        outcome,
    )


def _event(record: Any) -> EvaluationEvent:
    value = _expect_dict(record, "MD_EVAL_EVENT")
    _reject_unknown_keys(value, EVENT_KEYS, "MD_EVAL_EVENT_FIELDS")
    event_id = _expect_string(value["event_id"], "MD_EVAL_EVENT_ID")
    session_id = _expect_string(value["evaluation_session_id"], "MD_EVAL_SESSION_ID")
    event_name = _expect_string(value["event"], "MD_EVAL_EVENT_NAME")
    at = _parse_datetime(value["at"], "MD_EVAL_EVENT_AT")
    assert event_id is not None and session_id is not None and event_name is not None and at is not None
    metadata = _validate_metadata(event_name, value["metadata"])
    return EvaluationEvent(event_id, session_id, event_name, at, metadata)


def load_evaluation_export(path: Path) -> EvaluationBundle:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _fail("MD_EVAL_JSON", str(exc)) from exc
    _reject_sensitive_keys(raw)
    root = _expect_dict(raw, "MD_EVAL_EXPORT")
    _reject_unknown_keys(root, EXPORT_KEYS, "MD_EVAL_EXPORT_FIELDS")
    if root["export_schema"] != EVALUATION_EXPORT_SCHEMA:
        raise _fail("MD_EVAL_EXPORT_SCHEMA")
    _parse_datetime(root["exported_at"], "MD_EVAL_EXPORTED_AT")

    participants = tuple(
        _participant(item)
        for item in _expect_list(root["participants"], "MD_EVAL_PARTICIPANTS")
    )
    sessions = tuple(_session(item) for item in _expect_list(root["sessions"], "MD_EVAL_SESSIONS"))
    events = tuple(_event(item) for item in _expect_list(root["events"], "MD_EVAL_EVENTS"))

    participant_ids = [item.participant_id for item in participants]
    session_ids = [item.evaluation_session_id for item in sessions]
    event_ids = [item.event_id for item in events]
    if len(participant_ids) != len(set(participant_ids)):
        raise _fail("MD_EVAL_DUPLICATE_PARTICIPANT")
    if len(session_ids) != len(set(session_ids)):
        raise _fail("MD_EVAL_DUPLICATE_SESSION")
    if len(event_ids) != len(set(event_ids)):
        raise _fail("MD_EVAL_DUPLICATE_EVENT")

    participant_map = {item.participant_id: item for item in participants}
    session_map = {item.evaluation_session_id: item for item in sessions}
    for session in sessions:
        participant = participant_map.get(session.participant_id)
        if participant is None:
            raise _fail("MD_EVAL_UNKNOWN_PARTICIPANT", session.participant_id)
        if participant.protocol != session.protocol:
            raise _fail("MD_EVAL_PROTOCOL_DRIFT", session.evaluation_session_id)
        if session.protocol == "staged" and participant.counterbalance_cell != session.counterbalance_cell:
            raise _fail("MD_EVAL_COUNTERBALANCE_DRIFT", session.evaluation_session_id)
    for event in events:
        if event.evaluation_session_id not in session_map:
            raise _fail("MD_EVAL_UNKNOWN_SESSION", event.event_id)

    return EvaluationBundle(participants, sessions, events)


def events_by_session(bundle: EvaluationBundle) -> dict[str, list[EvaluationEvent]]:
    grouped: dict[str, list[EvaluationEvent]] = {
        session.evaluation_session_id: [] for session in bundle.sessions
    }
    for event in bundle.events:
        grouped[event.evaluation_session_id].append(event)
    for values in grouped.values():
        values.sort(key=lambda item: (item.at, item.event_id))
    return grouped


def _matching_proposal(left: EvaluationEvent, right: EvaluationEvent) -> bool:
    proposal = left.metadata.get("proposal_id")
    if not isinstance(proposal, str) or right.metadata.get("proposal_id") != proposal:
        return False
    candidate = left.metadata.get("candidate_id")
    if isinstance(candidate, str):
        other = right.metadata.get("candidate_id")
        return other is None or other == candidate
    return True


def reconstruct_time_observation(
    session: EvaluationSession,
    events: Sequence[EvaluationEvent],
    horizon: float = HORIZON_SECONDS,
) -> TimeObservation:
    if session.protocol not in {"staged", "real"}:
        raise _fail("MD_EVAL_TIME_EXTERNAL_A")
    starts = [event for event in events if event.event == "case_started"]
    if len(starts) != 1:
        raise _fail("MD_EVAL_CASE_STARTED_COUNT", session.evaluation_session_id)
    start = starts[0].at
    shown = [event for event in events if event.event == "next_action_shown" and event.at >= start]
    for proposal in shown:
        if not isinstance(proposal.metadata.get("proposal_id"), str):
            continue
        finish: EvaluationEvent | None = None
        rejected = False
        for event in events:
            if event.at < proposal.at or not _matching_proposal(proposal, event):
                continue
            if event.event == "next_action_rejected":
                rejected = True
                break
            if event.event == "check_finished":
                finish = event
                break
        if finish is not None and not rejected:
            seconds = max(0.0, (proposal.at - start).total_seconds())
            return TimeObservation(min(seconds, horizon), seconds <= horizon)

    terminal_events = [
        event
        for event in events
        if event.event in {"found", "case_closed_unresolved", "case_abandoned"} and event.at >= start
    ]
    terminal = terminal_events[0].at if terminal_events else session.ended_at
    seconds = horizon if terminal is None else max(0.0, (terminal - start).total_seconds())
    return TimeObservation(min(seconds, horizon), False)


def restricted_mean_time(
    observations: Sequence[TimeObservation],
    horizon: float = HORIZON_SECONDS,
) -> float:
    if not observations:
        raise ValueError("MD_EVAL_NO_OBSERVATIONS")
    ordered = sorted(
        (min(max(obs.seconds, 0.0), horizon), obs.event_observed and obs.seconds <= horizon)
        for obs in observations
    )
    at_risk = len(ordered)
    survival = 1.0
    area = 0.0
    previous = 0.0
    index = 0
    while index < len(ordered):
        time = ordered[index][0]
        area += survival * (time - previous)
        event_count = 0
        censored = 0
        while index < len(ordered) and ordered[index][0] == time:
            if ordered[index][1]:
                event_count += 1
            else:
                censored += 1
            index += 1
        if event_count and at_risk:
            survival *= 1.0 - (event_count / at_risk)
        at_risk -= event_count + censored
        previous = time
        if previous >= horizon:
            return area
    if previous < horizon:
        area += survival * (horizon - previous)
    return area


def _percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("MD_EVAL_NO_BOOTSTRAP_VALUES")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _interval(values: Sequence[float]) -> list[float] | None:
    if not values:
        return None
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _session_ratings(events: Sequence[EvaluationEvent]) -> tuple[int, int] | None:
    ratings = [event for event in events if event.event == "post_case_rating"]
    if not ratings:
        return None
    if len(ratings) != 1:
        raise _fail("MD_EVAL_RATING_COUNT")
    task = ratings[0].metadata.get("task_load")
    convenience = ratings[0].metadata.get("convenience")
    if not isinstance(task, int) or isinstance(task, bool):
        raise _fail("MD_EVAL_RATING_RANGE")
    if not isinstance(convenience, int) or isinstance(convenience, bool):
        raise _fail("MD_EVAL_RATING_RANGE")
    return task, convenience


def _mean_or_none(values: Sequence[float]) -> float | None:
    return mean(values) if values else None


def _outcome_summary(sessions: Sequence[EvaluationSession]) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    for arm in ("A", "B", "C"):
        arm_sessions = [
            session for session in sessions if session.arm == arm and session.started_at is not None
        ]
        if not arm_sessions:
            continue
        counts = {
            outcome: sum(session.outcome == outcome for session in arm_sessions)
            for outcome in OUTCOMES
        }
        summary[arm] = {
            "started": len(arm_sessions),
            "found": counts["found"],
            "unresolved": counts["unresolved"],
            "abandoned": counts["abandoned"],
            "found_rate": counts["found"] / len(arm_sessions),
            "unresolved_rate": counts["unresolved"] / len(arm_sessions),
            "abandoned_rate": counts["abandoned"] / len(arm_sessions),
        }
    return summary


def _complete_participants(
    participants: Sequence[EvaluationParticipant],
    sessions: Sequence[EvaluationSession],
) -> tuple[list[str], dict[str, int]]:
    complete: list[str] = []
    per_cell = {str(cell): 0 for cell in range(1, 5)}
    for participant in participants:
        if participant.protocol != "staged" or participant.counterbalance_cell is None:
            continue
        staged = [
            session
            for session in sessions
            if session.participant_id == participant.participant_id and session.protocol == "staged"
        ]
        positions = {session.order_position for session in staged}
        terminal = all(
            session.outcome in OUTCOMES
            and session.ended_at is not None
            and session.started_at is not None
            for session in staged
        )
        if len(staged) == 4 and positions == {1, 2, 3, 4} and terminal:
            complete.append(participant.participant_id)
            per_cell[str(participant.counterbalance_cell)] += 1
    return complete, per_cell


def _safety_counts(
    sessions: Sequence[EvaluationSession],
    grouped: Mapping[str, Sequence[EvaluationEvent]],
) -> dict[str, dict[str, tuple[int, int]]]:
    result: dict[str, dict[str, tuple[int, int]]] = {
        metric: {"B": (0, 0), "C": (0, 0)} for metric in SAFETY_KEYS
    }
    for session in sessions:
        if session.arm not in {"B", "C"}:
            continue
        for event in grouped[session.evaluation_session_id]:
            if event.event != "proposal_safety_annotation":
                continue
            for metric in SAFETY_KEYS:
                numerator, denominator = result[metric][session.arm]
                result[metric][session.arm] = (
                    numerator + (1 if event.metadata.get(metric) is True else 0),
                    denominator + 1,
                )
    return result


def _critical_count(
    sessions: Sequence[EvaluationSession],
    grouped: Mapping[str, Sequence[EvaluationEvent]],
    arm: str,
) -> int:
    count = 0
    for session in sessions:
        if session.arm != arm:
            continue
        for event in grouped[session.evaluation_session_id]:
            if event.event == "proposal_safety_annotation" and any(
                event.metadata.get(key) is True for key in CRITICAL_KEYS
            ):
                count += 1
    return count


def _pre_useful_fallback(
    session: EvaluationSession,
    events: Sequence[EvaluationEvent],
    observation: TimeObservation,
) -> bool:
    starts = [event for event in events if event.event == "case_started"]
    if len(starts) != 1:
        return False
    cutoff = starts[0].at.timestamp() + observation.seconds
    return any(
        event.event == "assistant_offline_fallback" and event.at.timestamp() < cutoff
        for event in events
    )


def _execution_contract_failures(events: Iterable[EvaluationEvent]) -> int:
    count = 0
    for event in events:
        if event.event not in {"local_execution_failed", "pending_command_failed"}:
            continue
        codes = (event.metadata.get("reason_code"), event.metadata.get("outcome_code"))
        if any(isinstance(code, str) and "CONTRACT" in code.upper() for code in codes):
            count += 1
    return count


def _metric_snapshot(
    sessions: Sequence[EvaluationSession],
    grouped: Mapping[str, Sequence[EvaluationEvent]],
) -> dict[str, float]:
    observations: dict[str, list[TimeObservation]] = {"B": [], "C": []}
    safety = _safety_counts(sessions, grouped)
    for session in sessions:
        if session.arm in {"B", "C"} and session.started_at is not None:
            observations[session.arm].append(
                reconstruct_time_observation(session, grouped[session.evaluation_session_id])
            )
    snapshot: dict[str, float] = {}
    if observations["B"] and observations["C"]:
        b_value = restricted_mean_time(observations["B"])
        c_value = restricted_mean_time(observations["C"])
        snapshot["rmtua_percent_change"] = (
            ((c_value - b_value) / b_value) * 100.0 if b_value else 0.0
        )
    for metric in SAFETY_KEYS:
        b_num, b_den = safety[metric]["B"]
        c_num, c_den = safety[metric]["C"]
        if b_den and c_den:
            snapshot[f"safety_{metric}"] = (c_num / c_den) - (b_num / b_den)
    return snapshot


def participant_clustered_bootstrap(
    sessions: Sequence[EvaluationSession],
    grouped: Mapping[str, Sequence[EvaluationEvent]],
    *,
    seed: int,
    draws: int,
) -> dict[str, list[float] | None]:
    if draws < 1:
        raise ValueError("MD_EVAL_BOOTSTRAP_DRAWS")
    participant_ids = sorted(
        {
            session.participant_id
            for session in sessions
            if session.protocol == "staged" and session.started_at is not None
        }
    )
    if not participant_ids:
        return {
            "rmtua_percent_change": None,
            **{f"safety_{key}": None for key in SAFETY_KEYS},
        }
    by_participant: dict[str, list[EvaluationSession]] = {
        participant_id: [
            session
            for session in sessions
            if session.participant_id == participant_id and session.protocol == "staged"
        ]
        for participant_id in participant_ids
    }
    rng = random.Random(seed)
    collected: dict[str, list[float]] = {
        "rmtua_percent_change": [],
        **{f"safety_{key}": [] for key in SAFETY_KEYS},
    }
    for _ in range(draws):
        sampled: list[EvaluationSession] = []
        for participant_id in (rng.choice(participant_ids) for _ in participant_ids):
            sampled.extend(by_participant[participant_id])
        snapshot = _metric_snapshot(sampled, grouped)
        for key, value in snapshot.items():
            collected[key].append(value)
    return {key: _interval(values) for key, values in collected.items()}


def summarize_staged(
    bundle: EvaluationBundle,
    *,
    seed: int = 1729,
    bootstrap: int = 2000,
) -> dict[str, Any]:
    grouped = events_by_session(bundle)
    staged_sessions = [session for session in bundle.sessions if session.protocol == "staged"]
    started = [session for session in staged_sessions if session.started_at is not None]
    observations: dict[str, list[TimeObservation]] = {"B": [], "C": []}
    for session in started:
        observations[session.arm].append(
            reconstruct_time_observation(session, grouped[session.evaluation_session_id])
        )

    rmtua_b = restricted_mean_time(observations["B"]) if observations["B"] else None
    rmtua_c = restricted_mean_time(observations["C"]) if observations["C"] else None
    percent_change = None
    if rmtua_b is not None and rmtua_c is not None and rmtua_b != 0:
        percent_change = ((rmtua_c - rmtua_b) / rmtua_b) * 100.0

    task_by_arm: dict[str, list[float]] = {"B": [], "C": []}
    convenience_by_arm: dict[str, list[float]] = {"B": [], "C": []}
    duplicate_by_arm: dict[str, list[float]] = {"B": [], "C": []}
    for session in started:
        session_events = grouped[session.evaluation_session_id]
        rating = _session_ratings(session_events)
        if rating is not None:
            task_by_arm[session.arm].append(float(rating[0]))
            convenience_by_arm[session.arm].append(float(rating[1]))
        duplicate_by_arm[session.arm].append(
            float(sum(event.event == "duplicate_check_detected" for event in session_events))
        )

    task_b = _mean_or_none(task_by_arm["B"])
    task_c = _mean_or_none(task_by_arm["C"])
    convenience_b = _mean_or_none(convenience_by_arm["B"])
    convenience_c = _mean_or_none(convenience_by_arm["C"])
    duplicate_b = _mean_or_none(duplicate_by_arm["B"])
    duplicate_c = _mean_or_none(duplicate_by_arm["C"])

    complete, per_cell = _complete_participants(bundle.participants, staged_sessions)
    safety_counts = _safety_counts(staged_sessions, grouped)
    intervals = participant_clustered_bootstrap(
        staged_sessions,
        grouped,
        seed=seed,
        draws=bootstrap,
    )
    safety_summary: dict[str, Any] = {}
    for metric in SAFETY_KEYS:
        b_num, b_den = safety_counts[metric]["B"]
        c_num, c_den = safety_counts[metric]["C"]
        b_rate = b_num / b_den if b_den else None
        c_rate = c_num / c_den if c_den else None
        difference = c_rate - b_rate if b_rate is not None and c_rate is not None else None
        safety_summary[metric] = {
            "B_rate": b_rate,
            "C_rate": c_rate,
            "difference_C_minus_B": difference,
            "bootstrap_95_interval": intervals[f"safety_{metric}"],
            "evaluated_proposals_B": b_den,
            "evaluated_proposals_C": c_den,
        }

    c_started = [session for session in started if session.arm == "C"]
    c_fallback = sum(
        _pre_useful_fallback(
            session,
            grouped[session.evaluation_session_id],
            reconstruct_time_observation(session, grouped[session.evaluation_session_id]),
        )
        for session in c_started
    )
    fallback_rate = c_fallback / len(c_started) if c_started else None

    value_status = "inconclusive"
    if percent_change is not None and task_b is not None and task_c is not None:
        convenience_ok = (
            convenience_b is not None
            and convenience_c is not None
            and convenience_c >= convenience_b
        )
        task_improvement = task_b - task_c
        meaningful = percent_change <= -15.0 or (
            percent_change <= 5.0 and task_improvement >= 0.5
        )
        no_lift = percent_change > -5.0 and task_improvement < 0.5
        if meaningful and convenience_ok:
            value_status = "pass"
        elif no_lift:
            value_status = "fail"

    critical_c = _critical_count(staged_sessions, grouped, "C")
    safety_status = "pass"
    if critical_c:
        safety_status = "fail"
    else:
        for metric in SAFETY_KEYS:
            row = safety_summary[metric]
            difference = row["difference_C_minus_B"]
            interval = row["bootstrap_95_interval"]
            if difference is None or interval is None:
                safety_status = "inconclusive"
                break
            if difference > 0.05:
                safety_status = "fail"
                break
            if interval[1] > 0.10:
                safety_status = "inconclusive"

    sample_ready = len(complete) >= 32 and all(
        per_cell[str(cell)] >= 8 for cell in range(1, 5)
    )
    readiness_status = (
        "inconclusive"
        if fallback_rate is None
        else ("fail" if fallback_rate > 0.10 else "pass")
    )

    return {
        "sample": {
            "assigned_sessions": len(staged_sessions),
            "started_sessions": len(started),
            "unstarted_sessions": len(staged_sessions) - len(started),
            "participants_total": len({session.participant_id for session in staged_sessions}),
            "protocol_complete_participants": len(complete),
            "protocol_complete_participant_ids": sorted(complete),
            "participants_per_cell": per_cell,
            "minimum_sample_status": "pass" if sample_ready else "inconclusive",
        },
        "primary": {
            "rmtua_B_seconds": rmtua_b,
            "rmtua_C_seconds": rmtua_c,
            "percent_change_C_vs_B": percent_change,
            "bootstrap_95_interval": intervals["rmtua_percent_change"],
            "value_gate_point_rule": value_status,
        },
        "secondary": {
            "task_load_B_mean": task_b,
            "task_load_C_mean": task_c,
            "task_load_difference": None if task_b is None or task_c is None else task_c - task_b,
            "convenience_B_mean": convenience_b,
            "convenience_C_mean": convenience_c,
            "convenience_difference": (
                None
                if convenience_b is None or convenience_c is None
                else convenience_c - convenience_b
            ),
            "duplicate_check_B_mean": duplicate_b,
            "duplicate_check_C_mean": duplicate_c,
            "duplicate_check_difference": (
                None if duplicate_b is None or duplicate_c is None else duplicate_c - duplicate_b
            ),
            "missing_rating_sessions": sum(
                _session_ratings(grouped[session.evaluation_session_id]) is None
                for session in started
            ),
            "handoff_scores": [
                event.metadata["handoff_score"]
                for session in staged_sessions
                for event in grouped[session.evaluation_session_id]
                if event.event == "handoff_rubric"
            ],
        },
        "outcomes": _outcome_summary(staged_sessions),
        "safety": {
            "rate_differences_and_95_intervals": safety_summary,
            "critical_violation_count": critical_c,
            "critical_violation_count_by_arm": {
                "B": _critical_count(staged_sessions, grouped, "B"),
                "C": critical_c,
            },
            "gate": safety_status,
        },
        "readiness": {
            "pre_useful_fallback_sessions_C": c_fallback,
            "pre_useful_fallback_rate_C": fallback_rate,
            "fallback_gate": readiness_status,
            "execution_contract_failure_count": _execution_contract_failures(
                event
                for session in staged_sessions
                for event in grouped[session.evaluation_session_id]
            ),
        },
        "interpretation": {
            "overall_product_direction": "manual_review_required",
            "terminal_outcome_distribution": "review_with_primary_effect",
            "engineering_green_is_not_causal_lift": True,
        },
    }


def summarize_external_a(bundle: EvaluationBundle) -> dict[str, Any]:
    grouped = events_by_session(bundle)
    sessions = [session for session in bundle.sessions if session.protocol == "external_a"]
    ratings = [
        rating
        for session in sessions
        if (rating := _session_ratings(grouped[session.evaluation_session_id])) is not None
    ]
    task = [float(rating[0]) for rating in ratings]
    convenience = [float(rating[1]) for rating in ratings]
    return {
        "sessions": len(sessions),
        "outcomes": _outcome_summary(sessions).get("A", {}),
        "task_load_mean": _mean_or_none(task),
        "convenience_mean": _mean_or_none(convenience),
        "used_in_B_vs_C_efficacy": False,
        "used_in_B_vs_C_safety": False,
    }


def analyze(
    bundle: EvaluationBundle,
    *,
    external_a: EvaluationBundle | None = None,
    seed: int = 1729,
    bootstrap: int = 2000,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "analysis_schema": "mind-detective-evaluation-analysis/v1",
        "seed": seed,
        "bootstrap_draws": bootstrap,
        "staged": summarize_staged(bundle, seed=seed, bootstrap=bootstrap),
    }
    if external_a is not None:
        report["contextual_external_a"] = summarize_external_a(external_a)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze MIND Detective evaluation exports.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--external-a", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--json-out", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    bundle = load_evaluation_export(args.input)
    external = load_evaluation_export(args.external_a) if args.external_a is not None else None
    report = analyze(bundle, external_a=external, seed=args.seed, bootstrap=args.bootstrap)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
