# Repository Governance and Housekeeping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Protect `main` with the repository's actual stable CI checks and remove only historical branches whose tips are proven reachable from `main`, without altering release tags or immutable releases.

**Architecture:** Treat repository governance as stateful infrastructure, not source-code refactoring. First capture an exact baseline, then enable a lockout-safe `main` rule, verify it through GitHub's read API, classify every branch by ancestry against the same `main` SHA, delete only branches classified `DELETE`, and finish with a fresh audit proving `main`, releases, and the active 0.4.0 design branch are unchanged.

**Tech Stack:** GitHub repository rules/branch protection, GitHub Actions, Git refs, GitHub REST/GraphQL or GitHub Settings UI, existing `CI` workflow.

**Spec:** `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`

## Global Constraints

- Baseline release is immutable repository/plugin `0.3.1` at `f338f9e6bfca49e01666990bd44109e3a8c34e2d`.
- Do not change, move, recreate, or delete any existing release tag or GitHub Release.
- `main` changes must enter through pull requests after protection is enabled.
- Required checks are exactly `Validate (Python 3.10)`, `Validate (Python 3.13)`, `Validate Web`, and `Secret scan`.
- `Reference freshness` remains scheduled/manual and is not a required PR check.
- Require the PR branch to be up to date with `main` before merge.
- Require conversation resolution before merge.
- Required approval count remains `0` while the repository is single-maintainer.
- Merge commits remain allowed and are the repository convention; do not require linear history.
- Force pushes and deletion of `main` must be blocked.
- Signed commits are not mandatory in this cycle.
- Preserve emergency/admin recovery bypass only if the selected GitHub protection mechanism supports it explicitly.
- Preserve the active branch `design/web-reconstruction-0.4.0` and its draft PR #23.
- Branch deletion is allowed only when the branch tip is proven reachable from current `main`, or an equivalent merged-PR proof has been explicitly recorded.

---

### Task 1: Capture the exact governance baseline

**Files:**
- No repository files are modified.

**Interfaces:**
- Consumes: GitHub repository `trafficolog/mind-detective`.
- Produces: one baseline record containing exact `main` SHA, current rules/protection, current branches, open PRs, and exact-main CI state used by Tasks 2–5.

- [ ] **Step 1: Read current `main` and assert the expected release SHA**

Read `GET /repos/trafficolog/mind-detective/branches/main` and record `commit.sha`.

Expected before any newly authorized merge to `main`:

```text
f338f9e6bfca49e01666990bd44109e3a8c34e2d
```

If `main` has moved, stop destructive governance work until the new SHA and its reason are reviewed; do not silently substitute a mutable `main` reference.

- [ ] **Step 2: Read repository rules and legacy branch protection**

Read both:

```text
GET /repos/trafficolog/mind-detective/rulesets
GET /repos/trafficolog/mind-detective/branches/main
```

Expected baseline from the post-release review:

```text
rulesets = []
main.protected = false
```

- [ ] **Step 3: Read all branches and open PRs**

Capture the full branch list and all open PRs. Before governance execution, the only intentionally active non-`main` branch is:

```text
design/web-reconstruction-0.4.0
```

and the only intentionally active PR is draft PR #23.

- [ ] **Step 4: Verify the exact-main CI evidence**

Read workflow run `34686717016` / CI #522 or the latest equivalent exact-main push run if `main` was legitimately moved after this plan was written.

The recorded run must satisfy:

```text
event = push
status = completed
conclusion = success
head_sha = <exact current main SHA>
```

- [ ] **Step 5: Record the baseline in the execution notes**

The execution notes must include the exact SHA and counts in this shape:

```text
main_sha=<40 hex>
rulesets=<count>
main_protected=<true|false>
open_prs=<numbers>
branches=<count and names>
exact_main_ci=<run id>:success
```

No source commit is required for this task.

---

### Task 2: Protect `main` with the stable CI contract

**Files:**
- No repository files are modified.

**Interfaces:**
- Consumes: baseline from Task 1 and the four stable CI context names from `.github/workflows/ci.yml`.
- Produces: an active GitHub rule targeting `main` with PR-only changes, strict required checks, conversation resolution, and destructive-ref protection.

- [ ] **Step 1: Configure the rule target**

Use a repository ruleset when the account/repository supports it; otherwise use legacy branch protection with equivalent behavior. The target is exactly:

```text
refs/heads/main
```

Do not target feature/design branches.

- [ ] **Step 2: Require pull requests without a review-count gate**

Configure:

```text
require pull request before merging = true
required approvals = 0
require conversation resolution = true
```

Do not enable CODEOWNERS approval or stale-review dismissal unless separately requested.

- [ ] **Step 3: Require the exact stable status checks in strict mode**

Configure these four checks exactly:

```text
Validate (Python 3.10)
Validate (Python 3.13)
Validate Web
Secret scan
```

Enable the equivalent of "Require branches to be up to date before merging" / strict status checks.

Do not add `Reference freshness` because it is not emitted on each PR.

- [ ] **Step 4: Protect the branch ref itself**

Configure:

```text
block force pushes = true
block deletion = true
require linear history = false
require signed commits = false
```

If the ruleset UI exposes bypass actors, keep only the repository administrator/owner recovery bypass and do not add ordinary development bypasses.

- [ ] **Step 5: Verify the effective rule through GitHub read APIs**

Re-read the repository rulesets and `main` branch/protection state. The verification must prove all four required contexts and the PR/deletion/force-push settings are present.

Expected invariant:

