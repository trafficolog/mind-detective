"""Deterministic R1 guided-clarification comparator for research only.

This module is deliberately outside the production portable Case kernel. It accepts
precomputed, approved clarification opportunities and returns either one neutral
question proposal or a stable stop decision. It performs no Case mutation and has
no provider/network dependency.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence, Set
from typing import Any

R1_SCHEMA = "mind-detective-reconstruction-r1/v1"
GENERATOR_KIND = "r1_deterministic"
SUPPORTED_LANGUAGES = ("ru", "en")

REASON_PRIORITY = (
    "timeline_gap",
    "temporal_order",
    "ambiguous_location",
    "ambiguous_action",
    "source_provenance",
    "contradiction",
    "object_interaction",
    "transition_between_places",
    "last_supported_interaction",
    "first_noticed_missing",
)

MAX_SHOWN_QUESTIONS = 5
MAX_CONSECUTIVE_SKIPS = 2

QUESTION_TEMPLATES: dict[str, dict[str, str]] = {
    "timeline_gap": {
        "ru": "Что вы помните о промежутке между этими событиями?",
        "en": "What do you remember about the interval between these events?",
    },
    "temporal_order": {
        "ru": "В каком порядке, насколько вы помните, происходили эти события?",
        "en": "What order do you remember these events occurring in?",
    },
    "ambiguous_location": {
        "ru": "Какое именно место вы имели в виду в этом фрагменте?",
        "en": "Which place did you mean in this part of the account?",
    },
    "ambiguous_action": {
        "ru": "Какое именно действие вы имели в виду в этом фрагменте?",
        "en": "Which action did you mean in this part of the account?",
    },
    "source_provenance": {
        "ru": "Это относится к тому, что вы помните в этом случае, к обычной привычке, к наблюдению или к неопределённости?",
        "en": "Is this something you remember in this case, a usual habit, an observation, or something you are unsure about?",
    },
    "contradiction": {
        "ru": "Эти утверждения расходятся. Что из этого вы действительно помните, если можете уточнить?",
        "en": "These statements conflict. What, if anything, do you actually remember well enough to clarify?",
    },
    "object_interaction": {
        "ru": "Что вы помните о взаимодействии с потерянной вещью в этот момент?",
        "en": "What do you remember about interacting with the lost item at this point?",
    },
    "transition_between_places": {
        "ru": "Что вы помните о переходе между уже отмеченными событиями или местами?",
        "en": "What do you remember about the transition between the already recorded events or places?",
    },
    "last_supported_interaction": {
        "ru": "Какое из уже описанных взаимодействий с вещью вы помните последним?",
        "en": "Which of the already described interactions with the item do you remember as the last one?",
    },
    "first_noticed_missing": {
        "ru": "Когда в уже описанной последовательности вы впервые заметили отсутствие вещи?",
        "en": "When in the already described sequence did you first notice the item was missing?",
    },
}


def _validate_language(language_code: str) -> None:
    if language_code not in SUPPORTED_LANGUAGES:
        raise ValueError(f"unsupported R1 language: {language_code}")


def _validate_reason(reason_code: str) -> None:
    if reason_code not in REASON_PRIORITY:
        raise ValueError(f"unsupported R1 reason code: {reason_code}")


def _validated_target_ids(target_ids: Sequence[str]) -> list[str]:
    result = list(target_ids)
    if not result or any(not isinstance(target_id, str) or not target_id for target_id in result):
        raise ValueError("R1 target_ids must contain at least one non-empty string")
    return result


def build_proposal(*, language_code: str, reason_code: str, target_ids: Sequence[str]) -> dict[str, object]:
    """Build one neutral deterministic question proposal for an approved target."""

    _validate_language(language_code)
    _validate_reason(reason_code)
    validated_target_ids = _validated_target_ids(target_ids)
    return {
        "question": QUESTION_TEMPLATES[reason_code][language_code],
        "reason_code": reason_code,
        "target_ids": validated_target_ids,
    }


def _validated_opportunities(opportunities: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    validated: list[dict[str, object]] = []
    for opportunity in opportunities:
        target_id = opportunity.get("target_id")
        reason_code = opportunity.get("reason_code")
        target_ids = opportunity.get("target_ids")
        if not isinstance(target_id, str) or not target_id:
            raise ValueError("R1 opportunity target_id must be a non-empty string")
        if not isinstance(reason_code, str):
            raise ValueError("R1 opportunity reason_code must be a string")
        _validate_reason(reason_code)
        if not isinstance(target_ids, Sequence) or isinstance(target_ids, (str, bytes)):
            raise ValueError("R1 opportunity target_ids must be a sequence of strings")
        validated.append(
            {
                "target_id": target_id,
                "reason_code": reason_code,
                "target_ids": _validated_target_ids(target_ids),
            }
        )
    return validated


def _stop(stop_reason: str) -> dict[str, object]:
    return {
        "kind": "stop",
        "generator_kind": GENERATOR_KIND,
        "stop_reason": stop_reason,
    }


def next_clarification(
    *,
    language_code: str,
    opportunities: Iterable[Mapping[str, Any]],
    completed_opportunity_ids: Set[str] | None = None,
    shown_question_count: int = 0,
    consecutive_skip_count: int = 0,
    user_continue_without_more: bool = False,
    reconstruction_ready: bool = False,
    session_terminal: bool = False,
) -> dict[str, object]:
    """Select the next R1 question or return a deterministic stop decision.

    Opportunity selection is independent of input order: reason taxonomy order is
    the primary key and opportunity id is the tie-breaker. Caller-owned inputs are
    only read and are never mutated.
    """

    _validate_language(language_code)
    if shown_question_count < 0 or consecutive_skip_count < 0:
        raise ValueError("R1 counters must be non-negative")

    validated = _validated_opportunities(opportunities)
    completed = set(completed_opportunity_ids or ())

    if session_terminal:
        return _stop("session_terminal")
    if reconstruction_ready:
        return _stop("reconstruction_ready")
    if user_continue_without_more:
        return _stop("user_continue_without_more")
    if shown_question_count >= MAX_SHOWN_QUESTIONS:
        return _stop("max_questions_reached")
    if consecutive_skip_count >= MAX_CONSECUTIVE_SKIPS:
        return _stop("consecutive_skips")

    eligible = [item for item in validated if item["target_id"] not in completed]
    if not eligible:
        return _stop("no_eligible_clarification")

    priority = {reason_code: index for index, reason_code in enumerate(REASON_PRIORITY)}
    selected = min(
        eligible,
        key=lambda item: (priority[str(item["reason_code"])], str(item["target_id"])),
    )
    proposal = build_proposal(
        language_code=language_code,
        reason_code=str(selected["reason_code"]),
        target_ids=selected["target_ids"],  # type: ignore[arg-type]
    )
    return {
        "kind": "question",
        "generator_kind": GENERATOR_KIND,
        "opportunity_id": selected["target_id"],
        "proposal": proposal,
    }
