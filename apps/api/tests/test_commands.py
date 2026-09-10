from __future__ import annotations

import unittest

from mind_detective_api.commands import CommandError, execute_command
from mind_detective_api.contracts import CommandEnvelope
from mind_detective_api.core_bridge import create_case_payload


class CommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_payload = create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z")
        self.command = CommandEnvelope(
            command_id="cmd-1",
            expected_updated_at="2026-09-10T07:00:00Z",
            command_type="record_search_check",
            now="2026-09-10T07:01:00Z",
            payload={
                "check_id": "check-1",
                "target": "карманы куртки",
                "result": "not_found",
            },
        )

    def test_retrying_same_command_against_same_case_is_deterministic(self):
        first = execute_command(self.case_payload, self.command)
        second = execute_command(self.case_payload, self.command)
        self.assertEqual(first, second)

    def test_one_tap_check_uses_neutral_reported_check(self):
        updated = execute_command(self.case_payload, self.command)
        self.assertEqual(updated["search_checks"][0]["method"], "reported_check")
        self.assertEqual(updated["search_checks"][0]["id"], "check-1")

    def test_stale_expected_updated_at_fails_closed(self):
        stale = self.command.model_copy(update={"expected_updated_at": "2026-09-10T06:59:00Z"})
        with self.assertRaises(CommandError) as ctx:
            execute_command(self.case_payload, stale)
        self.assertEqual(ctx.exception.code, "MD_WEB_STALE_COMMAND")

    def test_rejection_feedback_is_categorical_domain_state(self):
        command = CommandEnvelope(
            command_id="cmd-2",
            expected_updated_at="2026-09-10T07:00:00Z",
            command_type="reject_next_action",
            now="2026-09-10T07:02:00Z",
            payload={
                "feedback_id": "feedback-1",
                "candidate_id": "candidate-1",
                "reason": "irrelevant",
            },
        )
        updated = execute_command(self.case_payload, command)
        self.assertEqual(updated["action_feedback"][0]["reason"], "irrelevant")
        self.assertNotIn("score", updated["action_feedback"][0])

    def test_probability_field_is_rejected_recursively(self):
        command = CommandEnvelope(
            command_id="cmd-3",
            expected_updated_at="2026-09-10T07:00:00Z",
            command_type="close_found",
            now="2026-09-10T07:03:00Z",
            payload={"outcome": {"found_context": "unknown", "probability": 0.9}},
        )
        with self.assertRaises(CommandError) as ctx:
            execute_command(self.case_payload, command)
        self.assertEqual(ctx.exception.code, "MD_WEB_FORBIDDEN_FIELD")


if __name__ == "__main__":
    unittest.main()
