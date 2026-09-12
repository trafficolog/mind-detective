from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

_REQUIREMENT_RE = re.compile(r"MD(?:-(?:WEB|OFFLINE))?-REQ-[A-Z0-9]+-\d{2}")
_ACTIVE_FIELDS = ("skill", "helper", "test", "reference")
_TS_TEST_RE = re.compile(
    r"\b(?:test|it)\s*\(\s*(['\"])(?P<title>.*?)\1",
    re.DOTALL,
)
_WEB_SOURCE_SUFFIXES = {".ts", ".tsx", ".vue"}
_SEMANTIC_REVIEW_PROTOCOL = "docs/evaluation/SEMANTIC_SCENARIO_REVIEW.md"


def collect_requirement_ids(path: Path) -> tuple[set[str], set[str]]:
    matches = _REQUIREMENT_RE.findall(path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in matches:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return seen, duplicates


def _python_selector_exists(path: Path, member: str) -> bool:
    try:
        class_name, method_name = member.split(".", 1)
    except ValueError:
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return any(
                isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and child.name == method_name
                for child in node.body
            )
    return False


def _typescript_selector_exists(path: Path, title: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return any(match.group("title") == title for match in _TS_TEST_RE.finditer(text))


def selector_exists(root: Path, selector: str) -> bool:
    try:
        path_text, member = selector.split("::", 1)
    except ValueError:
        return False
    path = root / path_text
    if not path.is_file() or not member:
        return False
    if path.suffix == ".py":
        return _python_selector_exists(path, member)
    if path.suffix in {".ts", ".tsx"}:
        return _typescript_selector_exists(path, member)
    return False


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _web_sources(root: Path) -> list[Path]:
    app_root = root / "apps/web/app"
    if not app_root.is_dir():
        return []
    return [
        path
        for path in app_root.rglob("*")
        if path.is_file() and path.suffix in _WEB_SOURCE_SUFFIXES
    ]


def _web_source_references(source: Path, target: Path, app_root: Path) -> bool:
    if source == target:
        return False
    try:
        relative = target.relative_to(app_root)
    except ValueError:
        return False
    parts = relative.parts
    if not parts:
        return False

    text = _read_text(source)
    stem = target.stem
    if parts[0] == "components":
        marker = re.compile(rf"(?:<|\b){re.escape(stem)}\b")
        return bool(marker.search(text))

    if parts[0] == "composables":
        direct_call = re.compile(rf"\b{re.escape(stem)}\s*\(")
        module_import = re.compile(rf"from\s+['\"][^'\"]*{re.escape(stem)}['\"]")
        return bool(direct_call.search(text) or module_import.search(text))

    if parts[0] == "lib":
        module_key = target.parent.name if stem == "index" else stem
        marker = re.compile(rf"(?:/|\b){re.escape(module_key)}(?:['\"/]|\b)")
        return bool(marker.search(text))

    return False


def _web_production_root(path: Path, app_root: Path) -> bool:
    try:
        relative = path.relative_to(app_root)
    except ValueError:
        return False
    parts = relative.parts
    return relative.as_posix() == "app.vue" or bool(parts and parts[0] == "pages")


def _web_helper_reachable(root: Path, helper_text: str) -> bool:
    helper = root / helper_text
    web_root = root / "apps/web"
    app_root = web_root / "app"
    try:
        relative = helper.relative_to(web_root)
    except ValueError:
        return True

    if relative.as_posix() == "nuxt.config.ts":
        return True
    try:
        app_relative = helper.relative_to(app_root)
    except ValueError:
        return True

    parts = app_relative.parts
    if parts and parts[0] == "pages":
        return True

    sources = _web_sources(root)
    if not sources:
        return False

    pending = [helper]
    visited = {helper}
    while pending:
        target = pending.pop()
        for source in sources:
            if source in visited or not _web_source_references(source, target, app_root):
                continue
            if _web_production_root(source, app_root):
                return True
            visited.add(source)
            pending.append(source)
    return False


def _api_helper_reachable(root: Path, helper_text: str) -> bool:
    helper = root / helper_text
    package_root = root / "apps/api/mind_detective_api"
    try:
        relative = helper.relative_to(package_root)
    except ValueError:
        return True
    if relative.name in {"app.py", "__main__.py"}:
        return True
    module = relative.with_suffix("").as_posix().replace("/", ".")
    for source in package_root.rglob("*.py"):
        if source == helper:
            continue
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported = node.module.lstrip(".")
                if imported == module or imported.endswith(f".{module}") or imported == helper.stem:
                    return True
            if isinstance(node, ast.Import):
                if any(alias.name.endswith(module) for alias in node.names):
                    return True
    return False


def helper_reachable(root: Path, helper_text: str) -> bool:
    if helper_text.startswith("apps/web/"):
        return _web_helper_reachable(root, helper_text)
    if helper_text.startswith("apps/api/mind_detective_api/"):
        return _api_helper_reachable(root, helper_text)
    return True


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
            helper = raw.get("helper")
            if (
                isinstance(helper, str)
                and (root / helper).is_file()
                and not helper_reachable(root, helper)
            ):
                errors.append(f"MD_CONTRACT_REACHABILITY:{requirement_id}:{helper}")
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


def _validate_semantic_governance(data: dict[str, Any]) -> list[str]:
    governance = data.get("semantic_validation")
    if not isinstance(governance, dict):
        return ["MD_EVAL_SEMANTIC_GOVERNANCE"]

    errors: list[str] = []
    if governance.get("automated_runner") is not False:
        errors.append("MD_EVAL_SEMANTIC_AUTOMATION_UNAVAILABLE")
    if governance.get("mode") != "manual":
        errors.append("MD_EVAL_SEMANTIC_MODE")
    if governance.get("protocol") != _SEMANTIC_REVIEW_PROTOCOL:
        errors.append("MD_EVAL_SEMANTIC_PROTOCOL")
    return errors


def validate_eval_data(data: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 2:
        errors.append("MD_EVAL_SCHEMA_VERSION")
    errors.extend(_validate_semantic_governance(data))
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
    errors = validate_eval_data(data, registry)
    governance = data.get("semantic_validation")
    if isinstance(governance, dict) and governance.get("protocol") == _SEMANTIC_REVIEW_PROTOCOL:
        if not (root / _SEMANTIC_REVIEW_PROTOCOL).is_file():
            errors.append("MD_EVAL_SEMANTIC_PROTOCOL_PATH")
    return errors
