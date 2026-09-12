# Post-release Governance and Housekeeping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Protect `main` with the approved merge contract and remove only historical branches proven safely integrated into `main`, without rewriting history or weakening the canonical release process.

**Architecture:** Governance remains outside product runtime code. Branch safety is established from GitHub compare/PR/release evidence; repository rules are applied through GitHub-native branch/ruleset administration only. No workflow hack, no synthetic commit, and no ref move substitutes for a missing administrative API.

**Tech Stack:** GitHub Actions, GitHub repository rules/branch protection, Git refs, immutable GitHub Releases.

**Spec:** `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`

## Global Constraints

- `main` remains the only integration branch.
- Direct pushes, force-pushes, and deletion of `main` must be blocked by a GitHub-native rule.
- Required PR checks: `Validate (Python 3.10)`, `Validate (Python 3.13)`, `Validate Web`, `Secret scan`.
- `Reference freshness` remains scheduled/manual and is not a required PR context.
- Required approvals remain `0` while the repository is single-maintainer.
- Merge commits remain allowed and linear-history enforcement remains disabled.
- Historical release tags/releases are immutable and must not be changed.
- A branch is deletable only when its tip is reachable from `main` or a merged PR proves equivalent integration.
- Do not emulate branch protection by changing CI triggers, adding a temporary publisher path, or force-moving refs.

---

### Task 1: Capture the exact Phase 0 baseline

**Files:**
- No repository file changes.

**Interfaces:**
- Consumes: current `main`, repository rulesets, branch list, open PR list.
- Produces: a dated audit table of branch tip SHA, integration evidence, and keep/delete decision.

- [ ] **Step 1: Read current `main` and rulesets**

Expected baseline before Phase 0 mutation:

```text
main = f338f9e6bfca49e01666990bd44109e3a8c34e2d
repository rulesets = []
```

- [ ] **Step 2: List all branches**

Record each branch name and exact tip SHA. Do not infer integration from naming.

- [ ] **Step 3: Confirm no unrelated open PR would be invalidated by branch deletion**

Expected at design time: only draft design PR #23 is open; remediation PRs are merged/closed.

- [ ] **Step 4: Save the audit result in the execution notes/PR body**

The table must include:

```text
branch | tip_sha | main_reachability | merged_pr_evidence | release_evidence | decision
```

Do not create a repository file solely for transient branch inventory.

### Task 2: Verify ancestry for the nine 0.3.1 remediation branches

**Files:**
- No repository file changes.

**Interfaces:**
- Consumes: branch tip SHAs and current `main`.
- Produces: exact deletion eligibility for `review-remediation-task1-*` through `task9-*`.

- [ ] **Step 1: Compare each remediation tip against `main`**

For each branch, compare:

```text
base = <remediation branch tip>
head = main
```

A branch tip is directly reachable when the compare result proves the `main` head is ahead of/equal to the branch tip with no divergence from the branch tip.

- [ ] **Step 2: Cross-check the matching merged PR**

Expected mapping:

```text
Task 1 -> PR #13
Task 2 -> PR #14
Task 3 -> PR #16
Task 4 -> PR #17
Task 5 -> PR #18
Task 6 -> PR #19
Task 7 -> PR #20
Task 8 -> PR #21
Task 9 -> PR #22
```

PR #15 is obsolete/closed and is not integration evidence for a branch deletion decision.

- [ ] **Step 3: Mark each proven branch DELETE and any unexpected divergence KEEP**

Never delete a branch on expected naming alone.

### Task 3: Audit pre-0.3.1 historical branches

**Files:**
- No repository file changes.

**Interfaces:**
- Consumes: branch list, compare results, historical PR/release metadata.
- Produces: keep/delete decisions for `design/*`, `feature/*`, `fix/*`, `implementation/*`, and `maintenance/*` branches.

- [ ] **Step 1: Compare every historical branch tip against `main`**

