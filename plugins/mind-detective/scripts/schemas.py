from __future__ import annotations

from collections.abc import Mapping

LEGACY_CASE_SCHEMA = "mind-detective-case/v1"
CASE_SCHEMA = "mind-detective-case/v2"


class SchemaError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def validate_case_payload(data: Mapping[str, object]) -> None:
    if data.get("schema") != CASE_SCHEMA:
        raise SchemaError("MD_STORE_SCHEMA_VERSION", "unsupported case schema")
    required = {
        "case_id",
        "item_label",
        "created_at",
        "updated_at",
        "lifecycle",
        "statements",
        "timeline",
        "search_checks",
        "candidates",
        "next_action",
        "constraints",
        "outcome",
        "current_mode",
        "interaction_journal",
        "action_feedback",
    }
    missing = sorted(required - set(data))
    if missing:
        raise SchemaError("MD_STORE_SCHEMA_INVALID", "missing fields: " + ",".join(missing))
