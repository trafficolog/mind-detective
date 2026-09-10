import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.case import CaseError  # noqa: E402
from scripts.controller import CaseController  # noqa: E402
from scripts.feedback import ActionFeedback, ActionFeedbackReason  # noqa: E402
from scripts.journal import InteractionMode  # noqa: E402
from scripts.portable_intrinsics import PortableKernelError  # noqa: E402
from scripts.portable_kernel import (  # noqa: E402
    close_found_json,
    pause_json,
    record_action_feedback_json,
    resume_json,
    set_mode_json,
)
from scripts.store import case_to_dict  # noqa: E402


class ControllerPortableParityTests(unittest.TestCase):
    def setUp(self):
        self.controller = CaseController()
        self.case = self.controller.create_case("case-1", "ключи", "2026-09-10T18:00:00Z")

    def test_set_mode_matches_portable_primitive(self):
        typed = self.controller.set_mode(self.case, InteractionMode.SEARCH, "2026-09-10T18:01:00Z")
        portable = set_mode_json(case_to_dict(self.case), "search", "2026-09-10T18:01:00Z")
        self.assertEqual(case_to_dict(typed), portable)

    def test_lifecycle_matches_portable_primitives(self):
        paused_typed = self.controller.pause(self.case, "2026-09-10T18:01:00Z")
        paused_json = pause_json(case_to_dict(self.case), "2026-09-10T18:01:00Z")
        self.assertEqual(case_to_dict(paused_typed), paused_json)

        resumed_typed = self.controller.resume(paused_typed, "2026-09-10T18:02:00Z")
        resumed_json = resume_json(paused_json, "2026-09-10T18:02:00Z")
        self.assertEqual(case_to_dict(resumed_typed), resumed_json)

        found_typed = self.controller.close_found(
            resumed_typed,
            "2026-09-10T18:03:00Z",
            {"found_context": "unknown"},
        )
        found_json = close_found_json(
            resumed_json,
            "2026-09-10T18:03:00Z",
            {"found_context": "unknown"},
        )
        self.assertEqual(case_to_dict(found_typed), found_json)

    def test_feedback_matches_portable_primitive_without_journal_side_effect(self):
        feedback = ActionFeedback(
            id="feedback-1",
            candidate_id="candidate-1",
            reason=ActionFeedbackReason.IRRELEVANT,
            recorded_at="2026-09-10T18:01:00Z",
        )
        typed = self.controller.record_action_feedback(
            self.case,
            feedback,
            "2026-09-10T18:01:00Z",
        )
        portable = record_action_feedback_json(
            case_to_dict(self.case),
            {
                "id": "feedback-1",
                "candidate_id": "candidate-1",
                "reason": "irrelevant",
                "recorded_at": "2026-09-10T18:01:00Z",
            },
            "2026-09-10T18:01:00Z",
        )
        self.assertEqual(case_to_dict(typed), portable)
        self.assertEqual(typed.interaction_journal, ())

    def test_controller_preserves_case_error_type_for_terminal_transition(self):
        closed = self.controller.close_found(self.case, "2026-09-10T18:01:00Z")
        with self.assertRaises(CaseError) as typed_error:
            self.controller.pause(closed, "2026-09-10T18:02:00Z")
        with self.assertRaises(PortableKernelError) as portable_error:
            pause_json(case_to_dict(closed), "2026-09-10T18:02:00Z")
        self.assertEqual(typed_error.exception.code, portable_error.exception.code)
        self.assertEqual(typed_error.exception.code, "MD_CASE_TERMINAL")


if __name__ == "__main__":
    unittest.main()
