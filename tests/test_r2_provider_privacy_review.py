from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.reconstruction_r2_context import CONTEXT_SCHEMA, build_provider_context
from scripts.reconstruction_r2_guard import GUARD_SCHEMA
from scripts.reconstruction_r2_provider_review import (
    PROVIDER_REVIEW_SCHEMA,
    REVIEW_DOMAINS,
    ProviderReviewValidationError,
    review_attestation,
    screening_config_from_review,
    validate_provider_review,
)
from scripts.reconstruction_r2_screening import (
    PROPOSAL_SCHEMA_VERSION,
    screen_offline_call,
)


DOC = Path("docs/evaluation/R2_PROVIDER_PRIVACY_REVIEW_V1.md")
TEMPLATE = Path("docs/evaluation/R2_PROVIDER_PRIVACY_REVIEW_TEMPLATE_V1.json")


def _domain(decision: str = "acceptable") -> dict[str, object]:
    return {
        "decision": decision,
        "evidence_refs": ["https://example.invalid/provider-policy"],
    }


def _review(*, status: str = "approved") -> dict[str, object]:
    return {
        "review_schema": PROVIDER_REVIEW_SCHEMA,
        "provider_research_id": "provider_fixture",
        "provider_review_version": "provider-fixture-review-v1",
        "reviewed_scope": {
            "purpose": "offline_reconstruction_r2_screening",
            "context_schema_version": CONTEXT_SCHEMA,
            "credential_boundary": "server_side_only",
            "raw_content_export": False,
        },
        "domains": {domain: _domain() for domain in REVIEW_DOMAINS},
        "review_status": status,
    }


def _visible_context() -> dict[str, object]:
    return {
        "language_code": "en",
        "supported_entities": ["keys"],
        "supported_locations": ["office"],
        "supported_actions": ["left"],
        "timeline_refs": ["evt_1"],
        "statement_refs": ["stmt_1"],
        "unknown_markers": ["unk_1"],
        "contradiction_refs": [],
    }


