import json
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.case import CaseLifecycle  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.journal import InteractionMode  # noqa: E402
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
from scripts.store import StoreError, delete_case, load_case, save_case  # noqa: E402


class StoreTests(unittest.TestCase):
    def _case(self):
        controller = CaseController()
        case = controller.create_case("case-1", "ключи", "2026-09-09T18:00:00Z")
        statement = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Ключи были у меня перед выходом.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time="2026-09-09T17:55:00Z",
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("time approximate",),
        )
        case = controller.add_statement(case, statement, "2026-09-09T18:01:00Z")
        candidate = CandidateCheck(
            id="p1",
            target="карманы куртки",
            route_relation=RouteRelation.DIRECT,
            check_state=CheckState.PARTIAL,
            effort=Effort.LOW,
            safety=Safety.SAFE,
            urgency_relevance=UrgencyRelevance.NORMAL,
            basis=CandidateBasis.EPISODE,
            based_on=("s1",),
            rationale=("direct route",),
        )
        case = controller.replace_candidates(case, (candidate,), "2026-09-09T18:02:00Z")
        case = controller.refresh_next_action(case, "2026-09-09T18:03:00Z")
        check = SearchCheck(
            id="c1",
            target="карманы куртки",
            method=SearchMethod.GLANCE,
            started_at="2026-09-09T18:04:00Z",
            completed_at="2026-09-09T18:05:00Z",
            result=SearchResult.NOT_FOUND,
            inaccessible_parts=("внутренний карман",),
            based_on=("p1",),
            notes=("checked while standing",),
        )
        case = controller.record_search_check(case, check, "2026-09-09T18:05:00Z")
        return controller.pause(case, "2026-09-09T18:06:00Z")

    def test_save_load_round_trip_preserves_case_state(self):
        case = self._case()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = save_case(case, root)
            loaded = load_case("case-1", root)
            self.assertEqual(path, root / ".mind-detective/cases/case-1/case.json")
            self.assertEqual(loaded, case)
            self.assertEqual(loaded.schema, "mind-detective-case/v2")
            self.assertEqual(loaded.current_mode, InteractionMode.UNSELECTED)
            self.assertEqual(loaded.lifecycle, CaseLifecycle.PAUSED)

    def test_save_creates_no_profile_or_cross_case_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_case(self._case(), root)
            memory_root = root / ".mind-detective"
            self.assertFalse((memory_root / "profile.json").exists())
            self.assertFalse((memory_root / "profile.yaml").exists())
            self.assertFalse((memory_root / "index.json").exists())
            self.assertEqual(
                sorted(path.relative_to(memory_root).as_posix() for path in memory_root.rglob("*") if path.is_file()),
                ["cases/case-1/case.json"],
            )

    def test_delete_removes_only_selected_case(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case1 = self._case()
            controller = CaseController()
            case2 = controller.create_case("case-2", "паспорт", "2026-09-09T19:00:00Z")
            save_case(case1, root)
            save_case(case2, root)
            self.assertTrue(delete_case("case-1", root))
            self.assertFalse((root / ".mind-detective/cases/case-1").exists())
            self.assertTrue((root / ".mind-detective/cases/case-2/case.json").exists())
            self.assertFalse(delete_case("case-1", root))

    def test_unsupported_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ".mind-detective/cases/case-1/case.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"schema": "mind-detective-case/v999"}), encoding="utf-8")
            with self.assertRaises(StoreError) as ctx:
                load_case("case-1", root)
            self.assertEqual(ctx.exception.code, "MD_STORE_SCHEMA_VERSION")

    def test_persisted_artifact_has_no_forbidden_reasoning_or_probability_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = save_case(self._case(), Path(directory))
            text = path.read_text(encoding="utf-8").casefold()
            for forbidden in ("chain_of_thought", "belief_weight", '"probability"', '"pod"', "user_profile"):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
