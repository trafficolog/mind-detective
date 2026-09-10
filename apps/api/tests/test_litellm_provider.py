from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mind_detective_api.litellm_provider import LiteLLMProposalClient, ProviderError


class LiteLLMProviderTests(unittest.TestCase):
    def test_from_env_uses_litellm_key_default_proxy_endpoint_and_model_alias(self) -> None:
        with patch.dict(
            os.environ,
            {
                "LITELLM_API_KEY": "sk-litellm-test",
                "MIND_DETECTIVE_LITELLM_MODEL": "mind-detective-proposal",
            },
            clear=True,
        ):
            with patch("mind_detective_api.litellm_provider.AsyncOpenAI") as client_cls:
                client = LiteLLMProposalClient.from_env()

        client_cls.assert_called_once_with(
            api_key="sk-litellm-test",
            base_url="http://127.0.0.1:4000",
        )
        self.assertEqual(client.model_id, "mind-detective-proposal")

    def test_from_env_accepts_custom_litellm_proxy_endpoint(self) -> None:
        with patch.dict(
            os.environ,
            {
                "LITELLM_API_KEY": "sk-litellm-test",
                "MIND_DETECTIVE_LITELLM_BASE_URL": "https://llm.example.test/v1",
                "MIND_DETECTIVE_LITELLM_MODEL": "claude-search",
            },
            clear=True,
        ):
            with patch("mind_detective_api.litellm_provider.AsyncOpenAI") as client_cls:
                client = LiteLLMProposalClient.from_env()

        client_cls.assert_called_once_with(
            api_key="sk-litellm-test",
            base_url="https://llm.example.test/v1",
        )
        self.assertEqual(client.model_id, "claude-search")

    def test_from_env_fails_closed_without_key_or_model(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderError) as key_ctx:
                LiteLLMProposalClient.from_env()
        self.assertEqual(key_ctx.exception.code, "MD_WEB_PROVIDER_CONFIG")
        self.assertIn("LITELLM_API_KEY", str(key_ctx.exception))

        with patch.dict(os.environ, {"LITELLM_API_KEY": "sk-litellm-test"}, clear=True):
            with self.assertRaises(ProviderError) as model_ctx:
                LiteLLMProposalClient.from_env()
        self.assertEqual(model_ctx.exception.code, "MD_WEB_PROVIDER_CONFIG")
        self.assertIn("MIND_DETECTIVE_LITELLM_MODEL", str(model_ctx.exception))


if __name__ == "__main__":
    unittest.main()
