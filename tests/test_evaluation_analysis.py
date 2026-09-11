from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_evaluation import (
    EvaluationBundle,
    EvaluationDataError,
    TimeObservation,
    analyze,
    load_evaluation_export,
    participant_clustered_bootstrap,
    reconstruct_time_observation,
    restricted_mean_time,
)

FIXTURES = Path(__file__).parent / "fixtures" / "evaluation"


class EvaluationAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.staged_path = FIXTURES / "staged-v1.json"
        self.external_path = FIXTURES / "external-a-v1.json"

    def test_restricted_mean_time_hand_calculated_cases(self) -> None:
        self.assertEqual(restricted_mean_time([TimeObservation(0.0, True)]), 0.0)
        self.assertEqual(
            restricted_mean_time(
                [TimeObservation(100.0, True), TimeObservation(200.0, False)]
            ),
            350.0,
        )
        self.assertEqual(
            restricted_mean_time(
                [TimeObservation(100.0, False), TimeObservation(200.0, False)]
            ),
            600.0,
        )

    def test_fixture_keeps_abandoned_incomplete_fallback_and_duplicate_visible(self) -> None:
        bundle = load_evaluation_export(self.staged_path)
        report = analyze(bundle, seed=1729, bootstrap=100)["staged"]

        self.assertEqual(report["sample"]["protocol_complete_participants"], 2)
        self.assertEqual(report["sample"]["participants_total"], 3)
        self.assertEqual(report["sample"]["participants_per_cell"]["1"], 1)
        self.assertEqual(report["sample"]["participants_per_cell"]["2"], 1)
        self.assertEqual(report["sample"]["participants_per_cell"]["3"], 0)
        self.assertEqual(report["sample"]["started_sessions"], 9)
        self.assertEqual(report["outcomes"]["C"]["abandoned"], 1)
        self.assertEqual(report["readiness"]["pre_useful_fallback_sessions_C"], 1)
        self.assertGreater(report["readiness"]["pre_useful_fallback_rate_C"], 0.0)
        self.assertGreater(report["secondary"]["duplicate_check_B_mean"], 0.0)
        self.assertEqual(report["secondary"]["missing_rating_sessions"], 5)
        self.assertEqual(report["sample"]["minimum_sample_status"], "inconclusive")

    def test_first_useful_action_uses_shown_time_and_censors_abandonment(self) -> None:
        bundle = load_evaluation_export(self.staged_path)
        grouped: dict[str, list[object]] = {}
        for event in bundle.events:
            grouped.setdefault(event.evaluation_session_id, []).append(event)
        ordered = {
            key: sorted(values, key=lambda event: (event.at, event.event_id))
            for key, values in grouped.items()
        }

        useful = next(session for session in bundle.sessions if session.evaluation_session_id == "s1")
        abandoned = next(session for session in bundle.sessions if session.outcome == "abandoned")
        useful_observation = reconstruct_time_observation(
            useful,
            ordered[useful.evaluation_session_id],
        )
        abandoned_observation = reconstruct_time_observation(
            abandoned,
            ordered[abandoned.evaluation_session_id],
        )
        self.assertEqual(useful_observation, TimeObservation(seconds=45.0, event_observed=True))
        self.assertEqual(
            abandoned_observation,
            TimeObservation(seconds=180.0, event_observed=False),
        )

    def test_bootstrap_is_deterministic_by_seed(self) -> None:
        bundle = load_evaluation_export(self.staged_path)
        grouped: dict[str, list[object]] = {}
        for event in bundle.events:
            grouped.setdefault(event.evaluation_session_id, []).append(event)
        first = participant_clustered_bootstrap(bundle.sessions, grouped, seed=77, draws=100)
        second = participant_clustered_bootstrap(bundle.sessions, grouped, seed=77, draws=100)
        self.assertEqual(first, second)
        self.assertIsNotNone(first["rmtua_percent_change"])

    def test_external_a_is_contextual_only(self) -> None:
        staged = load_evaluation_export(self.staged_path)
        external = load_evaluation_export(self.external_path)
        report = analyze(staged, external_a=external, seed=1729, bootstrap=20)
        contextual = report["contextual_external_a"]
        self.assertEqual(contextual["sessions"], 2)
        self.assertFalse(contextual["used_in_B_vs_C_efficacy"])
        self.assertFalse(contextual["used_in_B_vs_C_safety"])
        self.assertNotIn("A", report["staged"]["primary"])

    def test_sensitive_key_is_rejected_anywhere(self) -> None:
        payload = json.loads(self.staged_path.read_text(encoding="utf-8"))
        payload["events"][0]["metadata"]["item_label"] = "private"
        with self.assertRaisesRegex(EvaluationDataError, "MD_EVAL_SENSITIVE_KEY"):
            self._load_payload(payload)

    def test_unknown_event_metadata_is_rejected(self) -> None:
        payload = json.loads(self.staged_path.read_text(encoding="utf-8"))
        payload["events"][0]["metadata"]["custom_note"] = "not allowed"
        with self.assertRaisesRegex(EvaluationDataError, "MD_EVAL_METADATA_KEY"):
            self._load_payload(payload)

    def test_invalid_handoff_score_is_rejected(self) -> None:
        payload = json.loads(self.staged_path.read_text(encoding="utf-8"))
        handoff = next(event for event in payload["events"] if event["event"] == "handoff_rubric")
        handoff["metadata"]["handoff_score"] = 0
        with self.assertRaisesRegex(EvaluationDataError, "MD_EVAL_HANDOFF_SCORE"):
            self._load_payload(payload)

    def test_wrong_external_arm_is_rejected(self) -> None:
        payload = json.loads(self.external_path.read_text(encoding="utf-8"))
        payload["sessions"][0]["arm"] = "B"
        with self.assertRaisesRegex(EvaluationDataError, "MD_EVAL_EXTERNAL_ARM"):
            self._load_payload(payload)

    def test_duplicate_ids_are_rejected(self) -> None:
        payload = json.loads(self.staged_path.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(payload["events"][0])
        duplicate["at"] = "2026-09-11T13:00:00Z"
        payload["events"].append(duplicate)
        with self.assertRaisesRegex(EvaluationDataError, "MD_EVAL_DUPLICATE_EVENT"):
            self._load_payload(payload)

    def _load_payload(self, payload: dict[str, object]) -> EvaluationBundle:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return load_evaluation_export(path)


if __name__ == "__main__":
    unittest.main()
