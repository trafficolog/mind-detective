import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.safety import SafetyRoute, classify_request  # noqa: E402


class SafetyTests(unittest.TestCase):
    def test_physical_medicine_package_search_stays_ordinary(self):
        decision = classify_request("Где упаковка лекарства?")
        self.assertEqual(decision.route, SafetyRoute.ORDINARY_SEARCH)
        self.assertEqual(decision.codes, ())

    def test_medication_action_uncertainty_exits_search_reasoning(self):
        decision = classify_request("Я уже принял таблетку?")
        self.assertEqual(decision.route, SafetyRoute.LIMIT_AND_ESCALATE)
        self.assertIn("MD_SAFE_MEDICATION_ACTION", decision.codes)

    def test_hazardous_equipment_action_uncertainty_exits_search_reasoning(self):
        decision = classify_request("Я выключил плиту перед уходом?")
        self.assertEqual(decision.route, SafetyRoute.LIMIT_AND_ESCALATE)
        self.assertIn("MD_SAFE_HAZARDOUS_ACTION", decision.codes)

    def test_security_action_uncertainty_exits_search_reasoning(self):
        decision = classify_request("Я запер входную дверь?")
        self.assertEqual(decision.route, SafetyRoute.LIMIT_AND_ESCALATE)
        self.assertIn("MD_SAFE_SECURITY_ACTION", decision.codes)

    def test_lost_keys_query_is_not_security_action_uncertainty(self):
        decision = classify_request("Не могу найти ключи от двери")
        self.assertEqual(decision.route, SafetyRoute.ORDINARY_SEARCH)
