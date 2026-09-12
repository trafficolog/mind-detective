from __future__ import annotations

import os
from pathlib import Path

_PLUGIN_MARKER = Path("scripts/controller.py")
_PLUGIN_ENV = "MIND_DETECTIVE_PLUGIN_ROOT"


def _valid_plugin_root(path: Path) -> bool:
    return (path / _PLUGIN_MARKER).is_file()


def resolve_plugin_root(source_file: Path | None = None) -> Path:
    """Resolve the installable plugin root without assuming monorepo parent depth."""
    configured = os.environ.get(_PLUGIN_ENV)
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if _valid_plugin_root(candidate):
            return candidate
        raise RuntimeError(f"MD_API_PLUGIN_ROOT_NOT_FOUND: {_PLUGIN_ENV}={candidate}")

    source = (source_file or Path(__file__)).resolve()
    start = source if source.is_dir() else source.parent
    for ancestor in (start, *start.parents):
        for candidate in (ancestor, ancestor / "plugins" / "mind-detective"):
            if _valid_plugin_root(candidate):
                return candidate.resolve()

    raise RuntimeError("MD_API_PLUGIN_ROOT_NOT_FOUND")
