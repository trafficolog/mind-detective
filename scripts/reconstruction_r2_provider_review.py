"""Fail-closed provider privacy review helpers for R2 reconstruction research."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypedDict, cast

from scripts.reconstruction_r2_context import CONTEXT_SCHEMA
from scripts.reconstruction_r2_guard import GUARD_SCHEMA
from scripts.reconstruction_r2_screening import (
    PROPOSAL_SCHEMA_VERSION,
    ScreeningConfig,
)

PROVIDER_REVIEW_SCHEMA = "mind-detective-reconstruction-r2-provider-privacy-review/v1"
REVIEW_DOMAINS = (
    "request_retention",
    "training_secondary_use",
    "deletion_control",
    "geographic_processing",
    "credential_transport",
    "logging_observability",
)

_REVIEW_KEYS = {
    "review_schema",
    "provider_research_id",
    "provider_review_version",
    "reviewed_scope",
    "domains",
    "review_status",
}
_SCOPE_KEYS = {
    "purpose",
    "context_schema_version",
    "credential_boundary",
    "raw_content_export",
}
_DOMAIN_KEYS = {"decision", "evidence_refs"}
_DOMAIN_DECISIONS = {"acceptable", "unknown", "blocked"}
_REVIEW_STATUSES = {"approved", "blocked", "incomplete"}


class ProviderReviewValidationError(ValueError):
    """Raised when a provider privacy review violates the frozen research contract."""


class ReviewScope(TypedDict):
    purpose: str
    context_schema_version: str
    credential_boundary: str
    raw_content_export: bool


class ReviewDomain(TypedDict):
    decision: str
    evidence_refs: list[str]


class ProviderReview(TypedDict):
    review_schema: str
    provider_research_id: str
    provider_review_version: str
    reviewed_scope: ReviewScope
    domains: dict[str, ReviewDomain]
    review_status: str


class ProviderReviewAttestation(TypedDict):
    provider_research_id: str
    provider_review_version: str
    privacy_review_approved: bool


def _nonempty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProviderReviewValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _evidence_refs(value: object, *, decision: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ProviderReviewValidationError("evidence_refs must be a sequence of strings")
    refs = list(value)
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ProviderReviewValidationError("evidence_refs must contain non-empty strings")
    normalized = [cast(str, ref).strip() for ref in refs]
    if len(set(normalized)) != len(normalized):
        raise ProviderReviewValidationError("evidence_refs must not contain duplicates")
    if decision in {"acceptable", "blocked"} and not normalized:
        raise ProviderReviewValidationError(
            "acceptable or blocked domain decisions require evidence_refs"
        )
    return normalized


def _validate_scope(value: object) -> ReviewScope:
    if not isinstance(value, Mapping) or set(value) != _SCOPE_KEYS:
        raise ProviderReviewValidationError("reviewed_scope has an unexpected field set")
    if value.get("purpose") != "offline_reconstruction_r2_screening":
        raise ProviderReviewValidationError("review purpose is outside the frozen research scope")
    if value.get("context_schema_version") != CONTEXT_SCHEMA:
        raise ProviderReviewValidationError("review context schema does not match")
    if value.get("credential_boundary") != "server_side_only":
        raise ProviderReviewValidationError("credentials must remain server-side only")
    if value.get("raw_content_export") is not False:
        raise ProviderReviewValidationError("raw content export must remain disabled")
    return {
        "purpose": "offline_reconstruction_r2_screening",
        "context_schema_version": CONTEXT_SCHEMA,
        "credential_boundary": "server_side_only",
        "raw_content_export": False,
    }


def _validate_domains(value: object) -> dict[str, ReviewDomain]:
    if not isinstance(value, Mapping) or set(value) != set(REVIEW_DOMAINS):
        raise ProviderReviewValidationError("review domains must match the frozen six-domain set")

    validated: dict[str, ReviewDomain] = {}
    for domain in REVIEW_DOMAINS:
        raw_domain = value.get(domain)
        if not isinstance(raw_domain, Mapping) or set(raw_domain) != _DOMAIN_KEYS:
            raise ProviderReviewValidationError(f"{domain} has an unexpected field set")
        decision = raw_domain.get("decision")
        if decision not in _DOMAIN_DECISIONS:
            raise ProviderReviewValidationError(f"{domain} has an unknown decision")
        decision_value = cast(str, decision)
        validated[domain] = {
            "decision": decision_value,
            "evidence_refs": _evidence_refs(
                raw_domain.get("evidence_refs"), decision=decision_value
            ),
        }
    return validated


def validate_provider_review(review: Mapping[str, object]) -> ProviderReview:
    """Validate one provider privacy review against the frozen governance boundary."""

    if set(review) != _REVIEW_KEYS:
        raise ProviderReviewValidationError("provider review has an unexpected field set")
    if review.get("review_schema") != PROVIDER_REVIEW_SCHEMA:
        raise ProviderReviewValidationError("provider review schema does not match")

    provider_research_id = _nonempty_string(
        review.get("provider_research_id"), field="provider_research_id"
    )
    provider_review_version = _nonempty_string(
        review.get("provider_review_version"), field="provider_review_version"
    )
    scope = _validate_scope(review.get("reviewed_scope"))
    domains = _validate_domains(review.get("domains"))

    status = review.get("review_status")
    if status not in _REVIEW_STATUSES:
        raise ProviderReviewValidationError("provider review has an unknown review_status")
    status_value = status

    decisions = {entry["decision"] for entry in domains.values()}
    if status_value == "approved" and decisions != {"acceptable"}:
        raise ProviderReviewValidationError(
            "approved review requires all six domains to be acceptable"
        )
    if status_value == "blocked" and "blocked" not in decisions:
        raise ProviderReviewValidationError(
            "blocked review requires at least one blocked domain"
        )
    if status_value == "incomplete" and "unknown" not in decisions:
        raise ProviderReviewValidationError(
            "incomplete review requires at least one unknown domain"
        )

    return {
        "review_schema": PROVIDER_REVIEW_SCHEMA,
        "provider_research_id": provider_research_id,
        "provider_review_version": provider_review_version,
        "reviewed_scope": scope,
        "domains": domains,
        "review_status": status_value,
    }


def review_attestation(review: Mapping[str, object]) -> ProviderReviewAttestation:
    """Emit only the content-free provider-review fields allowed in screening metadata."""

    validated = validate_provider_review(review)
    return {
        "provider_research_id": validated["provider_research_id"],
        "provider_review_version": validated["provider_review_version"],
        "privacy_review_approved": validated["review_status"] == "approved",
    }


def screening_config_from_review(
    review: Mapping[str, object],
    *,
    model_research_id: str,
    prompt_version: str,
) -> ScreeningConfig:
    """Derive Phase 6 screening metadata from a validated provider review artifact."""

    attestation = review_attestation(review)
    return {
        "provider_research_id": attestation["provider_research_id"],
        "model_research_id": _nonempty_string(
            model_research_id, field="model_research_id"
        ),
        "prompt_version": _nonempty_string(prompt_version, field="prompt_version"),
        "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
        "context_schema_version": CONTEXT_SCHEMA,
        "guard_schema_version": GUARD_SCHEMA,
        "provider_review_version": attestation["provider_review_version"],
        "privacy_review_approved": attestation["privacy_review_approved"],
    }
