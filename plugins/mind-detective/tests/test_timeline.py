import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.statements import StatementSource, StatementType, create_statement  # noqa: E402
from scripts.timeline import TimelineEvent, build_timeline  # noqa: E402


class TimelineTests(unittest.TestCase):
    def test_unknown_last_interaction_remains_unknown(self):
        timeline = build_timeline([], [], None, None)
        self.assertIsNone(timeline.last_supported_interaction_id)
        self.assertEqual(timeline.unknown_intervals, ())

    def test_uncertain_statement_does_not_create_inferred_event(self):
        statement = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Не помню, выходил ли я после этого.",
            recorded_at="2026-09-09T18:00:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("unknown whether user left the room",),
        )
        timeline = build_timeline([statement], [], None, None)
        self.assertEqual(timeline.events, ())
        self.assertTrue(any("s1" in item for item in timeline.unknown_intervals))
        self.assertFalse(
            any("inside" in item.lower() or "внутри" in item.lower() for item in timeline.unknown_intervals)
        )

    def test_explicit_reversed_supported_times_add_contradiction(self):
        last = create_statement(
            statement_id="last",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Последний раз держал ключи.",
            recorded_at="2026-09-09T18:00:00Z",
            event_time="2026-09-09T18:30:00Z",
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=(),
        )
        missing = create_statement(
            statement_id="missing",
            source=StatementSource.USER,
            statement_type=StatementType.OBSERVATION,
            original_text="Заметил пропажу.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time="2026-09-09T18:20:00Z",
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=(),
        )
        timeline = build_timeline([last, missing], [], "last", "missing")
        self.assertIn("MD_TIME_ORDER_CONTRADICTION", timeline.contradictions)

    def test_explicit_events_are_preserved_only_as_supplied(self):
        statement = create_statement(
            statement_id="s1",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Вошёл на кухню.",
            recorded_at="2026-09-09T18:00:00Z",
            event_time="2026-09-09T18:10:00Z",
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=(),
        )
        event = TimelineEvent(
            id="e1",
            label="entered kitchen",
            statement_ids=("s1",),
            event_time="2026-09-09T18:10:00Z",
            time_precision="minute",
        )
        timeline = build_timeline([statement], [event], None, None)
        self.assertEqual(timeline.events, (event,))


if __name__ == "__main__":
    unittest.main()
