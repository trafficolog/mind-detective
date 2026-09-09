from __future__ import annotations

from .case import Case, CaseLifecycle
from .statements import StatementSource
from .store import case_to_dict

HANDOFF_SCHEMA = "mind-detective-handoff/v1"
OUTCOME_SCHEMA = "mind-detective-outcome/v1"


class ArtifactError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def build_handoff(case: Case) -> dict[str, object]:
    canonical = case_to_dict(case)
    timeline = canonical["timeline"]
    return {
        "schema": HANDOFF_SCHEMA,
        "case_id": case.case_id,
        "item_label": case.item_label,
        "lifecycle": case.lifecycle.value,
        "statements": canonical["statements"],
        "timeline": timeline,
        "search_history": canonical["search_checks"],
        "next_action": canonical["next_action"],
        "constraints": canonical["constraints"],
        "limitations": [
            "Derived handoff artifact; the canonical Case remains the source of truth.",
            "Statement provenance and uncertainty are preserved without promotion.",
        ],
    }


def _outcome_status(case: Case, raw: dict[str, object]) -> str:
    if case.lifecycle is CaseLifecycle.CLOSED_FOUND:
        return "found"
    if case.lifecycle is CaseLifecycle.CLOSED_UNRESOLVED:
        requested = raw.get("status")
        if requested is None:
            return "unresolved"
        if requested not in {"unresolved", "abandoned"}:
            raise ArtifactError("MD_OUTCOME_STATUS", "invalid unresolved outcome status")
        return str(requested)
    raise ArtifactError("MD_OUTCOME_CASE_OPEN", "outcome requires a closed case")


def build_outcome(case: Case) -> dict[str, object]:
    if case.lifecycle not in {CaseLifecycle.CLOSED_FOUND, CaseLifecycle.CLOSED_UNRESOLVED}:
        raise ArtifactError("MD_OUTCOME_CASE_OPEN", "outcome requires a closed case")

    raw = case.outcome or {}
    cause_id = raw.get("possible_cause_statement_id")
    if cause_id is not None:
        if not isinstance(cause_id, str):
            raise ArtifactError("MD_OUTCOME_CAUSE_ID", "possible cause statement id must be a string")
        statement = next((item for item in case.statements if item.id == cause_id), None)
        if statement is None:
            raise ArtifactError("MD_OUTCOME_CAUSE_MISSING", "possible cause statement not found")
        if statement.source is not StatementSource.USER:
            raise ArtifactError(
                "MD_OUTCOME_CAUSE_NOT_USER",
                "possible cause must reference a user-authored statement",
            )

    preceding_id = raw.get("preceding_search_check_id")
    if preceding_id is not None and not isinstance(preceding_id, str):
        raise ArtifactError("MD_OUTCOME_CHECK_ID", "preceding search check id must be a string")

    return {
        "schema": OUTCOME_SCHEMA,
        "case_id": case.case_id,
        "status": _outcome_status(case, raw),
        "user_reported_found_location": raw.get("user_reported_found_location"),
        "preceding_search_check_id": preceding_id,
        "possible_cause_statement_id": cause_id,
        "prevention_note": raw.get("prevention_note"),
        "retention_decision": raw.get("retention_decision"),
        "limitations": [
            "Possible cause is user-authored context, not a diagnosed forgetting mechanism.",
        ],
    }
