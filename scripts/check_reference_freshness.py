from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

MARKER_RE = re.compile(
    r"Reviewed:\s*(\d{4}-\d{2}-\d{2})\.\s*Class:\s*(scientific|safety|external)\.",
    re.IGNORECASE,
)
LIMIT_DAYS = {"scientific": 365, "safety": 180, "external": 90}


@dataclass(frozen=True)
class FreshnessResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _reference_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for base in (root / "docs", root / "plugins/mind-detective/references"):
        if base.exists():
            files.update(path for path in base.rglob("*.md") if path.is_file())
    return sorted(files)


def check_reference_freshness(
    root: Path,
    *,
    today: date | None = None,
    changed_files: set[str] | None = None,
    strict: bool = False,
) -> FreshnessResult:
    now = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    for path in _reference_files(root):
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "Reviewed:" not in line:
                continue
            match = MARKER_RE.search(line)
            if match is None:
                errors.append(f"MD_FRESH_MALFORMED:{rel}:{line_no}")
                continue
            reviewed_text, class_name = match.groups()
            reviewed = date.fromisoformat(reviewed_text)
            class_name = class_name.lower()
            if reviewed > now:
                errors.append(f"MD_FRESH_FUTURE:{rel}:{reviewed_text}")
                continue
            stale = (now - reviewed).days > LIMIT_DAYS[class_name]
            if not stale:
                continue
            code = f"MD_FRESH_STALE:{rel}:{class_name}"
            if strict or changed_files is None or rel in changed_files:
                errors.append(code)
            else:
                warnings.append(code)
    return FreshnessResult(tuple(errors), tuple(warnings))


def _load_changed_files(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--changed-files-file", type=Path)
    parser.add_argument("--today")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    today = date.fromisoformat(args.today) if args.today else None
    result = check_reference_freshness(
        root,
        today=today,
        changed_files=_load_changed_files(args.changed_files_file),
        strict=args.strict,
    )
    for warning in result.warnings:
        print(f"WARNING:{warning}")
    for error in result.errors:
        print(error, file=sys.stderr)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
