from __future__ import annotations

import json
import unittest

from mind_detective_api.contracts import ProposalModel, ProposalRequest
from mind_detective_api.core_bridge import create_case_payload
from mind_detective_api.openai_provider import build_provider_context
from mind_detective_api.privacy_log import PrivacyLogError, build_privacy_log
from mind_detective_api.proposals import build_assistant_proposal


class FakeProposalClient:
    def __init__(self, proposal: ProposalModel) -> None:
        self.proposal = proposal

    async def propose(self, case: dict[str, object], mode: str) -> ProposalModel:
        return self.proposal


class AssistantProposalTests(unittest.IsolatedAsyncioTestCase):
    def _request(self, mode: str = "reconstruction") -> ProposalRequest:
        return ProposalRequest(
            request_id="proposal-1",
            now="2026-09-10T07:01:00Z",
            case=create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z"),
            mode=mode,
            locale="ru",
            experimental_arm="assistant",
        )

    async def test_reconstruction_location_injection_is_blocked_and_discarded(self):
        fake = FakeProposalClient(
            ProposalModel(
                kind="next_action",
                candidate_id="candidate-car",
                target="машина",
                copy_key="next_action.check_target",
            )
        )
        result = await build_assistant_proposal(self._request(), fake)
        self.assertEqual(result.guard_code, "MD_G_RECON_NEW_LOCATION")
        self.assertEqual(result.proposal.kind, "clarification")
        self.assertIsNone(result.proposal.target)
        journal = result.case["interaction_journal"]
        self.assertEqual(len(journal), 1)
        self.assertEqual(journal[0]["id"], "guard-proposal-1")
        self.assertEqual(journal[0]["mode"], "system")
        self.assertEqual(journal[0]["text"], "guard.ai_proposal_blocked")
        self.assertNotIn("машина", json.dumps(result.case, ensure_ascii=False))

    async def test_same_guard_request_is_idempotent_on_already_updated_case(self):
        fake = FakeProposalClient(
            ProposalModel(
                kind="next_action",
                target="машина",
                copy_key="next_action.check_target",
            )
        )
        first = await build_assistant_proposal(self._request(), fake)
        retry = self._request().model_copy(update={"case": first.case})
        second = await build_assistant_proposal(retry, fake)
        self.assertEqual(second.case, first.case)
        self.assertEqual(len(second.case["interaction_journal"]), 1)

    async def test_probability_claim_is_blocked_in_search_mode(self):
        fake = FakeProposalClient(
            ProposalModel(
                kind="next_action",
                target="карманы куртки — 70%",
                copy_key="next_action.check_target",
            )
        )
        result = await build_assistant_proposal(self._request("search"), fake)
        self.assertEqual(result.guard_code, "MD_G_LOCATION_PROBABILITY")
        self.assertNotIn("70%", json.dumps(result.case, ensure_ascii=False))

    def test_provider_context_excludes_duplicate_journal_and_outcome_payloads(self):
        case = create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z")
        context = build_provider_context(case, "search")
        self.assertNotIn("interaction_journal", context)
        self.assertNotIn("outcome", context)
        self.assertNotIn("created_at", context)
        self.assertNotIn("updated_at", context)

    def test_privacy_log_rejects_sensitive_fields(self):
        with self.assertRaises(PrivacyLogError) as ctx:
            build_privacy_log("assistant_proposal", {"request_id": "r1", "target": "рюкзак"})
        self.assertEqual(ctx.exception.code, "MD_WEB_LOG_SENSITIVE_FIELD")
        safe = build_privacy_log(
            "assistant_proposal",
            {
                "request_id": "r1",
                "arm": "assistant",
                "outcome_code": "allowed",
                "latency_bucket": "lt_1s",
                "model_id": "configured-model",
            },
        )
        self.assertEqual(safe["event"], "assistant_proposal")


if __name__ == "__main__":
    unittest.main()
