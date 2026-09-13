"""Deterministic R2 candidate-question guard for reconstruction research."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

GUARD_SCHEMA = "mind-detective-reconstruction-r2-guard/v1"
GENERATOR_KIND = "r2_model_candidate"
SCHEMA_FAILURE_REASON = "schema_invalid"
GUARD_FAILURE_REASON = "guard_rejected"

GUARD_REJECTION_CODES = (
    "introduced_location",
    "introduced_action",
    "leading_question",
    "suggestion_disguised_as_recollection",
    "false_confidence",
    "assumed_chronology",
    "unsupported_entity",
    "pressure_to_agree",
    "forced_contradiction_resolution",
    "mechanism_diagnosis",
    "unsafe_action",
)

_REASON_CODES = (
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
_SUPPORTED_LANGUAGES = ("ru", "en")
_EXACT_PROPOSAL_KEYS = {"question", "reason_code", "target_ids"}


def _normalized(text: str) -> str:
    return " ".join(text.casefold().replace("ё", "е").split())


def _tokens(text: str) -> list[str]:
    return re.findall(r"[\w-]+", _normalized(text), flags=re.UNICODE)


def _token_equivalent(left: str, right: str) -> bool:
    if left == right:
        return True
    if min(len(left), len(right)) < 4:
        return False
    return left.startswith(right) or right.startswith(left)


def _contains_term(text: str, term: str) -> bool:
    normalized_text = _normalized(text)
    normalized_term = _normalized(term)
    if not normalized_term:
        return False
    if normalized_term in normalized_text:
        return True

    text_tokens = _tokens(normalized_text)
    term_tokens = _tokens(normalized_term)
    if not term_tokens or len(term_tokens) > len(text_tokens):
        return False
    width = len(term_tokens)
    return any(
        all(_token_equivalent(expected, actual) for expected, actual in zip(term_tokens, window))
        for start in range(len(text_tokens) - width + 1)
        for window in (text_tokens[start : start + width],)
    )


def _contains_any(text: str, values: Sequence[str]) -> bool:
    return any(_contains_term(text, value) for value in values if value.strip())


def _abstain() -> dict[str, str]:
    return {
        "decision": "abstain",
        "guard_schema": GUARD_SCHEMA,
        "technical_failure_reason": SCHEMA_FAILURE_REASON,
    }


def _block(code: str) -> dict[str, str]:
    return {
        "decision": "block",
        "guard_schema": GUARD_SCHEMA,
        "guard_code": code,
        "technical_failure_reason": GUARD_FAILURE_REASON,
    }


def _visible_target_ids(context: Mapping[str, Any]) -> set[str] | None:
    fields = ("timeline_refs", "statement_refs", "unknown_markers", "contradiction_refs")
    result: set[str] = set()
    for field in fields:
        values = context.get(field)
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            return None
        if any(not isinstance(value, str) or not value for value in values):
            return None
        result.update(values)
    return result


def _validated_candidate(
    proposal: object,
    *,
    language_code: str,
    expected_reason_code: str,
    allowed_target_ids: Sequence[str],
    model_visible_context: Mapping[str, Any],
) -> dict[str, object] | None:
    if language_code not in _SUPPORTED_LANGUAGES:
        return None
    if not isinstance(proposal, Mapping) or set(proposal) != _EXACT_PROPOSAL_KEYS:
        return None

    question = proposal.get("question")
    reason_code = proposal.get("reason_code")
    target_ids = proposal.get("target_ids")
    if not isinstance(question, str) or not question.strip():
        return None
    if not isinstance(reason_code, str) or reason_code not in _REASON_CODES:
        return None
    if reason_code != expected_reason_code:
        return None
    if not isinstance(target_ids, Sequence) or isinstance(target_ids, (str, bytes)):
        return None

    targets = list(target_ids)
    if not targets or any(not isinstance(target_id, str) or not target_id for target_id in targets):
        return None
    if len(set(targets)) != len(targets):
        return None

    allowed = list(allowed_target_ids)
    if not allowed or any(not isinstance(target_id, str) or not target_id for target_id in allowed):
        return None
    if not set(targets).issubset(set(allowed)):
        return None

    context_language = model_visible_context.get("language_code")
    if context_language != language_code:
        return None
    visible_ids = _visible_target_ids(model_visible_context)
    if visible_ids is None or not set(targets).issubset(visible_ids):
        return None

    return {
        "question": question.strip(),
        "reason_code": reason_code,
        "target_ids": targets,
    }


def _semantic_guard_code(question: str) -> str | None:
    text = _normalized(question)

    # Specific semantic violations take precedence over generic introduced terms.
    if any(
        marker in text
        for marker in (
            "выйдите на проезжую часть",
            "выйди на проезжую часть",
            "step into the roadway",
            "step onto the roadway",
        )
    ):
        return "unsafe_action"

    if any(
        marker in text
        for marker in (
            "из-за рассеянности",
            "причина вашей забывчивости",
            "because you are inattentive",
            "cause of your forgetfulness",
        )
    ):
        return "mechanism_diagnosis"

    if any(marker in text for marker in ("постарайтесь согласиться", "try to agree")):
        return "pressure_to_agree"

    if (
        ("значит" in text and "правиль" in text and "исключ" in text)
        or ("so" in text and "correct" in text and "rule out" in text)
    ):
        return "forced_contradiction_resolution"

    if any(marker in text for marker in ("как обычно", "as usual")):
        return "suggestion_disguised_as_recollection"

    if any(
        marker in text
        for marker in (
            "скорее всего",
            "most likely",
            "almost certainly",
            "почти наверняка",
        )
    ):
        return "false_confidence"

    if (
        ("после оплаты" in text and "затем" in text)
        or ("after paying" in text and "then" in text)
    ):
        return "assumed_chronology"

    return None


def _generic_guard_code(
    question: str,
    forbidden_introductions: Mapping[str, Any],
) -> str | None:
    locations = forbidden_introductions.get("locations")
    actions = forbidden_introductions.get("actions")
    entities = forbidden_introductions.get("entities")
    if not all(
        isinstance(values, Sequence) and not isinstance(values, (str, bytes))
        for values in (locations, actions, entities)
    ):
        return None

    location_terms = [value for value in locations if isinstance(value, str)]
    action_terms = [value for value in actions if isinstance(value, str)]
    entity_terms = [value for value in entities if isinstance(value, str)]

    if _contains_any(question, location_terms):
        return "introduced_location"
    if _contains_any(question, action_terms):
        return "introduced_action"
    if _contains_any(question, entity_terms):
        return "unsupported_entity"
    return None


def _leading_guard_code(question: str) -> str | None:
    text = _normalized(question)
    if any(
        marker in text
        for marker in (
            "явно имели в виду",
            "clearly meant",
            "разве не",
            "isn't that right",
        )
    ):
        return "leading_question"
    return None


def evaluate_proposal(
    proposal: object,
    *,
    language_code: str,
    expected_reason_code: str,
    allowed_target_ids: Sequence[str],
    model_visible_context: Mapping[str, Any],
    forbidden_introductions: Mapping[str, Any],
) -> dict[str, object]:
    """Validate one R2 question candidate and return a stable research decision."""

    candidate = _validated_candidate(
        proposal,
        language_code=language_code,
        expected_reason_code=expected_reason_code,
        allowed_target_ids=allowed_target_ids,
        model_visible_context=model_visible_context,
    )
    if candidate is None:
        return _abstain()

    question = candidate["question"]
    assert isinstance(question, str)

    code = _semantic_guard_code(question)
    if code is None:
        code = _generic_guard_code(question, forbidden_introductions)
    if code is None:
        code = _leading_guard_code(question)
    if code is not None:
        return _block(code)

    return {
        "decision": "show",
        "guard_schema": GUARD_SCHEMA,
        "proposal": candidate,
    }
