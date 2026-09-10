from __future__ import annotations

from copy import deepcopy

from .schemas import CASE_SCHEMA, LEGACY_CASE_SCHEMA, SchemaError


def migrate_case_payload(data: dict[str, object]) -> dict[str, object]:
    migrated = deepcopy(data)
    schema = migrated.get("schema")
    if schema == CASE_SCHEMA:
        return migrated
    if schema != LEGACY_CASE_SCHEMA:
        raise SchemaError("MD_STORE_SCHEMA_VERSION", "unsupported case schema")

    migrated["schema"] = CASE_SCHEMA
    migrated["current_mode"] = "unselected"
    migrated["interaction_journal"] = []
    migrated["action_feedback"] = []
    return migrated
