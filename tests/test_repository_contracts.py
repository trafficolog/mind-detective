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
        self.assertEqual(codex["version"], "0.2.0")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(agents["plugins"][0]["version"], codex["version"])
        self.assertEqual(market["plugins"][0]["version"], codex["version"])

    def test_only_codex_and_claude_plugin_descriptors_exist(self):
        self.assertFalse((ROOT / "plugins/mind-detective/.agents-plugin/plugin.json").exists())
