import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.journal import InteractionMode  # noqa: E402
from scripts.migrations import migrate_case_payload  # noqa: E402
from scripts.schemas import SchemaError  # noqa: E402
from scripts.store import case_from_dict, case_to_dict  # noqa: E402


class MigrationTests(unittest.TestCase):
    def _legacy(self):
        return json.loads((FIXTURES / "case-v1-active.json").read_text(encoding="utf-8"))

    def test_v1_migration_never_infers_historical_mode(self):
        source = self._legacy()
        before = deepcopy(source)
        migrated = migrate_case_payload(source)
        self.assertEqual(source, before)
        self.assertEqual(migrated["schema"], "mind-detective-case/v2")
        self.assertEqual(migrated["current_mode"], "unselected")
        self.assertEqual(migrated["interaction_journal"], [])
        self.assertEqual(migrated["action_feedback"], [])

    def test_v1_payload_loads_as_canonical_v2_without_fabricated_history(self):
        case = case_from_dict(self._legacy())
        self.assertEqual(case.schema, "mind-detective-case/v2")
        self.assertEqual(case.current_mode, InteractionMode.UNSELECTED)
        self.assertEqual(case.interaction_journal, ())
        self.assertEqual(case.action_feedback, ())
        serialized = case_to_dict(case)
        self.assertEqual(serialized["schema"], "mind-detective-case/v2")

    def test_future_schema_fails_closed(self):
        with self.assertRaises(SchemaError) as ctx:
            migrate_case_payload({"schema": "mind-detective-case/v999"})
        self.assertEqual(ctx.exception.code, "MD_STORE_SCHEMA_VERSION")


if __name__ == "__main__":
    unittest.main()
