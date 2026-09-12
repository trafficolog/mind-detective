import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.3.1"
EXPECTED_DOIS = {
    "10.1037/0021-9010.74.5.722",
    "10.1101/lm.94705",
    "10.1037/xlm0001529",
    "10.1167/jov.24.9.9",
}


def project_version(path: Path) -> str:
    match = re.search(r'^version = "([^"]+)"$', path.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        raise AssertionError(f"version not found in {path}")
    return match.group(1)


class Task9HardeningTests(unittest.TestCase):
    def test_patch_release_surfaces_are_0_3_1(self):
        self.assertEqual(project_version(ROOT / "pyproject.toml"), EXPECTED_VERSION)
        self.assertEqual(project_version(ROOT / "apps/api/pyproject.toml"), EXPECTED_VERSION)
        web = json.loads((ROOT / "apps/web/package.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / "plugins/mind-detective/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / "plugins/mind-detective/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(web["version"], EXPECTED_VERSION)
        self.assertEqual(codex["version"], EXPECTED_VERSION)
        self.assertEqual(claude["version"], EXPECTED_VERSION)
        self.assertEqual(agents["plugins"][0]["version"], EXPECTED_VERSION)
        self.assertEqual(marketplace["plugins"][0]["version"], EXPECTED_VERSION)

        release = json.loads((ROOT / ".github/releases/release.json").read_text(encoding="utf-8"))
        self.assertEqual(release["repository"]["tag"], EXPECTED_VERSION)
        self.assertEqual(release["repository"]["notes_file"], ".github/releases/0.3.1.md")
        self.assertEqual(release["plugins"][0]["tag"], "mind-detective-v0.3.1")
        self.assertTrue((ROOT / ".github/releases/0.3.1.md").is_file())

    def test_docs_are_current_and_getting_started_documents_portable_api(self):
        for path in (ROOT / "README.md", ROOT / "README.en.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("0.3.1", text)
        for path in (ROOT / "docs/GETTING_STARTED.md", ROOT / "docs/GETTING_STARTED.en.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("0.3.1", text)
            self.assertIn("MIND_DETECTIVE_PLUGIN_ROOT", text)
            self.assertIn("pnpm install --frozen-lockfile", text)
            self.assertIn("uvicorn", text)

        for path in (ROOT / "apps/web/app/lib/i18n/ru.ts", ROOT / "apps/web/app/lib/i18n/en.ts"):
            self.assertNotIn("0.2.0", path.read_text(encoding="utf-8"))

    def test_eval_corpus_no_longer_describes_web_as_deferred_or_version_bound(self):
        data = json.loads((ROOT / "plugins/mind-detective/evals/scenarios.json").read_text(encoding="utf-8"))
        serialized = json.dumps(data, ensure_ascii=False)
        self.assertNotIn("0.1.0", serialized)
        self.assertNotIn("MD_SCOPE_PWA_DEFERRED", serialized)
        self.assertIn("MD_SCOPE_WEB_SEPARATE_SURFACE", serialized)

        registry = json.loads((ROOT / "docs/EVAL_TOKEN_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertNotIn("MD_SCOPE_PWA_DEFERRED", registry["tokens"])
        self.assertIn("MD_SCOPE_WEB_SEPARATE_SURFACE", registry["tokens"])

    def test_api_bridge_has_no_fixed_monorepo_parent_depth(self):
        bridge = (ROOT / "apps/api/mind_detective_api/core_bridge.py").read_text(encoding="utf-8")
        self.assertNotIn("parents[3]", bridge)
        self.assertIn("resolve_plugin_root", bridge)
        resolver = (ROOT / "apps/api/mind_detective_api/runtime_paths.py").read_text(encoding="utf-8")
        self.assertIn("MIND_DETECTIVE_PLUGIN_ROOT", resolver)
        self.assertIn("MD_API_PLUGIN_ROOT_NOT_FOUND", resolver)

    def test_scientific_references_have_machine_readable_verification(self):
        data = json.loads((ROOT / "docs/REFERENCE_VERIFICATION.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        records = data["references"]
        self.assertEqual({record["doi"] for record in records}, EXPECTED_DOIS)
        for record in records:
            self.assertEqual(record["status"], "verified")
            self.assertEqual(record["verified_on"], "2026-09-12")
            self.assertEqual(record["url"], f"https://doi.org/{record['doi']}")

        methodology = (ROOT / "docs/METHODOLOGY.md").read_text(encoding="utf-8")
        methodology_en = (ROOT / "docs/METHODOLOGY.en.md").read_text(encoding="utf-8")
        for doi in EXPECTED_DOIS:
            self.assertIn(doi, methodology)
            self.assertIn(doi, methodology_en)


if __name__ == "__main__":
    unittest.main()
