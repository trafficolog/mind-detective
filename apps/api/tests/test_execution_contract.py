from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from mind_detective_api.app import app
from mind_detective_api.core_bridge import create_case_payload


EXPECTED_IDENTITY = {
    "version": "mind-detective-local-execution/v1",
    "kernel_sha256": "sha256:006cb63798762d4168479ab97779346e9962a11201b68119a9a60d38b1a44548",
    "generated_sha256": "sha256:682967a39dec98008c5ac92fce6e434f498cf24101a591168afd22ea8dac86e3",
    "generator_version": "local-execution-generator/v1",
}


class ExecutionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _assistant_request(self, identity: dict[str, str]) -> dict[str, object]:
        return {
            "request_id": "proposal-skew-1",
            "now": "2026-09-10T18:00:00Z",
            "case": create_case_payload("case-skew-1", "ключи", "2026-09-10T17:59:00Z"),
            "mode": "search",
            "locale": "ru",
            "experimental_arm": "assistant",
            "execution_identity": identity,
        }

    def test_execution_contract_endpoint_exposes_full_generated_identity(self) -> None:
        response = self.client.get("/api/v1/execution/contract")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["version"], EXPECTED_IDENTITY["version"])
        self.assertEqual(payload["kernel_sha256"], EXPECTED_IDENTITY["kernel_sha256"])
        self.assertEqual(payload["generated_sha256"], EXPECTED_IDENTITY["generated_sha256"])
        self.assertEqual(payload["generator_version"], EXPECTED_IDENTITY["generator_version"])
        self.assertEqual(payload["case_schemas"], ["mind-detective-case/v2"])

    def test_each_assistant_execution_identity_mismatch_fails_before_provider_creation(self) -> None:
        mutations = {
            "version": "mind-detective-local-execution/v999",
            "kernel_sha256": "sha256:" + "0" * 64,
            "generated_sha256": "sha256:" + "1" * 64,
            "generator_version": "local-execution-generator/v999",
        }

        with patch(
            "mind_detective_api.litellm_provider.LiteLLMProposalClient.from_env"
        ) as from_env:
            for field, replacement in mutations.items():
                with self.subTest(field=field):
                    identity = copy.deepcopy(EXPECTED_IDENTITY)
                    identity[field] = replacement
                    response = self.client.post(
                        "/api/v1/proposal/next",
                        json=self._assistant_request(identity),
                    )
                    self.assertEqual(response.status_code, 409)
                    self.assertEqual(
                        response.json()["code"],
                        "MD_WEB_EXECUTION_CONTRACT_MISMATCH",
                    )
            from_env.assert_not_called()

    def test_missing_assistant_execution_identity_fails_closed_before_provider_creation(self) -> None:
        body = self._assistant_request(EXPECTED_IDENTITY)
        body.pop("execution_identity")

        with patch(
            "mind_detective_api.litellm_provider.LiteLLMProposalClient.from_env"
        ) as from_env:
            response = self.client.post("/api/v1/proposal/next", json=body)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["code"], "MD_WEB_EXECUTION_CONTRACT_MISMATCH")
        from_env.assert_not_called()


if __name__ == "__main__":
    unittest.main()
