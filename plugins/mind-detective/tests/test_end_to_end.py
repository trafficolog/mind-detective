import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.artifacts import build_outcome  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.planner import (  # noqa: E402
    CandidateBasis,
    CandidateCheck,
    CheckState,
    Effort,
    RouteRelation,
    Safety,
    UrgencyRelevance,
)
from scripts.search_log import SearchCheck, SearchMethod, SearchResult  # noqa: E402
from scripts.statements import StatementSource, StatementType, create_statement  # noqa: E402
from scripts.store import case_to_dict, load_case, save_case  # noqa: E402
from scripts.timeline import build_timeline  # noqa: E402


APPROVED_SKILLS = {
    "mind-detective",
    "mind-detective-reconstruct",
    "mind-detective-plan",
    "mind-detective-resume",
    "mind-detective-close",
}


class EndToEndTests(unittest.TestCase):
    def test_plugin_exposes_exactly_five_approved_skills(self):
        skills_root = PLUGIN_ROOT / "skills"
        actual = {path.name for path in skills_root.iterdir() if path.is_dir()} if skills_root.exists() else set()
        self.assertEqual(actual, APPROVED_SKILLS)
        for name in APPROVED_SKILLS:
            self.assertTrue((skills_root / name / "SKILL.md").is_file())
        for legacy in ("mind-detective-quickcheck", "mind-detective-zones", "mind-detective-hypotheses", "mind-detective-fallback", "mind-detective-debrief"):
            self.assertFalse((skills_root / legacy).exists())

    def test_pause_save_resume_found_flow_has_no_numeric_probability_state(self):
        controller = CaseController()
        case = controller.create_case("case-e2e", "ключи", "2026-09-09T18:00:00Z")
        recollection = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Перед выходом ключи были у меня в руке.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time="2026-09-09T17:55:00Z",
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=(),
        )
        case = controller.add_statement(case, recollection, "2026-09-09T18:01:00Z")
        case = controller.set_timeline(
            case,
            build_timeline([recollection], [], "s1", None),
            "2026-09-09T18:02:00Z",
        )
        first = CandidateCheck(
            id="p1",
            target="внешние карманы куртки",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=("s1",),
            rationale=("direct route",),
        )
        second = CandidateCheck(
            id="p2",
            target="внутренний карман куртки",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.MEDIUM,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=("s1",),
            rationale=("same route, separate compartment",),
        )
        case = controller.replace_candidates(case, (first, second), "2026-09-09T18:03:00Z")
        case = controller.refresh_next_action(case, "2026-09-09T18:03:30Z")
        self.assertEqual(case.next_action.candidate_id, "p1")

        glance = SearchCheck(
            id="c1",
            target=first.target,
            method=SearchMethod.GLANCE,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:04:30Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=("p1",),
            notes=(),
        )
        case = controller.record_search_check(case, glance, "2026-09-09T18:04:30Z")
        first_partial = CandidateCheck(
            id=first.id,
            target=first.target,
            route_relation=first.route_relation,
            check_state=CheckState.PARTIAL,
            effort=first.effort,
            safety=first.safety,
            urgency_relevance=first.urgency_relevance,
            basis=first.basis,
            based_on=first.based_on,
            rationale=first.rationale,
        )
        case = controller.replace_candidates(case, (first_partial, second), "2026-09-09T18:05:00Z")
        case = controller.refresh_next_action(case, "2026-09-09T18:05:30Z")
        self.assertEqual(case.next_action.candidate_id, "p2")

        paused = controller.pause(case, "2026-09-09T18:06:00Z")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_case(paused, root)
            resumed = controller.resume(load_case("case-e2e", root), "2026-09-09T18:30:00Z")

        found_check = SearchCheck(
            id="c2",
            target=second.target,
            method=SearchMethod.TACTILE,
            started_at="2026-09-09T18:31:00Z",
            completed_at="2026-09-09T18:32:00Z",
            result=SearchResult.FOUND,
            inaccessible_parts=(),
            based_on=("p2",),
            notes=(),
        )
        resumed = controller.record_search_check(resumed, found_check, "2026-09-09T18:32:00Z")
        closed = controller.close_found(
            resumed,
            "2026-09-09T18:33:00Z",
            outcome={
                "user_reported_found_location": second.target,
                "preceding_search_check_id": "c2",
                "retention_decision": "retain",
            },
        )
        outcome = build_outcome(closed)
        self.assertEqual(outcome["status"], "found")
        serialized = repr(case_to_dict(closed)).casefold()
        for forbidden in ("belief_weight", "probability", "posterior", "pod"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
