import copy
import json
import unittest
from pathlib import Path

from scripts import reconstruction_r1 as r1

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.json"
CORPUS_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_SCENARIO_CORPUS_V1.json"
REVIEW_PATH = ROOT / "docs/evaluation/R1_DETERMINISTIC_GUIDANCE_V1.md"

REVIEWED_TEMPLATES = {
    "timeline_gap": {
        "ru": "Что вы помните о промежутке между этими событиями?",
        "en": "What do you remember about the interval between these events?",
    },
    "temporal_order": {
        "ru": "В каком порядке, насколько вы помните, происходили эти события?",
        "en": "What order do you remember these events occurring in?",
    },
    "ambiguous_location": {
        "ru": "Какое именно место вы имели в виду в этом фрагменте?",
        "en": "Which place did you mean in this part of the account?",
    },
    "ambiguous_action": {
        "ru": "Какое именно действие вы имели в виду в этом фрагменте?",
        "en": "Which action did you mean in this part of the account?",
    },
    "source_provenance": {
        "ru": "Это относится к тому, что вы помните в этом случае, к обычной привычке, к наблюдению или к неопределённости?",
        "en": "Is this something you remember in this case, a usual habit, an observation, or something you are unsure about?",
    },
    "contradiction": {
        "ru": "Эти утверждения расходятся. Что из этого вы действительно помните, если можете уточнить?",
        "en": "These statements conflict. What, if anything, do you actually remember well enough to clarify?",
    },
    "object_interaction": {
        "ru": "Что вы помните о взаимодействии с потерянной вещью в этот момент?",
        "en": "What do you remember about interacting with the lost item at this point?",
    },
    "transition_between_places": {
        "ru": "Что вы помните о переходе между уже отмеченными событиями или местами?",
        "en": "What do you remember about the transition between the already recorded events or places?",
    },
    "last_supported_interaction": {
        "ru": "Какое из уже описанных взаимодействий с вещью вы помните последним?",
        "en": "Which of the already described interactions with the item do you remember as the last one?",
    },
    "first_noticed_missing": {
        "ru": "Когда в уже описанной последовательности вы впервые заметили отсутствие вещи?",
        "en": "When in the already described sequence did you first notice the item was missing?",
    },
}


