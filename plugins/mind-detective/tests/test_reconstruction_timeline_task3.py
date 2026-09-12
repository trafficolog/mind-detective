import copy
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.controller import CaseController  # noqa: E402
from scripts.journal import InteractionMode  # noqa: E402
from scripts.portable_intrinsics import PortableKernelError  # noqa: E402
from scripts.portable_kernel import apply_command, create_case  # noqa: E402
from scripts.statements import StatementSource, StatementType, create_statement  # noqa: E402
from scripts.timeline import Timeline, TimelineEvent, build_timeline  # noqa: E402


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


def reconstruction_case() -> dict[str, object]:
    case = create_case("case-timeline", "ключи", "2026-09-12T08:00:00+03:00")
    case = apply_command(
        case,
        command(
            "set_mode",
            command_id="cmd-mode",
            expected="2026-09-12T08:00:00+03:00",
            now="2026-09-12T08:01:00+03:00",
            payload={"mode": "reconstruction"},
        ),
    )
    return apply_command(
        case,
        command(
            "record_free_account",
            command_id="cmd-free",
            expected="2026-09-12T08:01:00+03:00",
            now="2026-09-12T08:02:00+03:00",
            payload={"entry_id": "free-1", "text": "Сначала свободно вспоминаю эпизод."},
        ),
    )


def add_statement(
    case: dict[str, object],
    *,
    command_id: str,
    statement_id: str,
    now: str,
    event_time: str | None,
    limitations: list[str] | None = None,
) -> dict[str, object]:
    return apply_command(
        case,
        command(
            "add_statement",
            command_id=command_id,
            expected=str(case["updated_at"]),
            now=now,
            payload={
                "statement_id": statement_id,
                "source": "user",
                "statement_type": "recollection",
                "original_text": f"Подтверждённое утверждение {statement_id}",
                "event_time": event_time,
                "user_confirmation": True,
                "supporting_evidence_ids": [],
                "limitations": limitations or [],
            },
        ),
    )


def rebuild(
    case: dict[str, object],
    *,
    payload: dict[str, object],
    now: str = "2026-09-12T08:10:00+03:00",
) -> dict[str, object]:
    try:
        return apply_command(
            case,
            command(
                "rebuild_timeline",
                command_id="cmd-timeline",
                expected=str(case["updated_at"]),
                now=now,
                payload=payload,
            ),
        )
    except PortableKernelError as exc:
        if exc.code == "MD_WEB_COMMAND_TYPE":
            raise AssertionError("rebuild_timeline is not implemented in the portable kernel") from exc
        raise


