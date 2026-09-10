import json
import unittest
from pathlib import Path

from scripts.release_manifest import (
    consensus_recovery_target,
    release_items,
    validate_full_sha,
    validate_release_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-current-release.yml"


class ReleaseContractTests(unittest.TestCase):
    def test_repository_manifest_is_valid(self):
        self.assertEqual(validate_release_manifest(ROOT), [])
        items = release_items(ROOT)
        self.assertEqual([item.tag for item in items], ["0.1.0", "mind-detective-v0.1.0"])

    def test_manifest_version_parity_and_notes_file(self):
        data = json.loads((ROOT / ".github/releases/release.json").read_text(encoding="utf-8"))
        self.assertEqual(data["repository"]["version"], "0.1.0")
        self.assertEqual(data["repository"]["tag"], "0.1.0")
        self.assertEqual(data["plugins"][0]["plugin"], "mind-detective")
        self.assertEqual(data["plugins"][0]["version"], "0.1.0")
        self.assertEqual(data["plugins"][0]["tag"], "mind-detective-v0.1.0")
        self.assertTrue((ROOT / data["repository"]["notes_file"]).is_file())

    def test_recovery_sha_requires_full_40_hex(self):
        with self.assertRaisesRegex(ValueError, "MD_RELEASE_SHA"):
            validate_full_sha("main")
        with self.assertRaisesRegex(ValueError, "MD_RELEASE_SHA"):
            validate_full_sha("abc123")

    def test_conflicting_recovery_targets_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "MD_RELEASE_CONFLICT_TARGETS"):
            consensus_recovery_target(["a" * 40, "b" * 40])

    def test_same_sha_recovery_is_idempotent(self):
        sha = "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
        self.assertEqual(
            consensus_recovery_target([sha, sha.lower()]),
            sha.lower(),
        )

    def test_exactly_one_active_publisher(self):
        publishers = sorted((ROOT / ".github/workflows").glob("*publish*release*.yml"))
        self.assertEqual(publishers, [WORKFLOW])

    def test_publisher_requires_manual_full_sha_human_gate(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("target_sha:", text)
        self.assertIn("Human-approved exact main SHA to publish", text)
        self.assertIn('[[ "$TARGET_SHA" =~ ^[0-9a-fA-F]{40}$ ]]', text)
        self.assertNotIn("workflow_run:", text)

    def test_publisher_verifies_ci_main_and_exact_target_before_mutation(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        verify_i = text.find("Verify exact target and successful main CI")
        create_i = text.find("gh release create")
        self.assertGreaterEqual(verify_i, 0)
        self.assertGreater(create_i, verify_i)
        self.assertIn('live_main="$(git rev-parse origin/main)"', text)
        self.assertIn('gh run list --workflow CI --commit "$TARGET_SHA"', text)
        self.assertIn("No successful CI run for exact target SHA", text)

    def test_publisher_reuses_hardened_fail_closed_recovery_contracts(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in (
            "Existing declared release state spans multiple commits",
            "Standalone remote tag $tag exists without a GitHub Release.",
            "Published release $tag is not immutable.",
            "Draft release $tag has non-immutable target",
            'git worktree add --detach "$WT" "$RELEASE_TARGET"',
            "rollback_published_release",
            "Rollback residue: tag $tag remains.",
            "Final verification: release $tag is not immutable.",
            "Final verification: tag $tag points to",
        ):
            self.assertIn(token, text)

    def test_publisher_actions_are_full_sha_pinned(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "uses:" in line:
                ref = line.split("@", 1)[-1].split()[0]
                self.assertRegex(ref, r"^[0-9a-f]{40}$")

    def test_release_requirement_is_active_and_exactly_traced(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        entry = next(e for e in matrix["entries"] if e["requirement_id"] == "MD-REQ-RELEASE-01")
        self.assertEqual(entry["status"], "active")
        self.assertEqual(entry["helper"], "scripts/release_manifest.py")
        self.assertEqual(
            entry["test"],
            "tests/test_release_contract.py::ReleaseContractTests.test_repository_manifest_is_valid",
        )


if __name__ == "__main__":
    unittest.main()