class R1DeterministicClarificationTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        self.scenarios = self.corpus["scenarios"]

    def test_frozen_identity_taxonomy_and_stopping_policy_match_protocol(self):
        self.assertEqual(r1.R1_SCHEMA, "mind-detective-reconstruction-r1/v1")
        self.assertEqual(r1.GENERATOR_KIND, "r1_deterministic")
        self.assertEqual(tuple(r1.REASON_PRIORITY), tuple(self.protocol["clarification_reason_codes"]))
        self.assertEqual(r1.MAX_SHOWN_QUESTIONS, self.protocol["stopping_policy"]["max_shown_questions"])
        self.assertEqual(r1.MAX_CONSECUTIVE_SKIPS, self.protocol["stopping_policy"]["max_consecutive_skips"])
        self.assertFalse(self.protocol["stopping_policy"]["model_may_decide_completion"])

    def test_every_reason_code_has_exact_reviewed_ru_en_template(self):
        self.assertEqual(set(REVIEWED_TEMPLATES), set(self.protocol["clarification_reason_codes"]))
        self.assertEqual(r1.QUESTION_TEMPLATES, REVIEWED_TEMPLATES)
        for reason_code in self.protocol["clarification_reason_codes"]:
            for language_code in ("ru", "en"):
                proposal = r1.build_proposal(
                    language_code=language_code,
                    reason_code=reason_code,
                    target_ids=["target_1", "target_2"],
                )
                self.assertEqual(set(proposal), {"question", "reason_code", "target_ids"})
                self.assertEqual(proposal["question"], REVIEWED_TEMPLATES[reason_code][language_code])
                self.assertEqual(proposal["reason_code"], reason_code)
                self.assertEqual(proposal["target_ids"], ["target_1", "target_2"])
                self.assertEqual(
                    proposal,
                    r1.build_proposal(
                        language_code=language_code,
                        reason_code=reason_code,
                        target_ids=["target_1", "target_2"],
                    ),
                )

    def test_build_proposal_fails_closed_for_invalid_language_reason_or_targets(self):
        with self.assertRaises(ValueError):
            r1.build_proposal(language_code="de", reason_code="timeline_gap", target_ids=["evt_1"])
        with self.assertRaises(ValueError):
            r1.build_proposal(language_code="ru", reason_code="not_a_reason", target_ids=["evt_1"])
        with self.assertRaises(ValueError):
            r1.build_proposal(language_code="ru", reason_code="timeline_gap", target_ids=[])

    def test_all_corpus_targets_use_only_reviewed_templates_without_latent_or_forbidden_introductions(self):
        for scenario in self.scenarios:
            original = copy.deepcopy(scenario)
            forbidden = scenario["forbidden_introductions"]
            forbidden_terms = [
                *forbidden["entities"],
                *forbidden["locations"],
                *forbidden["actions"],
            ]

            for target in scenario["allowed_clarification_targets"]:
                proposal = r1.build_proposal(
                    language_code=scenario["language_code"],
                    reason_code=target["reason_code"],
                    target_ids=target["target_ids"],
                )
                self.assertEqual(
                    proposal["question"],
                    REVIEWED_TEMPLATES[target["reason_code"]][scenario["language_code"]],
                    scenario["scenario_id"],
                )
                question_folded = str(proposal["question"]).casefold()
                for term in forbidden_terms:
                    self.assertNotIn(str(term).casefold(), question_folded, scenario["scenario_id"])

            self.assertEqual(scenario, original, scenario["scenario_id"])

    def test_selector_is_order_independent_and_returns_only_approved_opportunity(self):
        for scenario in self.scenarios:
            opportunities = scenario["allowed_clarification_targets"]
            forward = r1.next_clarification(
                language_code=scenario["language_code"],
                opportunities=opportunities,
            )
            reverse = r1.next_clarification(
                language_code=scenario["language_code"],
                opportunities=list(reversed(opportunities)),
            )
            self.assertEqual(forward, reverse, scenario["scenario_id"])
            self.assertEqual(forward["kind"], "question")
            self.assertEqual(forward["generator_kind"], "r1_deterministic")
            selected = next(
                target for target in opportunities if target["target_id"] == forward["opportunity_id"]
            )
            self.assertEqual(forward["proposal"]["reason_code"], selected["reason_code"])
            self.assertEqual(forward["proposal"]["target_ids"], selected["target_ids"])

    def test_completed_opportunity_is_not_selected_again(self):
        opportunities = [
            {"target_id": "first", "reason_code": "timeline_gap", "target_ids": ["evt_1", "evt_2"]},
            {"target_id": "second", "reason_code": "temporal_order", "target_ids": ["evt_2", "evt_3"]},
        ]
        result = r1.next_clarification(
            language_code="en",
            opportunities=opportunities,
            completed_opportunity_ids={"first"},
        )
        self.assertEqual(result["kind"], "question")
        self.assertEqual(result["opportunity_id"], "second")

    def test_no_eligible_opportunity_abstains_with_frozen_stop_reason(self):
        result = r1.next_clarification(language_code="ru", opportunities=[])
        self.assertEqual(
            result,
            {
                "kind": "stop",
                "generator_kind": "r1_deterministic",
                "stop_reason": "no_eligible_clarification",
            },
        )

    def test_stopping_policy_is_deterministic_and_model_independent(self):
        opportunity = [
            {"target_id": "gap", "reason_code": "timeline_gap", "target_ids": ["evt_1", "evt_2"]}
        ]
        cases = [
            ({"session_terminal": True}, "session_terminal"),
            ({"reconstruction_ready": True}, "reconstruction_ready"),
            ({"user_continue_without_more": True}, "user_continue_without_more"),
            ({"shown_question_count": r1.MAX_SHOWN_QUESTIONS}, "max_questions_reached"),
            ({"consecutive_skip_count": r1.MAX_CONSECUTIVE_SKIPS}, "consecutive_skips"),
        ]
        for kwargs, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                result = r1.next_clarification(
                    language_code="ru",
                    opportunities=opportunity,
                    **kwargs,
                )
                self.assertEqual(result["kind"], "stop")
                self.assertEqual(result["stop_reason"], expected_reason)
                self.assertIn(expected_reason, self.protocol["stop_reasons"])

    def test_one_below_each_stopping_threshold_still_returns_a_question(self):
        opportunity = [
            {"target_id": "gap", "reason_code": "timeline_gap", "target_ids": ["evt_1", "evt_2"]}
        ]
        cases = [
            {"shown_question_count": r1.MAX_SHOWN_QUESTIONS - 1},
            {"consecutive_skip_count": r1.MAX_CONSECUTIVE_SKIPS - 1},
            {
                "shown_question_count": r1.MAX_SHOWN_QUESTIONS - 1,
                "consecutive_skip_count": r1.MAX_CONSECUTIVE_SKIPS - 1,
            },
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                result = r1.next_clarification(
                    language_code="en",
                    opportunities=opportunity,
                    **kwargs,
                )
                self.assertEqual(result["kind"], "question")
                self.assertEqual(result["opportunity_id"], "gap")

    def test_invalid_opportunity_fails_closed(self):
        invalid = [{"target_id": "x", "reason_code": "unsupported", "target_ids": ["evt_1"]}]
        with self.assertRaises(ValueError):
            r1.next_clarification(language_code="en", opportunities=invalid)

    def test_research_review_document_freezes_non_production_boundary(self):
        review = REVIEW_PATH.read_text(encoding="utf-8")
        lowered = review.lower()
        self.assertIn("research-only", lowered)
        self.assertIn("r1", lowered)
        self.assertIn("r2", lowered)
        self.assertIn("case v2", lowered)
        self.assertIn("no case mutation", lowered)
        self.assertIn("ru/en", lowered)
        self.assertIn("five", lowered)
        self.assertIn("two consecutive skips", lowered)


if __name__ == "__main__":
    unittest.main()
