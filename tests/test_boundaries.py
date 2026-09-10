import json
import unittest
from pathlib import Path

from scripts.validate_repo import scan_source_for_forbidden_imports, validate_boundaries

ROOT = Path(__file__).resolve().parents[1]


class BoundaryTests(unittest.TestCase):
    def test_forbidden_import_returns_stable_machine_code(self):
        self.assertEqual(
            scan_source_for_forbidden_imports("import requests\n"),
            ["MD_BOUNDARY_FORBIDDEN_IMPORT:requests"],
        )

    def test_nested_forbidden_import_returns_root_module_code(self):
        self.assertEqual(
            scan_source_for_forbidden_imports("from google.cloud import storage\n"),
            ["MD_BOUNDARY_FORBIDDEN_IMPORT:google.cloud"],
        )

    def test_current_runtime_satisfies_transport_and_scope_boundary(self):
        self.assertEqual(validate_boundaries(ROOT), [])

    def test_forbidden_runtime_names_are_part_of_boundary_contract(self):
        for name in ("zones.py", "ach.py", "model_adapter.py"):
            self.assertFalse((ROOT / "plugins/mind-detective/scripts" / name).exists())

    def test_frontend_manifests_are_absent_from_p0_plugin(self):
        plugin = ROOT / "plugins/mind-detective"
        forbidden = [plugin / "package.json", plugin / "nuxt.config.ts", plugin / "vite.config.ts"]
        self.assertFalse(any(path.exists() for path in forbidden))

    def test_web_workspace_is_pinned_and_core_stays_dependency_free(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["packageManager"], "pnpm@12.3.4")
        self.assertEqual((ROOT / ".node-version").read_text(encoding="utf-8").strip(), "24.21.0")
        api_pyproject = (ROOT / "apps/api/pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('fastapi==0.141.1', api_pyproject)
        self.assertIn('openai==3.8.0', api_pyproject)
        self.assertNotIn("fastapi", (ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertFalse((ROOT / "plugins/mind-detective/apps").exists())

    def test_pnpm_build_script_allowlist_is_version_scoped(self):
        workspace = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
        self.assertIn("allowBuilds:", workspace)
        self.assertIn("esbuild@0.28.2: true", workspace)
        self.assertNotIn("dangerouslyAllowAllBuilds", workspace)

    def test_web_ci_uses_committed_frozen_lockfile(self):
        self.assertTrue((ROOT / "pnpm-lock.yaml").is_file())
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("pnpm install --frozen-lockfile", ci)
        self.assertNotIn("pnpm install --no-frozen-lockfile", ci)
        self.assertNotIn("generated-pnpm-lock", ci)

    def test_web_has_no_client_domain_reducer_or_case_controller_port(self):
        forbidden = ("reduceCase", "applyCommandLocally", "class CaseController")
        offenders: list[str] = []
        for path in sorted((ROOT / "apps/web").rglob("*")):
            if path.suffix not in {".ts", ".tsx", ".vue"} or "node_modules" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)}:{token}")
        self.assertEqual(offenders, [])

    def test_ci_uses_python_matrix_quality_gates_and_full_sha_actions(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("'3.10'", ci)
        self.assertIn("'3.13'", ci)
        self.assertIn("ruff check .", ci)
        self.assertIn("mypy plugins/mind-detective/scripts scripts", ci)
        self.assertIn("ruff==0.16.6", ci)
        self.assertIn("mypy==2.3.1", ci)
        self.assertIn("gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e", ci)
        for line in ci.splitlines():
            if "uses:" in line:
                ref = line.split("@", 1)[-1].split()[0]
                self.assertRegex(ref, r"^[0-9a-f]{40}$")

    def test_ruff_rule_set_is_explicit_and_stable(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[tool.ruff.lint]", pyproject)
        self.assertIn('select = ["E4", "E7", "E9", "F", "B", "UP"]', pyproject)

    def test_pr_ci_checks_out_every_job_at_exact_head_sha(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        exact_ref = "ref: ${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha || github.sha }}"
        checkout_count = sum("uses: actions/checkout@" in line for line in ci.splitlines())
        self.assertGreaterEqual(checkout_count, 3)
        self.assertEqual(ci.count(exact_ref), checkout_count)
        self.assertIn('head="${{ github.event.pull_request.head.sha }}"', ci)
        self.assertIn('git diff --name-only "$base" "$head"', ci)

    def test_reference_freshness_workflow_opens_or_updates_issue(self):
        workflow = (ROOT / ".github/workflows/reference-freshness.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", workflow)
        self.assertIn("issues: write", workflow)
        self.assertIn("python scripts/check_reference_freshness.py --strict", workflow)
        self.assertIn("gh issue create", workflow)
        self.assertIn("gh issue edit", workflow)

    def test_dependabot_and_pr_template_exist(self):
        dependabot = (ROOT / ".github/dependabot.yml").read_text(encoding="utf-8")
        template = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: github-actions", dependabot)
        self.assertIn("exact PR head SHA", template)
        self.assertIn("Human merge authorization", template)


if __name__ == "__main__":
    unittest.main()
