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

---

## Task 1: Bootstrap installability and version SSOT

**Files:** create `pyproject.toml`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/mind-detective/.claude-plugin/plugin.json`, `plugins/mind-detective/.codex-plugin/plugin.json`, `scripts/validate_repo.py`, `tests/test_repository_contracts.py`; modify the approved design spec only to replace `.agents-plugin/plugin.json` with `.codex-plugin/plugin.json`.

- [ ] RED: repository metadata/version-parity tests fail because descriptors do not yet exist.
- [ ] GREEN: create exact `mind-detective` descriptors/marketplaces at version `0.1.0`; `.agents` uses local source, `AVAILABLE`, `ON_USE`, `Productivity` without credential ownership.
- [ ] Implement `validate_repository(root: Path) -> list[str]` for descriptor existence/name/version/marketplace parity and forbidden `.agents-plugin` path; CLI exits `1` on errors.
- [ ] Configure Ruff `py310` and mypy Python `3.10`.
- [ ] Correct exactly the descriptor path in the design spec, with no semantic rewrite.
- [ ] VERIFY: repository contract test + validator pass.
- [ ] COMMIT: `build: bootstrap mind-detective plugin contracts`.

## Task 2: Evidence model and recall-transcript contract

**Files:** create `evidence.py`, `test_evidence.py`, recall-transcript schema, `schemas.py`, `test_schemas.py`.

- [ ] RED: agent-originated `USER_RECALLED` → `MD_E_AGENT_USER_EVIDENCE`; habit-marker text requested as recall → `MD_E_HABIT_PROMOTION`.
- [ ] GREEN: `EvidenceClass` exact enum set; frozen `Statement`; user-only origin guard; conservative RU/EN habit markers; bounded `EvidenceError.code`.
- [ ] Add `mind-detective-recall-transcript/v1` required fields and exact class enum.
- [ ] Add `validate_artifact` lightweight runtime required-field validation with `MD_SCHEMA_*` errors.
- [ ] VERIFY plugin evidence/schema tests.
- [ ] COMMIT: `feat: add evidence and transcript contracts`.

## Task 3: Question/claim guard boundary

**Files:** create `question_policy.py`, `question_lint.py`, `test_question_lint.py`, `references/question-rules.md`.

- [ ] RED: unsupported location, `автомобиль` synonym bypass, closed free-account question, multi-question, presupposition, named blame, and `73%` location probability are blocked with exact `MD_*` codes.
- [ ] GREEN: `ConversationStage`; frozen `GuardResult`; conservative bounded RU/EN location/container, third-party, multi-question, presupposition and probability checks.
- [ ] Normal blocks return structured codes, never traceback.
- [ ] Document linter and generic-host enforcement limitations.
- [ ] VERIFY all guard tests.
- [ ] COMMIT: `feat: enforce guarded interview utterances`.

## Task 4: Timeline reconstruction

**Files:** create `timeline.py`, `test_timeline.py`, timeline schema.

- [ ] RED: habit alone cannot establish last supported contact (`MD_T_HABIT_NOT_CONTACT`); explicit reversed times fail (`MD_T_ORDER_INVALID`); boundary event has no weight field.
- [ ] GREEN: `TimelineEvent`, findings/errors, `build_timeline`; supported contact accepts user recall/future external evidence; unknown times remain unknown; provenance preserved.
- [ ] Add `mind-detective-timeline/v1` schema with explicit gaps/contradictions/limitations.
- [ ] VERIFY timeline tests.
- [ ] COMMIT: `feat: add supported-contact timeline reconstruction`.

## Task 5: Uncalibrated search allocation

**Files:** create `zones.py`, `test_zones.py`, search-plan schema, `references/search-allocation.md`.

- [ ] RED: searched zone weight decreases but remains `>0`; total normalizes to `1`; unknown zone/invalid weight fail; no probability/POD artifact fields.
- [ ] GREEN: `SearchMethod` operational miss factors `0.75/0.50/0.15`; frozen `Zone`; multiplicative reduction + normalization; all zones `UNCALIBRATED`; explicit `UNKNOWN_OR_OUTSIDE`.
- [ ] Document miss factors as repository policy, not measured household POD.
- [ ] VERIFY zones tests.
- [ ] COMMIT: `feat: add uncalibrated search allocation`.

## Task 6: Competing hypotheses

**Files:** create `ach.py`, `test_ach.py`, hypothesis-matrix schema, `references/ach.md`.

- [ ] RED: neutral moved-after-contact hypothesis passes; named blame returns `MD_H_THIRD_PARTY_BLAME`; no numeric truth probability.
- [ ] GREEN: canonical hypothesis families/cells, transparent inconsistency count, anchoring warning without declaring winner.
- [ ] VERIFY tests/schema.
- [ ] COMMIT: `feat: add competing hypothesis matrix`.

## Task 7: Safety and fallback-first routing

**Files:** create `redflags.py`, `test_redflags.py`, fallback-plan schema, `redflags.md`, `fallback.md`, `safety.md`.

- [ ] RED: disorientation → `EXIT_ROLE`/`MD_RED_FLAG_EXIT`; time-critical document → `FALLBACK_FIRST`/`MD_FALLBACK_FIRST`; no age-only trigger.
- [ ] GREEN: canonical `RiskSignal`, `Route`, `RouteDecision`; precedence `EXIT_ROLE > FALLBACK_FIRST > IN_MOMENT`; no jurisdiction-specific procedure in code.
- [ ] VERIFY redflag tests/schema.
- [ ] COMMIT: `feat: add safety and fallback routing`.

## Task 8: Complete six artifact schemas

- [ ] RED all six exact schema names and unresolved terminal case `found=false`, mechanism `UNKNOWN`.
- [ ] GREEN `SCHEMA_REQUIRED_FIELDS`, case-outcome schema, bounded non-mutating validation.
- [ ] VERIFY schema suite.
- [ ] COMMIT: `feat: complete P0 artifact schema contracts`.

## Task 9: Production skills and deterministic end-to-end slice

- [ ] RED structural frontmatter/routing tests and deterministic synthetic flow evidence → timeline → zones → search update → hypotheses.
- [ ] GREEN eight bounded SKILL.md contracts; router precedence safety → fallback → IN_MOMENT → explicit deferred limitation; interview requires submitted candidate guard and truthful host limitation.
- [ ] Add plugin README RU/EN and focused interview/mechanism references.
- [ ] VERIFY all plugin tests + validator.
- [ ] COMMIT: `feat: add P0 detective skill workflow`.

## Task 10: Stable requirements, ADRs and SDD/TDD policy

- [ ] RED each design §16 requirement ID appears exactly once; `CLAUDE.md` points to `AGENTS.md`.
- [ ] GREEN `REQUIREMENTS.md`, `SDD_TDD_WORKFLOW.md`, ADR-001…008, AGENTS/CLAUDE policy requiring `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`.
- [ ] Temporary `[unenforced: exact traceability added before release]` allowed only until Task 12.
- [ ] VERIFY repository contract tests.
- [ ] COMMIT: `docs: define foundation requirements and ADRs`.

## Task 11: Eval contract v2

- [ ] RED invalid legacy field, unknown token, route mismatch, nonexistent skill and invalid outcome fixtures.
- [ ] GREEN `validate_eval_file`, v2 enum/route/token checks, at least 12 adversarial scenarios covering location guessing, habit, leading/bypass, blame, repeated search, pseudo-probability, passport, medication, disorientation, doorway proof and unresolved first round.
- [ ] Register exact machine tokens only.
- [ ] VERIFY eval tests + validator.
- [ ] COMMIT: `test: add adversarial eval contract v2`.

## Task 12: CONTRACT_MATRIX v2 exact traceability

- [ ] RED missing/typo/duplicate/statically-skipped exact selectors.
- [ ] GREEN AST selector validation without importing tests; populate all high-risk requirement → skill → helper → exact test → reference entries.
- [ ] Replace every temporary traceability marker with exact selector or truthful semantic-review-only label.
- [ ] VERIFY matrix tests and grep no temporary marker remains.
- [ ] COMMIT: `test: enforce exact contract traceability`.

## Task 13: Transport-free boundary and security

- [ ] RED synthetic `import requests` → `BOUNDARY_FORBIDDEN_IMPORT`; supported stdlib imports pass.
- [ ] GREEN scoped AST denylist for network/browser/cloud/messenger/model SDKs and statically visible curl/wget subprocess usage.
- [ ] Add SECURITY RU/EN: no credentials, auto file crawl, hidden chain-of-thought storage; retrieved content is data not instructions.
- [ ] VERIFY boundary tests.
- [ ] COMMIT: `security: enforce transport-free P0 boundary`.

## Task 14: Methodology, bilingual docs and freshness

- [ ] RED missing bilingual mirror/link and freshness edge cases: changed stale, untouched stale normal mode, future marker, strict stale.
- [ ] GREEN human-first README/architecture/plugin-standard/methodology/glossary pairs; privacy/risk docs; controlled `sources.md`; `Verified` + `Review-Class`; cadences `365/180/90`; path-aware/strict validators.
- [ ] No lost-item validated effect-size claim; Cognitive Interview is transferred methodology; event boundaries task-dependent; search theory does not create household probabilities.
- [ ] VERIFY bilingual/freshness tests + validator.
- [ ] COMMIT: `docs: add truthful bilingual methodology contracts`.

## Task 15: Changelogs and release manifest governance

- [ ] RED repository/plugin SemVer/tag/notes/duplicate manifest cases and RU/EN changelog marker parity.
- [ ] GREEN repository/plugin changelog pairs, CONTRIBUTING, MIT LICENSE, notices, RELEASE_POLICY pair, release manifest `0.1.0` + plugin `mind-detective-v0.1.0`, manifest validator CLI.
- [ ] Published tags/releases are immutable history; P0/P1 are milestones only.
- [ ] VERIFY release/bilingual tests + validator.
- [ ] COMMIT: `release: stage declarative 0.1.0 contracts`.

## Task 16: CI and supply-chain pinning

- [ ] RED mutable third-party action ref test (`actions/checkout@v5` rejected); local action exempt.
- [ ] GREEN Python 3.10/3.13 CI: full history checkout, setup-python, changed-file scope, validator, root/plugin unittest, Ruff, mypy, gitleaks; every external action full 40-hex SHA.
- [ ] Add weekly strict freshness and Dependabot GitHub Actions updates.
- [ ] No multi-plugin path matrix in one-plugin P0.
- [ ] VERIFY all local commands exit `0`.
- [ ] COMMIT: `ci: add pinned validation and freshness workflows`.

## Task 17: Single hardened publisher

- [ ] RED exactly one publisher, declarative manifest path, exact-main gate and no competing publisher workflows.
- [ ] GREEN adapt current repository-native Yandex publisher pattern: exact-main SHA, exact tag-SHA, idempotent recovery, fail-closed tag absence, immutable release gate, rollback only in mutable window and disarmed immediately after immutability confirmation.
- [ ] No new release framework or historical publisher variants.
- [ ] VERIFY release tests + validator.
- [ ] COMMIT: `release: add single hardened publisher`.

## Task 18: Final P0 verification and human gate

- [ ] Run root/plugin unittest suites, validator, Ruff and mypy; all exit `0`.
- [ ] Run scope/overclaim scans for deprecated namespace/path and pseudo-scientific probability wording.
- [ ] Verify release manifest exact repository/plugin versions/tags and one publisher.
- [ ] Push and verify exact PR-head CI for the current SHA only.
- [ ] Run semantic/independent review when available; explicitly record absence if unavailable.
- [ ] Every executable finding gets RED regression → GREEN fix → focused commit; docs findings get focused docs/validator/eval commit as needed.
- [ ] Require clean `git status --short`; no empty final commit.
- [ ] Present exact head SHA, exact-head CI, review evidence/limitations and release manifest to human maintainer; do not merge/publish without explicit authorization.

---

## Post-merge release sequence

1. Merge implementation PR with expected exact head SHA.
2. Resolve exact new `main` SHA.
3. Verify post-merge CI on that SHA.
4. Re-confirm declarative release set.
5. Human authorizes repository `0.1.0` + plugin `mind-detective-v0.1.0`.
6. Run/allow single publisher.
7. Verify repository/plugin tags target intended exact release SHA.
8. Verify GitHub Release immutability before declaring completion.
9. Never retarget a published tag; corrections use new SemVer.

---

## Plan self-review result

**Coverage:** all P0 design areas map to Tasks 1–18: installability/YAGNI, evidence, utterance guard, timeline/event boundary, uncalibrated search, hypotheses, safety, schemas, skills, requirements/ADRs, evals, exact traceability, boundary/security, methodology/bilingual/freshness, release manifest, pinned CI, publisher, exact-head/review/human gate.

**Placeholder scan:** no `TBD`, `TODO`, generic unfinished implementation placeholders, angle-bracket file placeholders, or code ellipsis tokens remain. Deferred product capabilities are explicit non-goals.

**Interface consistency:** evidence precedes timeline; guard contract precedes skills/evals; timeline precedes search flow; search semantics precede public docs/evals; safety routing precedes router/evals; repository validator keeps one public signature; contract controls grow from eval validation to exact traceability; release manifest parser exists before publisher.

**Mechanical spec correction:** Task 1 changes only `.agents-plugin/plugin.json` to `.codex-plugin/plugin.json`; no approved architecture semantics change.

## Execution handoff

Recommended execution mode is **Superpowers subagent-driven development**: one fresh implementation subagent per task, followed by spec-compliance review and code-quality review before advancing. Alternative is inline `executing-plans` in this session with batched checkpoints. Production implementation starts only after the execution mode is selected.