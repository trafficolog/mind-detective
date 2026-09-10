from __future__ import annotations

from pathlib import Path

REQUIRED_PAIRS: tuple[tuple[str, str], ...] = (
    ("README.md", "README.en.md"),
    ("CHANGELOG.md", "CHANGELOG.en.md"),
    ("SECURITY.md", "SECURITY.en.md"),
    ("docs/ARCHITECTURE.md", "docs/ARCHITECTURE.en.md"),
    ("docs/GETTING_STARTED.md", "docs/GETTING_STARTED.en.md"),
    ("docs/METHODOLOGY.md", "docs/METHODOLOGY.en.md"),
    ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"),
    ("docs/RELEASE_POLICY.md", "docs/RELEASE_POLICY.en.md"),
    ("docs/GLOSSARY.md", "docs/GLOSSARY.en.md"),
    ("plugins/mind-detective/README.md", "plugins/mind-detective/README.en.md"),
    ("plugins/mind-detective/CHANGELOG.md", "plugins/mind-detective/CHANGELOG.en.md"),
)


def validate_bilingual_docs(root: Path) -> list[str]:
    errors: list[str] = []
    for ru_rel, en_rel in REQUIRED_PAIRS:
        ru = root / ru_rel
        en = root / en_rel
        if not ru.is_file():
            errors.append(f"MD_DOCS_MISSING:{ru_rel}")
            continue
        if not en.is_file():
            errors.append(f"MD_DOCS_MISSING:{en_rel}")
            continue
        ru_text = ru.read_text(encoding="utf-8")
        en_text = en.read_text(encoding="utf-8")
        if en.name not in ru_text:
            errors.append(f"MD_DOCS_LANG_LINK:{ru_rel}->{en.name}")
        if ru.name not in en_text:
            errors.append(f"MD_DOCS_LANG_LINK:{en_rel}->{ru.name}")
    return errors
