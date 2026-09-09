# Release Policy

[Русский](RELEASE_POLICY.md)

The repository has one SemVer line and an independent plugin SemVer with tags `mind-detective-vX.Y.Z`. Milestones/codenames are not version lines.

Publication requires reviewed feature/design work, exact PR-head CI, human merge authorization, CI on the exact new main SHA, a human-approved `.github/releases/release.json`, one active publisher, exact tag-SHA verification, and immutable publication.

The publisher must fail closed on stale main, conflicting tag SHA, ambiguous existing release state, or a mutable recovery target. Published tags/releases are never retargeted; corrections use a new version. Until Task 15, the release control remains explicitly planned in the contract matrix.
