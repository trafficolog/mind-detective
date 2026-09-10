import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.case import CaseError, CaseLifecycle  # noqa: E402
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


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = CaseController()
        self.case = self.controller.create_case("case-1", "ключи", "2026-09-09T18:00:00Z")

    def test_lifecycle_create_pause_resume_close(self):
        self.assertEqual(self.case.lifecycle, CaseLifecycle.ACTIVE)
        paused = self.controller.pause(self.case, "2026-09-09T18:01:00Z")
        self.assertEqual(paused.lifecycle, CaseLifecycle.PAUSED)
        resumed = self.controller.resume(paused, "2026-09-09T18:02:00Z")
        self.assertEqual(resumed.lifecycle, CaseLifecycle.ACTIVE)
        closed = self.controller.close_found(resumed, "2026-09-09T18:03:00Z")
        self.assertEqual(closed.lifecycle, CaseLifecycle.CLOSED_FOUND)

    def test_closed_case_rejects_search_mutation(self):
        closed = self.controller.close_unresolved(self.case, "2026-09-09T18:03:00Z")
        check = SearchCheck(
            id="c1",
            target="карманы куртки",
            method=SearchMethod.GLANCE,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=(),
            notes=(),
        )
        with self.assertRaises(CaseError) as ctx:
            self.controller.record_search_check(closed, check, "2026-09-09T18:05:00Z")
        self.assertEqual(ctx.exception.code, "MD_CASE_TERMINAL")

    def test_deleted_case_is_terminal(self):
        deleted = self.controller.mark_deleted(self.case, "2026-09-09T18:03:00Z")
        with self.assertRaises(CaseError) as ctx:
            self.controller.resume(deleted, "2026-09-09T18:04:00Z")
        self.assertEqual(ctx.exception.code, "MD_CASE_TERMINAL")

    def test_controller_delegates_statement_and_planning_rules(self):
        statement = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Ключи были в руке перед выходом.",
            recorded_at="2026-09-09T18:00:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=(),
        )
        updated = self.controller.add_statement(self.case, statement, "2026-09-09T18:01:00Z")
        candidate = CandidateCheck(
            id="p1",
            target="карманы куртки",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.UNCHECKED,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=("s1",),
            rationale=("direct route",),
        )
        updated = self.controller.replace_candidates(updated, (candidate,), "2026-09-09T18:02:00Z")
        updated = self.controller.refresh_next_action(updated, "2026-09-09T18:03:00Z")
        self.assertEqual(updated.statements, (statement,))
        self.assertEqual(updated.next_action.candidate_id, "p1")

    def test_controller_surfaces_near_duplicate_search_history(self):
        first = SearchCheck(
            id="c1",
            target="Карманы куртки",
            method=SearchMethod.GLANCE,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=("s1",),
            notes=(),
        )
        updated = self.controller.record_search_check(self.case, first, "2026-09-09T18:05:00Z")
        duplicates = self.controller.find_duplicate_search_checks(updated, "карманы вчерашней куртки")
        self.assertEqual(duplicates, (first,))
        self.assertEqual(duplicates[0].method, SearchMethod.GLANCE)
        self.assertEqual(duplicates[0].result, SearchResult.NOT_FOUND)
