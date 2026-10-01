"""Verify a static Web/PWA build is self-contained under a sub-path (GitHub Pages).

Usage: python scripts/check_pages_build.py apps/web/.output/public /mind-detective/
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ATTR = re.compile(r'(?:src|href)="([^"]+)"')
_CSS_URL = re.compile(r"url\(([^)]+)\)")


def _local(ref: str) -> bool:
    return not re.match(r"^(?:[a-z]+:|//|#)", ref)


def check_pages_build(root: Path, base: str) -> list[str]:
    errors: list[str] = []
    if not base.startswith("/") or not base.endswith("/"):
        return [f"MD_PAGES_BASE_FORMAT:{base}"]
    for required in ("index.html", "404.html", "manifest.webmanifest", "sw.js"):
        if not (root / required).is_file():
            errors.append(f"MD_PAGES_MISSING:{required}")
    for html in sorted(root.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        for ref in _ATTR.findall(text):
            if _local(ref) and ref.startswith("/") and not ref.startswith(base):
                errors.append(f"MD_PAGES_ROOT_REF:{html.relative_to(root)}:{ref}")
    for css in sorted(root.rglob("*.css")):
        for raw in _CSS_URL.findall(css.read_text(encoding="utf-8")):
            ref = raw.strip("'\" ")
            if _local(ref) and ref.startswith("/") and not ref.startswith(base):
                errors.append(f"MD_PAGES_ROOT_CSS_URL:{css.relative_to(root)}:{ref}")
    # Static public assets only: top-level files and directories that are not prerendered routes.
    public_entries = sorted(
        entry.name
        for entry in root.iterdir()
        if entry.name != "_nuxt"
        and not entry.name.endswith(".html")
        and not (entry.is_dir() and any(entry.rglob("index.html")))
    )
    scripts = sorted((root / "_nuxt").glob("*.js")) if base != "/" and (root / "_nuxt").is_dir() else []
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        for entry in public_entries:
            if re.search(r"[\"'`]/" + re.escape(entry) + r"(?:[/\"'`]|$)", text):
                errors.append(f"MD_PAGES_ROOT_JS_REF:{script.relative_to(root)}:/{entry}")
    manifest_path = root / "manifest.webmanifest"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        refs = [manifest.get("start_url", ""), manifest.get("scope", "")]
        refs += [icon.get("src", "") for icon in manifest.get("icons", [])]
        for ref in refs:
            if ref.startswith("/") and not ref.startswith(base):
                errors.append(f"MD_PAGES_ROOT_MANIFEST_REF:{ref}")
    sw = root / "sw.js"
    if sw.is_file() and base != "/":
        text = sw.read_text(encoding="utf-8")
        if f'createHandlerBoundToURL("{base}' not in text and f"createHandlerBoundToURL('{base}" not in text:
            errors.append("MD_PAGES_SW_NAVIGATE_FALLBACK")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    errors = check_pages_build(Path(argv[1]), argv[2])
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
