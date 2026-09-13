from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from scripts.reconstruction_r2_context import CONTEXT_SCHEMA
from scripts.reconstruction_r2_guard import GUARD_SCHEMA
from scripts.reconstruction_r2_provider_review import screening_config_from_review
from scripts.reconstruction_r2_screening import PROPOSAL_SCHEMA_VERSION


ROOT = Path(__file__).resolve().parents[1]
OPENAI_REVIEW = (
    ROOT
    / "docs"
    / "evaluation"
    / "provider-reviews"
    / "OPENAI_API_EU_ZDR_V1.json"
)
DOC = ROOT / "docs" / "evaluation" / "R2_EXECUTION_PREFLIGHT_V1.md"

try:
    preflight_module = importlib.import_module(
        "scripts.reconstruction_r2_execution_preflight"
    )
except ModuleNotFoundError as exc:  # RED state before implementation exists.
    preflight_module = None
    PREFLIGHT_IMPORT_ERROR: ModuleNotFoundError | None = exc
else:
    PREFLIGHT_IMPORT_ERROR = None


EXPECTED_CHECKS = (
    "profile_entitlement_verified",
    "model_endpoint_supported",
    "prohibited_features_disabled",
    "server_side_credentials_verified",
    "synthetic_corpus_only",
    "minimized_context_only",
    "frozen_versions_match",
    "raw_telemetry_disabled",
    "policy_evidence_current",
)


def _module():
    if PREFLIGHT_IMPORT_ERROR is not None:
        raise AssertionError(
            "execution preflight module is not implemented yet"
        ) from PREFLIGHT_IMPORT_ERROR
    assert preflight_module is not None
    return preflight_module


def _review() -> dict[str, object]:
    return json.loads(OPENAI_REVIEW.read_text(encoding="utf-8"))


def _config() -> dict[str, object]:
    return dict(
        screening_config_from_review(
            _review(),
            model_research_id="model-fixture-v1",
            prompt_version="r2-screening-prompt-v1",
        )
    )


def _check(status: str = "pass") -> dict[str, object]:
    refs = [] if status == "unknown" else ["evidence://fixture/control"]
    return {"status": status, "evidence_refs": refs}


def _preflight(*, status: str = "ready") -> dict[str, object]:
    config = _config()
    checks = {name: _check() for name in EXPECTED_CHECKS}
    if status == "blocked":
        checks["profile_entitlement_verified"] = _check("fail")
    elif status == "incomplete":
        checks["profile_entitlement_verified"] = _check("unknown")
    return {
        "preflight_schema": "mind-detective-reconstruction-r2-execution-preflight/v1",
        "provider_research_id": config["provider_research_id"],
        "provider_review_version": config["provider_review_version"],
        "model_research_id": config["model_research_id"],
        "prompt_version": config["prompt_version"],
        "proposal_schema_version": config["proposal_schema_version"],
        "context_schema_version": config["context_schema_version"],
        "guard_schema_version": config["guard_schema_version"],
        "corpus_id": "r2-fixed-corpus-v1",
        "checks": checks,
        "preflight_status": status,
    }


