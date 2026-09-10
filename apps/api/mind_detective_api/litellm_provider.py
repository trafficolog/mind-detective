from __future__ import annotations

import json
import os

from openai import AsyncOpenAI

from .contracts import ProposalModel
from .core_bridge import validate_or_migrate_case_payload

from scripts.store import case_from_dict

_DEFAULT_LITELLM_BASE_URL = "http://127.0.0.1:4000"


class ProviderError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def build_provider_context(case_payload: dict[str, object], mode: str) -> dict[str, object]:
    case = case_from_dict(validate_or_migrate_case_payload(case_payload))
    return {
        "item_label": case.item_label,
        "mode": mode,
        "statements": [
            {
                "id": statement.id,
                "source": statement.source.value,
                "statement_type": statement.statement_type.value,
                "original_text": statement.original_text,
            }
            for statement in case.statements
        ],
        "search_checks": [
            {
                "id": check.id,
                "target": check.target,
                "method": check.method.value,
                "result": check.result.value,
                "inaccessible_parts": list(check.inaccessible_parts),
            }
            for check in case.search_checks
        ],
        "candidates": [
            {
                "id": candidate.id,
                "target": candidate.target,
                "check_state": candidate.check_state.value,
                "safety": candidate.safety.value,
                "basis": candidate.basis.value,
                "based_on": list(candidate.based_on),
            }
            for candidate in case.candidates
        ],
        "constraints": list(case.constraints),
        "action_feedback": [
            {
                "candidate_id": feedback.candidate_id,
                "reason": feedback.reason.value,
            }
            for feedback in case.action_feedback
        ],
    }


class LiteLLMProposalClient:
    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    @property
    def model_id(self) -> str:
        return self._model

    @classmethod
    def from_env(cls) -> LiteLLMProposalClient:
        api_key = os.environ.get("LITELLM_API_KEY")
        base_url = os.environ.get("MIND_DETECTIVE_LITELLM_BASE_URL", _DEFAULT_LITELLM_BASE_URL)
        model = os.environ.get("MIND_DETECTIVE_LITELLM_MODEL")
        if not api_key:
            raise ProviderError("MD_WEB_PROVIDER_CONFIG", "LITELLM_API_KEY is required")
        if not model:
            raise ProviderError(
                "MD_WEB_PROVIDER_CONFIG",
                "MIND_DETECTIVE_LITELLM_MODEL is required",
            )
        if not base_url:
            raise ProviderError(
                "MD_WEB_PROVIDER_CONFIG",
                "MIND_DETECTIVE_LITELLM_BASE_URL must not be empty",
            )
        return cls(AsyncOpenAI(api_key=api_key, base_url=base_url), model)

    async def propose(self, case: dict[str, object], mode: str) -> ProposalModel:
        context = build_provider_context(case, mode)
        response = await self._client.responses.parse(
            model=self._model,
            store=False,
            instructions=(
                "Return only a structured MIND Detective proposal. "
                "Do not assign probabilities, diagnose forgetting, or claim a suggested place is a memory. "
                "In reconstruction mode do not introduce a concrete location absent from user-origin statements."
            ),
            input=json.dumps(context, ensure_ascii=False, sort_keys=True),
            text_format=ProposalModel,
        )
        for output in response.output:
            if output.type != "message":
                continue
            for content in output.content:
                if content.type == "output_text" and isinstance(content.parsed, ProposalModel):
                    return content.parsed
        raise ProviderError("MD_WEB_PROVIDER_OUTPUT", "LiteLLM returned no parsed proposal")
