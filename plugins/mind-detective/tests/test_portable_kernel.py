import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.portable_intrinsics import PortableKernelError  # noqa: E402
from scripts.portable_kernel import apply_command, create_case  # noqa: E402


def command(
    command_type: str,
    *,
    command_id: str,
    expected: str,
    now: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "command_id": command_id,
        "expected_updated_at": expected,
        "command_type": command_type,
        "now": now,
        "payload": payload or {},
    }


class PortableKernelTests(unittest.TestCase):
    def test_create_case_matches_case_v2_shape(self):
        case = create_case("case-1", "ключи", "2026-09-10T18:00:00Z")
        self.assertEqual(case["schema"], "mind-detective-case/v2")
        self.assertEqual(case["lifecycle"], "active")
        self.assertEqual(case["current_mode"], "unselected")
        self.assertEqual(case["statements"], [])
        self.assertEqual(case["interaction_journal"], [])
        self.assertEqual(case["action_feedback"], [])

    def test_mode_and_pause_transitions_do_not_mutate_input(self):
        source = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        original = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        search = apply_command(
            source,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "search"},
            ),
        )
        paused = apply_command(
            search,
            command(
                "pause",
                command_id="cmd-pause",
                expected="2026-09-10T18:01:00Z",
                now="2026-09-10T18:02:00Z",
            ),
        )
        self.assertEqual(source, original)
        self.assertEqual(search["current_mode"], "search")
        self.assertEqual(paused["lifecycle"], "paused")

    def test_record_free_account_appends_verbatim_journal_entry_only(self):
        case = create_case("case-1", "ключи", "2026-09-10T18:00:00Z")
        reconstruction = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "reconstruction"},
            ),
        )
        text = "Я пришёл домой и положил ключи, но не помню куда."
        result = apply_command(
            reconstruction,
            command(
                "record_free_account",
                command_id="cmd-free",
                expected="2026-09-10T18:01:00Z",
                now="2026-09-10T18:02:00Z",
                payload={"entry_id": "free-1", "text": text},
            ),
        )
        self.assertEqual(result["statements"], [])
        self.assertEqual(
            result["interaction_journal"],
            [
                {
                    "id": "free-1",
                    "author": "user",
                    "mode": "reconstruction",
                    "entry_type": "free_account",
                    "text": text,
                    "created_at": "2026-09-10T18:02:00Z",
                    "statement_ids": [],
                    "search_check_ids": [],
                }
            ],
        )
        self.assertEqual(reconstruction["interaction_journal"], [])

    def test_record_free_account_requires_reconstruction_mode(self):
        unselected = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        search = apply_command(
            unselected,
            command(
                "set_mode",
                command_id="cmd-search",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "search"},
            ),
        )
        for name, case, expected in (
            ("unselected", unselected, "2026-09-10T18:00:00Z"),
            ("search", search, "2026-09-10T18:01:00Z"),
        ):
            with self.subTest(mode=name):
                with self.assertRaises(PortableKernelError) as ctx:
                    apply_command(
                        case,
                        command(
                            "record_free_account",
                            command_id=f"cmd-free-{name}",
                            expected=expected,
                            now="2026-09-10T18:02:00Z",
                            payload={"entry_id": "free-1", "text": "Свободный рассказ"},
                        ),
                    )
                self.assertEqual(ctx.exception.code, "MD_RECON_MODE_REQUIRED")

    def test_record_free_account_rejects_empty_id_or_text(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        reconstruction = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "reconstruction"},
            ),
        )
        for payload in (
            {"entry_id": "", "text": "Свободный рассказ"},
            {"entry_id": "free-1", "text": ""},
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(PortableKernelError) as ctx:
                    apply_command(
                        reconstruction,
                        command(
                            "record_free_account",
                            command_id="cmd-free",
                            expected="2026-09-10T18:01:00Z",
                            now="2026-09-10T18:02:00Z",
                            payload=payload,
                        ),
                    )
                self.assertEqual(ctx.exception.code, "MD_WEB_COMMAND_PAYLOAD")

    def test_second_distinct_free_account_is_rejected(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        reconstruction = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "reconstruction"},
            ),
        )
        first = apply_command(
            reconstruction,
            command(
                "record_free_account",
                command_id="cmd-free-1",
                expected="2026-09-10T18:01:00Z",
                now="2026-09-10T18:02:00Z",
                payload={"entry_id": "free-1", "text": "Первый рассказ"},
            ),
        )
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                first,
                command(
                    "record_free_account",
                    command_id="cmd-free-2",
                    expected="2026-09-10T18:02:00Z",
                    now="2026-09-10T18:03:00Z",
                    payload={"entry_id": "free-2", "text": "Второй рассказ"},
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_FREE_ACCOUNT_EXISTS")
        self.assertEqual(len(first["interaction_journal"]), 1)

    def test_reconstruction_statement_requires_free_account(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        reconstruction = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "reconstruction"},
            ),
        )
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                reconstruction,
                command(
                    "add_statement",
                    command_id="cmd-statement",
                    expected="2026-09-10T18:01:00Z",
                    now="2026-09-10T18:02:00Z",
                    payload={
                        "statement_id": "stmt-1",
                        "source": "user",
                        "statement_type": "recollection",
                        "original_text": "Ключи были в руке у двери",
                    },
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_FREE_ACCOUNT_REQUIRED")
        self.assertEqual(reconstruction["statements"], [])
        self.assertEqual(reconstruction["interaction_journal"], [])

    def test_search_suggestion_creates_exact_user_supported_candidate_and_journal(self):
        case = create_case("case-1", "ключи", "2026-09-10T18:00:00Z")
        case = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "search"},
            ),
        )
        result = apply_command(
            case,
            command(
                "add_statement",
                command_id="cmd-statement",
                expected="2026-09-10T18:01:00Z",
                now="2026-09-10T18:02:00Z",
                payload={
                    "statement_id": "stmt-1",
                    "source": "user",
                    "statement_type": "search_suggestion",
                    "original_text": "карман синего рюкзака",
                    "event_time": None,
                    "user_confirmation": True,
                    "supporting_evidence_ids": [],
                    "limitations": [],
                },
            ),
        )
        candidates = result["candidates"]
        journal = result["interaction_journal"]
        self.assertIsInstance(candidates, list)
        self.assertIsInstance(journal, list)
        assert isinstance(candidates, list)
        assert isinstance(journal, list)
        candidate = candidates[0]
        entry = journal[-1]
        self.assertIsInstance(candidate, dict)
        self.assertIsInstance(entry, dict)
        assert isinstance(candidate, dict)
        assert isinstance(entry, dict)
        self.assertEqual(candidate["id"], "candidate-stmt-1")
        self.assertEqual(candidate["target"], "карман синего рюкзака")
        self.assertEqual(candidate["based_on"], ["stmt-1"])
        self.assertEqual(entry["id"], "journal-cmd-statement")
        self.assertEqual(entry["mode"], "search")

    def test_reconstruction_search_suggestion_does_not_create_candidate(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        case = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-mode",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:01:00Z",
                payload={"mode": "reconstruction"},
            ),
        )
        case = apply_command(
            case,
            command(
                "record_free_account",
                command_id="cmd-free",
                expected="2026-09-10T18:01:00Z",
                now="2026-09-10T18:02:00Z",
                payload={"entry_id": "free-1", "text": "Сначала свободно вспоминаю эпизод"},
            ),
        )
        result = apply_command(
            case,
            command(
                "add_statement",
                command_id="cmd-statement",
                expected="2026-09-10T18:02:00Z",
                now="2026-09-10T18:03:00Z",
                payload={
                    "statement_id": "stmt-1",
                    "source": "user",
                    "statement_type": "search_suggestion",
                    "original_text": "машина",
                },
            ),
        )
        self.assertEqual(result["candidates"], [])

    def test_reported_check_updates_only_referenced_candidate(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        case["current_mode"] = "search"
        case["candidates"] = [
            {
                "id": "candidate-1",
                "target": "рюкзак",
                "route_relation": "none",
                "check_state": "unchecked",
                "effort": "low",
                "safety": "caution",
                "urgency_relevance": "normal",
                "basis": "episode",
                "based_on": ["stmt-1"],
                "rationale": ["MD_PLAN_USER_SUPPORTED"],
            },
            {
                "id": "candidate-2",
                "target": "машина",
                "route_relation": "direct",
                "check_state": "unchecked",
                "effort": "low",
                "safety": "safe",
                "urgency_relevance": "normal",
                "basis": "episode",
                "based_on": ["stmt-2"],
                "rationale": [],
            },
        ]
        result = apply_command(
            case,
            command(
                "record_search_check",
                command_id="cmd-check",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:03:00Z",
                payload={
                    "check_id": "check-1",
                    "target": "рюкзак",
                    "based_on": ["candidate-1"],
                },
            ),
        )
        checks = result["search_checks"]
        candidates = result["candidates"]
        assert isinstance(checks, list)
        assert isinstance(candidates, list)
        assert isinstance(checks[-1], dict)
        assert isinstance(candidates[0], dict)
        assert isinstance(candidates[1], dict)
        self.assertEqual(checks[-1]["method"], "reported_check")
        self.assertEqual(candidates[0]["check_state"], "checked")
        self.assertEqual(candidates[1]["check_state"], "unchecked")

    def test_reject_next_action_records_categorical_feedback(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        result = apply_command(
            case,
            command(
                "reject_next_action",
                command_id="cmd-feedback",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:04:00Z",
                payload={
                    "feedback_id": "feedback-1",
                    "candidate_id": "candidate-1",
                    "reason": "irrelevant",
                },
            ),
        )
        feedback = result["action_feedback"]
        assert isinstance(feedback, list)
        assert isinstance(feedback[0], dict)
        self.assertEqual(feedback[0]["reason"], "irrelevant")
        self.assertNotIn("score", feedback[0])
        self.assertNotIn("probability", feedback[0])

    def test_stale_and_forbidden_commands_fail_with_exact_codes(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        with self.assertRaises(PortableKernelError) as stale:
            apply_command(
                case,
                command(
                    "pause",
                    command_id="cmd-stale",
                    expected="older",
                    now="2026-09-10T18:05:00Z",
                ),
            )
        self.assertEqual(stale.exception.code, "MD_WEB_STALE_COMMAND")

        with self.assertRaises(PortableKernelError) as forbidden:
            apply_command(
                case,
                command(
                    "close_found",
                    command_id="cmd-forbidden",
                    expected="2026-09-10T18:00:00Z",
                    now="2026-09-10T18:05:00Z",
                    payload={"outcome": {"probability": 0.9}},
                ),
            )
        self.assertEqual(forbidden.exception.code, "MD_WEB_FORBIDDEN_FIELD")

    def test_terminal_case_rejects_further_mutation(self):
        case = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
        closed = apply_command(
            case,
            command(
                "close_unresolved",
                command_id="cmd-close",
                expected="2026-09-10T18:00:00Z",
                now="2026-09-10T18:06:00Z",
            ),
        )
        with self.assertRaises(PortableKernelError) as terminal:
            apply_command(
                closed,
                command(
                    "set_mode",
                    command_id="cmd-mode",
                    expected="2026-09-10T18:06:00Z",
                    now="2026-09-10T18:07:00Z",
                    payload={"mode": "search"},
                ),
            )
        self.assertEqual(terminal.exception.code, "MD_CASE_TERMINAL")


if __name__ == "__main__":
    unittest.main()
