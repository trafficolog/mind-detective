import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.statements import (  # noqa: E402
    StatementError,
    StatementSource,
    StatementType,
    create_statement,
)


class StatementTests(unittest.TestCase):
    def test_assistant_cannot_originate_recollection(self):
        with self.assertRaises(StatementError) as ctx:
            create_statement(
                statement_id="s1",
                source=StatementSource.ASSISTANT,
                statement_type=StatementType.RECOLLECTION,
                original_text="Вы положили ключи на стол.",
                recorded_at="2026-09-09T18:00:00Z",
                event_time=None,
                user_confirmation=False,
                supporting_evidence_ids=(),
                limitations=(),
            )
        self.assertEqual(ctx.exception.code, "MD_STMT_ASSISTANT_ORIGIN")

    def test_probability_word_does_not_reclassify_user_statement(self):
        statement = create_statement(
            statement_id="s2",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Наверное, я положил ключи после магазина.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("uncertain wording",),
        )
        self.assertEqual(statement.statement_type, StatementType.RECOLLECTION)

    def test_file_can_only_originate_observation(self):
        with self.assertRaises(StatementError) as ctx:
            create_statement(
                statement_id="s3",
                source=StatementSource.FILE,
                statement_type=StatementType.HYPOTHESIS,
                original_text="metadata guess",
                recorded_at="2026-09-09T18:02:00Z",
                event_time=None,
                user_confirmation=False,
                supporting_evidence_ids=(),
                limitations=(),
            )
        self.assertEqual(ctx.exception.code, "MD_STMT_SOURCE_TYPE")
