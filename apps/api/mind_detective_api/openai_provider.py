from __future__ import annotations

import json
import os

from openai import AsyncOpenAI

from .contracts import ProposalModel
from .core_bridge import validate_or_migrate_case_payload

from scripts.store import case_from_dict


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


class OpenAIProposalClient:
    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    @classmethod
    def from_env(cls) -> OpenAIProposalClient:
        api_key = os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("MIND_DETECTIVE_OPENAI_MODEL")
        if not api_key:
            raise ProviderError("MD_WEB_PROVIDER_CONFIG", "OPENAI_API_KEY is required")
        if not model:
            raise ProviderError(
                "MD_WEB_PROVIDER_CONFIG",
                "MIND_DETECTIVE_OPENAI_MODEL is required",
            )
        return cls(AsyncOpenAI(api_key=api_key), model)

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
        raise ProviderError("MD_WEB_PROVIDER_OUTPUT", "provider returned no parsed proposal")