class PortableReconstructionTimelineTests(unittest.TestCase):
    def test_valid_rebuild_writes_canonical_timeline_and_preserves_unknown_interval(self):
        case = reconstruction_case()
        case = add_statement(
            case,
            command_id="cmd-s1",
            statement_id="stmt-1",
            now="2026-09-12T08:03:00+03:00",
            event_time="2026-09-12T08:30:00+03:00",
        )
        case = add_statement(
            case,
            command_id="cmd-s2",
            statement_id="stmt-2",
            now="2026-09-12T08:04:00+03:00",
            event_time=None,
            limitations=["неизвестно точное время"],
        )
        result = rebuild(
            case,
            payload={
                "events": [
                    {
                        "id": "event-1",
                        "label": "Последний подтверждённый контакт с ключами",
                        "statement_ids": ["stmt-1"],
                        "event_time": "2026-09-12T08:30:00+03:00",
                        "time_precision": "approximate",
                    }
                ],
                "last_supported_interaction_id": "stmt-1",
                "first_noticed_missing_id": None,
            },
        )
        self.assertEqual(
            result["timeline"],
            {
                "last_supported_interaction_id": "stmt-1",
                "first_noticed_missing_id": None,
                "events": [
                    {
                        "id": "event-1",
                        "label": "Последний подтверждённый контакт с ключами",
                        "statement_ids": ["stmt-1"],
                        "event_time": "2026-09-12T08:30:00+03:00",
                        "time_precision": "approximate",
                    }
                ],
                "unknown_intervals": ["statement:stmt-2:неизвестно точное время"],
                "contradictions": [],
            },
        )
        self.assertEqual(result["updated_at"], "2026-09-12T08:10:00+03:00")

    def test_rebuild_requires_reconstruction_mode(self):
        case = create_case("case-search", "ключи", "2026-09-12T08:00:00+03:00")
        case = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-search",
                expected="2026-09-12T08:00:00+03:00",
                now="2026-09-12T08:01:00+03:00",
                payload={"mode": "search"},
            ),
        )
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                case,
                command(
                    "rebuild_timeline",
                    command_id="cmd-timeline",
                    expected="2026-09-12T08:01:00+03:00",
                    now="2026-09-12T08:02:00+03:00",
                    payload={"events": []},
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_MODE_REQUIRED")

    def test_rebuild_requires_free_account(self):
        case = create_case("case-recon", "ключи", "2026-09-12T08:00:00+03:00")
        case = apply_command(
            case,
            command(
                "set_mode",
                command_id="cmd-recon",
                expected="2026-09-12T08:00:00+03:00",
                now="2026-09-12T08:01:00+03:00",
                payload={"mode": "reconstruction"},
            ),
        )
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                case,
                command(
                    "rebuild_timeline",
                    command_id="cmd-timeline",
                    expected="2026-09-12T08:01:00+03:00",
                    now="2026-09-12T08:02:00+03:00",
                    payload={"events": []},
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_FREE_ACCOUNT_REQUIRED")

    def test_duplicate_event_id_is_rejected_without_mutating_input(self):
        case = reconstruction_case()
        original = copy.deepcopy(case)
        payload = {
            "events": [
                {
                    "id": "event-1",
                    "label": "Первое событие",
                    "statement_ids": [],
                    "event_time": None,
                    "time_precision": "unknown",
                },
                {
                    "id": "event-1",
                    "label": "Дубликат",
                    "statement_ids": [],
                    "event_time": None,
                    "time_precision": "unknown",
                },
            ]
        }
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                case,
                command(
                    "rebuild_timeline",
                    command_id="cmd-timeline",
                    expected=str(case["updated_at"]),
                    now="2026-09-12T08:10:00+03:00",
                    payload=payload,
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_TIMELINE_EVENT_DUPLICATE")
        self.assertEqual(case, original)

    def test_missing_event_statement_is_rejected_without_mutating_input(self):
        case = reconstruction_case()
        original = copy.deepcopy(case)
        with self.assertRaises(PortableKernelError) as ctx:
            apply_command(
                case,
                command(
                    "rebuild_timeline",
                    command_id="cmd-timeline",
                    expected=str(case["updated_at"]),
                    now="2026-09-12T08:10:00+03:00",
                    payload={
                        "events": [
                            {
                                "id": "event-1",
                                "label": "Событие",
                                "statement_ids": ["missing-statement"],
                                "event_time": None,
                                "time_precision": "unknown",
                            }
                        ]
                    },
                ),
            )
        self.assertEqual(ctx.exception.code, "MD_RECON_STATEMENT_NOT_FOUND")
        self.assertEqual(case, original)

    def test_missing_anchor_is_preserved_as_reference_contradiction(self):
        case = reconstruction_case()
        result = rebuild(
            case,
            payload={
                "events": [],
                "last_supported_interaction_id": "missing-anchor",
                "first_noticed_missing_id": None,
            },
        )
        self.assertEqual(result["timeline"]["contradictions"], ["MD_TIME_REFERENCE_MISSING"])

    def test_invalid_comparable_anchor_timestamp_is_preserved_as_contradiction(self):
        case = reconstruction_case()
        case = add_statement(
            case,
            command_id="cmd-s1",
            statement_id="stmt-1",
            now="2026-09-12T08:03:00+03:00",
            event_time="not-a-timestamp",
        )
        case = add_statement(
            case,
            command_id="cmd-s2",
            statement_id="stmt-2",
            now="2026-09-12T08:04:00+03:00",
            event_time="2026-09-12T08:40:00+03:00",
        )
        result = rebuild(
            case,
            payload={
                "events": [],
                "last_supported_interaction_id": "stmt-1",
                "first_noticed_missing_id": "stmt-2",
            },
        )
        self.assertEqual(result["timeline"]["contradictions"], ["MD_TIME_INVALID_TIMESTAMP"])

    def test_reversed_supported_times_are_preserved_as_order_contradiction(self):
        case = reconstruction_case()
        case = add_statement(
            case,
            command_id="cmd-s1",
            statement_id="stmt-1",
            now="2026-09-12T08:03:00+03:00",
            event_time="2026-09-12T09:00:00+03:00",
        )
        case = add_statement(
            case,
            command_id="cmd-s2",
            statement_id="stmt-2",
            now="2026-09-12T08:04:00+03:00",
            event_time="2026-09-12T08:40:00+03:00",
        )
        result = rebuild(
            case,
            payload={
                "events": [],
                "last_supported_interaction_id": "stmt-1",
                "first_noticed_missing_id": "stmt-2",
            },
        )
        self.assertEqual(result["timeline"]["contradictions"], ["MD_TIME_ORDER_CONTRADICTION"])

    def test_offset_aware_order_compares_actual_instants(self):
        case = reconstruction_case()
        case = add_statement(
            case,
            command_id="cmd-s1",
            statement_id="stmt-1",
            now="2026-09-12T08:03:00+03:00",
            event_time="2026-09-12T10:30:00+03:00",
        )
        case = add_statement(
            case,
            command_id="cmd-s2",
            statement_id="stmt-2",
            now="2026-09-12T08:04:00+03:00",
            event_time="2026-09-12T08:00:00Z",
        )
        result = rebuild(
            case,
            payload={
                "events": [],
                "last_supported_interaction_id": "stmt-1",
                "first_noticed_missing_id": "stmt-2",
            },
        )
        self.assertEqual(result["timeline"]["contradictions"], [])


class TypedTimelineAdapterTests(unittest.TestCase):
    def test_build_timeline_rejects_event_referencing_missing_statement(self):
        event = TimelineEvent(
            id="event-1",
            label="Событие",
            statement_ids=("missing",),
            event_time=None,
            time_precision="unknown",
        )
        with self.assertRaises(PortableKernelError) as ctx:
            build_timeline([], [event], None, None)
        self.assertEqual(ctx.exception.code, "MD_RECON_STATEMENT_NOT_FOUND")

    def test_controller_rebuilds_timeline_instead_of_accepting_derived_fields(self):
        controller = CaseController()
        case = controller.create_case("case-controller", "ключи", "2026-09-12T08:00:00+03:00")
        case = controller.set_mode(case, InteractionMode.RECONSTRUCTION, "2026-09-12T08:01:00+03:00")
        case = controller.record_free_account(
            case,
            "free-1",
            "Свободный рассказ",
            "2026-09-12T08:02:00+03:00",
        )
        statement = create_statement(
            statement_id="stmt-1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Ключи были у двери",
            recorded_at="2026-09-12T08:03:00+03:00",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("точное время неизвестно",),
        )
        case = controller.add_statement(case, statement, "2026-09-12T08:03:00+03:00")
        supplied = Timeline(
            last_supported_interaction_id="stmt-1",
            first_noticed_missing_id=None,
            events=(),
            unknown_intervals=("fabricated",),
            contradictions=("fabricated",),
        )
        result = controller.set_timeline(case, supplied, "2026-09-12T08:04:00+03:00")
        self.assertEqual(result.timeline.unknown_intervals, ("statement:stmt-1:точное время неизвестно",))
        self.assertEqual(result.timeline.contradictions, ())


if __name__ == "__main__":
    unittest.main()
