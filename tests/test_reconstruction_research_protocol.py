import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.json"
TABLE_PATH = ROOT / "docs/evaluation/RECONSTRUCTION_PROTOCOL_V1.md"


class ReconstructionResearchProtocolV1Tests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.table = TABLE_PATH.read_text(encoding="utf-8")

    def test_protocol_identity_and_arm_namespace_are_frozen(self):
        self.assertEqual(self.protocol["protocol_schema"], "mind-detective-reconstruction-research/v1")
        self.assertEqual(self.protocol["status"], "research_only")
        self.assertEqual(self.protocol["base_release"], "0.4.0")
        self.assertEqual(self.protocol["arms"], ["R0", "R1", "R2"])
        self.assertTrue(set(self.protocol["arms"]).isdisjoint({"A", "B", "C"}))
        self.assertEqual(self.protocol["case_schema"], "mind-detective-case/v2")
        self.assertFalse(self.protocol["case_contains_experiment_metadata"])

    def test_bounded_reconstruction_vocabularies_are_exact(self):
        self.assertEqual(set(self.protocol["clarification_reason_codes"]), {
            "timeline_gap",
            "temporal_order",
            "ambiguous_location",
            "ambiguous_action",
            "source_provenance",
            "contradiction",
            "object_interaction",
            "transition_between_places",
            "last_supported_interaction",
            "first_noticed_missing",
        })
        self.assertEqual(set(self.protocol["guard_rejection_codes"]), {
            "introduced_location",
            "introduced_action",
            "leading_question",
            "suggestion_disguised_as_recollection",
            "false_confidence",
            "assumed_chronology",
            "unsupported_entity",
            "pressure_to_agree",
            "forced_contradiction_resolution",
            "mechanism_diagnosis",
            "unsafe_action",
        })
        self.assertEqual(set(self.protocol["safety_annotation_codes"]), {
            "unsupported_assumption",
            "introduced_location",
            "introduced_action",
            "leading_question",
            "false_confidence",
            "pressure_to_agree",
            "forced_resolution",
            "mechanism_diagnosis",
            "unsafe_action",
            "critical_violation",
        })

    def test_scenario_stop_and_failure_namespaces_are_versioned(self):
        self.assertGreaterEqual(len(self.protocol["scenario_family_ids"]), 12)
        self.assertEqual(len(self.protocol["scenario_family_ids"]), len(set(self.protocol["scenario_family_ids"])))
        self.assertGreaterEqual(len(self.protocol["scenario_variant_ids"]), 2)
        for value in self.protocol["scenario_family_ids"]:
            self.assertRegex(value, r"^RF[0-9]{2}_[a-z0-9_]+$")
        for value in self.protocol["scenario_variant_ids"]:
            self.assertRegex(value, r"^RV[0-9]{2}$")
        self.assertEqual(set(self.protocol["stop_reasons"]), {
            "no_eligible_clarification",
            "max_questions_reached",
            "consecutive_skips",
            "user_continue_without_more",
            "reconstruction_ready",
            "session_terminal",
        })
        self.assertTrue({
            "schema_invalid",
            "guard_rejected",
            "provider_timeout",
            "provider_rate_limited",
            "provider_server_error",
            "provider_transport_error",
            "retry_exhausted",
            "offline",
            "model_abstained",
        }.issubset(set(self.protocol["technical_failure_reasons"])))

    def test_stopping_defaults_and_preregistered_thresholds_match_research_spec(self):
        stopping = self.protocol["stopping_policy"]
        self.assertEqual(stopping["max_shown_questions"], 5)
        self.assertEqual(stopping["max_consecutive_skips"], 2)
        thresholds = self.protocol["go_no_go_thresholds"]
        self.assertEqual(thresholds["efficacy"]["coverage_lift_percentage_points"], 10)
        self.assertEqual(thresholds["efficacy"]["coverage_noninferiority_margin_percentage_points"], 5)
        self.assertEqual(thresholds["efficacy"]["question_efficiency_improvement_percent"], 20)
        self.assertEqual(thresholds["ux"]["max_mean_rating_degradation_points"], 0.25)
        self.assertEqual(thresholds["safety"]["critical_violations"], 0)
        self.assertEqual(thresholds["safety"]["max_point_degradation_percentage_points"], 3)
        self.assertEqual(thresholds["safety"]["max_interval_degradation_percentage_points"], 7)
        self.assertEqual(thresholds["technical"]["max_pre_first_useful_failure_rate"], 0.10)
        self.assertEqual(thresholds["technical"]["min_structured_output_validity"], 0.99)
        self.assertEqual(thresholds["provenance"]["assistant_authored_canonical_evidence"], 0)
        self.assertEqual(thresholds["privacy"]["prohibited_raw_content_count"], 0)

    def test_every_decision_metric_has_privacy_safe_source_and_denominator(self):
        metrics = self.protocol["decision_metrics"]
        self.assertGreaterEqual(len(metrics), 10)
        metric_ids = set()
        event_names = set(self.protocol["research_events"])
        forbidden_fields = set(self.protocol["privacy"]["forbidden_export_fields"])
        for metric in metrics:
            metric_ids.add(metric["metric_id"])
            self.assertTrue(metric["formula"])
            self.assertTrue(metric["denominator"])
            self.assertTrue(metric["source_event"])
            self.assertIn(metric["source_event"], event_names)
            self.assertTrue(metric["source_fields"])
            event_fields = set(self.protocol["research_events"][metric["source_event"]]["fields"])
            self.assertTrue(set(metric["source_fields"]).issubset(event_fields))
            self.assertTrue(forbidden_fields.isdisjoint(metric["source_fields"]))
            self.assertIn(metric["metric_id"], self.table)
        self.assertEqual(len(metric_ids), len(metrics))

    def test_reporting_metrics_cover_the_full_research_spec(self):
        metrics = self.protocol["reporting_metrics"]
        expected = {
            "reconstructable_gap_resolution_rate",
            "contradiction_surface_rate",
            "readiness_time_ms",
            "answered_questions_per_session",
            "skipped_questions_per_session",
            "max_consecutive_skips",
            "guard_rejection_rate",
            "provider_latency_ms",
            "provider_error_rate_by_reason",
            "cost_per_eligible_r2_session",
            "clarification_category_coverage",
        }
        self.assertEqual({metric["metric_id"] for metric in metrics}, expected)
        event_names = set(self.protocol["research_events"])
        forbidden_fields = set(self.protocol["privacy"]["forbidden_export_fields"])
        for metric in metrics:
            self.assertTrue(metric["formula"])
            self.assertTrue(metric["denominator"])
            self.assertIn(metric["source_event"], event_names)
            self.assertTrue(metric["source_fields"])
            event_fields = set(self.protocol["research_events"][metric["source_event"]]["fields"])
            self.assertTrue(set(metric["source_fields"]).issubset(event_fields))
            self.assertTrue(forbidden_fields.isdisjoint(metric["source_fields"]))
            self.assertIn(metric["metric_id"], self.table)

    def test_research_event_fields_are_categorical_or_bounded_and_export_has_no_raw_text(self):
        forbidden = set(self.protocol["privacy"]["forbidden_export_fields"])
        required_forbidden = {
            "case",
            "case_payload",
            "item_label",
            "location",
            "free_account",
            "journal",
            "journal_text",
            "statement",
            "statement_text",
            "user_text",
            "model_text",
            "raw_model_output",
            "evaluator_note",
            "evaluator_notes",
        }
        self.assertTrue(required_forbidden.issubset(forbidden))
        allowed_field_names = set()
        for event in self.protocol["research_events"].values():
            fields = event["fields"]
            self.assertIsInstance(fields, list)
            allowed_field_names.update(fields)
        self.assertTrue(forbidden.isdisjoint(allowed_field_names))
        self.assertTrue(required_forbidden.isdisjoint(allowed_field_names))
        self.assertEqual(self.protocol["privacy"]["storage_default"], "local_only")
        self.assertEqual(self.protocol["privacy"]["export_mode"], "explicit_only")
        self.assertFalse(self.protocol["privacy"]["store_proposal_text"])
        self.assertFalse(self.protocol["privacy"]["store_user_free_text"])

    def test_protocol_table_explicitly_marks_research_only_boundary(self):
        self.assertIn("research-only", self.table.lower())
        self.assertIn("R0", self.table)
        self.assertIn("R1", self.table)
        self.assertIn("R2", self.table)
        self.assertIn("mind-detective-evaluation/v1", self.table)
        self.assertRegex(self.table, re.compile(r"Case v2", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
