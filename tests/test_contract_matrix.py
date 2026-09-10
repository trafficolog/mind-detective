import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.contract_controls import collect_requirement_ids, selector_exists, validate_contract_matrix  # noqa: E402


class ContractMatrixTests(unittest.TestCase):
    def test_exact_selector_exists_for_real_unittest_method(self):
        selector = "plugins/mind-detective/tests/test_guard.py::GuardTests.test_new_location_blocked_in_reconstruction"
        self.assertTrue(selector_exists(ROOT, selector))

    def test_missing_exact_selector_is_rejected(self):
        selector = "plugins/mind-detective/tests/test_guard.py::GuardTests.test_not_real"
        self.assertFalse(selector_exists(ROOT, selector))

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