class R2ExecutionPreflightTests(unittest.TestCase):
    def test_schema_and_check_set_are_frozen(self) -> None:
        module = _module()
        self.assertEqual(
            module.EXECUTION_PREFLIGHT_SCHEMA,
            "mind-detective-reconstruction-r2-execution-preflight/v1",
        )
        self.assertEqual(module.PREFLIGHT_CHECKS, EXPECTED_CHECKS)

    def test_ready_preflight_validates_against_approved_provider_review(self) -> None:
        module = _module()
        validated = module.validate_execution_preflight(_review(), _preflight())
        self.assertEqual(validated["preflight_status"], "ready")
        self.assertEqual(validated["provider_research_id"], "openai-api-eu-zdr")
        self.assertEqual(validated["corpus_id"], "r2-fixed-corpus-v1")
        self.assertEqual(set(validated["checks"]), set(EXPECTED_CHECKS))

    def test_preflight_is_bound_to_review_and_frozen_screening_config(self) -> None:
        module = _module()
        mutation_cases = {
            "provider_research_id": "different-provider",
            "provider_review_version": "different-review-v1",
            "proposal_schema_version": "proposal/v999",
            "context_schema_version": "context/v999",
            "guard_schema_version": "guard/v999",
        }
        for field, value in mutation_cases.items():
            with self.subTest(field=field):
                payload = _preflight()
                payload[field] = value
                with self.assertRaises(module.ExecutionPreflightValidationError):
                    module.validate_execution_preflight(_review(), payload)

    def test_model_and_prompt_ids_are_required_nonempty_strings(self) -> None:
        module = _module()
        for field in ("model_research_id", "prompt_version", "corpus_id"):
            for value in ("", [], {}):
                with self.subTest(field=field, value=value):
                    payload = _preflight()
                    payload[field] = value
                    with self.assertRaises(module.ExecutionPreflightValidationError):
                        module.validate_execution_preflight(_review(), payload)

    def test_unknown_top_level_or_check_fields_fail_closed(self) -> None:
        module = _module()
        payload = _preflight()
        payload["api_key"] = "must-never-be-accepted"
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

        payload = _preflight()
        checks = dict(payload["checks"])
        entitlement = dict(checks["profile_entitlement_verified"])
        entitlement["raw_vendor_response"] = "forbidden"
        checks["profile_entitlement_verified"] = entitlement
        payload["checks"] = checks
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

    def test_exact_check_set_is_required(self) -> None:
        module = _module()
        payload = _preflight()
        checks = dict(payload["checks"])
        del checks["raw_telemetry_disabled"]
        payload["checks"] = checks
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

        payload = _preflight()
        checks = dict(payload["checks"])
        checks["browser_credentials"] = _check()
        payload["checks"] = checks
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

    def test_check_status_and_evidence_are_fail_closed(self) -> None:
        module = _module()
        for bad_status in ("yes", [], {}):
            with self.subTest(status=bad_status):
                payload = _preflight()
                checks = dict(payload["checks"])
                entry = dict(checks["profile_entitlement_verified"])
                entry["status"] = bad_status
                checks["profile_entitlement_verified"] = entry
                payload["checks"] = checks
                with self.assertRaises(module.ExecutionPreflightValidationError):
                    module.validate_execution_preflight(_review(), payload)

        for status in ("pass", "fail"):
            with self.subTest(status=status):
                payload = _preflight()
                checks = dict(payload["checks"])
                checks["profile_entitlement_verified"] = {
                    "status": status,
                    "evidence_refs": [],
                }
                payload["checks"] = checks
                payload["preflight_status"] = "blocked" if status == "fail" else "ready"
                with self.assertRaises(module.ExecutionPreflightValidationError):
                    module.validate_execution_preflight(_review(), payload)

    def test_preflight_status_is_derived_from_check_outcomes(self) -> None:
        module = _module()
        for status in ("ready", "blocked", "incomplete"):
            with self.subTest(status=status):
                validated = module.validate_execution_preflight(
                    _review(), _preflight(status=status)
                )
                self.assertEqual(validated["preflight_status"], status)

        payload = _preflight(status="incomplete")
        payload["preflight_status"] = "ready"
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

        payload = _preflight(status="blocked")
        payload["preflight_status"] = "incomplete"
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(_review(), payload)

    def test_nonapproved_provider_review_cannot_enter_execution_preflight(self) -> None:
        module = _module()
        review = _review()
        domains = dict(review["domains"])
        domain = dict(domains["request_retention"])
        domain["decision"] = "unknown"
        domain["evidence_refs"] = []
        domains["request_retention"] = domain
        review["domains"] = domains
        review["review_status"] = "incomplete"
        with self.assertRaises(module.ExecutionPreflightValidationError):
            module.validate_execution_preflight(review, _preflight())

    def test_attestation_is_content_free_and_not_execution_authorization(self) -> None:
        module = _module()
        attestation = module.preflight_attestation(_review(), _preflight())
        self.assertEqual(
            set(attestation),
            {
                "provider_research_id",
                "provider_review_version",
                "model_research_id",
                "prompt_version",
                "corpus_id",
                "preflight_status",
                "preflight_ready",
            },
        )
        self.assertIs(attestation["preflight_ready"], True)
        serialized = json.dumps(attestation)
        for forbidden in (
            "evidence_refs",
            "api_key",
            "credential",
            "raw_vendor_response",
            "execution_authorized",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_ready_preflight_can_rederive_exact_screening_config_only(self) -> None:
        module = _module()
        config = module.screening_config_from_preflight(_review(), _preflight())
        self.assertEqual(config, _config())
        self.assertEqual(config["proposal_schema_version"], PROPOSAL_SCHEMA_VERSION)
        self.assertEqual(config["context_schema_version"], CONTEXT_SCHEMA)
        self.assertEqual(config["guard_schema_version"], GUARD_SCHEMA)

        for status in ("blocked", "incomplete"):
            with self.subTest(status=status):
                with self.assertRaises(module.ExecutionPreflightValidationError):
                    module.screening_config_from_preflight(
                        _review(), _preflight(status=status)
                    )

    def test_documentation_preserves_separate_execution_authorization_gate(self) -> None:
        self.assertTrue(DOC.is_file(), f"missing preflight documentation: {DOC}")
        text = DOC.read_text(encoding="utf-8")
        required = (
            "does not authorize execution",
            "separate explicit human authorization",
            "server-side credentials",
            "synthetic",
            "Phase 5 minimized context",
            "no raw request/response",
            "no provider call",
            "human pilot",
            "production",
            "0.4.1",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
