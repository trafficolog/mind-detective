import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.contract_controls import collect_requirement_ids, selector_exists, validate_contract_matrix  # noqa: E402

WEB_REQUIREMENTS = {
    "MD-WEB-REQ-SHELL-01",
    "MD-WEB-REQ-MODE-01",
    "MD-WEB-REQ-MODE-02",
    "MD-WEB-REQ-STATE-01",
    "MD-WEB-REQ-QUEUE-01",
    "MD-WEB-REQ-CHECK-01",
    "MD-WEB-REQ-CHECK-02",
    "MD-WEB-REQ-SUMMARY-01",
    "MD-WEB-REQ-CREATE-01",
    "MD-WEB-REQ-RESUME-01",
    "MD-WEB-REQ-EMPTY-01",
    "MD-WEB-REQ-GUARD-01",
    "MD-WEB-REQ-ACTION-01",
    "MD-WEB-REQ-CLOSE-01",
    "MD-WEB-REQ-STORE-01",
    "MD-WEB-REQ-STORE-02",
    "MD-WEB-REQ-EXPORT-01",
    "MD-WEB-REQ-PWA-01",
    "MD-WEB-REQ-I18N-01",
    "MD-WEB-REQ-EVAL-01",
    "MD-WEB-REQ-CORE-01",
    "MD-WEB-REQ-PRIVACY-01",
    "MD-WEB-REQ-RELEASE-01",
}

OFFLINE_REQUIREMENTS = {
    "MD-OFFLINE-REQ-KERNEL-01",
    "MD-OFFLINE-REQ-GENERATOR-01",
    "MD-OFFLINE-REQ-CONFORMANCE-01",
    "MD-OFFLINE-REQ-API-01",
    "MD-OFFLINE-REQ-INTRINSIC-01",
    "MD-OFFLINE-REQ-LOCAL-01",
    "MD-OFFLINE-REQ-ATOMIC-01",
    "MD-OFFLINE-REQ-IDEMPOTENCE-01",
    "MD-OFFLINE-REQ-CREATE-01",
    "MD-OFFLINE-REQ-PROPOSAL-01",
    "MD-OFFLINE-REQ-ASSISTANT-01",
    "MD-OFFLINE-REQ-IDENTITY-01",
    "MD-OFFLINE-REQ-SKEW-01",
    "MD-OFFLINE-REQ-PRIVACY-01",
    "MD-OFFLINE-REQ-PWA-01",
    "MD-OFFLINE-REQ-RELEASE-01",
}

RECONSTRUCTION_REQUIREMENTS = {
    f"MD-WEB-REQ-RECONSTRUCT-{index:02d}" for index in range(1, 11)
}


class ContractMatrixTests(unittest.TestCase):
    def test_exact_selector_exists_for_real_unittest_method(self):
        selector = "plugins/mind-detective/tests/test_guard.py::GuardTests.test_new_location_blocked_in_reconstruction"
        self.assertTrue(selector_exists(ROOT, selector))

    def test_exact_selector_exists_for_real_playwright_test(self):
        selector = (
            "apps/web/tests/e2e/create-resume.spec.ts::"
            "production creation is one field and preserves a paused case for resume"
        )
        self.assertTrue(selector_exists(ROOT, selector))

    def test_missing_exact_selector_is_rejected(self):
        selector = "plugins/mind-detective/tests/test_guard.py::GuardTests.test_not_real"
        self.assertFalse(selector_exists(ROOT, selector))

    def test_web_requirement_ids_are_collected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requirements.md"
            path.write_text(
                "- `MD-REQ-CASE-01` core\n- `MD-WEB-REQ-SHELL-01` web\n",
                encoding="utf-8",
            )
            ids, duplicates = collect_requirement_ids(path)
        self.assertEqual(ids, {"MD-REQ-CASE-01", "MD-WEB-REQ-SHELL-01"})
        self.assertEqual(duplicates, set())

    def test_offline_requirement_ids_are_collected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requirements.md"
            path.write_text(
                "- `MD-OFFLINE-REQ-KERNEL-01` portable kernel\n",
                encoding="utf-8",
            )
            ids, duplicates = collect_requirement_ids(path)
        self.assertEqual(ids, {"MD-OFFLINE-REQ-KERNEL-01"})
        self.assertEqual(duplicates, set())

    def test_repository_declares_all_approved_web_requirements(self):
        ids, duplicates = collect_requirement_ids(ROOT / "docs/REQUIREMENTS.md")
        self.assertEqual(duplicates, set())
        self.assertTrue(WEB_REQUIREMENTS.issubset(ids))

    def test_repository_declares_all_approved_offline_requirements(self):
        ids, duplicates = collect_requirement_ids(ROOT / "docs/REQUIREMENTS.md")
        self.assertEqual(duplicates, set())
        self.assertTrue(OFFLINE_REQUIREMENTS.issubset(ids))

    def test_repository_declares_planned_reconstruction_requirements(self):
        ids, duplicates = collect_requirement_ids(ROOT / "docs/REQUIREMENTS.md")
        self.assertEqual(duplicates, set())
        self.assertTrue(RECONSTRUCTION_REQUIREMENTS.issubset(ids))

        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        rows = {
            row["requirement_id"]: row
            for row in matrix["entries"]
            if row["requirement_id"] in RECONSTRUCTION_REQUIREMENTS
        }
        self.assertEqual(set(rows), RECONSTRUCTION_REQUIREMENTS)
        self.assertTrue(all(row["status"] == "planned" for row in rows.values()))
        self.assertTrue(all("test" not in row and "helper" not in row for row in rows.values()))

    def test_privacy_requirement_is_active_and_exactly_traced(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        privacy = next(
            entry
            for entry in matrix["entries"]
            if entry["requirement_id"] == "MD-WEB-REQ-PRIVACY-01"
        )
        self.assertEqual(privacy["status"], "active")
        self.assertEqual(
            privacy["test"],
            "apps/web/tests/unit/i18n.spec.ts::preserves required safety and provider-processing semantics in both locales",
        )
        self.assertTrue(selector_exists(ROOT, privacy["test"]))

    def test_duplicate_requirement_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs/REQUIREMENTS.md").write_text("- `MD-REQ-X-01` first\n- `MD-REQ-X-01` duplicate\n", encoding="utf-8")
            ids, duplicates = collect_requirement_ids(root / "docs/REQUIREMENTS.md")
            self.assertEqual(ids, {"MD-REQ-X-01"})
            self.assertEqual(duplicates, {"MD-REQ-X-01"})

    def test_reconstruct_skill_requires_free_account_before_clarification(self):
        text = (ROOT / "plugins/mind-detective/skills/mind-detective-reconstruct/SKILL.md").read_text(encoding="utf-8").casefold()
        self.assertIn("free account before detailed clarification", text)
        self.assertIn("do not seed it with candidate locations", text)

    def test_repository_contract_matrix_is_valid(self):
        self.assertEqual(validate_contract_matrix(ROOT), [])


if __name__ == "__main__":
    unittest.main()
