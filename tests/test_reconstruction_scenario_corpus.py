import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.json"
CORPUS_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_SCENARIO_CORPUS_V1.json"
REVIEW_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_SCENARIO_CORPUS_V1.md"


class ReconstructionScenarioCorpusV1Tests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        self.review = REVIEW_PATH.read_text(encoding="utf-8")
        self.scenarios = self.corpus["scenarios"]

    def test_identity_and_minimum_family_variant_matrix_are_frozen(self):
        self.assertEqual(self.corpus["corpus_schema"], "mind-detective-reconstruction-corpus/v1")
        self.assertEqual(self.corpus["protocol_schema"], self.protocol["protocol_schema"])
        self.assertEqual(self.corpus["status"], "synthetic_research_only")
        self.assertEqual(len(self.scenarios), 24)
        self.assertEqual(len({s["scenario_id"] for s in self.scenarios}), 24)

        by_family = defaultdict(list)
        for scenario in self.scenarios:
            by_family[scenario["family_id"]].append(scenario)

        self.assertEqual(set(by_family), set(self.protocol["scenario_family_ids"]))
        for family_id, fixtures in by_family.items():
            self.assertEqual({f["variant_id"] for f in fixtures}, {"RV01", "RV02"}, family_id)
            self.assertEqual({f["language_code"] for f in fixtures}, {"ru", "en"}, family_id)
            self.assertEqual(len({f["isomorphism_key"] for f in fixtures}), 1, family_id)

    def test_each_fixture_has_required_research_instrument_fields(self):
        required = {
            "scenario_id",
            "scenario_version",
            "family_id",
            "variant_id",
            "language_code",
            "isomorphism_key",
            "user_visible_initial_account",
            "model_visible_context",
            "participant_latent",
            "genuinely_unknown_facts",
            "contradictions",
            "allowed_clarification_targets",
            "forbidden_introductions",
            "adversarial_examples",
            "critical_violation_triggers",
            "expected_outcome",
        }
        allowed_model_context_keys = {
            "language_code",
            "supported_entities",
            "supported_locations",
            "supported_actions",
            "timeline_refs",
            "statement_refs",
            "unknown_markers",
            "contradiction_refs",
        }
        for scenario in self.scenarios:
            self.assertTrue(required.issubset(scenario), scenario["scenario_id"])
            self.assertEqual(set(scenario["model_visible_context"]), allowed_model_context_keys)
            self.assertTrue(scenario["user_visible_initial_account"])
            self.assertTrue(scenario["participant_latent"]["facts"])
            self.assertTrue(scenario["critical_violation_triggers"])

            model_serialized = json.dumps(scenario["model_visible_context"], ensure_ascii=False)
            for fact in scenario["participant_latent"]["facts"]:
                self.assertNotIn(fact["text"], model_serialized, scenario["scenario_id"])
            for unknown in scenario["genuinely_unknown_facts"]:
                if unknown.get("hidden_text"):
                    self.assertNotIn(unknown["hidden_text"], model_serialized, scenario["scenario_id"])

    def test_reason_code_positive_coverage_is_at_least_two_examples_each(self):
        counts = Counter()
        for scenario in self.scenarios:
            for target in scenario["allowed_clarification_targets"]:
                self.assertIn(target["reason_code"], self.protocol["clarification_reason_codes"])
                self.assertTrue(target["target_ids"])
                counts[target["reason_code"]] += 1
        for code in self.protocol["clarification_reason_codes"]:
            self.assertGreaterEqual(counts[code], 2, code)

    def test_every_guard_rejection_code_has_two_adversarial_examples(self):
        counts = Counter()
        for scenario in self.scenarios:
            for example in scenario["adversarial_examples"]:
                self.assertIn(example["guard_code"], self.protocol["guard_rejection_codes"])
                self.assertTrue(example["candidate_question"])
                self.assertTrue(example["why_forbidden"])
                counts[example["guard_code"]] += 1
        for code in self.protocol["guard_rejection_codes"]:
            self.assertGreaterEqual(counts[code], 2, code)

    def test_relevant_families_contain_a_preserve_unknown_outcome(self):
        relevant = {
            "RF03_contradictory_recollection",
            "RF04_habit_vs_actual_recollection",
            "RF05_multiple_similar_locations",
            "RF06_false_friend_location",
            "RF07_genuine_unknown",
            "RF08_ambiguous_pronoun_entity",
            "RF10_high_risk_unsafe_context",
        }
        for family_id in relevant:
            fixtures = [s for s in self.scenarios if s["family_id"] == family_id]
            self.assertTrue(any(s["expected_outcome"]["preserve_unknown"] for s in fixtures), family_id)

    def test_prompt_injection_family_exists_in_ru_and_en(self):
        fixtures = [s for s in self.scenarios if s["family_id"] == "RF11_prompt_injection_free_account"]
        self.assertEqual({s["language_code"] for s in fixtures}, {"ru", "en"})
        for scenario in fixtures:
            self.assertTrue(scenario["expected_outcome"]["prompt_injection_must_not_change_policy"])
            self.assertTrue(scenario["user_visible_initial_account"])

    def test_ru_en_pairs_are_structurally_isomorphic(self):
        by_key = defaultdict(list)
        for scenario in self.scenarios:
            by_key[scenario["isomorphism_key"]].append(scenario)
        for key, pair in by_key.items():
            self.assertEqual(len(pair), 2, key)
            ru = next(s for s in pair if s["language_code"] == "ru")
            en = next(s for s in pair if s["language_code"] == "en")
            self.assertEqual(
                {f["fact_id"] for f in ru["participant_latent"]["facts"]},
                {f["fact_id"] for f in en["participant_latent"]["facts"]},
                key,
            )
            self.assertEqual(
                {(t["target_id"], t["reason_code"]) for t in ru["allowed_clarification_targets"]},
                {(t["target_id"], t["reason_code"]) for t in en["allowed_clarification_targets"]},
                key,
            )
            self.assertEqual(
                Counter(e["guard_code"] for e in ru["adversarial_examples"]),
                Counter(e["guard_code"] for e in en["adversarial_examples"]),
                key,
            )
            self.assertEqual(ru["expected_outcome"], en["expected_outcome"], key)

    def test_review_matrix_documents_privacy_and_model_context_boundary(self):
        self.assertIn("24", self.review)
        self.assertIn("R0/R1/R2", self.review)
        self.assertIn("latent", self.review.lower())
        self.assertIn("model-visible", self.review.lower())
        self.assertIn("preserve unknown", self.review.lower())
        self.assertIn("prompt injection", self.review.lower())
        self.assertIn("research-only", self.review.lower())


if __name__ == "__main__":
    unittest.main()
