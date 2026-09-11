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

    def test_create_case_blocks_high_risk_forgotten_action_before_case_creation(self):
        with self.assertRaises(PortableKernelError) as blocked:
            create_case("case-risk", "Принимал ли я уже таблетки?", "2026-09-10T18:00:00Z")
        self.assertEqual(blocked.exception.code, "MD_SAFE_MEDICATION_ACTION")

    def test_create_case_does_not_block_ordinary_lost_medication_item(self):
        case = create_case("case-ordinary", "коробка с таблетками", "2026-09-10T18:00:00Z")
        self.assertEqual(case["item_label"], "коробка с таблетками")

    def test_add_statement_blocks_high_risk_forgotten_action_before_journal_write(self):
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
        with self.assertRaises(PortableKernelError) as blocked:
            apply_command(
                case,
                command(
                    "add_statement",
                    command_id="cmd-risk",
                    expected="2026-09-10T18:01:00Z",
                    now="2026-09-10T18:02:00Z",
                    payload={
                        "statement_id": "stmt-risk",
                        "source": "user",
                        "statement_type": "recollection",
                        "original_text": "Did I turn off the stove?",
                        "event_time": None,
                        "user_confirmation": False,
                        "supporting_evidence_ids": [],
                        "limitations": [],
                    },
                ),
            )
        self.assertEqual(blocked.exception.code, "MD_SAFE_HAZARDOUS_ACTION")
        self.assertEqual(case["statements"], [])
        self.assertEqual(case["interaction_journal"], [])

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
