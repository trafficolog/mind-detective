import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.portable_kernel import (  # noqa: E402
    build_checklist_proposal_json,
    create_case,
    select_next_action_json,
)


def candidate(
    candidate_id: str,
    *,
    target: str = "место",
    route: str = "none",
    state: str = "unchecked",
    effort: str = "low",
    safety: str = "safe",
    urgency: str = "normal",
    basis: str = "generic",
) -> dict[str, object]:
    return {
        "id": candidate_id,
        "target": target,
        "route_relation": route,
        "check_state": state,
        "effort": effort,
        "safety": safety,
        "urgency_relevance": urgency,
        "basis": basis,
        "based_on": [],
        "rationale": [],
    }


class PortablePlannerTests(unittest.TestCase):
    def test_categorical_order_is_urgency_basis_route_state_effort_then_id(self):
        candidates = [
            candidate("z", basis="episode", route="direct", state="unchecked", effort="low"),
            candidate("a", urgency="high", basis="generic", route="none", state="checked", effort="high"),
        ]
        action = select_next_action_json(candidates)
        self.assertIsNotNone(action)
        assert action is not None
        self.assertEqual(action["candidate_id"], "a")
        self.assertIn("MD_PLAN_URGENT", action["rationale_codes"])

        same_rank = [candidate("b", basis="episode"), candidate("a", basis="episode")]
        action = select_next_action_json(same_rank)
        assert action is not None
        self.assertEqual(action["candidate_id"], "a")

    def test_unsafe_candidate_is_excluded(self):
        action = select_next_action_json(
            [candidate("unsafe", safety="unsafe"), candidate("safe", safety="caution")]
        )
        assert action is not None
        self.assertEqual(action["candidate_id"], "safe")

    def test_search_proposal_excludes_rejected_candidate(self):
        case = create_case("case-1", "ключи", "2026-09-10T18:00:00Z")
        case["current_mode"] = "search"
        case["candidates"] = [candidate("a"), candidate("b")]
        case["action_feedback"] = [
            {
                "id": "feedback-1",
                "candidate_id": "a",
                "reason": "irrelevant",
                "recorded_at": "2026-09-10T18:01:00Z",
            }
        ]
        proposal = build_checklist_proposal_json(case, "search")
        self.assertEqual(proposal["kind"], "next_action")
        self.assertEqual(proposal["candidate_id"], "b")

    def test_partial_or_inaccessible_check_becomes_clarification_when_no_candidate(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        case["current_mode"] = "search"
        case["search_checks"] = [
            {
                "id": "check-1",
                "target": "рюкзак",
                "method": "reported_check",
                "started_at": "2026-09-10T18:01:00Z",
                "completed_at": "2026-09-10T18:01:00Z",
                "result": "partial",
                "inaccessible_parts": ["внутренний карман"],
                "based_on": [],
                "notes": [],
            }
        ]
        proposal = build_checklist_proposal_json(case, "search")
        self.assertEqual(proposal["kind"], "clarification")
        self.assertEqual(proposal["target"], "рюкзак")
        self.assertEqual(proposal["copy_key"], "empty.resolve_partial_check")

    def test_empty_search_and_reconstruction_are_neutral(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        search = build_checklist_proposal_json(case, "search")
        self.assertEqual(search["kind"], "need_more_information")
        self.assertIsNone(search["target"])

        reconstruction = build_checklist_proposal_json(case, "reconstruction")
        self.assertEqual(reconstruction["kind"], "clarification")
        self.assertIsNone(reconstruction["target"])
        self.assertEqual(reconstruction["copy_key"], "reconstruction.clarify_supported_sequence")


if __name__ == "__main__":
    unittest.main()
