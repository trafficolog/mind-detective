from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

CANONICAL_NAME = "mind-detective"
CANONICAL_VERSION = "0.1.0"


FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "requests",
    "httpx",
    "aiohttp",
    "boto3",
    "google.cloud",
    "openai",
    "anthropic",
    "telegram",
    "aiogram",
    "slack_sdk",
    "discord",
    "vk_api",
    "playwright",
    "selenium",
)
FORBIDDEN_RUNTIME_FILES: tuple[str, ...] = ("zones.py", "ach.py", "model_adapter.py")
FORBIDDEN_PLUGIN_MANIFESTS: tuple[str, ...] = ("package.json", "nuxt.config.ts", "vite.config.ts")
FORBIDDEN_PLUGIN_DIRECTORIES: tuple[str, ...] = ("apps",)


def _normalized_forbidden_import(module: str) -> str | None:
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        if module == prefix or module.startswith(prefix + "."):
            return prefix
    return None


def scan_source_for_forbidden_imports(source: str) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["MD_BOUNDARY_SYNTAX"]
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        for module in modules:
            prefix = _normalized_forbidden_import(module)
            if prefix is not None:
                code = f"MD_BOUNDARY_FORBIDDEN_IMPORT:{prefix}"
                if code not in errors:
                    errors.append(code)
    return errors


def validate_boundaries(root: Path) -> list[str]:
    errors: list[str] = []
    runtime = root / "plugins/mind-detective/scripts"
    plugin = root / "plugins/mind-detective"
    for name in FORBIDDEN_RUNTIME_FILES:
        if (runtime / name).exists():
            errors.append(f"MD_BOUNDARY_FORBIDDEN_FILE:plugins/mind-detective/scripts/{name}")
    for name in FORBIDDEN_PLUGIN_MANIFESTS:
        if (plugin / name).exists():
            errors.append(f"MD_BOUNDARY_FORBIDDEN_FILE:plugins/mind-detective/{name}")
    for name in FORBIDDEN_PLUGIN_DIRECTORIES:
        if (plugin / name).exists():
            errors.append(f"MD_BOUNDARY_FORBIDDEN_DIR:plugins/mind-detective/{name}")
    for path in sorted(runtime.glob("*.py")):
        for code in scan_source_for_forbidden_imports(path.read_text(encoding="utf-8")):
            errors.append(f"{code}:{path.relative_to(root)}")
    return errors


def _load_json(path: Path, errors: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"MD_REPO_JSON:{path}:{exc.__class__.__name__}")
        return None
    if not isinstance(value, dict):
        errors.append(f"MD_REPO_JSON_OBJECT:{path}")
        return None
    return value


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    paths = {
        "claude_market": root / ".claude-plugin/marketplace.json",
        "agents_market": root / ".agents/plugins/marketplace.json",
        "claude_plugin": root / "plugins/mind-detective/.claude-plugin/plugin.json",
        "codex_plugin": root / "plugins/mind-detective/.codex-plugin/plugin.json",
    }
    for path in paths.values():
        if not path.is_file():
            errors.append(f"MD_REPO_MISSING:{path.relative_to(root)}")

    errors.extend(validate_boundaries(root))

    forbidden = root / "plugins/mind-detective/.agents-plugin/plugin.json"
    if forbidden.exists():
        errors.append("MD_REPO_FORBIDDEN:.agents-plugin/plugin.json")

    if errors:
        return errors

    docs = {key: _load_json(path, errors) for key, path in paths.items()}
    if errors:
        return errors

    codex = docs["codex_plugin"] or {}
    claude = docs["claude_plugin"] or {}
    agents = docs["agents_market"] or {}
    market = docs["claude_market"] or {}

    if codex.get("name") != CANONICAL_NAME:
        errors.append("MD_REPO_NAME:codex")
    if codex.get("version") != CANONICAL_VERSION:
        errors.append("MD_REPO_VERSION:codex")
    if claude.get("name") != CANONICAL_NAME:
        errors.append("MD_REPO_NAME:claude")
    if claude.get("version") != CANONICAL_VERSION:
        errors.append("MD_REPO_VERSION:claude")

    for label, payload in (("agents", agents), ("claude-market", market)):
        plugins = payload.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
            errors.append(f"MD_REPO_PLUGIN_COUNT:{label}")
            continue
        plugin_payload = plugins[0]
        if plugin_payload.get("name") != CANONICAL_NAME:
            errors.append(f"MD_REPO_NAME:{label}")
        if plugin_payload.get("version") != CANONICAL_VERSION:
            errors.append(f"MD_REPO_VERSION:{label}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
