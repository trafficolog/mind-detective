from __future__ import annotations

import sys

from .runtime_paths import resolve_plugin_root

_PLUGIN_ROOT = resolve_plugin_root()
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from scripts.controller import CaseController  # noqa: E402
from scripts.store import case_from_dict, case_to_dict  # noqa: E402


def create_case_payload(case_id: str, item_label: str, now: str) -> dict[str, object]:
    case = CaseController().create_case(case_id, item_label, now)
    return case_to_dict(case)


def validate_or_migrate_case_payload(payload: dict[str, object]) -> dict[str, object]:
    return case_to_dict(case_from_dict(payload))
