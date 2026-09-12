import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.case import CaseError, CaseLifecycle  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.journal import JournalAuthor, JournalEntry, JournalMode  # noqa: E402
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

    def _candidate(self, candidate_id: str = "p1") -> CandidateCheck:
        return CandidateCheck(
            id=candidate_id,
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

    def test_high_risk_forgotten_action_exits_before_case_creation(self):
        with self.assertRaises(CaseError) as ctx:
            self.controller.create_case(
                "case-risk",
                "Принимал ли я таблетки?",
                "2026-09-09T18:00:00Z",
            )
        self.assertEqual(ctx.exception.code, "MD_SAFE_MEDICATION_ACTION")

    def test_ordinary_lost_medication_item_remains_searchable(self):
        created = self.controller.create_case(
            "case-ordinary",
            "коробка с таблетками",
            "2026-09-09T18:00:00Z",
        )
        self.assertEqual(created.item_label, "коробка с таблетками")

    def test_high_risk_statement_exits_before_case_mutation(self):
        statement = create_statement(
            statement_id="risk-1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Я выключил плиту перед уходом?",
            recorded_at="2026-09-09T18:01:00Z",
            event_time=None,
            user_confirmation=False,
            supporting_evidence_ids=(),
            limitations=(),
        )
        with self.assertRaises(CaseError) as ctx:
            self.controller.add_statement(self.case, statement, "2026-09-09T18:01:00Z")
        self.assertEqual(ctx.exception.code, "MD_SAFE_HAZARDOUS_ACTION")
        self.assertEqual(self.case.statements, ())

    def test_high_risk_user_journal_entry_exits_before_case_mutation(self):
        entry = JournalEntry(
            id="journal-risk",
            author=JournalAuthor.USER,
            mode=JournalMode.RECONSTRUCTION,
            entry_type="note",
            text="Я запер входную дверь?",
            created_at="2026-09-09T18:01:00Z",
        )
        with self.assertRaises(CaseError) as ctx:
            self.controller.append_journal_entry(self.case, entry, "2026-09-09T18:01:00Z")
        self.assertEqual(ctx.exception.code, "MD_SAFE_SECURITY_ACTION")
        self.assertEqual(self.case.interaction_journal, ())

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
        candidate = self._candidate()
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

    def test_controller_refines_reported_check_without_replacing_identity(self):
        candidate = self._candidate()
        case = self.controller.replace_candidates(self.case, (candidate,), "2026-09-09T18:03:00Z")
        reported = SearchCheck(
            id="c1",
            target="Рюкзак",
            method=SearchMethod.REPORTED_CHECK,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=("p1",),
            notes=("user reported check",),
        )
        updated = self.controller.record_search_check(case, reported, "2026-09-09T18:05:00Z")
        self.assertEqual(updated.candidates[0].check_state, CheckState.CHECKED)
        refined = self.controller.refine_search_check(
            updated,
            "c1",
            SearchMethod.EMPTY_AND_CHECK,
            ("секретный карман",),
            "2026-09-09T18:06:00Z",
        )
        self.assertEqual(len(refined.search_checks), 1)
        check = refined.search_checks[0]
        self.assertEqual(check.id, "c1")
        self.assertEqual(check.started_at, reported.started_at)
        self.assertEqual(check.result, reported.result)
        self.assertEqual(check.method, SearchMethod.EMPTY_AND_CHECK)
        self.assertEqual(check.inaccessible_parts, ("секретный карман",))
        self.assertEqual(refined.candidates[0].check_state, CheckState.PARTIAL)

    def test_record_check_updates_only_referenced_candidate_progress(self):
        first = self._candidate("p1")
        second = self._candidate("p2")
        case = self.controller.replace_candidates(self.case, (first, second), "2026-09-09T18:03:00Z")
        check = SearchCheck(
            id="c1",
            target="карманы куртки",
            method=SearchMethod.REPORTED_CHECK,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=(),
            based_on=("p1",),
            notes=(),
        )
        updated = self.controller.record_search_check(case, check, "2026-09-09T18:05:00Z")
        self.assertEqual(updated.candidates[0].check_state, CheckState.CHECKED)
        self.assertEqual(updated.candidates[1].check_state, CheckState.UNCHECKED)


if __name__ == "__main__":
    unittest.main()
