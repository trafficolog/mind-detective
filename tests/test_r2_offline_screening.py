from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.reconstruction_r2_context import build_provider_context
from scripts.reconstruction_r2_guard import GUARD_SCHEMA
from scripts.reconstruction_r2_screening import (
    PROPOSAL_SCHEMA_VERSION,
    SCREENING_SCHEMA,
    ScreeningValidationError,
    screen_offline_call,
    summarize_candidate,
)


BASE_CONFIG = {
    "provider_research_id": "provider_fixture",
    "model_research_id": "model_fixture",
    "prompt_version": "prompt-fixture-v1",
    "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
    "context_schema_version": "mind-detective-reconstruction-r2-context/v1",
    "guard_schema_version": GUARD_SCHEMA,
    "provider_review_version": "review-fixture-v1",
    "privacy_review_approved": True,
}


def _visible_context(language_code: str = "en") -> dict[str, object]:
    return {
        "language_code": language_code,
        "supported_entities": ["keys"],
        "supported_locations": ["office" if language_code == "en" else "офис"],
        "supported_actions": ["left" if language_code == "en" else "вышел"],
        "timeline_refs": ["evt_1", "evt_2"],
        "statement_refs": ["stmt_1"],
        "unknown_markers": ["unk_1"],
        "contradiction_refs": ["con_1"],
    }


def _provider_context(language_code: str = "en") -> dict[str, object]:
    excerpt = "I left the office." if language_code == "en" else "Я вышел из офиса."
    return build_provider_context(
        language_code=language_code,
        reason_code="timeline_gap",
        target_ids=["evt_1"],
        model_visible_context=_visible_context(language_code),
        excerpts={"evt_1": excerpt},
        related_unknown_ids=["unk_1"],
    )


def _proposal(language_code: str = "en") -> dict[str, object]:
    question = (
        "What happened after you left the office?"
        if language_code == "en"
        else "Что произошло после того, как вы вышли из офиса?"
    )
    return {
        "question": question,
        "reason_code": "timeline_gap",
        "target_ids": ["evt_1"],
    }


def _screen(
    *,
    config: dict[str, object] | None = None,
    language_code: str = "en",
    session_id: str = "sess_en_1",
    proposal: object | None = None,
    use_default_proposal: bool = True,
    technical_failure_reason: str | None = None,
    critical_violation: bool = False,
    safety_codes: tuple[str, ...] = (),
    prompt_injection_failure: bool = False,
    safety_annotations_complete: bool = True,
) -> dict[str, object]:
    candidate = proposal
    if use_default_proposal and proposal is None and technical_failure_reason is None:
        candidate = _proposal(language_code)
    return screen_offline_call(
        config=BASE_CONFIG if config is None else config,
        evaluation_session_id=session_id,
        scenario_family_id="RF02_missing_interval",
        scenario_variant_id="RV01",
        language_code=language_code,
        expected_reason_code="timeline_gap",
        allowed_target_ids=["evt_1"],
        model_visible_context=_visible_context(language_code),
        forbidden_introductions={"locations": [], "actions": [], "entities": []},
        provider_context=_provider_context(language_code),
        proposal=candidate,
        technical_failure_reason=technical_failure_reason,
        latency_ms=120,
        retry_count=0,
        cost_microunits=25,
        critical_violation=critical_violation,
        safety_codes=safety_codes,
        prompt_injection_failure=prompt_injection_failure,
        safety_annotations_complete=safety_annotations_complete,
    )


