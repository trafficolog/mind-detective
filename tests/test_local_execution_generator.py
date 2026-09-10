from __future__ import annotations

import unittest
from pathlib import Path

from scripts.local_execution_ast import (
    PortableSourceError,
    validate_portable_source,
    validate_source_text,
)

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "plugins/mind-detective/scripts/portable_kernel.py"
INTRINSICS = ROOT / "plugins/mind-detective/scripts/portable_intrinsics.py"


class LocalExecutionAstTests(unittest.TestCase):
    def test_committed_kernel_and_intrinsics_are_accepted(self) -> None:
        validate_portable_source(KERNEL, profile="kernel")
        validate_portable_source(INTRINSICS, profile="intrinsics")

    def test_kernel_rejects_unsupported_nodes_and_calls(self) -> None:
        cases = {
            "async def run():\n    return 1\n": "MD_CODEGEN_ASYNC",
            "class Reducer:\n    pass\n": "MD_CODEGEN_CLASS",
            "def run():\n    return eval('1')\n": "MD_CODEGEN_CALL",
            "def run():\n    return open('case.json')\n": "MD_CODEGEN_CALL",
            "def run():\n    return mystery()\n": "MD_CODEGEN_CALL",
            "def run():\n    value = 0.5\n    return value\n": "MD_CODEGEN_FLOAT",
            "import os\ndef run():\n    return os.environ.get('KEY')\n": "MD_CODEGEN_IMPORT",
            "import random\ndef run():\n    return random.random()\n": "MD_CODEGEN_IMPORT",
            "import time\ndef run():\n    return time.time()\n": "MD_CODEGEN_IMPORT",
        }
        for source, expected_code in cases.items():
            with self.subTest(expected_code=expected_code, source=source):
                with self.assertRaises(PortableSourceError) as ctx:
                    validate_source_text(source, profile="kernel", source_name="fixture.py")
                self.assertEqual(ctx.exception.code, expected_code)
                self.assertGreaterEqual(ctx.exception.line, 1)

    def test_kernel_rejects_unrecognized_method_call(self) -> None:
        source = "def run(value):\n    return value.magic()\n"
        with self.assertRaises(PortableSourceError) as ctx:
            validate_source_text(source, profile="kernel", source_name="fixture.py")
        self.assertEqual(ctx.exception.code, "MD_CODEGEN_CALL")


if __name__ == "__main__":
    unittest.main()
