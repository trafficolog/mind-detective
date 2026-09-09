import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.artifacts import ArtifactError, build_handoff, build_outcome  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.search_log import SearchCheck, SearchMethod, SearchResult  # noqa: E402
from scripts.statements import StatementSource, StatementType, create_statement  # noqa: E402
from scripts.timeline import build_timeline  # noqa: E402


class ArtifactTests(unittest.TestCase):
    def _active_case(self):
        controller = CaseController()
        case = controller.create_case("case-1", "ключи", "2026-09-09T18:00:00Z")
        recollection = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Помню ключи в руке перед выходом.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("точное время неизвестно",),
        )
        possible_cause = create_statement(
            statement_id="s2",
            source=StatementSource.USER,
            statement_type=StatementType.HYPOTHESIS,
            original_text="Я думаю, что мог отвлечься на звонок.",
            recorded_at="2026-09-09T18:02:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("user-authored possible cause",),
        )
        case = controller.add_statement(case, recollection, "2026-09-09T18:01:00Z")
        case = controller.add_statement(case, possible_cause, "2026-09-09T18:02:00Z")
        timeline = build_timeline([recollection, possible_cause], [], "s1", None)
        case = controller.set_timeline(case, timeline, "2026-09-09T18:03:00Z")
        check = SearchCheck(
            id="c1",
            target="карманы куртки",
            method=SearchMethod.TACTILE,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.PARTIAL,
            inaccessible_parts=("застёгнутый внутренний карман",),
            based_on=("s1",),
            notes=(),
        )
        case = controller.record_search_check(case, check, "2026-09-09T18:05:00Z")
        case = controller.set_constraints(case, ("нужно выйти через 20 минут",), "2026-09-09T18:06:00Z")
        return controller, case

    def test_handoff_preserves_statement_provenance_and_search_method(self):
        _, case = self._active_case()
        artifact = build_handoff(case)
        self.assertEqual(artifact["schema"], "mind-detective-handoff/v1")
        statement = artifact["statements"][0]
        self.assertEqual(statement["source"], "user")
        self.assertEqual(statement["statement_type"], "recollection")
        self.assertEqual(statement["original_text"], "Помню ключи в руке перед выходом.")
        self.assertEqual(artifact["search_history"][0]["method"], "tactile")
        self.assertEqual(
            artifact["search_history"][0]["inaccessible_parts"],
            ["застёгнутый внутренний карман"],
        )

    def test_outcome_references_user_authored_possible_cause_without_diagnosis(self):
        controller, case = self._active_case()
        outcome_data = {
            "user_reported_found_location": "внутренний карман куртки",
            "preceding_search_check_id": "c1",
            "possible_cause_statement_id": "s2",
            "prevention_note": "класть ключи в одно место",
            "retention_decision": "retain",
        }
        closed = controller.close_found(case, "2026-09-09T18:10:00Z", outcome=outcome_data)
        artifact = build_outcome(closed)
        self.assertEqual(artifact["status"], "found")
        self.assertEqual(artifact["possible_cause_statement_id"], "s2")
        self.assertNotIn("forgetting_mechanism", artifact)
        self.assertNotIn("diagnosis", artifact)

    def test_outcome_rejects_assistant_authored_possible_cause(self):
        controller, case = self._active_case()
        assistant_hypothesis = create_statement(
            statement_id="s3",
            source=StatementSource.ASSISTANT,
            statement_type=StatementType.HYPOTHESIS,
            original_text="Возможно, вас отвлёк звонок.",
            recorded_at="2026-09-09T18:07:00Z",
            event_time=None,
            user_confirmation=False,
            supporting_evidence_ids=(),
            limitations=(),
        )
        case = controller.add_statement(case, assistant_hypothesis, "2026-09-09T18:07:00Z")
        closed = controller.close_unresolved(
            case,
            "2026-09-09T18:10:00Z",
            outcome={
                "possible_cause_statement_id": "s3",
                "retention_decision": "delete",
            },
        )
        with self.assertRaises(ArtifactError) as ctx:
            build_outcome(closed)
        self.assertEqual(ctx.exception.code, "MD_OUTCOME_CAUSE_NOT_USER")

    def test_artifacts_never_emit_private_reasoning_fields(self):
        controller, case = self._active_case()
        closed = controller.close_unresolved(
            case,
            "2026-09-09T18:10:00Z",
            outcome={"retention_decision": "retain"},
        )
        text = repr(build_handoff(case)).casefold() + repr(build_outcome(closed)).casefold()
        for forbidden in ("chain_of_thought", "belief_weight", "forgetting_mechanism"):
            self.assertNotIn(forbidden, text)

    def test_outcome_requires_closed_case(self):
        _, case = self._active_case()
        with self.assertRaises(ArtifactError) as ctx:
            build_outcome(case)
        self.assertEqual(ctx.exception.code, "MD_OUTCOME_CASE_OPEN")


if __name__ == "__main__":
    unittest.main()
