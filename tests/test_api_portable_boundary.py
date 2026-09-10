import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "apps/api/mind_detective_api/commands.py"
CHECKLIST = ROOT / "apps/api/mind_detective_api/checklist.py"


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

    def test_checklist_adapter_delegates_portable_proposal_semantics(self):
        tree = ast.parse(CHECKLIST.read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "scripts.portable_kernel"
            for alias in node.names
        }
        self.assertIn("build_checklist_proposal_json", imported)
        direct_planner_imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "scripts.planner"
            for alias in node.names
        }
        self.assertNotIn("select_next_action", direct_planner_imports)


if __name__ == "__main__":
    unittest.main()
