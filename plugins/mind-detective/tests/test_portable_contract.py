import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.portable_contract import (  # noqa: E402
    GENERATOR_VERSION,
    LOCAL_EXECUTION_CONTRACT,
    STABLE_LOCAL_ERRORS,
    SUPPORTED_CASE_SCHEMAS,
    SUPPORTED_COMMAND_TYPES,
)


class PortableContractTests(unittest.TestCase):
    def test_local_execution_v1_contract_is_exact(self):
        self.assertEqual(LOCAL_EXECUTION_CONTRACT, "mind-detective-local-execution/v1")
        self.assertEqual(GENERATOR_VERSION, "local-execution-generator/v1")
        self.assertEqual(SUPPORTED_CASE_SCHEMAS, ("mind-detective-case/v2",))
        self.assertEqual(
            SUPPORTED_COMMAND_TYPES,
            (
                "set_mode",
                "add_statement",
                "record_search_check",
                "refine_search_check",
                "reject_next_action",
                "pause",
                "resume",
                "close_found",
                "close_unresolved",
            ),
        )

    def test_local_execution_errors_are_stable_and_non_probabilistic(self):
        self.assertEqual(
            STABLE_LOCAL_ERRORS,
            frozenset(
                {
                    "MD_WEB_STALE_COMMAND",
                    "MD_WEB_FORBIDDEN_FIELD",
                    "MD_WEB_COMMAND_PAYLOAD",
                    "MD_WEB_COMMAND_ID_CONFLICT",
                    "MD_WEB_CASE_ID_CONFLICT",
                    "MD_WEB_EXECUTION_CONTRACT_MISMATCH",
                }
            ),
        )
        joined = " ".join(sorted(STABLE_LOCAL_ERRORS)).lower()
        self.assertNotIn("probability", joined)
        self.assertNotIn("belief", joined)
        self.assertNotIn("pod", joined)


if __name__ == "__main__":
    unittest.main()
