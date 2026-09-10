import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.contract_controls import validate_eval_data  # noqa: E402


class EvalContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "docs/EVAL_TOKEN_REGISTRY.json").read_text(encoding="utf-8"))
        self.eval_data = json.loads((ROOT / "plugins/mind-detective/evals/scenarios.json").read_text(encoding="utf-8"))

    def test_repository_eval_contract_is_valid(self):
        self.assertEqual(validate_eval_data(self.eval_data, self.registry), [])

    def test_unknown_token_is_rejected(self):
        broken = copy.deepcopy(self.eval_data)
        broken["scenarios"][0]["must_mention_tokens"] = ["UNKNOWN_TOKEN"]
        self.assertIn("MD_EVAL_UNKNOWN_TOKEN:UNKNOWN_TOKEN", validate_eval_data(broken, self.registry))

    def test_unknown_outcome_is_rejected(self):
        broken = copy.deepcopy(self.eval_data)
        broken["scenarios"][0]["outcome"] = "maybe"
        self.assertIn("MD_EVAL_OUTCOME:maybe", validate_eval_data(broken, self.registry))

    def test_missing_route_is_rejected(self):
        broken = copy.deepcopy(self.eval_data)
        del broken["scenarios"][0]["must_route_to"]
        self.assertIn("MD_EVAL_ROUTE_MISSING:recon-unsupported-location", validate_eval_data(broken, self.registry))


if __name__ == "__main__":
    unittest.main()
