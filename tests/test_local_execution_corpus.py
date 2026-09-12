from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.generate_local_execution_corpus import render_corpus

ROOT = Path(__file__).resolve().parents[1]


class LocalExecutionCorpusTests(unittest.TestCase):
    def test_corpus_is_byte_deterministic_and_covers_contract_surface(self) -> None:
        first_vectors, first_manifest = render_corpus(ROOT)
        second_vectors, second_manifest = render_corpus(ROOT)
        self.assertEqual(first_vectors, second_vectors)
        self.assertEqual(first_manifest, second_manifest)

        vectors = json.loads(first_vectors.decode("utf-8"))
        manifest = json.loads(first_manifest.decode("utf-8"))
        ids = {vector["id"] for vector in vectors}
        operations = {vector["operation"] for vector in vectors}

        self.assertEqual(operations, {"create_case", "command", "proposal", "planner"})
        self.assertGreaterEqual(len(vectors), 50)
        self.assertEqual(manifest["seed"], 303001)
        self.assertEqual(manifest["vector_count"], len(vectors))
        self.assertEqual(manifest["contract_version"], "mind-detective-local-execution/v1")
        self.assertTrue(str(manifest["vectors_sha256"]).startswith("sha256:"))

        required_ids = {
            "command-set-mode",
            "command-add-search-suggestion",
            "command-search-suggestion-unicode-whitespace-dedup",
            "command-record-reported-check",
            "command-record-partial-check",
            "command-refine-check",
            "command-reject-action",
            "command-pause",
            "command-resume",
            "command-close-found",
            "command-close-unresolved",
            "failure-stale-command",
            "failure-forbidden-probability-nested",
            "failure-float",
            "failure-terminal-mutation",
            "failure-invalid-refinement-method",
            "proposal-reconstruction",
            "proposal-search-next-action",
            "proposal-rejected-excluded",
            "proposal-partial-clarification",
            "proposal-empty-search",
            "planner-urgency",
            "planner-basis",
            "planner-route",
            "planner-check-state",
            "planner-effort",
            "planner-id-unicode",
            "planner-unsafe-excluded",
            "reconstruction_record_free_account",
            "reconstruction_statement_requires_free_account",
            "reconstruction_rebuild_timeline_unknowns",
            "reconstruction_rebuild_timeline_contradiction",
            "reconstruction_transition_to_search_preserves_evidence",
        }
        self.assertTrue(required_ids <= ids)

        for vector in vectors:
            expected = vector["expected"]
            self.assertEqual(set(expected) in ({"result"}, {"error_code"}), True)

    def test_committed_corpus_matches_generator_when_present(self) -> None:
        vectors_path = ROOT / "conformance/local-execution/v1/vectors.json"
        manifest_path = ROOT / "conformance/local-execution/v1/manifest.json"
        if not vectors_path.exists() or not manifest_path.exists():
            self.skipTest("RED until the generated corpus is committed")
        vectors, manifest = render_corpus(ROOT)
        self.assertEqual(vectors_path.read_bytes(), vectors)
        self.assertEqual(manifest_path.read_bytes(), manifest)


if __name__ == "__main__":
    unittest.main()
