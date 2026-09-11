from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.local_execution_hashing import canonical_json, canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/local-execution-canonical-json-v1.json"


class LocalExecutionHashingTests(unittest.TestCase):
    def test_python_canonical_json_matches_committed_vectors(self) -> None:
        vectors = json.loads(FIXTURES.read_text(encoding="utf-8"))
        for vector in vectors:
            with self.subTest(vector=vector["name"]):
                self.assertEqual(canonical_json(vector["value"]), vector["canonical"])
                self.assertEqual(canonical_sha256(vector["value"]), vector["sha256"])

    def test_non_json_or_floating_values_fail_closed(self) -> None:
        for value in ({"x": 1.25}, {"x": float("nan")}, {1: "non-string-key"}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "MD_LOCAL_CANONICAL_JSON"):
                    canonical_json(value)


if __name__ == "__main__":
    unittest.main()
