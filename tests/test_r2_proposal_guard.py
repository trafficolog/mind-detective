import ast
import copy
import json
import unittest
from pathlib import Path

from scripts import reconstruction_r1 as r1
from scripts import reconstruction_r2_guard as r2_guard

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.json"
CORPUS_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_SCENARIO_CORPUS_V1.json"
REVIEW_PATH = ROOT / "docs/evaluation/R2_PROPOSAL_GUARD_V1.md"
SCRIPT_PATH = ROOT / "scripts/reconstruction_r2_guard.py"


class R2ProposalGuardTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        self.scenarios = self.corpus["scenarios"]

    def _guard_for_target(self, scenario, target, proposal):
        return r2_guard.evaluate_proposal(
            proposal,
            language_code=scenario["language_code"],
            expected_reason_code=target["reason_code"],
            allowed_target_ids=target["target_ids"],
            model_visible_context=scenario["model_visible_context"],
            forbidden_introductions=scenario["forbidden_introductions"],
        )

    def test_identity_and_guard_vocabulary_match_frozen_protocol(self):
        self.assertEqual(r2_guard.GUARD_SCHEMA, "mind-detective-reconstruction-r2-guard/v1")
        self.assertEqual(r2_guard.GENERATOR_KIND, "r2_model_candidate")
        self.assertEqual(
            tuple(r2_guard.GUARD_REJECTION_CODES),
            tuple(self.protocol["guard_rejection_codes"]),
        )
        self.assertEqual(r2_guard.SCHEMA_FAILURE_REASON, "schema_invalid")
        self.assertEqual(r2_guard.GUARD_FAILURE_REASON, "guard_rejected")
        self.assertIn(r2_guard.SCHEMA_FAILURE_REASON, self.protocol["technical_failure_reasons"])
        self.assertIn(r2_guard.GUARD_FAILURE_REASON, self.protocol["technical_failure_reasons"])

    def test_exact_proposal_schema_is_required_and_unknown_fields_fail_closed(self):
        valid = {
            "question": "What do you remember about the interval between these events?",
            "reason_code": "timeline_gap",
            "target_ids": ["evt_1", "evt_2"],
        }
        context = {
            "language_code": "en",
            "supported_entities": ["lost_item"],
            "supported_locations": [],
            "supported_actions": [],
            "timeline_refs": ["evt_1", "evt_2"],
            "statement_refs": [],
            "unknown_markers": [],
            "contradiction_refs": [],
        }
        forbidden = {"entities": [], "locations": [], "actions": []}

        malformed = [
            None,
            [],
            [valid],
            "not an object",
            7,
            True,
            {**valid, "probability": 0.8},
            {**valid, "confidence": "high"},
            {**valid, "suggested_answer": "car"},
            {"reason_code": "timeline_gap", "target_ids": ["evt_1"]},
            {**valid, "question": ""},
            {**valid, "question": 123},
            {**valid, "reason_code": "not_a_reason"},
            {**valid, "target_ids": []},
            {**valid, "target_ids": ["evt_1", "evt_1"]},
            {**valid, "target_ids": ["evt_1", 2]},
        ]
        for candidate in malformed:
            with self.subTest(candidate=candidate):
                result = r2_guard.evaluate_proposal(
                    candidate,
                    language_code="en",
                    expected_reason_code="timeline_gap",
                    allowed_target_ids=["evt_1", "evt_2"],
                    model_visible_context=context,
                    forbidden_introductions=forbidden,
                )
                self.assertEqual(
                    result,
                    {
                        "decision": "abstain",
                        "guard_schema": r2_guard.GUARD_SCHEMA,
                        "technical_failure_reason": "schema_invalid",
                    },
                )

    def test_reason_and_target_scope_must_match_current_approved_opportunity(self):
        context = {
            "language_code": "en",
            "supported_entities": ["lost_item"],
            "supported_locations": [],
            "supported_actions": [],
            "timeline_refs": ["evt_1", "evt_2", "evt_3"],
            "statement_refs": [],
            "unknown_markers": [],
            "contradiction_refs": [],
        }
        forbidden = {"entities": [], "locations": [], "actions": []}
        wrong_reason = {
            "question": "Which place did you mean?",
            "reason_code": "ambiguous_location",
            "target_ids": ["evt_1"],
        }
        wrong_target = {
            "question": "What do you remember about the interval?",
            "reason_code": "timeline_gap",
            "target_ids": ["evt_3"],
        }
        for candidate in (wrong_reason, wrong_target):
            result = r2_guard.evaluate_proposal(
                candidate,
                language_code="en",
                expected_reason_code="timeline_gap",
                allowed_target_ids=["evt_1", "evt_2"],
                model_visible_context=context,
                forbidden_introductions=forbidden,
            )
            self.assertEqual(result["decision"], "abstain")
            self.assertEqual(result["technical_failure_reason"], "schema_invalid")
            self.assertNotIn("proposal", result)

    def test_all_r1_reviewed_templates_pass_guard_for_same_approved_target(self):
        for scenario in self.scenarios:
            for target in scenario["allowed_clarification_targets"]:
                proposal = r1.build_proposal(
                    language_code=scenario["language_code"],
                    reason_code=target["reason_code"],
                    target_ids=target["target_ids"],
                )
                result = self._guard_for_target(scenario, target, proposal)
                self.assertEqual(result["decision"], "show", scenario["scenario_id"])
                self.assertEqual(result["guard_schema"], r2_guard.GUARD_SCHEMA)
                self.assertEqual(result["proposal"], proposal)

    def test_every_corpus_adversarial_example_is_blocked_with_exact_frozen_guard_code(self):
        observed_codes = set()
        for scenario in self.scenarios:
            target = scenario["allowed_clarification_targets"][0]
            for example in scenario["adversarial_examples"]:
                candidate = {
                    "question": example["candidate_question"],
                    "reason_code": target["reason_code"],
                    "target_ids": target["target_ids"],
                }
                original_scenario = copy.deepcopy(scenario)
                result = self._guard_for_target(scenario, target, candidate)
                self.assertEqual(
                    result,
                    {
                        "decision": "block",
                        "guard_schema": r2_guard.GUARD_SCHEMA,
                        "guard_code": example["guard_code"],
                        "technical_failure_reason": "guard_rejected",
                    },
                    scenario["scenario_id"],
                )
                observed_codes.add(example["guard_code"])
                self.assertEqual(scenario, original_scenario, scenario["scenario_id"])

        self.assertEqual(observed_codes, set(self.protocol["guard_rejection_codes"]))

    def test_block_and_abstain_results_never_echo_raw_question_text(self):
        scenario = self.scenarios[0]
        target = scenario["allowed_clarification_targets"][0]
        adversarial = scenario["adversarial_examples"][0]
        blocked = self._guard_for_target(
            scenario,
            target,
            {
                "question": adversarial["candidate_question"],
                "reason_code": target["reason_code"],
                "target_ids": target["target_ids"],
            },
        )
        abstained = self._guard_for_target(
            scenario,
            target,
            {
                "question": adversarial["candidate_question"],
                "reason_code": target["reason_code"],
                "target_ids": target["target_ids"],
                "raw_model_output": "must never be accepted",
            },
        )
        self.assertNotIn("question", json.dumps(blocked, ensure_ascii=False))
        self.assertNotIn(adversarial["candidate_question"], json.dumps(blocked, ensure_ascii=False))
        self.assertNotIn("question", json.dumps(abstained, ensure_ascii=False))
        self.assertNotIn(adversarial["candidate_question"], json.dumps(abstained, ensure_ascii=False))

    def test_guard_imports_only_stdlib_and_stays_outside_case_mutation_surface(self):
        tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertLessEqual(imported_roots, {"__future__", "re", "collections", "typing"})

    def test_review_document_freezes_research_only_and_existing_safety_boundary(self):
        review = REVIEW_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("research-only", review)
        self.assertIn("provider-agnostic", review)
        self.assertIn("case v2", review)
        self.assertIn("no case mutation", review)
        self.assertIn("existing safety ingress", review)
        self.assertIn("limit_and_escalate", review)
        self.assertIn("fixture deny terms", review)
        self.assertIn("not a production provider contract", review)


if __name__ == "__main__":
    unittest.main()