Current candidates include:

```text
design/foundation-0.1.0
design/web-pwa-0.2.0
design/offline-execution-0.3.0
design/product-evaluation-readiness-2026-09-11
feature/foundation-v2-0.1.0
feature/web-pwa-0.2.0
feature/offline-execution-0.3.0
fix/web-pwa-review-gates-0.2.0
implementation/product-evaluation-readiness-2026-09-11
maintenance/github-actions-2026-09-11
```

- [ ] **Step 2: For release-era branches, verify immutable release/tag evidence**

Use existing immutable releases/tags for `0.1.0`, `0.2.0`, `0.3.0`, and plugin equivalents as durable archival evidence where relevant.

- [ ] **Step 3: Preserve any branch with unmerged/divergent content**

If compare evidence is ambiguous, decision is `KEEP_FOR_REVIEW`, never delete.

### Task 4: Apply the approved `main` protection rule

**Files:**
- No product source files.

**Interfaces:**
- Consumes: stable CI job names from `.github/workflows/ci.yml`.
- Produces: GitHub-native rule applying only to `main`.

- [ ] **Step 1: Create or configure a GitHub-native repository rule for `main`**

Required configuration:

```text
Require pull request before merging: yes
Required approvals: 0
Require conversation resolution: yes
Require branch to be up to date: yes
Block force pushes: yes
Block deletion: yes
Required status checks:
  - Validate (Python 3.10)
  - Validate (Python 3.13)
  - Validate Web
  - Secret scan
Linear history: no
Required signed commits: no
```

- [ ] **Step 2: Do not add `Reference freshness` as a PR requirement**

It is not emitted on normal PR runs and requiring it would deadlock merges.

- [ ] **Step 3: Verify the rule by reading back repository rules/protection**

The verification must show a rule targeting `main` and the four exact CI contexts above.

- [ ] **Step 4: Capability fallback**

If the active automation surface does not expose repository administration, stop this task at the administrative gate. Do **not** replace it with a workflow/config workaround. Record the exact GitHub UI/API settings to apply manually, then verify them read-only after application.

### Task 5: Delete only proven-safe historical branches

**Files:**
- No repository file changes.

**Interfaces:**
- Consumes: Task 2/3 audit decisions.
- Produces: remote branch set containing `main` plus active/unmerged design/implementation work only.

- [ ] **Step 1: Delete each branch marked DELETE using GitHub's branch/ref deletion operation**

Do not force-update a branch to `main` as a substitute for deletion.

- [ ] **Step 2: If the automation surface lacks delete-ref support, stop at the deletion gate**

Provide the exact proven deletion set for manual removal. Do not use `update_ref(force=true)` to erase branch history.

- [ ] **Step 3: Re-list branches**

Expected invariant:

```text
main remains unchanged
active design/plan/implementation branches remain
no branch classified DELETE remains
```

- [ ] **Step 4: Re-read immutable release tags**

Confirm branch cleanup did not alter tags/releases.

### Task 6: Validate merge governance with the design/plan PR path

**Files:**
- No new product files.

**Interfaces:**
- Consumes: protected `main`, draft design/plan PRs.
- Produces: evidence that ordinary development can still pass the intended governance path.

- [ ] **Step 1: Ensure the design/plan PR is based on current `main` and exact-head CI runs**

- [ ] **Step 2: Confirm required checks appear under the exact names configured in protection**

- [ ] **Step 3: Do not merge the design/plan PR merely to test protection**

Use normal review approval and implementation-plan gates.

- [ ] **Step 4: Record Phase 0 completion criteria**

Phase 0 is complete only when:

```text
main protection read-back matches the approved contract
AND branch deletion/retention set has been executed and re-read
AND immutable release state is unchanged
```

If administration/deletion tooling is unavailable, Phase 0 status is `BLOCKED_ON_ADMIN_ACTION`, not `COMPLETE`.
