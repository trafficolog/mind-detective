# MIND Detective Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build repository `0.1.0` and independently installable plugin `mind-detective-v0.1.0` with one complete transport-free IN_MOMENT flow, deterministic evidence/question/timeline/search/hypothesis/safety guards, exact SDD/TDD traceability, adversarial eval fixtures, bilingual documentation, CI, and fail-closed release governance.

**Architecture:** Repository-level files own contracts, schemas, validators, traceability, eval vocabulary and release governance. Executable runtime stays under `plugins/mind-detective/`. The LLM owns dialogue/orchestration; deterministic Python helpers own high-risk invariants. P0 has no connector, model SDK, network client, persistent cross-case memory, calibrated probability model, or shared runtime package.

**Tech Stack:** Python 3.10 and 3.13 compatibility; Python standard library only for plugin runtime; `unittest` for executable regression tests; `ruff` and `mypy` for development/CI; JSON/Markdown contracts; GitHub Actions pinned to immutable 40-hex SHAs; gitleaks for repository secret scanning.

**Spec:** `docs/superpowers/specs/2026-09-08-mind-detective-foundation-design.md`

## Global Constraints

- Canonical namespace is `mind-detective`; do not create a `memory-detective` runtime namespace.
- Correct the approved-spec tree typo in Task 1: plugin-local Codex descriptor is `.codex-plugin/plugin.json`; `.agents-plugin/plugin.json` must not exist.
- Repository release is `0.1.0`; plugin version/tag is `0.1.0` / `mind-detective-v0.1.0`.
- Runtime code under `plugins/mind-detective/scripts/` uses Python standard library only.
- CI compatibility matrix is Python `3.10` and `3.13`.
- P0 is transport-free: no HTTP, browser, cloud, messenger or model-provider SDKs and no credentials.
- No root/shared runtime package in `0.1.0`.
- No `.mind-detective/` persistence, personal baseline, LONG_TERM, PROSPECTIVE, connectors, model adapters, web/bot/voice surfaces, or calibrated location probabilities in P0.
- `USER_RECALLED`, `HABITUAL`, and `USER_STATED` originate only from user-authored case data.
- Sensory/context detail is metadata, not a truth-certification rule.
- Event boundaries are methodology cues and never mechanically boost zone weights.
- Search weights are `UNCALIBRATED`; user-facing contracts never present them as location probabilities.
- A failed search reduces a nonzero zone weight but never zeroes it by search result alone.
- Generic Claude Code/Codex hosts cannot prove every free-form model utterance invoked the linter. P0 guarantees fail-closed behavior only for submitted candidates; host invocation remains skill/eval/review evidence until a dedicated pre-send surface is separately designed.
- High-risk tests assert stable machine codes, not only generic exceptions.
- Stable requirement IDs and exact Python test selectors are mandatory from the first release.
- Green CI is mechanical evidence, not proof of scientific validity or live model semantic behavior.
- Key public docs are RU-primary with EN mirrors and reciprocal navigation.
- One repository SemVer line, independent plugin SemVer, one declarative release manifest and one active publisher govern releases.
- Published release history is immutable; corrections use a new version.

## Task Sequence

1. Bootstrap installability and version SSOT.
2. Evidence model and recall-transcript contract.
3. Question/claim guard boundary.
4. Timeline reconstruction.
5. Uncalibrated search allocation.
6. Competing hypotheses.
7. Safety and fallback-first routing.
8. Complete six artifact schemas.
9. Production skills and deterministic end-to-end slice.
10. Stable requirements, ADRs and SDD/TDD policy.
11. Eval contract v2.
12. CONTRACT_MATRIX v2 exact traceability.
13. Transport-free boundary and security.
14. Methodology, bilingual docs and freshness.
15. Changelogs and release manifest governance.
16. CI and supply-chain pinning.
17. Single hardened publisher.
18. Final P0 verification and human gate.

## Mandatory TDD pattern for every executable task

