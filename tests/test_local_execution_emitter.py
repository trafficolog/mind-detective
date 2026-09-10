from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.generate_local_execution import generate_typescript
from scripts.local_execution_manifest import build_execution_metadata

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "plugins/mind-detective/scripts/portable_kernel.py"
CONTRACT = ROOT / "plugins/mind-detective/scripts/portable_contract.py"


class LocalExecutionEmitterTests(unittest.TestCase):
    def test_generation_is_byte_deterministic_and_source_identified(self) -> None:
        first = generate_typescript(KERNEL, CONTRACT)
        second = generate_typescript(KERNEL, CONTRACT)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("// GENERATED FILE — DO NOT EDIT\n"))
        self.assertIn("mind-detective-local-execution/v1", first)
        self.assertIn("local-execution-generator/v1", first)
        self.assertIn("export function create_case", first)
        self.assertIn("export function apply_command", first)
        self.assertIn("export function build_checklist_proposal_json", first)

        metadata = build_execution_metadata(
            kernel_bytes=KERNEL.read_bytes(),
            generated_bytes=first.encode("utf-8"),
            contract_path=CONTRACT,
        )
        self.assertEqual(metadata["version"], "mind-detective-local-execution/v1")
        self.assertEqual(metadata["generator_version"], "local-execution-generator/v1")
        self.assertEqual(metadata["case_schemas"], ["mind-detective-case/v2"])
        for field in ("kernel_sha256", "generated_sha256"):
            value = metadata[field]
            self.assertIsInstance(value, str)
            assert isinstance(value, str)
            self.assertRegex(value, r"^sha256:[0-9a-f]{64}$")

    def test_generated_executor_contains_certified_intrinsic_prelude_only(self) -> None:
        generated = generate_typescript(KERNEL, CONTRACT)
        for required in (
            "function pyClone",
            "function pyCasefold",
            "function pySplitWhitespace",
            "function pyCompareStrings",
            "class PortableKernelError",
        ):
            self.assertIn(required, generated)
        forbidden = (
            "eval(",
            "new Function",
            "fetch(",
            "XMLHttpRequest",
            "Math.random",
            "Date.now",
            "openai",
            "litellm",
        )
        lowered = generated.lower()
        for token in forbidden:
            self.assertNotIn(token.lower(), lowered)

    def test_metadata_json_is_canonicalizable(self) -> None:
        generated = generate_typescript(KERNEL, CONTRACT)
        metadata = build_execution_metadata(
            kernel_bytes=KERNEL.read_bytes(),
            generated_bytes=generated.encode("utf-8"),
            contract_path=CONTRACT,
        )
        encoded = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(encoded), metadata)


if __name__ == "__main__":
    unittest.main()
