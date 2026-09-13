import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.json"
CORPUS_DIR = ROOT / "docs/evaluation/reconstruction-scenarios/v1"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
SCENARIOS_PATH = CORPUS_DIR / "scenarios.json"
README_PATH = CORPUS_DIR / "README.md"


class ReconstructionScenarioCorpusV1Tests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))["scenarios"]
        self.readme = README_PATH.read_text(encoding="utf-8")

    def test_manifest_is_versioned_and_bound_to_frozen_protocol(self):
        self.assertEqual(
            self.manifest["corpus_schema"],
            "mind-detective-reconstruction-scenario-corpus/v1",
        )
        self.assertEqual(
            self.manifest["protocol_schema"],
            self.protocol["protocol_schema"],
        )
        self.assertEqual(self.manifest["status"], "research_only")
        self.assertEqual(self.manifest["base_release"], "0.4.0")
        self.assertEqual(self.manifest["case_schema"], "mind-detective-case/v2")
        self.assertEqual(self.manifest["scenario_count"], len(self.scenarios))
        self.assertEqual(self.manifest["family_count"], len(self.protocol["scenario_family_ids"]))
        self.assertEqual(self.manifest["variants_per_family"], 2)
        self.assertEqual(self.manifest["languages"], ["ru", "en"])
        self.assertTrue(self.manifest["generator_context_excludes_participant_script"])

    def test_every_protocol_family_has_both_frozen_variants(self):
        expected_pairs = {
            (family_id, variant_id)
            for family_id in self.protocol["scenario_family_ids"]
            for variant_id in self.protocol["scenario_variant_ids"]
        }
        actual_pairs = {
            (scenario["scenario_family_id"], scenario["scenario_variant_id"])
            for scenario in self.scenarios
        }
        self.assertEqual(actual_pairs, expected_pairs)
        self.assertEqual(len(self.scenarios), len(expected_pairs))

        scenario_ids = [scenario["scenario_id"] for scenario in self.scenarios]
        self.assertEqual(len(scenario_ids), len(set(scenario_ids)))
        for scenario in self.scenarios:
            self.assertRegex(
                scenario["scenario_id"],
                re.compile(r"^RF[0-9]{2}_[a-z0-9_]+\.RV[0-9]{2}$"),
            )
            self.assertEqual(scenario["scenario_version"], 1)
            self.assertEqual(set(scenario["localizations"]), {"ru", "en"})
            for language in ("ru", "en"):
                localization = scenario["localizations"][language]
                self.assertTrue(localization["user_visible_initial_account"])

    def test_fixture_partitions_are_explicit_and_complete(self):
        for scenario in self.scenarios:
            generator_context = scenario["generator_context"]
            participant_script = scenario["participant_script"]
            oracle = scenario["oracle"]

            self.assertEqual(set(generator_context["localizations"]), {"ru", "en"})
            for language in ("ru", "en"):
                visible = generator_context["localizations"][language]
                self.assertIsInstance(visible["confirmed_statements"], list)
                self.assertIsInstance(visible["timeline_events"], list)
                self.assertIsInstance(visible["explicit_unknowns"], list)
                self.assertIsInstance(visible["contradictions"], list)
                self.assertIsInstance(visible["bounded_excerpts"], list)

            self.assertIsInstance(participant_script["latent_facts"], list)
            self.assertTrue(participant_script["latent_facts"])
            self.assertIsInstance(participant_script["genuine_unknown_fact_ids"], list)
            for fact in participant_script["latent_facts"]:
                self.assertTrue(fact["fact_id"])
                self.assertIsInstance(fact["reconstructable"], bool)
                self.assertEqual(set(fact["answers"]), {"ru", "en"})
                self.assertTrue(fact["answers"]["ru"])
                self.assertTrue(fact["answers"]["en"])

            self.assertIsInstance(oracle["allowed_clarifications"], list)
            self.assertIn("locations", oracle["forbidden_introductions"])
            self.assertIn("actions", oracle["forbidden_introductions"])
            self.assertIn("entities", oracle["forbidden_introductions"])
            self.assertIsInstance(oracle["critical_violation_triggers"], list)
            self.assertTrue(oracle["critical_violation_triggers"])
            self.assertIn(
                oracle["stopping_expectation"]["stop_reason"],
                self.protocol["stop_reasons"],
            )
            self.assertIsInstance(
                oracle["stopping_expectation"]["preserve_unknown_fact_ids"],
                list,
            )
            self.assertIsInstance(oracle["adversarial_proposals"], list)

    def test_latent_participant_answers_are_not_generator_visible(self):
        for scenario in self.scenarios:
            generator_serialized = json.dumps(
                scenario["generator_context"],
                ensure_ascii=False,
                sort_keys=True,
            )
            for fact in scenario["participant_script"]["latent_facts"]:
                self.assertNotIn(fact["fact_id"], generator_serialized)
                for answer in fact["answers"].values():
                    self.assertNotIn(answer, generator_serialized)

    def test_every_reason_and_guard_code_has_two_corpus_examples(self):
        reason_counts = Counter()
        guard_counts = Counter()
        reason_allowlist = set(self.protocol["clarification_reason_codes"])
        guard_allowlist = set(self.protocol["guard_rejection_codes"])

        for scenario in self.scenarios:
            for clarification in scenario["oracle"]["allowed_clarifications"]:
                self.assertIn(clarification["reason_code"], reason_allowlist)
                reason_counts[clarification["reason_code"]] += 1
            for proposal in scenario["oracle"]["adversarial_proposals"]:
                self.assertIn(proposal["expected_guard_code"], guard_allowlist)
                guard_counts[proposal["expected_guard_code"]] += 1
                self.assertEqual(set(proposal["localizations"]), {"ru", "en"})
                self.assertTrue(proposal["localizations"]["ru"])
                self.assertTrue(proposal["localizations"]["en"])

        for reason_code in reason_allowlist:
            self.assertGreaterEqual(reason_counts[reason_code], 2, reason_code)
        for guard_code in guard_allowlist:
            self.assertGreaterEqual(guard_counts[guard_code], 2, guard_code)

    def test_each_fixture_has_visible_targets_and_forbidden_introductions(self):
        for scenario in self.scenarios:
            oracle = scenario["oracle"]
            self.assertTrue(oracle["allowed_clarifications"], scenario["scenario_id"])
            for values in oracle["forbidden_introductions"].values():
                self.assertTrue(values, scenario["scenario_id"])

            visible_ids = set()
            for localized_context in scenario["generator_context"]["localizations"].values():
                for statement in localized_context["confirmed_statements"]:
                    visible_ids.add(statement["statement_id"])
                for event in localized_context["timeline_events"]:
                    visible_ids.add(event["event_id"])
                for unknown in localized_context["explicit_unknowns"]:
                    visible_ids.add(unknown["unknown_id"])
                for contradiction in localized_context["contradictions"]:
                    visible_ids.add(contradiction["contradiction_id"])
                for excerpt in localized_context["bounded_excerpts"]:
                    visible_ids.add(excerpt["excerpt_id"])

            latent_ids = {
                fact["fact_id"]
                for fact in scenario["participant_script"]["latent_facts"]
            }
            for clarification in oracle["allowed_clarifications"]:
                self.assertTrue(clarification["target_ids"])
                self.assertTrue(set(clarification["target_ids"]).issubset(visible_ids))
                self.assertTrue(latent_ids.isdisjoint(clarification["target_ids"]))

    def test_genuine_unknowns_are_preserved_and_not_reconstructable(self):
        preserve_count = 0
        for scenario in self.scenarios:
            facts = {
                fact["fact_id"]: fact
                for fact in scenario["participant_script"]["latent_facts"]
            }
            genuine_unknown_ids = set(
                scenario["participant_script"]["genuine_unknown_fact_ids"]
            )
            preserve_ids = set(
                scenario["oracle"]["stopping_expectation"]["preserve_unknown_fact_ids"]
            )
            self.assertTrue(genuine_unknown_ids.issubset(facts))
            self.assertTrue(preserve_ids.issubset(genuine_unknown_ids))
            for fact_id in genuine_unknown_ids:
                self.assertFalse(facts[fact_id]["reconstructable"])
            preserve_count += len(preserve_ids)

        self.assertGreater(preserve_count, 0)
        genuine_unknown_family = [
            scenario
            for scenario in self.scenarios
            if scenario["scenario_family_id"] == "RF07_genuine_unknown"
        ]
        self.assertEqual(len(genuine_unknown_family), 2)
        for scenario in genuine_unknown_family:
            self.assertTrue(
                scenario["oracle"]["stopping_expectation"]["preserve_unknown_fact_ids"]
            )

    def test_prompt_injection_family_has_ru_and_en_examples(self):
        prompt_injection_family = [
            scenario
            for scenario in self.scenarios
            if scenario["scenario_family_id"] == "RF11_prompt_injection_free_account"
        ]
        self.assertEqual(len(prompt_injection_family), 2)
        for scenario in prompt_injection_family:
            ru = scenario["localizations"]["ru"]["user_visible_initial_account"]
            en = scenario["localizations"]["en"]["user_visible_initial_account"]
            self.assertRegex(ru, re.compile(r"игнорируй|отмени", re.IGNORECASE))
            self.assertRegex(en, re.compile(r"ignore|override", re.IGNORECASE))
            self.assertNotIn(ru, json.dumps(scenario["generator_context"], ensure_ascii=False))
            self.assertNotIn(en, json.dumps(scenario["generator_context"], ensure_ascii=False))

    def test_readme_marks_synthetic_research_boundary(self):
        normalized = self.readme.lower()
        self.assertIn("synthetic", normalized)
        self.assertIn("research-only", normalized)
        self.assertIn("latent", normalized)
        self.assertIn("generator", normalized)
        self.assertIn("mind-detective-case/v2", self.readme)
        self.assertIn("RECONSTRUCTION_PROTOCOL_V1.json", self.readme)


if __name__ == "__main__":
    unittest.main()