```text
main commit SHA is unchanged from Task 1
```

If enabling protection unexpectedly changes the branch ref, stop and investigate; protection must be metadata-only.

---

### Task 3: Build the complete ancestry classification matrix

**Files:**
- No repository files are modified.

**Interfaces:**
- Consumes: exact `main` SHA from Task 1 and branch list refreshed immediately before classification.
- Produces: explicit `DELETE` or `PRESERVE` classification for every non-`main` branch.

- [ ] **Step 1: Refresh branch names immediately before classification**

The expected historical candidates are:

```text
design/foundation-0.1.0
design/offline-execution-0.3.0
design/product-evaluation-readiness-2026-09-11
design/web-pwa-0.2.0
feature/foundation-v2-0.1.0
feature/offline-execution-0.3.0
feature/web-pwa-0.2.0
fix/web-pwa-review-gates-0.2.0
implementation/product-evaluation-readiness-2026-09-11
maintenance/github-actions-2026-09-11
review-remediation-task1-safety
review-remediation-task2-checklist
review-remediation-task3-reachability
review-remediation-task4-eval-events
review-remediation-task5-local-import
review-remediation-task6-reconstruction-boundary
review-remediation-task7-semantic-eval-governance
review-remediation-task8-web-contract-pwa
review-remediation-task9-portability-docs-release
```

The active branch is:

```text
design/web-reconstruction-0.4.0
```

Any additional branch discovered at execution time starts as `PRESERVE` until separately proven safe.

- [ ] **Step 2: Compare every historical candidate to the exact `main` SHA**

For each candidate `B`, perform the equivalent of:

```bash
git merge-base --is-ancestor "B" "<exact-main-sha>"
```

or GitHub Compare API with `base=B`, `head=<exact-main-sha>`.

A branch is `DELETE` only when the evidence shows:

```text
behind_by = 0
merge_base_commit.sha = branch_tip_sha
```

The post-release review already observed this condition for all 19 historical candidates; execution must still refresh the proof before deletion.

- [ ] **Step 3: Mark the active design branch `PRESERVE` without ancestry-based deletion**

Always classify:

```text
design/web-reconstruction-0.4.0 = PRESERVE
```

because it contains the current approved design/plan work and PR #23 is open.

- [ ] **Step 4: Freeze the deletion set**

Before any deletion, write the final deletion set in execution notes. It must contain only branches with positive ancestry proof. If any expected historical branch is no longer an ancestor of `main`, remove it from the deletion set and investigate rather than force-deleting it.

---

### Task 4: Delete only the proven historical branch refs

**Files:**
- No repository files are modified.

**Interfaces:**
- Consumes: frozen `DELETE` set from Task 3.
- Produces: remote branch namespace containing `main`, `design/web-reconstruction-0.4.0`, and any newly discovered active/preserved work only.

- [ ] **Step 1: Re-read `main` before the first deletion**

Assert the exact SHA still equals the Task 1 baseline. If it changed, repeat Task 3 against the new reviewed exact SHA before deleting anything.

- [ ] **Step 2: Delete each `DELETE` branch through GitHub's supported ref deletion mechanism**

For each proven branch `B`, perform the equivalent of:

```text
DELETE /repos/trafficolog/mind-detective/git/refs/heads/<url-encoded-B>
```

or use GitHub Settings/Branches UI's Delete branch action when the connected API surface does not expose ref deletion.

Never delete:

```text
main
design/web-reconstruction-0.4.0
```

Do not delete tags with the same or similar names.

- [ ] **Step 3: Verify each deleted branch is absent before continuing**

After each deletion batch, refresh the branch list. A failure to delete one branch must not cause force-updating or repointing that branch; record it and continue only with branches whose deletion semantics are clear.

---

### Task 5: Verify governance and repository history after housekeeping

**Files:**
- No repository files are modified.

**Interfaces:**
- Consumes: final GitHub state after Tasks 2 and 4.
- Produces: final post-housekeeping evidence proving branch protection, branch cleanup, exact `main`, and release immutability.

- [ ] **Step 1: Verify remaining branches**

Expected minimum set:

```text
main
design/web-reconstruction-0.4.0
```

Any other remaining branch must have an explicit `PRESERVE` reason in execution notes.

- [ ] **Step 2: Verify draft PR #23 still resolves to its design branch**

Read PR #23 and assert:

```text
state = open
draft = true
head = design/web-reconstruction-0.4.0
base = main
```

- [ ] **Step 3: Verify `main` did not move**

Read `main` again and assert it equals the reviewed Task 1 exact SHA. Branch protection and housekeeping are ref-metadata operations and must not create source commits on `main`.

- [ ] **Step 4: Verify release immutability**

Read releases/tags:

```text
0.3.1
mind-detective-v0.3.1
mind-detective-v0.3.0
```

Assert `0.3.1` and `mind-detective-v0.3.1` remain immutable and target `f338f9e6bfca49e01666990bd44109e3a8c34e2d`; the historical `mind-detective-v0.3.0` remains immutable at `66325b32304d7741cffbfaacc2891c91602d59d2`.

- [ ] **Step 5: Re-read the effective `main` rule**

Final required state:

```text
PR-only changes
strict required checks:
  Validate (Python 3.10)
  Validate (Python 3.13)
  Validate Web
  Secret scan
conversation resolution required
force push blocked
main deletion blocked
approval count 0
linear history not required
```

If all assertions pass, repository governance/housekeeping is complete and product implementation can proceed under the new merge discipline.
