import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from scripts.portable_intrinsics import (  # noqa: E402
    PortableKernelError,
    clone_json,
    compare_python_strings,
    portable_error,
    split_python_whitespace,
    unicode_casefold,
)


class PortableIntrinsicTests(unittest.TestCase):
    def test_casefold_matches_python_observable_semantics(self):
        self.assertEqual(unicode_casefold("Straße"), "strasse")
        self.assertEqual(unicode_casefold("ЁЖ"), "ёж")

    def test_python_whitespace_split_handles_unicode_whitespace(self):
        self.assertEqual(split_python_whitespace("  ключ\u00a0машина\u2028дом  "), ["ключ", "машина", "дом"])
        self.assertEqual(split_python_whitespace("\t\n"), [])

    def test_python_string_order_uses_unicode_code_points(self):
        self.assertEqual(compare_python_strings("a", "a"), 0)
        self.assertEqual(compare_python_strings("a", "b"), -1)
        self.assertEqual(compare_python_strings("\U00010000", "\ue000"), 1)

    def test_clone_json_is_deep_and_non_aliasing(self):
        source = {"nested": [{"value": "ключи"}], "none": None}
        cloned = clone_json(source)
        self.assertEqual(cloned, source)
        self.assertIsNot(cloned, source)
        self.assertIsNot(cloned["nested"], source["nested"])
        cloned["nested"][0]["value"] = "changed"
        self.assertEqual(source["nested"][0]["value"], "ключи")

    def test_portable_error_preserves_exact_machine_code(self):
        with self.assertRaises(PortableKernelError) as ctx:
            portable_error("MD_WEB_COMMAND_PAYLOAD", "missing payload")
        self.assertEqual(ctx.exception.code, "MD_WEB_COMMAND_PAYLOAD")
        self.assertEqual(str(ctx.exception), "missing payload")


if __name__ == "__main__":
    unittest.main()
