import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_marketplace_versions_match_codex_descriptor(self):
        codex = json.loads((ROOT / "plugins/mind-detective/.codex-plugin/plugin.json").read_text())
        claude = json.loads((ROOT / "plugins/mind-detective/.claude-plugin/plugin.json").read_text())
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(agents["plugins"][0]["version"], codex["version"])
        self.assertEqual(market["plugins"][0]["version"], codex["version"])

    def test_only_codex_and_claude_plugin_descriptors_exist(self):
        self.assertFalse((ROOT / "plugins/mind-detective/.agents-plugin/plugin.json").exists())

    def test_adr_015_records_the_web_reconstruction_portable_boundary(self):
        path = ROOT / "docs/adr/015-web-reconstruction-portable-boundary.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").casefold()
        for expected in (
            "record_free_account",
            "rebuild_timeline",
            "generated local execution",
            "vue",
            "reconstruction truth",
            "live-model clarification",
            "not a dependency",
            "mind-detective-case/v2",
        ):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
