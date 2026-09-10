from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

_REQUIREMENT_RE = re.compile(r"MD-REQ-[A-Z]+-\d{2}")
_ACTIVE_FIELDS = ("skill", "helper", "test", "reference")


def collect_requirement_ids(path: Path) -> tuple[set[str], set[str]]:
    matches = _REQUIREMENT_RE.findall(path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in matches:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return seen, duplicates


def selector_exists(root: Path, selector: str) -> bool:
    try:
        path_text, member = selector.split("::", 1)
        class_name, method_name = member.split(".", 1)
    except ValueError:
        return False
    path = root / path_text
    if not path.is_file():
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return any(isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method_name for child in node.body)
    return False


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_contract_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    requirement_ids, requirement_duplicates = collect_requirement_ids(root / "docs/REQUIREMENTS.md")
    for item in sorted(requirement_duplicates):
        errors.append(f"MD_CONTRACT_REQUIREMENT_DUPLICATE:{item}")
    try:
        matrix = _load_json_object(root / "docs/CONTRACT_MATRIX.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return errors + [f"MD_CONTRACT_JSON:{exc.__class__.__name__}"]
    if matrix.get("schema_version") != 2:
        errors.append("MD_CONTRACT_SCHEMA_VERSION")
    entries = matrix.get("entries")
    if not isinstance(entries, list):
        return errors + ["MD_CONTRACT_ENTRIES"]
    matrix_ids: list[str] = []
    for raw in entries:
        if not isinstance(raw, dict):
            errors.append("MD_CONTRACT_ENTRY_OBJECT")
            continue
        requirement_id = raw.get("requirement_id")
        if not isinstance(requirement_id, str):
            errors.append("MD_CONTRACT_ID_MISSING")
            continue
        matrix_ids.append(requirement_id)
        if requirement_id not in requirement_ids:
            errors.append(f"MD_CONTRACT_UNKNOWN_REQUIREMENT:{requirement_id}")
        status = raw.get("status")
        if status == "active":
            for field in _ACTIVE_FIELDS:
                value = raw.get(field)
                if not isinstance(value, str) or not value:
                    errors.append(f"MD_CONTRACT_ACTIVE_FIELD:{requirement_id}:{field}")
            for field in ("skill", "helper", "reference"):
                value = raw.get(field)
                if isinstance(value, str) and not (root / value).is_file():
                    errors.append(f"MD_CONTRACT_PATH:{requirement_id}:{field}")
            test_selector = raw.get("test")
            if isinstance(test_selector, str) and not selector_exists(root, test_selector):
                errors.append(f"MD_CONTRACT_SELECTOR:{requirement_id}:{test_selector}")
        elif status == "planned":
            if not isinstance(raw.get("planned_task"), int):
                errors.append(f"MD_CONTRACT_PLANNED_TASK:{requirement_id}")
            if not isinstance(raw.get("reason"), str) or not raw.get("reason"):
                errors.append(f"MD_CONTRACT_PLANNED_REASON:{requirement_id}")
            if any(field in raw for field in _ACTIVE_FIELDS):
                errors.append(f"MD_CONTRACT_PLANNED_ACTIVE_FIELDS:{requirement_id}")
        else:
            errors.append(f"MD_CONTRACT_STATUS:{requirement_id}:{status}")
    duplicates = {item for item in matrix_ids if matrix_ids.count(item) > 1}
    for item in sorted(duplicates):
        errors.append(f"MD_CONTRACT_MATRIX_DUPLICATE:{item}")
    for item in sorted(requirement_ids - set(matrix_ids)):
        errors.append(f"MD_CONTRACT_MISSING:{item}")
    for item in sorted(set(matrix_ids) - requirement_ids):
        errors.append(f"MD_CONTRACT_EXTRA:{item}")
    return errors


def validate_eval_data(data: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 2:
        errors.append("MD_EVAL_SCHEMA_VERSION")
    known_tokens = set(registry.get("tokens", []))
    known_outcomes = set(registry.get("outcomes", []))
    known_routes = set(registry.get("routes", []))
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        return errors + ["MD_EVAL_SCENARIOS"]
    ids: list[str] = []
    for raw in scenarios:
        if not isinstance(raw, dict):
            errors.append("MD_EVAL_SCENARIO_OBJECT")
            continue
        scenario_id = raw.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append("MD_EVAL_ID_MISSING")
            continue
        ids.append(scenario_id)
        route = raw.get("must_route_to")
        if route is None:
            errors.append(f"MD_EVAL_ROUTE_MISSING:{scenario_id}")
        elif route not in known_routes:
            errors.append(f"MD_EVAL_ROUTE_UNKNOWN:{route}")
        outcome = raw.get("outcome")
        if outcome not in known_outcomes:
            errors.append(f"MD_EVAL_OUTCOME:{outcome}")
        tokens = raw.get("must_mention_tokens")
        if not isinstance(tokens, list):
            errors.append(f"MD_EVAL_TOKENS:{scenario_id}")
        else:
            for token in tokens:
                if token not in known_tokens:
                    errors.append(f"MD_EVAL_UNKNOWN_TOKEN:{token}")
        for field in ("must_convey", "must_not_claim"):
            values = raw.get(field)
            if not isinstance(values, list) or not values or not all(isinstance(item, str) for item in values):
                errors.append(f"MD_EVAL_SEMANTIC_FIELD:{scenario_id}:{field}")
    duplicates = {item for item in ids if ids.count(item) > 1}
    for item in sorted(duplicates):
        errors.append(f"MD_EVAL_DUPLICATE_ID:{item}")
    return errors


def validate_eval_files(root: Path) -> list[str]:
    try:
        registry = _load_json_object(root / "docs/EVAL_TOKEN_REGISTRY.json")
        data = _load_json_object(root / "plugins/mind-detective/evals/scenarios.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"MD_EVAL_JSON:{exc.__class__.__name__}"]
    return validate_eval_data(data, registry)