class R2ProviderPrivacyReviewTests(unittest.TestCase):
    def test_schema_and_required_domains_are_frozen(self) -> None:
        self.assertEqual(
            PROVIDER_REVIEW_SCHEMA,
            "mind-detective-reconstruction-r2-provider-privacy-review/v1",
        )
        self.assertEqual(
            REVIEW_DOMAINS,
            (
                "request_retention",
                "training_secondary_use",
                "deletion_control",
                "geographic_processing",
                "credential_transport",
                "logging_observability",
            ),
        )

    def test_complete_approved_review_validates(self) -> None:
        validated = validate_provider_review(_review())
        self.assertEqual(validated["provider_research_id"], "provider_fixture")
        self.assertEqual(validated["review_status"], "approved")
        self.assertEqual(set(validated["domains"]), set(REVIEW_DOMAINS))

    def test_unknown_top_level_or_domain_fields_fail_closed(self) -> None:
        review = _review()
        review["provider_token"] = "secret"
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

        review = _review()
        domains = dict(review["domains"])
        retention = dict(domains["request_retention"])
        retention["raw_policy_text"] = "must not be machine review payload"
        domains["request_retention"] = retention
        review["domains"] = domains
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

    def test_exact_review_scope_is_required(self) -> None:
        review = _review()
        scope = dict(review["reviewed_scope"])
        scope["raw_content_export"] = True
        review["reviewed_scope"] = scope
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

        review = _review()
        scope = dict(review["reviewed_scope"])
        scope["credential_boundary"] = "browser"
        review["reviewed_scope"] = scope
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

    def test_all_six_domains_are_required_exactly_once(self) -> None:
        review = _review()
        domains = dict(review["domains"])
        del domains["deletion_control"]
        review["domains"] = domains
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

        review = _review()
        domains = dict(review["domains"])
        domains["vendor_marketing_claims"] = _domain()
        review["domains"] = domains
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

    def test_each_domain_requires_evidence(self) -> None:
        review = _review()
        domains = dict(review["domains"])
        domains["request_retention"] = {
            "decision": "acceptable",
            "evidence_refs": [],
        }
        review["domains"] = domains
        with self.assertRaises(ProviderReviewValidationError):
            validate_provider_review(review)

    def test_approved_review_requires_every_domain_acceptable(self) -> None:
        for decision in ("unknown", "blocked"):
            with self.subTest(decision=decision):
                review = _review(status="approved")
                domains = dict(review["domains"])
                domains["training_secondary_use"] = _domain(decision)
                review["domains"] = domains
                with self.assertRaises(ProviderReviewValidationError):
                    validate_provider_review(review)

    def test_nonapproved_review_cannot_produce_positive_attestation(self) -> None:
        review = _review(status="blocked")
        domains = dict(review["domains"])
        domains["logging_observability"] = _domain("blocked")
        review["domains"] = domains

        attestation = review_attestation(review)
        self.assertEqual(
            attestation,
            {
                "provider_research_id": "provider_fixture",
                "provider_review_version": "provider-fixture-review-v1",
                "privacy_review_approved": False,
            },
        )

    def test_attestation_is_content_free(self) -> None:
        attestation = review_attestation(_review())
        self.assertEqual(
            set(attestation),
            {
                "provider_research_id",
                "provider_review_version",
                "privacy_review_approved",
            },
        )
        serialized = json.dumps(attestation)
        self.assertNotIn("evidence_refs", serialized)
        self.assertNotIn("provider-policy", serialized)
        self.assertIs(attestation["privacy_review_approved"], True)

    def test_screening_config_is_derived_from_validated_review(self) -> None:
        config = screening_config_from_review(
            _review(),
            model_research_id="model_fixture",
            prompt_version="prompt-fixture-v1",
        )
        self.assertEqual(
            config,
            {
                "provider_research_id": "provider_fixture",
                "model_research_id": "model_fixture",
                "prompt_version": "prompt-fixture-v1",
                "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
                "context_schema_version": CONTEXT_SCHEMA,
                "guard_schema_version": GUARD_SCHEMA,
                "provider_review_version": "provider-fixture-review-v1",
                "privacy_review_approved": True,
            },
        )

        visible = _visible_context()
        provider_context = build_provider_context(
            language_code="en",
            reason_code="timeline_gap",
            target_ids=["evt_1"],
            model_visible_context=visible,
            excerpts={"evt_1": "I left the office."},
            related_unknown_ids=["unk_1"],
        )
        record = screen_offline_call(
            config=config,
            evaluation_session_id="privacy_review_bridge",
            scenario_family_id="RF02_missing_interval",
            scenario_variant_id="RV01",
            language_code="en",
            expected_reason_code="timeline_gap",
            allowed_target_ids=["evt_1"],
            model_visible_context=visible,
            forbidden_introductions={"locations": [], "actions": [], "entities": []},
            provider_context=provider_context,
            proposal={
                "question": "What happened after you left the office?",
                "reason_code": "timeline_gap",
                "target_ids": ["evt_1"],
            },
            safety_annotations_complete=True,
        )
        self.assertIs(record["privacy_review_approved"], True)
        self.assertEqual(record["provider_review_version"], "provider-fixture-review-v1")

    def test_blocked_review_derives_ineligible_screening_config(self) -> None:
        review = _review(status="blocked")
        domains = dict(review["domains"])
        domains["request_retention"] = _domain("blocked")
        review["domains"] = domains
        config = screening_config_from_review(
            review,
            model_research_id="model_fixture",
            prompt_version="prompt-fixture-v1",
        )
        self.assertIs(config["privacy_review_approved"], False)

    def test_template_is_not_an_approval(self) -> None:
        payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        validated = validate_provider_review(payload)
        self.assertEqual(validated["review_status"], "incomplete")
        self.assertIs(review_attestation(validated)["privacy_review_approved"], False)

    def test_documentation_preserves_governance_boundary(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        required = (
            "not a legal or compliance certification",
            "does not select or recommend a provider",
            "must not contain credentials",
            "all six domains",
            "separate explicit research execution action",
            "no live provider call",
            "human pilot",
            "production",
            "0.4.1",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