- [ ] SPEC: confirm owning stable requirement/schema/ADR.
- [ ] RED: add exact failing regression test; high-risk guards include bypass/negative case.
- [ ] GREEN: add the minimum implementation satisfying that test.
- [ ] REFACTOR: simplify without changing behavior.
- [ ] TRACE: add/update exact CONTRACT_MATRIX selector where applicable.
- [ ] EVAL: add/update adversarial scenario where conversational behavior is affected.
- [ ] VERIFY: run focused test, then impacted suite/validator.
- [ ] COMMIT: focused conventional commit; no unrelated refactor.

## Exact task contracts

### Task 1 — Bootstrap
Create both root marketplaces, plugin `.claude-plugin` and `.codex-plugin` descriptors, `pyproject.toml`, base validator and repository metadata tests. Version `0.1.0` in `.codex-plugin/plugin.json` is SSOT. `.agents` uses local source, `AVAILABLE`, `ON_USE`, `Productivity`. The incorrect `.agents-plugin` path is absent and the approved design spec receives only that path correction. Commit: `build: bootstrap mind-detective plugin contracts`.

### Task 2 — Evidence
Implement exact evidence enum, frozen statement, origin/non-promotion guard, conservative RU/EN habit markers, recall-transcript schema and bounded schema errors. RED codes: `MD_E_AGENT_USER_EVIDENCE`, `MD_E_HABIT_PROMOTION`. Commit: `feat: add evidence and transcript contracts`.

### Task 3 — Guard
Implement `ConversationStage`, frozen `GuardResult`, conservative question/claim lint for new concrete locations, free-account closed questions, multiple questions, presupposition, named blame and pseudo-probability. Required codes include `MD_Q_NEW_LOCATION`, `MD_Q_CLOSED_FREE_ACCOUNT`, `MD_Q_MULTI`, `MD_Q_PRESUPPOSITION`, `MD_Q_THIRD_PARTY_BLAME`, `MD_CLAIM_UNSUPPORTED_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`. Test synonym bypass `автомобиль`. Document generic-host limitation. Commit: `feat: enforce guarded interview utterances`.

### Task 4 — Timeline
Implement supported-contact semantics, explicit unknowns/contradictions, boundary annotation without weight effect, and errors `MD_T_HABIT_NOT_CONTACT`, `MD_T_ORDER_INVALID`. Add timeline schema. Commit: `feat: add supported-contact timeline reconstruction`.

### Task 5 — Search allocation
Implement operational miss factors `GLANCE=0.75`, `SYSTEMATIC_VISUAL=0.50`, `EMPTY_AND_REPLACE=0.15`, multiplicative reduction + normalization, `UNCALIBRATED`, and `UNKNOWN_OR_OUTSIDE`. Failed search alone never zeroes nonzero zone. No `probability`/`pod` artifact fields. Commit: `feat: add uncalibrated search allocation`.

### Task 6 — Hypotheses
Implement canonical ACH-like families/cells, transparent inconsistency count, anchoring warning and no named blame/numeric truth probability. Commit: `feat: add competing hypothesis matrix`.

### Task 7 — Safety
Implement `RiskSignal`, `Route`, `RouteDecision`; precedence `EXIT_ROLE > FALLBACK_FIRST > IN_MOMENT`; `DISORIENTATION` → `MD_RED_FLAG_EXIT`; time-critical document → `MD_FALLBACK_FIRST`; no age-only trigger or jurisdiction-specific procedure in Python. Commit: `feat: add safety and fallback routing`.

### Task 8 — Schemas
Complete six exact schema contracts including terminal unresolved `case-outcome/v1` with `found=false`, mechanism `UNKNOWN`. Commit: `feat: complete P0 artifact schema contracts`.

### Task 9 — Skills
Create eight bounded SKILL.md files, plugin README pair and deterministic synthetic end-to-end test. Router precedence is safety → fallback → IN_MOMENT → explicit limitation for LONG_TERM/PROSPECTIVE. Interview contract requires submitted candidate guard while preserving generic-host limitation. Commit: `feat: add P0 detective skill workflow`.

