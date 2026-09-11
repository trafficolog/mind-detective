# Release Policy

[Русский](RELEASE_POLICY.md)

The repository has one repository SemVer line and an independent plugin SemVer tagged `mind-detective-vX.Y.Z`. For `0.3.0`, `.github/releases/release.json` declares repository `0.3.0` and plugin `mind-detective-v0.3.0`.

## Single publication path

Publication runs only through `.github/workflows/publish-current-release.yml`. A parallel publisher, manually substituted tags, or retargeting published tags are not permitted.

The gate sequence is:

1. reviewed design/implementation;
2. CI on the exact PR head SHA;
3. explicitly authorized merge;
4. CI on the exact new `main` SHA;
5. manual `workflow_dispatch` of the canonical publisher with the **full 40-hex `target_sha`** for that verified `main`;
6. before mutation, the publisher rechecks live `origin/main`, successful CI for the exact target, the declarative manifest, and existing release state;
7. after publication it verifies exact tag SHA and immutable release state.

The publisher fails closed on stale main, conflicting tag SHA, standalone tags without consistent releases, ambiguous existing release state, mutable recovery targets, or rollback residue. Published tags/releases are never retargeted; corrections use a new version.

Release controls `MD-REQ-RELEASE-01`, `MD-WEB-REQ-RELEASE-01`, and `MD-OFFLINE-REQ-RELEASE-01` are active and trace to exact tests in `CONTRACT_MATRIX.json`.
