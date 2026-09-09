from __future__ import annotations

import json
import sys
from pathlib import Path

CANONICAL_NAME = "mind-detective"
CANONICAL_VERSION = "0.1.0"


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
        plugin = plugins[0]
        if plugin.get("name") != CANONICAL_NAME:
            errors.append(f"MD_REPO_NAME:{label}")
        if plugin.get("version") != CANONICAL_VERSION:
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
