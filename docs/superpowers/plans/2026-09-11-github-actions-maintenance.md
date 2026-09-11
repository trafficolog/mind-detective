# GitHub Actions Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the repository's SHA-pinned `actions/checkout` and `actions/setup-python` dependencies on top of released `0.3.0` without changing product or release semantics.

**Architecture:** Keep the existing three workflow files and all current jobs/gates unchanged. Replace only the action commit SHAs and version comments already proposed by Dependabot PRs #3 and #4, then require a fresh full PR CI run against current `main` before any merge decision.

**Tech Stack:** GitHub Actions, pinned action commit SHAs, Python 3.10/3.13, Node/pnpm, Playwright.

**Spec:** Dependabot PR #3 (`actions/setup-python` 6.3.0 → 7.0.0) and PR #4 (`actions/checkout` 5.1.0 → 7.0.1).

## Global Constraints

- Base branch must be exact released `main` SHA `66325b32304d7741cffbfaacc2891c91602d59d2`.
- Preserve full commit-SHA pinning for third-party actions.
- Do not change publisher logic, release manifest, product code, tests, or historical release artifacts.
- Do not merge until fresh exact-head CI is GREEN.

---

### Task 1: Refresh pinned GitHub Actions

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `.github/workflows/publish-current-release.yml`
- Modify: `.github/workflows/reference-freshness.yml`

**Interfaces:**
- Consumes: existing workflow topology and hardened publisher gates from `0.3.0`.
- Produces: identical workflow behavior using `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`) and `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` (`v7.0.0`).

- [ ] **Step 1: Replace only the pinned action SHAs and version comments**

  Replace every current `actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5` occurrence in the three workflow files with `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`.

  Replace every current `actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6` occurrence in the three workflow files with `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0`.

- [ ] **Step 2: Review the resulting diff**

  Expected: exactly three workflow files changed; no job, permission, trigger, shell command, publisher guard, product code, or release artifact changes.

### Task 2: Verify on current 0.3.0 main

**Files:**
- Test: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Task 1 workflow-only dependency changes.
- Produces: exact-head GitHub Actions evidence suitable for merge review.

- [ ] **Step 1: Open a maintenance PR against `main`**

  The PR body must identify Dependabot PRs #3 and #4 as the source upgrades and state that this fresh branch starts from released `0.3.0` main.

- [ ] **Step 2: Require the full CI matrix to complete**

  Expected: Python 3.10 and 3.13 validation, Web generated-artifact/conformance checks, Vitest, production PWA build, Playwright Chromium/WebKit, and secret scan all PASS on the exact PR head.

- [ ] **Step 3: Verify no release-state mutation**

  Expected: `main`, tags `0.3.0` / `mind-detective-v0.3.0`, and immutable releases remain unchanged while this PR is under review.

- [ ] **Step 4: Mark Dependabot PRs #3 and #4 superseded only after the fresh maintenance PR is GREEN**

  Do not merge or close the maintenance PR without explicit merge authorization.