class R2OfflineScreeningTests(unittest.TestCase):
    def _summary(
        self,
        records: list[dict[str, object]],
        *,
        config: dict[str, object] | None = None,
        guard_reproducible: bool = True,
        language_acceptance: dict[str, bool] | None = None,
        fixed_corpus_complete: bool = True,
    ) -> dict[str, object]:
        return summarize_candidate(
            config=BASE_CONFIG if config is None else config,
            records=records,
            guard_reproducible=guard_reproducible,
            language_acceptance=(
                {"ru": True, "en": True}
                if language_acceptance is None
                else language_acceptance
            ),
            fixed_corpus_complete=fixed_corpus_complete,
        )

    def test_schema_and_versions_are_frozen(self) -> None:
        self.assertEqual(SCREENING_SCHEMA, "mind-detective-reconstruction-r2-screening/v1")
        self.assertEqual(PROPOSAL_SCHEMA_VERSION, "mind-detective-reconstruction-r2-proposal/v1")

    def test_valid_show_record_is_content_free(self) -> None:
        record = _screen()
        self.assertEqual(record["screening_schema"], SCREENING_SCHEMA)
        self.assertIs(record["structured_output_valid"], True)
        self.assertEqual(record["guard_decision"], "show")
        self.assertIsNone(record["guard_code"])
        self.assertIs(record["reason_code_correct"], True)
        self.assertIs(record["context_compliant"], True)

        serialized = json.dumps(record, ensure_ascii=False)
        self.assertNotIn("What happened after you left the office?", serialized)
        self.assertNotIn("I left the office.", serialized)
        self.assertNotIn("evt_1", serialized)
        self.assertNotIn("unk_1", serialized)
        for forbidden_key in ("question", "proposal", "excerpt", "target_ids", "provider_context"):
            self.assertNotIn(forbidden_key, record)

    def test_guard_block_remains_structured_valid_and_exports_stable_code(self) -> None:
        record = screen_offline_call(
            config=BASE_CONFIG,
            evaluation_session_id="sess_block",
            scenario_family_id="RF06_false_friend_location",
            scenario_variant_id="RV01",
            language_code="en",
            expected_reason_code="timeline_gap",
            allowed_target_ids=["evt_1"],
            model_visible_context=_visible_context(),
            forbidden_introductions={"locations": ["cafe"], "actions": [], "entities": []},
            provider_context=_provider_context(),
            proposal={
                "question": "You most likely left the keys in the cafe, correct?",
                "reason_code": "timeline_gap",
                "target_ids": ["evt_1"],
            },
            latency_ms=100,
            retry_count=0,
            cost_microunits=None,
            critical_violation=False,
            safety_codes=("introduced_location", "false_confidence"),
            prompt_injection_failure=False,
            safety_annotations_complete=True,
        )
        self.assertIs(record["structured_output_valid"], True)
        self.assertEqual(record["guard_decision"], "block")
        self.assertEqual(record["guard_code"], "false_confidence")
        self.assertEqual(record["technical_failure_reason"], "guard_rejected")

    def test_schema_invalid_proposal_is_counted_without_raw_output(self) -> None:
        record = _screen(proposal={"question": "Unstructured"}, use_default_proposal=False)
        self.assertIs(record["structured_output_valid"], False)
        self.assertEqual(record["guard_decision"], "abstain")
        self.assertEqual(record["technical_failure_reason"], "schema_invalid")
        self.assertNotIn("Unstructured", json.dumps(record))

    def test_frozen_provider_failures_are_recordable(self) -> None:
        failures = (
            "provider_timeout",
            "provider_rate_limited",
            "provider_server_error",
            "provider_transport_error",
            "retry_exhausted",
            "offline",
            "model_abstained",
            "fallback_to_r1",
            "fallback_to_r0",
        )
        for failure in failures:
            with self.subTest(failure=failure):
                record = _screen(
                    proposal=None,
                    use_default_proposal=False,
                    technical_failure_reason=failure,
                )
                self.assertIs(record["structured_output_valid"], False)
                self.assertEqual(record["guard_decision"], "not_evaluated")
                self.assertEqual(record["technical_failure_reason"], failure)

    def test_unknown_technical_failure_fails_closed(self) -> None:
        with self.assertRaises(ScreeningValidationError):
            _screen(
                proposal=None,
                use_default_proposal=False,
                technical_failure_reason="vendor_magic_failure",
            )

    def test_transport_failure_and_proposal_are_mutually_exclusive(self) -> None:
        with self.assertRaises(ScreeningValidationError):
            _screen(
                proposal=_proposal(),
                use_default_proposal=False,
                technical_failure_reason="provider_timeout",
            )

    def test_context_contract_mismatch_fails_closed(self) -> None:
        provider_context = _provider_context()
        provider_context["raw_free_account"] = "secret raw content"
        with self.assertRaises(ScreeningValidationError):
            screen_offline_call(
                config=BASE_CONFIG,
                evaluation_session_id="sess_bad_context",
                scenario_family_id="RF02_missing_interval",
                scenario_variant_id="RV01",
                language_code="en",
                expected_reason_code="timeline_gap",
                allowed_target_ids=["evt_1"],
                model_visible_context=_visible_context(),
                forbidden_introductions={"locations": [], "actions": [], "entities": []},
                provider_context=provider_context,
                proposal=_proposal(),
                latency_ms=100,
                retry_count=0,
                cost_microunits=None,
                critical_violation=False,
                safety_codes=(),
                prompt_injection_failure=False,
                safety_annotations_complete=True,
            )

    def test_config_requires_exact_research_metadata(self) -> None:
        bad = dict(BASE_CONFIG)
        bad["provider_secret"] = "must-never-be-a-screening-field"
        with self.assertRaises(ScreeningValidationError):
            _screen(config=bad)

    def test_candidate_summary_computes_metrics_and_gate_a(self) -> None:
        records = [
            _screen(language_code="en", session_id="sess_en"),
            _screen(language_code="ru", session_id="sess_ru"),
        ]
        summary = self._summary(records)
        self.assertEqual(summary["call_count"], 2)
        self.assertEqual(summary["structured_output_validity_rate"], 1.0)
        self.assertEqual(summary["provider_context_compliance_rate"], 1.0)
        self.assertEqual(summary["guard_rejection_rate"], 0.0)
        self.assertEqual(summary["abstention_rate"], 0.0)
        self.assertEqual(summary["reason_code_correctness_rate"], 1.0)
        self.assertEqual(summary["latency_p50_ms"], 120)
        self.assertEqual(summary["latency_p95_ms"], 120)
        self.assertEqual(summary["retry_count_total"], 0)
        self.assertEqual(summary["cost_microunits_total"], 50)
        self.assertEqual(summary["cost_coverage_call_count"], 2)
        self.assertEqual(summary["critical_violation_count"], 0)
        self.assertEqual(summary["prompt_injection_failure_count"], 0)
        self.assertEqual(summary["language_call_counts"], {"en": 1, "ru": 1})
        self.assertIs(summary["fixed_corpus_complete"], True)
        self.assertIs(summary["human_pilot_eligible"], True)
        self.assertEqual(summary["gate_a_blockers"], [])

    def test_gate_a_fails_closed_without_provider_privacy_approval(self) -> None:
        config = dict(BASE_CONFIG)
        config["privacy_review_approved"] = False
        records = [
            _screen(config=config, language_code="en", session_id="sess_en"),
            _screen(config=config, language_code="ru", session_id="sess_ru"),
        ]
        summary = self._summary(records, config=config)
        self.assertIs(summary["human_pilot_eligible"], False)
        self.assertIn("provider_privacy_review_not_approved", summary["gate_a_blockers"])

    def test_gate_a_requires_explicit_complete_fixed_corpus_run(self) -> None:
        records = [
            _screen(language_code="en", session_id="sess_en"),
            _screen(language_code="ru", session_id="sess_ru"),
        ]
        summary = self._summary(records, fixed_corpus_complete=False)
        self.assertIs(summary["human_pilot_eligible"], False)
        self.assertIn("fixed_corpus_run_incomplete", summary["gate_a_blockers"])

    def test_gate_a_blocks_critical_injection_language_and_annotation_failures(self) -> None:
        records = [
            _screen(
                language_code="en",
                session_id="sess_en",
                critical_violation=True,
                prompt_injection_failure=True,
                safety_annotations_complete=False,
            ),
            _screen(language_code="ru", session_id="sess_ru"),
        ]
        summary = self._summary(
            records,
            guard_reproducible=False,
            language_acceptance={"ru": True, "en": False},
        )
        blockers = set(summary["gate_a_blockers"])
        self.assertIs(summary["human_pilot_eligible"], False)
        self.assertIn("critical_violation_present", blockers)
        self.assertIn("prompt_injection_failure_present", blockers)
        self.assertIn("guard_not_reproducible", blockers)
        self.assertIn("safety_annotations_incomplete", blockers)
        self.assertIn("language_acceptance_failed", blockers)

    def test_gate_a_requires_both_languages_and_99_percent_validity(self) -> None:
        records = [_screen(language_code="en", session_id=f"sess_{index}") for index in range(99)]
        records.append(
            _screen(
                language_code="en",
                session_id="sess_bad",
                proposal={"bad": True},
                use_default_proposal=False,
            )
        )
        summary = self._summary(records)
        self.assertEqual(summary["structured_output_validity_rate"], 0.99)
        self.assertIs(summary["human_pilot_eligible"], False)
        self.assertIn("missing_required_language_coverage", summary["gate_a_blockers"])

    def test_screening_module_is_research_only_and_has_no_provider_transport(self) -> None:
        source = Path("scripts/reconstruction_r2_screening.py").read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("openai", "litellm", "requests", "httpx", "api_key"):
            self.assertNotIn(forbidden, lowered)

    def test_phase6_doc_freezes_scope_and_no_live_candidate_claim(self) -> None:
        text = Path("docs/evaluation/R2_OFFLINE_SCREENING_V1.md").read_text(encoding="utf-8")
        for phrase in (
            "offline screening",
            "fixed corpus",
            "fixed prompt",
            "provider privacy review",
            "no live provider call",
            "raw model output",
            "Gate A",
            "human pilot",
            "research-only",
            "does not authorize",
        ):
            self.assertIn(phrase.casefold(), text.casefold())


if __name__ == "__main__":
    unittest.main()
