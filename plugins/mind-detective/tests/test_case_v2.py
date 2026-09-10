import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.case import CaseError  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.feedback import ActionFeedback, ActionFeedbackReason  # noqa: E402
from scripts.journal import (  # noqa: E402
    InteractionMode,
    JournalAuthor,
    JournalEntry,
    JournalMode,
)


class CaseV2Tests(unittest.TestCase):
    def setUp(self):
        self.controller = CaseController()
        self.case = self.controller.create_case("case-1", "ключи", "2026-09-10T07:00:00Z")

    def test_new_case_is_v2_with_unselected_mode_and_empty_audit_state(self):
        self.assertEqual(self.case.schema, "mind-detective-case/v2")
        self.assertEqual(self.case.current_mode, InteractionMode.UNSELECTED)
        self.assertEqual(self.case.interaction_journal, ())
        self.assertEqual(self.case.action_feedback, ())

    def test_mode_journal_and_feedback_are_controller_owned(self):
        updated = self.controller.set_mode(
            self.case,
            InteractionMode.RECONSTRUCTION,
            "2026-09-10T07:01:00Z",
        )
        entry = JournalEntry(
            id="entry-1",
            author=JournalAuthor.USER,
            mode=JournalMode.RECONSTRUCTION,
            entry_type="statement",
            text="Я точно помню, что вышел из машины.",
            created_at="2026-09-10T07:01:30Z",
            statement_ids=("statement-1",),
        )
        updated = self.controller.append_journal_entry(
            updated,
            entry,
            "2026-09-10T07:01:30Z",
        )
        feedback = ActionFeedback(
            id="feedback-1",
            candidate_id="candidate-1",
            reason=ActionFeedbackReason.IRRELEVANT,
            recorded_at="2026-09-10T07:02:00Z",
        )
        updated = self.controller.record_action_feedback(
            updated,
            feedback,
            "2026-09-10T07:02:00Z",
        )
        self.assertEqual(updated.current_mode, InteractionMode.RECONSTRUCTION)
        self.assertEqual(updated.interaction_journal, (entry,))
        self.assertEqual(updated.action_feedback, (feedback,))

    def test_terminal_case_rejects_new_interaction_mutations(self):
        closed = self.controller.close_unresolved(self.case, "2026-09-10T07:03:00Z")
        entry = JournalEntry(
            id="entry-1",
            author=JournalAuthor.SYSTEM,
            mode=JournalMode.SYSTEM,
            entry_type="system",
            text="closed",
            created_at="2026-09-10T07:03:00Z",
        )
        feedback = ActionFeedback(
            id="feedback-1",
            candidate_id="candidate-1",
            reason=ActionFeedbackReason.OTHER,
            recorded_at="2026-09-10T07:03:00Z",
        )
        operations = (
            lambda: self.controller.set_mode(closed, InteractionMode.SEARCH, "2026-09-10T07:04:00Z"),
            lambda: self.controller.append_journal_entry(closed, entry, "2026-09-10T07:04:00Z"),
            lambda: self.controller.record_action_feedback(closed, feedback, "2026-09-10T07:04:00Z"),
        )
        for operation in operations:
            with self.assertRaises(CaseError) as ctx:
                operation()
            self.assertEqual(ctx.exception.code, "MD_CASE_TERMINAL")


if __name__ == "__main__":
    unittest.main()
