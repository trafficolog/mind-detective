from __future__ import annotations

import unittest

from mind_detective_api.checklist import build_checklist_proposal
from mind_detective_api.core_bridge import create_case_payload

from scripts.controller import CaseController
from scripts.feedback import ActionFeedback, ActionFeedbackReason
from scripts.planner import (
    CandidateBasis,
    CandidateCheck,
    CheckState,
    Effort,
    RouteRelation,
    Safety,
    UrgencyRelevance,
)
from scripts.store import case_from_dict, case_to_dict


class ChecklistProposalTests(unittest.TestCase):
    def test_empty_search_case_returns_information_needed_without_location(self) -> None:
        case = create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z")
        proposal = build_checklist_proposal(case, "search")
        self.assertEqual(proposal.kind, "need_more_information")
        self.assertIsNone(proposal.target)

    def test_existing_safe_candidate_becomes_structured_next_action(self) -> None:
        controller = CaseController()
        case = case_from_dict(create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z"))
        candidate = CandidateCheck(
            id="candidate-1",
            target="карманы куртки",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=(),
            rationale=("direct route",),
        )
        case = controller.replace_candidates(case, (candidate,), "2026-09-10T07:01:00Z")
        proposal = build_checklist_proposal(case_to_dict(case), "search")
        self.assertEqual(proposal.kind, "next_action")
        self.assertEqual(proposal.candidate_id, "candidate-1")
        self.assertEqual(proposal.target, "карманы куртки")
        self.assertFalse(hasattr(proposal, "probability"))

    def test_rejected_candidate_is_not_immediately_repeated(self) -> None:
        controller = CaseController()
        case = case_from_dict(create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z"))
        first = CandidateCheck(
            id="candidate-1",
            target="рюкзак",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=(),
            rationale=(),
        )
        second = CandidateCheck(
            id="candidate-2",
            target="куртка",
            route_relation=RouteRelation.INDIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=(),
            rationale=(),
        )
        case = controller.replace_candidates(case, (first, second), "2026-09-10T07:01:00Z")
        case = controller.record_action_feedback(
            case,
            ActionFeedback(
                id="feedback-1",
                candidate_id="candidate-1",
                reason=ActionFeedbackReason.IRRELEVANT,
                recorded_at="2026-09-10T07:02:00Z",
            ),
            "2026-09-10T07:02:00Z",
        )
        proposal = build_checklist_proposal(case_to_dict(case), "search")
        self.assertEqual(proposal.candidate_id, "candidate-2")

    def test_reconstruction_never_generates_location_target(self) -> None:
        case = create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z")
        proposal = build_checklist_proposal(case, "reconstruction")
        self.assertEqual(proposal.kind, "clarification")
        self.assertIsNone(proposal.target)


if __name__ == "__main__":
    unittest.main()