### Task 10 — Requirements/ADRs
Create stable requirements, ADR-001…008, SDD/TDD policy, AGENTS.md and CLAUDE.md. Require `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`. Temporary trace marker may exist only until Task 12. Commit: `docs: define foundation requirements and ADRs`.

### Task 11 — Evals
Create eval v2 validator, token registry and at least 12 adversarial scenarios: direct location demand, habit-as-proof, new location, synonym bypass, blame, repeated quick searches as absence proof, percentage request, imminent passport, medication uncertainty, disorientation, doorway proof, unresolved first round. No claim of live model execution. Commit: `test: add adversarial eval contract v2`.

### Task 12 — Traceability
Create CONTRACT_MATRIX v2 and AST exact-selector validation without importing tests. Reject missing/typo/duplicate/static-skip selectors. Eliminate all temporary trace markers. Commit: `test: enforce exact contract traceability`.

### Task 13 — Boundary/security
Create scoped AST denylist for network/browser/cloud/messenger/model SDK imports and statically visible curl/wget subprocess use; `import requests` must fail with `BOUNDARY_FORBIDDEN_IMPORT`. Add SECURITY RU/EN. Commit: `security: enforce transport-free P0 boundary`.

### Task 14 — Docs/freshness
Create human-first RU/EN docs, privacy/risk, methodology sources and freshness validators. Review classes/cadences: scientific `365`, safety `180`, api `90`; path-aware normal mode and strict scheduled mode. No validated lost-item effect-size claim. Commit: `docs: add truthful bilingual methodology contracts`.

### Task 15 — Release manifest
Create changelog pairs, CONTRIBUTING, MIT LICENSE, notices, release-policy pair, manifest and validator. Repository version/tag `0.1.0`; plugin `0.1.0` tag `mind-detective-v0.1.0`. Published history immutable. Commit: `release: stage declarative 0.1.0 contracts`.

### Task 16 — CI
Create Python 3.10/3.13 CI with full-history checkout, validator, root/plugin tests, Ruff, mypy, gitleaks, strict freshness and Dependabot. Every third-party Action uses full 40-hex SHA. No multi-plugin path matrix in P0. Commit: `ci: add pinned validation and freshness workflows`.

### Task 17 — Publisher
Adapt current repository-native Yandex single-publisher pattern: declarative manifest, exact-main SHA, exact tag-SHA, idempotent recovery, fail-closed tag absence, immutable release gate, rollback only in mutable window and disarmed after immutability. No new framework/historical variants. Commit: `release: add single hardened publisher`.

### Task 18 — Final gate
Run root/plugin tests, validator, Ruff, mypy, scope/overclaim scans, release manifest verification, exact PR-head CI, independent/semantic review when available, and clean-worktree check. Every executable finding gets RED→GREEN focused fix. Present exact head SHA, exact-head CI, review evidence/limitations and manifest to human. Do not merge/publish without explicit authorization.

## Post-merge release sequence

1. Merge implementation PR with expected exact head SHA.
2. Resolve exact new `main` SHA.
3. Verify post-merge CI on that SHA.
4. Re-confirm declarative release set.
5. Human authorizes repository `0.1.0` + plugin `mind-detective-v0.1.0`.
6. Run/allow the single publisher.
7. Verify repository/plugin tags target intended exact release SHA.
8. Verify GitHub Release immutability before declaring completion.
9. Never retarget a published tag; corrections use new SemVer.

## Plan self-review

Coverage maps every approved P0 area to Tasks 1–18. No `TBD`, `TODO`, generic unfinished implementation placeholders, angle-bracket file placeholders or code ellipsis tokens remain. Evidence precedes timeline; guard precedes skills/evals; timeline precedes search; safety precedes router/evals; manifest parser precedes publisher. Task 1 changes only the incorrect `.agents-plugin` descriptor path to `.codex-plugin`; no approved semantic decision changes.

## Execution handoff

Recommended mode: **Superpowers subagent-driven development** — one fresh implementation subagent per task, then spec-compliance review and code-quality review before advancing. Alternative: inline `executing-plans` with batched checkpoints. Production implementation starts only after selecting the execution mode.