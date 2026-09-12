import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mind_detective_api.runtime_paths import resolve_plugin_root


class RuntimePathTests(unittest.TestCase):
    def make_plugin_root(self, root: Path) -> Path:
        plugin = root / "portable-plugin"
        scripts = plugin / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "controller.py").write_text("# test marker\n", encoding="utf-8")
        return plugin

    def test_explicit_plugin_root_allows_relocated_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = self.make_plugin_root(root)
            unrelated_api_file = root / "elsewhere" / "installed" / "core_bridge.py"
            unrelated_api_file.parent.mkdir(parents=True)
            unrelated_api_file.write_text("# relocated\n", encoding="utf-8")

            with patch.dict(os.environ, {"MIND_DETECTIVE_PLUGIN_ROOT": str(plugin)}, clear=False):
                self.assertEqual(resolve_plugin_root(unrelated_api_file), plugin.resolve())

    def test_repository_discovery_does_not_depend_on_fixed_parent_depth(self):
        with patch.dict(os.environ, {}, clear=True):
            resolved = resolve_plugin_root(Path(__file__).resolve())
        self.assertEqual(resolved.name, "mind-detective")
        self.assertTrue((resolved / "scripts/controller.py").is_file())

    def test_missing_plugin_root_fails_with_stable_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            isolated = Path(tmp) / "api" / "core_bridge.py"
            isolated.parent.mkdir(parents=True)
            isolated.write_text("# isolated\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "MD_API_PLUGIN_ROOT_NOT_FOUND"):
                    resolve_plugin_root(isolated)


if __name__ == "__main__":
    unittest.main()
