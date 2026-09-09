#!/usr/bin/env python3
"""Validate and normalize the declarative MIND Detective release manifest."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence

DEFAULT_MANIFEST = Path(".github/releases/release.json")
RELEASES_DIR = Path(".github/releases")
FULL_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
TSV_CONTROL_CHARS = ("\t", "\r", "\n")


@dataclass(frozen=True)
class ReleaseItem:
    kind: str
    name: str
    version: str
    tag: str
    title: str
    notes_file: str


def validate_full_sha(value: str) -> str:
    if FULL_SHA_RE.fullmatch(value) is None:
        raise ValueError(f"MD_RELEASE_SHA:{value}")
    return value.lower()


def consensus_recovery_target(targets: Sequence[str]) -> str | None:
    normalized = [validate_full_sha(target) for target in targets]
    if not normalized:
        return None
    first = normalized[0]
    if any(target != first for target in normalized[1:]):
        raise ValueError("MD_RELEASE_CONFLICT_TARGETS")
    return first


def _manifest_file(root: Path, manifest_path: Path | None) -> Path:
    selected = manifest_path or DEFAULT_MANIFEST
    return selected if selected.is_absolute() else root / selected


def load_release_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    path = _manifest_file(root.resolve(), manifest_path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("release manifest root must be a JSON object")
    return data


def _required_string(obj: dict[str, Any], key: str, label: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{key} must be a non-empty string")
        return None
    if any(control in value for control in TSV_CONTROL_CHARS):
        errors.append(f"{label}.{key} must not contain a TSV control character")
        return None
    return value.strip()


def _validate_notes_file(root: Path, value: str | None, label: str, errors: list[str]) -> None:
    if value is None:
        return
    relative = Path(value)
    releases_root = (root / RELEASES_DIR).resolve()
    if relative.is_absolute():
        errors.append(f"{label}.notes_file must be repository-relative")
        return
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(releases_root)
    except ValueError:
        errors.append(f"{label}.notes_file must stay under .github/releases")
        return
    if resolved.suffix.lower() != ".md":
        errors.append(f"{label}.notes_file must be Markdown")
    if not resolved.is_file():
        errors.append(f"{label} notes file does not exist: {value}")


def _read_json(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{label} is unreadable or invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return None
    return value


def _require_marker(path: Path, marker: str, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path.name} unreadable: {exc}")
        return
    if marker not in text:
        errors.append(f"{path.name} must contain release marker {marker!r}")


def validate_release_manifest(root: Path, manifest_path: Path | None = None) -> list[str]:
    root = root.resolve()
    path = _manifest_file(root, manifest_path)
    errors: list[str] = []
    try:
        data = load_release_manifest(root, manifest_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"release manifest is invalid: {path}: {exc}"]

    if data.get("schema_version") != 1:
        errors.append("release manifest schema_version must equal 1")

    repository = data.get("repository")
    if not isinstance(repository, dict):
        errors.append("release manifest repository must be an object")
        repository = {}
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        errors.append("release manifest plugins must be a list")
        plugins = []

    repo_version = _required_string(repository, "version", "repository", errors)
    repo_tag = _required_string(repository, "tag", "repository", errors)
    _required_string(repository, "title", "repository", errors)
    repo_notes = _required_string(repository, "notes_file", "repository", errors)
    if repo_version and SEMVER_RE.fullmatch(repo_version) is None:
        errors.append(f"repository version must be strict SemVer: {repo_version}")
    if repo_version and repo_tag and repo_tag != repo_version:
        errors.append("repository tag must equal repository version")
    _validate_notes_file(root, repo_notes, "repository", errors)
    if repo_version:
        _require_marker(root / "README.md", f"release-{repo_version}", errors)
        _require_marker(root / "README.en.md", f"release-{repo_version}", errors)
        _require_marker(root / "CHANGELOG.md", f"## [{repo_version}]", errors)
        _require_marker(root / "CHANGELOG.en.md", f"## [{repo_version}]", errors)

    seen_tags = {repo_tag} if repo_tag else set()
    seen_plugins: set[str] = set()
    for index, raw in enumerate(plugins):
        label = f"plugins[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{label} must be an object")
            continue
        plugin = _required_string(raw, "plugin", label, errors)
        version = _required_string(raw, "version", label, errors)
        tag = _required_string(raw, "tag", label, errors)
        _required_string(raw, "title", label, errors)
        notes_file = _required_string(raw, "notes_file", label, errors)
        _validate_notes_file(root, notes_file, label, errors)
        if plugin:
            if plugin in seen_plugins:
                errors.append(f"duplicate plugin in release manifest: {plugin}")
            seen_plugins.add(plugin)
        if tag:
            if tag in seen_tags:
                errors.append(f"duplicate release tag in release manifest: {tag}")
            seen_tags.add(tag)
        if version and SEMVER_RE.fullmatch(version) is None:
            errors.append(f"{label}.version must be strict SemVer: {version}")
        if plugin and version and tag and tag != f"{plugin}-v{version}":
            errors.append(f"{label}.tag must equal {plugin}-v{version}")
        if not plugin or not version:
            continue
        plugin_root = root / "plugins" / plugin
        for rel in (Path(".codex-plugin/plugin.json"), Path(".claude-plugin/plugin.json")):
            manifest = _read_json(plugin_root / rel, f"{plugin} {rel.as_posix()}", errors)
            if manifest is not None and manifest.get("version") != version:
                errors.append(f"{plugin} {rel.as_posix()} version must equal {version}")
        _require_marker(plugin_root / "CHANGELOG.md", f"## [{version}]", errors)
        _require_marker(plugin_root / "CHANGELOG.en.md", f"## [{version}]", errors)

    if len(plugins) != 1 or not isinstance(plugins[0], dict) or plugins[0].get("plugin") != "mind-detective":
        errors.append("0.1.0 release manifest must declare exactly the mind-detective plugin")
    return errors


def release_items(root: Path, manifest_path: Path | None = None) -> list[ReleaseItem]:
    errors = validate_release_manifest(root, manifest_path)
    if errors:
        raise ValueError("; ".join(errors))
    data = load_release_manifest(root.resolve(), manifest_path)
    repository = data["repository"]
    items = [
        ReleaseItem(
            "repository",
            "repository",
            repository["version"],
            repository["tag"],
            repository["title"],
            repository["notes_file"],
        )
    ]
    for plugin in data["plugins"]:
        items.append(
            ReleaseItem(
                "plugin",
                plugin["plugin"],
                plugin["version"],
                plugin["tag"],
                plugin["title"],
                plugin["notes_file"],
            )
        )
    return items


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    items = sub.add_parser("items")
    items.add_argument("--format", choices=("tsv",), default="tsv")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = Path(args.root)
    manifest = Path(args.manifest) if args.manifest else None
    if args.command == "validate":
        errors = validate_release_manifest(root, manifest)
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    try:
        items = release_items(root, manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for item in items:
        print("\t".join((item.kind, item.name, item.version, item.tag, item.title, item.notes_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
