from __future__ import annotations

import unittest

from mind_detective_api.commands import CommandError, execute_command
from mind_detective_api.contracts import CommandEnvelope
from mind_detective_api.core_bridge import create_case_payload

from scripts.store import case_from_dict


class CommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_payload = create_case_payload("case-1", "ключи", "2026-09-10T07:00:00Z")
        self.case_payload["current_mode"] = "search"
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

    def test_retrying_same_command_against_same_case_is_deterministic(self) -> None:
        first = execute_command(self.case_payload, self.command)
        second = execute_command(self.case_payload, self.command)
        self.assertEqual(first, second)

    def test_one_tap_check_uses_neutral_reported_check(self) -> None:
        updated = case_from_dict(execute_command(self.case_payload, self.command))
        self.assertEqual(updated.search_checks[0].method.value, "reported_check")
        self.assertEqual(updated.search_checks[0].id, "check-1")
        self.assertEqual(updated.interaction_journal[0].id, "journal-cmd-1")
        self.assertEqual(updated.interaction_journal[0].mode.value, "search")
        self.assertEqual(updated.interaction_journal[0].search_check_ids, ("check-1",))

    def test_user_statement_creates_server_owned_journal_provenance(self) -> None:
        command = CommandEnvelope(
            command_id="cmd-statement",
            expected_updated_at="2026-09-10T07:00:00Z",
            command_type="add_statement",
            now="2026-09-10T07:01:30Z",
            payload={
                "statement_id": "statement-1",
                "source": "user",
                "statement_type": "observation",
                "original_text": "Я уже проверил стол.",
                "event_time": None,
                "user_confirmation": True,
                "supporting_evidence_ids": [],
                "limitations": [],
            },
        )
        updated = case_from_dict(execute_command(self.case_payload, command))
        self.assertEqual(updated.interaction_journal[0].id, "journal-cmd-statement")
        self.assertEqual(updated.interaction_journal[0].author.value, "user")
        self.assertEqual(updated.interaction_journal[0].mode.value, "search")
        self.assertEqual(updated.interaction_journal[0].statement_ids, ("statement-1",))
        self.assertEqual(updated.interaction_journal[0].text, "Я уже проверил стол.")

    def test_unselected_case_rejects_journal_activity(self) -> None:
        unselected = create_case_payload("case-2", "паспорт", "2026-09-10T07:00:00Z")
        with self.assertRaises(CommandError) as ctx:
            execute_command(unselected, self.command)
        self.assertEqual(ctx.exception.code, "MD_WEB_MODE_REQUIRED")

    def test_web_statement_source_must_be_user(self) -> None:
        command = CommandEnvelope(
            command_id="cmd-assistant-statement",
            expected_updated_at="2026-09-10T07:00:00Z",
            command_type="add_statement",
            now="2026-09-10T07:01:30Z",
            payload={
                "statement_id": "statement-1",
                "source": "assistant",
                "statement_type": "hypothesis",
                "original_text": "Проверить машину.",
                "event_time": None,
                "user_confirmation": False,
                "supporting_evidence_ids": [],
                "limitations": [],
            },
        )
        with self.assertRaises(CommandError) as ctx:
            execute_command(self.case_payload, command)
        self.assertEqual(ctx.exception.code, "MD_WEB_STATEMENT_SOURCE")

    def test_stale_expected_updated_at_fails_closed(self) -> None:
        stale = self.command.model_copy(update={"expected_updated_at": "2026-09-10T06:59:00Z"})
        with self.assertRaises(CommandError) as ctx:
            execute_command(self.case_payload, stale)
        self.assertEqual(ctx.exception.code, "MD_WEB_STALE_COMMAND")

    def test_rejection_feedback_is_categorical_domain_state(self) -> None:
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
        updated = case_from_dict(execute_command(self.case_payload, command))
        self.assertEqual(updated.action_feedback[0].reason.value, "irrelevant")
        self.assertFalse(hasattr(updated.action_feedback[0], "score"))

    def test_probability_field_is_rejected_recursively(self) -> None:
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
