import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.contract_controls import helper_reachable, validate_contract_matrix  # noqa: E402


class ContractReachabilityTests(unittest.TestCase):
    def test_active_web_composable_must_be_reachable_from_production_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir(parents=True)
            (root / "docs/REQUIREMENTS.md").write_text(
                "- `MD-WEB-REQ-QUEUE-01` queue contract\n",
                encoding="utf-8",
            )
            (root / "docs/reference.md").write_text("reference\n", encoding="utf-8")
            (root / "plugins/mind-detective/skills/mind-detective").mkdir(parents=True)
            (root / "plugins/mind-detective/skills/mind-detective/SKILL.md").write_text(
                "# skill\n",
                encoding="utf-8",
            )
            (root / "apps/web/app/composables").mkdir(parents=True)
            (root / "apps/web/app/pages").mkdir(parents=True)
            (root / "apps/web/app/composables/useDeadQueue.ts").write_text(
                "export function useDeadQueue() { return {} }\n",
                encoding="utf-8",
            )
            (root / "apps/web/app/pages/index.vue").write_text(
                "<template><main>production</main></template>\n",
                encoding="utf-8",
            )
            (root / "apps/web/tests/unit").mkdir(parents=True)
            (root / "apps/web/tests/unit/dead.spec.ts").write_text(
                "test('dead helper contract', () => {})\n",
                encoding="utf-8",
            )
            matrix = {
                "schema_version": 2,
                "entries": [
                    {
                        "requirement_id": "MD-WEB-REQ-QUEUE-01",
                        "status": "active",
                        "enforcement": "unit+browser_contract",
                        "skill": "plugins/mind-detective/skills/mind-detective/SKILL.md",
                        "helper": "apps/web/app/composables/useDeadQueue.ts",
                        "test": "apps/web/tests/unit/dead.spec.ts::dead helper contract",
                        "reference": "docs/reference.md",
                    }
                ],
            }
            (root / "docs/CONTRACT_MATRIX.json").write_text(
                json.dumps(matrix),
                encoding="utf-8",
            )

            errors = validate_contract_matrix(root)

        self.assertIn(
            "MD_CONTRACT_REACHABILITY:MD-WEB-REQ-QUEUE-01:apps/web/app/composables/useDeadQueue.ts",
            errors,
        )

    def test_active_web_helper_must_reach_a_page_not_only_another_dead_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir(parents=True)
            (root / "docs/REQUIREMENTS.md").write_text(
                "- `MD-WEB-REQ-MODE-01` component contract\n",
                encoding="utf-8",
            )
            (root / "docs/reference.md").write_text("reference\n", encoding="utf-8")
            (root / "plugins/mind-detective/skills/mind-detective").mkdir(parents=True)
            (root / "plugins/mind-detective/skills/mind-detective/SKILL.md").write_text(
                "# skill\n",
                encoding="utf-8",
            )
            components = root / "apps/web/app/components/dead"
            components.mkdir(parents=True)
            (root / "apps/web/app/pages").mkdir(parents=True)
            (components / "DeadLeaf.vue").write_text(
                "<template><span>leaf</span></template>\n",
                encoding="utf-8",
            )
            (components / "DeadParent.vue").write_text(
                "<template><DeadLeaf /></template>\n",
                encoding="utf-8",
            )
            (root / "apps/web/app/pages/index.vue").write_text(
                "<template><main>production</main></template>\n",
                encoding="utf-8",
            )
            (root / "apps/web/tests/unit").mkdir(parents=True)
            (root / "apps/web/tests/unit/dead.spec.ts").write_text(
                "test('dead component contract', () => {})\n",
                encoding="utf-8",
            )
            matrix = {
                "schema_version": 2,
                "entries": [
                    {
                        "requirement_id": "MD-WEB-REQ-MODE-01",
                        "status": "active",
                        "enforcement": "browser_contract",
                        "skill": "plugins/mind-detective/skills/mind-detective/SKILL.md",
                        "helper": "apps/web/app/components/dead/DeadLeaf.vue",
                        "test": "apps/web/tests/unit/dead.spec.ts::dead component contract",
                        "reference": "docs/reference.md",
                    }
                ],
            }
            (root / "docs/CONTRACT_MATRIX.json").write_text(
                json.dumps(matrix),
                encoding="utf-8",
            )

            errors = validate_contract_matrix(root)

        self.assertIn(
            "MD_CONTRACT_REACHABILITY:MD-WEB-REQ-MODE-01:apps/web/app/components/dead/DeadLeaf.vue",
            errors,
        )

    def test_reconstruction_web_helpers_are_reachable_from_production_roots(self):
        helpers = (
            "apps/web/app/components/reconstruction/ReconstructionPanel.vue",
            "apps/web/app/components/reconstruction/FreeAccountCard.vue",
            "apps/web/app/components/reconstruction/StatementCapture.vue",
            "apps/web/app/components/reconstruction/TimelineEditor.vue",
            "apps/web/app/components/reconstruction/TimelineSummary.vue",
            "apps/web/app/composables/useReconstruction.ts",
        )
        for helper in helpers:
            with self.subTest(helper=helper):
                self.assertTrue(helper_reachable(ROOT, helper), helper)

    def test_removed_runtime_surfaces_do_not_return_as_test_only_dead_code(self):
        self.assertFalse((ROOT / "apps/web/app/composables/useCommandQueue.ts").exists())
        self.assertFalse((ROOT / "apps/web/tests/unit/commandQueue.spec.ts").exists())
        self.assertFalse((ROOT / "apps/api/mind_detective_api/privacy_log.py").exists())

        case_api = (ROOT / "apps/web/app/composables/useCaseApi.ts").read_text(encoding="utf-8")
        self.assertNotIn("createCase(", case_api)
        self.assertNotIn("sendCommand(", case_api)
        self.assertNotIn("validateCase(", case_api)
        self.assertNotIn("/api/v1/case/validate", case_api)
        self.assertIn("nextProposal(", case_api)

        index_page = (ROOT / "apps/web/app/pages/index.vue").read_text(encoding="utf-8")
        self.assertNotIn("validateCase", index_page)
        self.assertNotIn("/api/v1/case/validate", index_page)


if __name__ == "__main__":
    unittest.main()
