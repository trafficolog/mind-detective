import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.contract_controls import validate_contract_matrix  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
