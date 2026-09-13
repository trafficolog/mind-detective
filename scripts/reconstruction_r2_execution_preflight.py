"""Fail-closed execution preflight helpers for R2 reconstruction research."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypedDict, cast

from scripts.reconstruction_r2_context import CONTEXT_SCHEMA
from scripts.reconstruction_r2_guard import GUARD_SCHEMA
from scripts.reconstruction_r2_provider_review import (
    ProviderReviewValidationError,
    screening_config_from_review,
    validate_provider_review,
)
from scripts.reconstruction_r2_screening import (
    PROPOSAL_SCHEMA_VERSION,
    ScreeningConfig,
)

EXECUTION_PREFLIGHT_SCHEMA = (
    "mind-detective-reconstruction-r2-execution-preflight/v1"
)
PREFLIGHT_CHECKS = (
    "profile_entitlement_verified",
    "model_endpoint_supported",
    "prohibited_features_disabled",
    "server_side_credentials_verified",
    "synthetic_corpus_only",
    "minimized_context_only",
    "frozen_versions_match",
    "raw_telemetry_disabled",
    "policy_evidence_current",
)

_PREFLIGHT_KEYS = {
    "preflight_schema",
    "provider_research_id",
    "provider_review_version",
    "model_research_id",
    "prompt_version",
    "proposal_schema_version",
    "context_schema_version",
    "guard_schema_version",
    "corpus_id",
    "checks",
    "preflight_status",
}
_CHECK_KEYS = {"status", "evidence_refs"}
_CHECK_STATUSES = {"pass", "fail", "unknown"}
_PREFLIGHT_STATUSES = {"ready", "blocked", "incomplete"}


class ExecutionPreflightValidationError(ValueError):
    """Raised when execution preflight input violates the frozen research boundary."""


class PreflightCheck(TypedDict):
    status: str
    evidence_refs: list[str]


class ExecutionPreflight(TypedDict):
    preflight_schema: str
    provider_research_id: str
    provider_review_version: str
    model_research_id: str
    prompt_version: str
    proposal_schema_version: str
    context_schema_version: str
    guard_schema_version: str
    corpus_id: str
    checks: dict[str, PreflightCheck]
    preflight_status: str


class PreflightAttestation(TypedDict):
    provider_research_id: str
    provider_review_version: str
    model_research_id: str
    prompt_version: str
    corpus_id: str
    preflight_status: str
    preflight_ready: bool


def _nonempty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExecutionPreflightValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _evidence_refs(value: object, *, status: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ExecutionPreflightValidationError(
            "evidence_refs must be a sequence of strings"
        )
    refs = list(value)
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ExecutionPreflightValidationError(
            "evidence_refs must contain non-empty strings"
        )
    normalized = [cast(str, ref).strip() for ref in refs]
    if len(set(normalized)) != len(normalized):
        raise ExecutionPreflightValidationError(
            "evidence_refs must not contain duplicates"
        )
    if status in {"pass", "fail"} and not normalized:
        raise ExecutionPreflightValidationError(
            "pass or fail preflight checks require evidence_refs"
        )
    return normalized


def _validate_checks(value: object) -> tuple[dict[str, PreflightCheck], str]:
    if not isinstance(value, Mapping) or set(value) != set(PREFLIGHT_CHECKS):
        raise ExecutionPreflightValidationError(
            "preflight checks must match the frozen exact check set"
        )

    validated: dict[str, PreflightCheck] = {}
    statuses: set[str] = set()
    for check_name in PREFLIGHT_CHECKS:
        raw_check = value.get(check_name)
        if not isinstance(raw_check, Mapping) or set(raw_check) != _CHECK_KEYS:
            raise ExecutionPreflightValidationError(
                f"{check_name} has an unexpected field set"
            )
        status = raw_check.get("status")
        if not isinstance(status, str) or status not in _CHECK_STATUSES:
            raise ExecutionPreflightValidationError(
                f"{check_name} has an unknown status"
            )
        validated[check_name] = {
            "status": status,
            "evidence_refs": _evidence_refs(
                raw_check.get("evidence_refs"), status=status
            ),
        }
        statuses.add(status)

    if "fail" in statuses:
        derived_status = "blocked"
    elif "unknown" in statuses:
        derived_status = "incomplete"
    else:
        derived_status = "ready"
    return validated, derived_status


def validate_execution_preflight(
    review: Mapping[str, object],
    preflight: Mapping[str, object],
) -> ExecutionPreflight:
    """Validate content-free execution preconditions against one approved review."""

    try:
        validated_review = validate_provider_review(review)
    except ProviderReviewValidationError as exc:
        raise ExecutionPreflightValidationError(
            "provider review is invalid for execution preflight"
        ) from exc

    if validated_review["review_status"] != "approved":
        raise ExecutionPreflightValidationError(
            "execution preflight requires an approved provider privacy review"
        )

    if set(preflight) != _PREFLIGHT_KEYS:
        raise ExecutionPreflightValidationError(
            "execution preflight has an unexpected field set"
        )
    if preflight.get("preflight_schema") != EXECUTION_PREFLIGHT_SCHEMA:
        raise ExecutionPreflightValidationError(
            "execution preflight schema does not match"
        )

    provider_research_id = _nonempty_string(
        preflight.get("provider_research_id"), field="provider_research_id"
    )
    provider_review_version = _nonempty_string(
        preflight.get("provider_review_version"), field="provider_review_version"
    )
    model_research_id = _nonempty_string(
        preflight.get("model_research_id"), field="model_research_id"
    )
    prompt_version = _nonempty_string(
        preflight.get("prompt_version"), field="prompt_version"
    )
    corpus_id = _nonempty_string(preflight.get("corpus_id"), field="corpus_id")

    if provider_research_id != validated_review["provider_research_id"]:
        raise ExecutionPreflightValidationError(
            "provider_research_id does not match the reviewed provider profile"
        )
    if provider_review_version != validated_review["provider_review_version"]:
        raise ExecutionPreflightValidationError(
            "provider_review_version does not match the reviewed provider profile"
        )

    expected_config = screening_config_from_review(
        validated_review,
        model_research_id=model_research_id,
        prompt_version=prompt_version,
    )
    if expected_config["privacy_review_approved"] is not True:
        raise ExecutionPreflightValidationError(
            "provider review cannot derive an approved screening config"
        )

    frozen_fields = {
        "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
        "context_schema_version": CONTEXT_SCHEMA,
        "guard_schema_version": GUARD_SCHEMA,
    }
    for field, expected_value in frozen_fields.items():
        if preflight.get(field) != expected_value:
            raise ExecutionPreflightValidationError(
                f"{field} does not match the frozen screening contract"
            )

    checks, derived_status = _validate_checks(preflight.get("checks"))
    status = preflight.get("preflight_status")
    if not isinstance(status, str) or status not in _PREFLIGHT_STATUSES:
        raise ExecutionPreflightValidationError(
            "execution preflight has an unknown preflight_status"
        )
    if status != derived_status:
        raise ExecutionPreflightValidationError(
            "preflight_status does not match deterministic check outcomes"
        )

    return {
        "preflight_schema": EXECUTION_PREFLIGHT_SCHEMA,
        "provider_research_id": provider_research_id,
        "provider_review_version": provider_review_version,
        "model_research_id": model_research_id,
        "prompt_version": prompt_version,
        "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
        "context_schema_version": CONTEXT_SCHEMA,
        "guard_schema_version": GUARD_SCHEMA,
        "corpus_id": corpus_id,
        "checks": checks,
        "preflight_status": status,
    }


def preflight_attestation(
    review: Mapping[str, object],
    preflight: Mapping[str, object],
) -> PreflightAttestation:
    """Emit only content-free preflight metadata; this is not execution authorization."""

    validated = validate_execution_preflight(review, preflight)
    return {
        "provider_research_id": validated["provider_research_id"],
        "provider_review_version": validated["provider_review_version"],
        "model_research_id": validated["model_research_id"],
        "prompt_version": validated["prompt_version"],
        "corpus_id": validated["corpus_id"],
        "preflight_status": validated["preflight_status"],
        "preflight_ready": validated["preflight_status"] == "ready",
    }


def screening_config_from_preflight(
    review: Mapping[str, object],
    preflight: Mapping[str, object],
) -> ScreeningConfig:
    """Re-derive screening metadata only after a ready preflight; performs no I/O."""

    validated = validate_execution_preflight(review, preflight)
    if validated["preflight_status"] != "ready":
        raise ExecutionPreflightValidationError(
            "screening config requires a ready execution preflight"
        )
    return screening_config_from_review(
        review,
        model_research_id=validated["model_research_id"],
        prompt_version=validated["prompt_version"],
    )
