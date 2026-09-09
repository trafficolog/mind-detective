import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.planner import (  # noqa: E402
    CandidateBasis,
    CandidateCheck,
    CheckState,
    Effort,
    RouteRelation,
    Safety,
    UrgencyRelevance,
    select_next_action,
)


def candidate(
    candidate_id: str,
    *,
    route: RouteRelation = RouteRelation.DIRECT,
    state: CheckState = CheckState.UNCHECKED,
    effort: Effort = Effort.LOW,
    safety: Safety = Safety.SAFE,
    urgency: UrgencyRelevance = UrgencyRelevance.NORMAL,
    basis: CandidateBasis = CandidateBasis.EPISODE,
) -> CandidateCheck:
    return CandidateCheck(
        id=candidate_id,
        target=f"target-{candidate_id}",
        route_relation=route,
        check_state=state,
        effort=effort,
        safety=safety,
        urgency_relevance=urgency,
        basis=basis,
        based_on=("s1",),
        rationale=("test",),
    )


class PlannerTests(unittest.TestCase):
    def test_unsafe_candidate_is_never_selected(self):
        action = select_next_action([
            candidate("unsafe", safety=Safety.UNSAFE),
            candidate("safe", route=RouteRelation.INDIRECT),
        ])
        self.assertIsNotNone(action)
        self.assertEqual(action.candidate_id, "safe")

    def test_direct_episode_unchecked_beats_indirect(self):
        action = select_next_action([
            candidate("indirect", route=RouteRelation.INDIRECT),
            candidate("direct", route=RouteRelation.DIRECT),
        ])
        self.assertEqual(action.candidate_id, "direct")

    def test_partial_beats_checked_when_route_equal(self):
        action = select_next_action([
            candidate("checked", state=CheckState.CHECKED),
            candidate("partial", state=CheckState.PARTIAL),
        ])
        self.assertEqual(action.candidate_id, "partial")

    def test_low_effort_breaks_remaining_tie(self):
        action = select_next_action([
            candidate("high", effort=Effort.HIGH),
            candidate("low", effort=Effort.LOW),
        ])
        self.assertEqual(action.candidate_id, "low")

    def test_habit_beats_generic_after_episode_candidates_exhausted(self):
        action = select_next_action([
            candidate("generic", basis=CandidateBasis.GENERIC),
            candidate("habit", basis=CandidateBasis.HABIT),
        ])
        self.assertEqual(action.candidate_id, "habit")

    def test_urgent_recovery_action_outranks_ordinary_check(self):
        action = select_next_action([
            candidate("ordinary", urgency=UrgencyRelevance.NORMAL),
            candidate(
                "fallback",
                route=RouteRelation.NONE,
                basis=CandidateBasis.GENERIC,
                urgency=UrgencyRelevance.HIGH,
            ),
        ])
        self.assertEqual(action.candidate_id, "fallback")
        self.assertIn("MD_PLAN_URGENT", action.rationale_codes)

    def test_empty_candidates_returns_none(self):
        self.assertIsNone(select_next_action([]))
