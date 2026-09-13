"""Minimized provider-context builder for R2 reconstruction research."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypedDict

CONTEXT_SCHEMA = "mind-detective-reconstruction-r2-context/v1"
MAX_EXCERPT_CHARS = 240

_SUPPORTED_LANGUAGES = ("ru", "en")
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
_VISIBLE_CONTEXT_KEYS = {
    "language_code",
    "supported_entities",
    "supported_locations",
    "supported_actions",
    "timeline_refs",
    "statement_refs",
    "unknown_markers",
    "contradiction_refs",
}


class ContextValidationError(ValueError):
    """Raised when staged source context cannot be minimized safely."""


class ProviderTarget(TypedDict):
    ref_id: str
    ref_kind: str
    excerpt: str
    source: str


class ProviderContext(TypedDict):
    context_schema: str
    language_code: str
    reason_code: str
    targets: list[ProviderTarget]
    unknown_refs: list[str]
    contradiction_refs: list[str]


class ContextAudit(TypedDict):
    context_schema: str
    target_count: int
    unknown_ref_count: int
    contradiction_ref_count: int
    excerpt_char_count: int


def _string_list(value: object, *, field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ContextValidationError(f"{field} must be a sequence of strings")
    values = list(value)
    if any(not isinstance(item, str) or not item for item in values):
        raise ContextValidationError(f"{field} must contain non-empty strings")
    return values


def _unique_strings(value: Sequence[str] | None, *, field: str) -> list[str]:
    if value is None:
        return []
    values = list(value)
    if any(not isinstance(item, str) or not item for item in values):
        raise ContextValidationError(f"{field} must contain non-empty strings")
    if len(set(values)) != len(values):
        raise ContextValidationError(f"{field} must not contain duplicates")
    return values


def _validated_visible_context(
    model_visible_context: Mapping[str, object],
    *,
    language_code: str,
) -> dict[str, list[str]]:
    if set(model_visible_context) != _VISIBLE_CONTEXT_KEYS:
        raise ContextValidationError("model_visible_context has an unexpected field set")
    if model_visible_context.get("language_code") != language_code:
        raise ContextValidationError("context language does not match request language")

    return {
        "supported_entities": _string_list(
            model_visible_context.get("supported_entities"), field="supported_entities"
        ),
        "supported_locations": _string_list(
            model_visible_context.get("supported_locations"), field="supported_locations"
        ),
        "supported_actions": _string_list(
            model_visible_context.get("supported_actions"), field="supported_actions"
        ),
        "timeline_refs": _string_list(
            model_visible_context.get("timeline_refs"), field="timeline_refs"
        ),
        "statement_refs": _string_list(
            model_visible_context.get("statement_refs"), field="statement_refs"
        ),
        "unknown_markers": _string_list(
            model_visible_context.get("unknown_markers"), field="unknown_markers"
        ),
        "contradiction_refs": _string_list(
            model_visible_context.get("contradiction_refs"), field="contradiction_refs"
        ),
    }


def build_provider_context(
    *,
    language_code: str,
    reason_code: str,
    target_ids: Sequence[str],
    model_visible_context: Mapping[str, object],
    excerpts: Mapping[str, str],
    related_unknown_ids: Sequence[str] | None = None,
    related_contradiction_ids: Sequence[str] | None = None,
) -> ProviderContext:
    """Build the exact minimized payload eligible for a future research provider call."""

    if language_code not in _SUPPORTED_LANGUAGES:
        raise ContextValidationError("unsupported language")
    if reason_code not in _REASON_CODES:
        raise ContextValidationError("unsupported clarification reason")

    visible = _validated_visible_context(
        model_visible_context,
        language_code=language_code,
    )
    targets = _unique_strings(target_ids, field="target_ids")
    if not targets:
        raise ContextValidationError("target_ids must not be empty")

    timeline_refs = set(visible["timeline_refs"])
    statement_refs = set(visible["statement_refs"])
    textual_refs = timeline_refs | statement_refs
    if not set(targets).issubset(textual_refs):
        raise ContextValidationError("targets must be visible timeline or statement refs")

    if set(excerpts) != set(targets):
        raise ContextValidationError("excerpts must match target_ids exactly")

    provider_targets: list[ProviderTarget] = []
    for ref_id in targets:
        excerpt = excerpts.get(ref_id)
        if not isinstance(excerpt, str) or not excerpt.strip():
            raise ContextValidationError("target excerpts must be non-empty strings")
        excerpt = excerpt.strip()
        if len(excerpt) > MAX_EXCERPT_CHARS:
            raise ContextValidationError("target excerpt exceeds the frozen bound")
        provider_targets.append(
            {
                "ref_id": ref_id,
                "ref_kind": "timeline" if ref_id in timeline_refs else "statement",
                "excerpt": excerpt,
                "source": "user_confirmed",
            }
        )

    unknown_refs = _unique_strings(related_unknown_ids, field="related_unknown_ids")
    contradiction_refs = _unique_strings(
        related_contradiction_ids,
        field="related_contradiction_ids",
    )
    if not set(unknown_refs).issubset(set(visible["unknown_markers"])):
        raise ContextValidationError("unknown refs must remain inside visible scope")
    if not set(contradiction_refs).issubset(set(visible["contradiction_refs"])):
        raise ContextValidationError("contradiction refs must remain inside visible scope")

    return {
        "context_schema": CONTEXT_SCHEMA,
        "language_code": language_code,
        "reason_code": reason_code,
        "targets": provider_targets,
        "unknown_refs": unknown_refs,
        "contradiction_refs": contradiction_refs,
    }


def context_audit(context: ProviderContext) -> ContextAudit:
    """Return content-free local audit metadata for a minimized context payload."""

    targets = context["targets"]
    return {
        "context_schema": context["context_schema"],
        "target_count": len(targets),
        "unknown_ref_count": len(context["unknown_refs"]),
        "contradiction_ref_count": len(context["contradiction_refs"]),
        "excerpt_char_count": sum(len(target["excerpt"]) for target in targets),
    }
