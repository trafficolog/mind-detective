import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.guard import InteractionMode, lint_candidate  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_new_location_blocked_in_reconstruction(self):
        result = lint_candidate(
            "Вы не оставили ключи в машине?",
            mode=InteractionMode.RECONSTRUCTION,
            known_locations={"кухня"},
        )
        self.assertFalse(result.allowed)
        self.assertIn("MD_G_RECON_NEW_LOCATION", result.codes)

    def test_same_new_location_allowed_as_search_proposal(self):
        result = lint_candidate(
            "Предлагаю проверить машину.",
            mode=InteractionMode.SEARCH_PLANNING,
            known_locations={"кухня"},
        )
        self.assertTrue(result.allowed)

    def test_probability_claim_blocked_in_search_mode(self):
        result = lint_candidate(
            "Вероятность 70%, что ключи в машине.",
            mode=InteractionMode.SEARCH_PLANNING,
            known_locations={"машина"},
        )
        self.assertFalse(result.allowed)
        self.assertIn("MD_G_LOCATION_PROBABILITY", result.codes)

    def test_false_memory_assertion_is_blocked(self):
        result = lint_candidate(
            "Вы точно положили ключи на кухне.",
            mode=InteractionMode.RECONSTRUCTION,
            known_locations={"кухня"},
        )
        self.assertIn("MD_G_FALSE_MEMORY", result.codes)

    def test_mechanism_diagnosis_is_blocked(self):
        result = lint_candidate(
            "Вы забыли ключи из-за стресса.",
            mode=InteractionMode.RECONSTRUCTION,
            known_locations=set(),
        )
        self.assertIn("MD_G_MECHANISM_DIAGNOSIS", result.codes)

    def test_superficial_search_does_not_prove_absence(self):
        result = lint_candidate(
            "Вы уже быстро посмотрели, значит там точно нет ключей.",
            mode=InteractionMode.SEARCH_PLANNING,
            known_locations=set(),
        )
        self.assertIn("MD_G_SUPERFICIAL_PROVES_ABSENCE", result.codes)
