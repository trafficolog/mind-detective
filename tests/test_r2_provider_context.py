import ast
import json
import unittest
from pathlib import Path

from scripts import reconstruction_r2_context as r2_context

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "docs/evaluation/R2_PROVIDER_CONTEXT_V1.md"
SCRIPT_PATH = ROOT / "scripts/reconstruction_r2_context.py"


class R2ProviderContextTests(unittest.TestCase):
    def setUp(self):
        self.visible = {
            "language_code": "en",
            "supported_entities": ["lost_item"],
            "supported_locations": ["office", "car", "home"],
            "supported_actions": ["left", "drove", "noticed missing"],
            "timeline_refs": ["evt_1", "evt_2", "evt_3"],
            "statement_refs": ["stmt_1", "stmt_2"],
            "unknown_markers": ["u1"],
            "contradiction_refs": ["c1"],
        }

    def _build(self, **overrides):
        args = {
            "language_code": "en",
            "reason_code": "timeline_gap",
            "target_ids": ["evt_1", "stmt_1"],
            "model_visible_context": self.visible,
            "excerpts": {
                "evt_1": "I left the office.",
                "stmt_1": "I remember getting into the car.",
            },
            "related_unknown_ids": ["u1"],
            "related_contradiction_ids": ["c1"],
        }
        args.update(overrides)
        return r2_context.build_provider_context(**args)

    def test_identity_and_excerpt_bound_are_frozen(self):
        self.assertEqual(
            r2_context.CONTEXT_SCHEMA,
            "mind-detective-reconstruction-r2-context/v1",
        )
        self.assertEqual(r2_context.MAX_EXCERPT_CHARS, 240)

    def test_provider_payload_is_minimized_and_target_scoped(self):
        result = self._build()
        self.assertEqual(
            result,
            {
                "context_schema": r2_context.CONTEXT_SCHEMA,
                "language_code": "en",
                "reason_code": "timeline_gap",
                "targets": [
                    {
                        "ref_id": "evt_1",
                        "ref_kind": "timeline",
                        "excerpt": "I left the office.",
                        "source": "user_confirmed",
                    },
                    {
                        "ref_id": "stmt_1",
                        "ref_kind": "statement",
                        "excerpt": "I remember getting into the car.",
                        "source": "user_confirmed",
                    },
                ],
                "unknown_refs": ["u1"],
                "contradiction_refs": ["c1"],
            },
        )

    def test_unrelated_visible_content_is_not_serialized(self):
        result = self._build()
        encoded = json.dumps(result, ensure_ascii=False)
        for value in ("home", "noticed missing", "lost_item", "evt_3", "stmt_2"):
            self.assertNotIn(value, encoded)

    def test_unknown_source_fields_fail_closed(self):
        forbidden_fields = {
            "raw_free_account": "verbatim account",
            "full_case": {"schema": "mind-detective-case/v2"},
            "interaction_journal": ["raw event"],
            "evaluation_history": ["R2"],
            "provider_secret": "secret",
            "cross_case_profile": {"habit": "desk"},
        }
        for key, value in forbidden_fields.items():
            with self.subTest(key=key):
                visible = dict(self.visible)
                visible[key] = value
                with self.assertRaises(r2_context.ContextValidationError):
                    self._build(model_visible_context=visible)

    def test_targets_and_metadata_refs_must_remain_in_visible_scope(self):
        invalid = (
            {"target_ids": ["evt_404"], "excerpts": {"evt_404": "hidden"}},
            {"related_unknown_ids": ["u404"]},
            {"related_contradiction_ids": ["c404"]},
        )
        for kwargs in invalid:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(r2_context.ContextValidationError):
                    self._build(**kwargs)

    def test_excerpts_are_exactly_target_scoped_nonempty_and_bounded(self):
        invalid_excerpts = (
            {"evt_1": "I left the office."},
            {
                "evt_1": "I left the office.",
                "stmt_1": "I remember the car.",
                "evt_2": "unrelated",
            },
            {"evt_1": "", "stmt_1": "I remember the car."},
            {"evt_1": "x" * 241, "stmt_1": "I remember the car."},
        )
        for excerpts in invalid_excerpts:
            with self.subTest(excerpts=excerpts):
                with self.assertRaises(r2_context.ContextValidationError):
                    self._build(excerpts=excerpts)

    def test_unknown_and_contradiction_metadata_are_reference_only(self):
        result = self._build()
        self.assertEqual(result["unknown_refs"], ["u1"])
        self.assertEqual(result["contradiction_refs"], ["c1"])
        self.assertNotIn("unknown_text", json.dumps(result))
        self.assertNotIn("contradiction_text", json.dumps(result))

    def test_context_audit_is_content_free(self):
        context = self._build()
        audit = r2_context.context_audit(context)
        self.assertEqual(audit["context_schema"], r2_context.CONTEXT_SCHEMA)
        self.assertEqual(audit["target_count"], 2)
        self.assertEqual(audit["unknown_ref_count"], 1)
        self.assertEqual(audit["contradiction_ref_count"], 1)
        self.assertEqual(audit["excerpt_char_count"], 50)
        encoded = json.dumps(audit, ensure_ascii=False)
        for raw in ("I left the office", "evt_1", "stmt_1", "u1", "c1"):
            self.assertNotIn(raw, encoded)

    def test_builder_is_stdlib_only_and_has_no_provider_or_case_dependency(self):
        tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertLessEqual(imported_roots, {"__future__", "collections", "typing"})

    def test_review_document_freezes_context_matrix_and_phase_boundary(self):
        review = REVIEW_PATH.read_text(encoding="utf-8").lower()
        required = (
            "research-only",
            "provider-agnostic",
            "context matrix",
            "user content",
            "retention",
            "telemetry",
            "raw free account",
            "full case",
            "full interaction journal",
            "evaluation history",
            "provider secrets",
            "cross-case",
            "240",
            "no case mutation",
            "phase 6",
        )
        for phrase in required:
            self.assertIn(phrase, review)


if __name__ == "__main__":
    unittest.main()
