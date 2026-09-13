from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.reconstruction_r2_provider_review import (
    REVIEW_DOMAINS,
    review_attestation,
    validate_provider_review,
)

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_DIR = ROOT / "docs" / "evaluation" / "provider-reviews"

EXPECTED_REVIEWS = {
    "OPENAI_API_EU_ZDR_V1.json": "openai-api-eu-zdr",
    "ANTHROPIC_API_ZDR_V1.json": "anthropic-api-zdr",
    "GOOGLE_VERTEX_AI_EU_ZDR_V1.json": "google-vertex-ai-eu-zdr",
}


class ProviderSpecificPrivacyReviewsTest(unittest.TestCase):
    def test_review_files_exist_and_validate_as_approved(self) -> None:
        for filename, provider_research_id in EXPECTED_REVIEWS.items():
            with self.subTest(filename=filename):
                path = REVIEWS_DIR / filename
                self.assertTrue(path.is_file(), f"missing provider review: {path}")
                raw = json.loads(path.read_text(encoding="utf-8"))
                validated = validate_provider_review(raw)

                self.assertEqual(validated["provider_research_id"], provider_research_id)
                self.assertEqual(validated["review_status"], "approved")
                self.assertEqual(set(validated["domains"]), set(REVIEW_DOMAINS))
                for domain in REVIEW_DOMAINS:
                    self.assertEqual(validated["domains"][domain]["decision"], "acceptable")
                    self.assertTrue(validated["domains"][domain]["evidence_refs"])

                attestation = review_attestation(raw)
                self.assertEqual(attestation["provider_research_id"], provider_research_id)
                self.assertTrue(attestation["privacy_review_approved"])

    def test_review_artifacts_contain_only_machine_contract_fields(self) -> None:
        expected_keys = {
            "review_schema",
            "provider_research_id",
            "provider_review_version",
            "reviewed_scope",
            "domains",
            "review_status",
        }
        forbidden_fragments = {
            "api_key",
            "token",
            "secret",
            "prompt",
            "response_text",
            "free_account",
            "case_payload",
        }

        for filename in EXPECTED_REVIEWS:
            with self.subTest(filename=filename):
                raw_text = (REVIEWS_DIR / filename).read_text(encoding="utf-8")
                raw = json.loads(raw_text)
                self.assertEqual(set(raw), expected_keys)
                lowered = raw_text.lower()
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, lowered)


if __name__ == "__main__":
    unittest.main()
