import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.check_reference_freshness import check_reference_freshness

ROOT = Path(__file__).resolve().parents[1]


class ReferenceFreshnessTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, text: str) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_malformed_marker_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "docs/x.md", "Reviewed: yesterday. Class: scientific.\n")
            result = check_reference_freshness(root, today=date(2026, 9, 9))
            self.assertEqual(result.errors, ("MD_FRESH_MALFORMED:docs/x.md:1",))

    def test_future_marker_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "docs/x.md", "Reviewed: 2026-09-10. Class: scientific.\n")
            result = check_reference_freshness(root, today=date(2026, 9, 9))
            self.assertEqual(result.errors, ("MD_FRESH_FUTURE:docs/x.md:2026-09-10",))

    def test_changed_stale_reference_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "docs/x.md", "Reviewed: 2025-01-01. Class: scientific.\n")
            result = check_reference_freshness(
                root,
                today=date(2026, 9, 9),
                changed_files={"docs/x.md"},
            )
            self.assertEqual(result.errors, ("MD_FRESH_STALE:docs/x.md:scientific",))
            self.assertEqual(result.warnings, ())

    def test_untouched_stale_reference_is_warning_on_path_aware_pr_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "docs/x.md", "Reviewed: 2025-01-01. Class: scientific.\n")
            result = check_reference_freshness(
                root,
                today=date(2026, 9, 9),
                changed_files={"README.md"},
            )
            self.assertEqual(result.errors, ())
            self.assertEqual(result.warnings, ("MD_FRESH_STALE:docs/x.md:scientific",))

    def test_strict_scheduled_check_fails_stale_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "docs/x.md", "Reviewed: 2025-01-01. Class: scientific.\n")
            result = check_reference_freshness(root, today=date(2026, 9, 9), strict=True)
            self.assertEqual(result.errors, ("MD_FRESH_STALE:docs/x.md:scientific",))

    def test_repository_reference_markers_are_current(self):
        result = check_reference_freshness(ROOT, today=date(2026, 9, 9), strict=True)
        self.assertEqual(result.errors, ())


if __name__ == "__main__":
    unittest.main()
