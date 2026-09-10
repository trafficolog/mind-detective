import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "apps/api/mind_detective_api/commands.py"


class ApiPortableBoundaryTests(unittest.TestCase):
    def test_command_adapter_does_not_construct_domain_objects(self):
        tree = ast.parse(COMMANDS.read_text(encoding="utf-8"))
        forbidden_calls = {
            "ActionFeedback",
            "CandidateCheck",
            "JournalEntry",
            "SearchCheck",
            "create_statement",
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertEqual(calls & forbidden_calls, set())

    def test_command_adapter_imports_portable_apply_command(self):
        tree = ast.parse(COMMANDS.read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "scripts.portable_kernel"
            for alias in node.names
        }
        self.assertIn("apply_command", imported)


if __name__ == "__main__":
    unittest.main()
