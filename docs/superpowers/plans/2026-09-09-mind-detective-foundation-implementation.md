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

**Produces:** `validate_repository(root: Path) -> list[str]`; plugin version SSOT in `plugins/mind-detective/.codex-plugin/plugin.json`.

- [ ] Write the failing metadata test that loads all four descriptors/marketplaces, requires version `0.1.0` parity, and asserts `plugins/mind-detective/.agents-plugin/plugin.json` does not exist.
- [ ] Run `python -m unittest tests.test_repository_contracts -v`; expect missing-file failures.
- [ ] Create Claude descriptor exactly `{"name":"mind-detective","version":"0.1.0","skills":"./skills/"}`.
- [ ] Create Codex descriptor with `name=mind-detective`, `version=0.1.0`, author `Trafficolog`, license `MIT`, display name `MIND Detective`, category `Productivity`, capabilities `Research`, `Analysis`, `Productivity`.
- [ ] Create `.agents/plugins/marketplace.json` with local source `./plugins/mind-detective`, `installation: AVAILABLE`, `authentication: ON_USE`, category `Productivity`; document that `ON_USE` is schema-compatible metadata, not credential ownership.
- [ ] Implement `validate_repository(root)` to check required descriptors, canonical name, exact version parity, marketplace parity, and forbidden `.agents-plugin` path; `main()` prints errors and exits `1` when any exist.
- [ ] Configure Ruff `target-version = "py310"` and mypy `python_version = "3.10"` in `pyproject.toml`.
- [ ] Correct exactly one path in the design spec; no semantic rewrite.
- [ ] Run repository contract test and `python scripts/validate_repo.py`; require PASS/0.
- [ ] Commit `build: bootstrap mind-detective plugin contracts`.

---

## Task 2: Evidence model and recall-transcript contract

**Files:** create `plugins/mind-detective/scripts/evidence.py`, `plugins/mind-detective/tests/test_evidence.py`, `docs/schemas/mind-detective-recall-transcript-v1.schema.json`, `plugins/mind-detective/scripts/schemas.py`, `plugins/mind-detective/tests/test_schemas.py`.

**Produces:** `EvidenceClass`, frozen `Statement`, `EvidenceError` with `.code`, `normalize_statement(statement_id, text, evidence_class, author, created_at, elicited_by=None, detail_level="LOW", confidence_self="UNSTATED", limitations=())`, and `validate_artifact(schema_name, artifact)`.

- [ ] Write RED tests: agent-originated `USER_RECALLED` raises code `MD_E_AGENT_USER_EVIDENCE`; text `Я обычно всегда кладу ключи сюда` requested as `USER_RECALLED` raises `MD_E_HABIT_PROMOTION`.
- [ ] Run only `test_evidence.py`; expect missing module.
- [ ] Implement `EvidenceClass` values `USER_RECALLED`, `HABITUAL`, `USER_STATED`, `EXTERNAL`, `SEARCHED`, `INFERRED`, `HYPOTHESIS`, `METHODOLOGY`.
- [ ] Implement `USER_ONLY` origin guard and conservative RU/EN habit markers `обычно`, `всегда`, `как правило`, `usually`, `always`, `normally`; do not claim exhaustive NLP classification.
- [ ] Create recall-transcript schema requiring `schema`, `generated_at`, `case_id`, `statements`, `limitations`; statement class enum exactly matches `EvidenceClass`.
- [ ] Implement lightweight schema-name/required-field validation with bounded `MD_SCHEMA_*` errors.
- [ ] Run evidence/schema tests; require PASS.
- [ ] Commit `feat: add evidence and transcript contracts`.

---

## Task 3: Question/claim guard boundary

**Files:** create `question_policy.py`, `question_lint.py`, `test_question_lint.py`, `references/question-rules.md`.

**Produces:** `ConversationStage` values `FREE_ACCOUNT`, `CONTEXT_RECONSTRUCTION`, `TIMELINE_CLARIFICATION`, `CONTRADICTION_CLARIFICATION`, `SEARCH_FOLLOWUP`; frozen `GuardResult(allowed, codes, details)`; `lint_utterance(text, stage, known_locations, known_third_parties)`; stable codes `MD_Q_NEW_LOCATION`, `MD_Q_CLOSED_FREE_ACCOUNT`, `MD_Q_MULTI`, `MD_Q_PRESUPPOSITION`, `MD_Q_THIRD_PARTY_BLAME`, `MD_CLAIM_UNSUPPORTED_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`.

- [ ] Write RED tests for unsupported `машина`, synonym `автомобиль`, closed yes/no in `FREE_ACCOUNT`, two material questions, presupposition, named third-party blame, and `Вероятность 73%, что ключи в машине`.
- [ ] Run guard tests; expect missing module.
- [ ] Implement stage policy: `FREE_ACCOUNT` permits neutral open prompts and rejects yes/no-leading templates.
- [ ] Implement conservative linter with bounded RU/EN location/container lexicon, context-supplied third-party terms, multi-question patterns, presupposition lexicon, and probability patterns `%`, `вероят`, `chance`, `probab`.
- [ ] Return all matched codes as data; normal blocks do not emit traceback.
- [ ] Document that the linter does not prove all semantic suggestion is caught and generic host cannot prove invocation for arbitrary output.
- [ ] Run GREEN guard suite.
- [ ] Commit `feat: enforce guarded interview utterances`.

---

## Task 4: Timeline reconstruction

**Files:** create `timeline.py`, `test_timeline.py`, timeline schema.

**Produces:** frozen `TimelineEvent(id, time, label, statement_id, boundary, limitations)`, `TimelineFinding`, `TimelineError`; `build_timeline(last_contact, first_missing, events, generated_at, case_id)`.

- [ ] Write RED test that a normalized `HABITUAL` statement cannot establish last supported contact and raises `MD_T_HABIT_NOT_CONTACT`.
- [ ] Write RED test with one concrete boundary event and assert resulting event contains `boundary=true` but no `weight` key.
- [ ] Write RED test that explicit `first_missing < last_contact` raises `MD_T_ORDER_INVALID`.
- [ ] Run timeline tests; expect RED.
- [ ] Implement supported-contact logic accepting `USER_RECALLED` and future `EXTERNAL`; preserve original evidence class; unknown time remains limitation/null rather than fabricated timestamp.
- [ ] Create schema requiring `last_supported_contact`, `first_noticed_missing`, `loss_window`, `events`, `gaps`, `contradictions`, `limitations`; precision enum includes `UNKNOWN`.
- [ ] Run GREEN.
- [ ] Commit `feat: add supported-contact timeline reconstruction`.

---

## Task 5: Uncalibrated search allocation

**Files:** create `zones.py`, `test_zones.py`, search-plan schema, `references/search-allocation.md`.

**Produces:** `SearchMethod` values `GLANCE`, `SYSTEMATIC_VISUAL`, `EMPTY_AND_REPLACE`; operational miss factors `0.75`, `0.50`, `0.15`; frozen `Zone`; `SearchError`; `update_after_search`; `rank_zones`.

- [ ] Write RED test with zones `desk=0.6` and `UNKNOWN_OR_OUTSIDE=0.4`; after `EMPTY_AND_REPLACE`, desk weight stays `>0`, becomes `<0.6`, and all normalized weights sum to `1`.
- [ ] Add RED tests for invalid weight, unknown zone, persistent `UNCALIBRATED`, and absence of artifact keys named `probability` or `pod`.
- [ ] Run RED.
- [ ] Implement multiplicative selected-zone reduction, unchanged raw weights for other zones, normalization to sum `1`, and failure for invalid inputs.
- [ ] State in schema/reference that miss factors are operational repository policy, not measured household POD.
- [ ] Ensure failed search alone cannot zero a nonzero zone.
- [ ] Run GREEN.
- [ ] Commit `feat: add uncalibrated search allocation`.

---

## Task 6: Competing hypotheses

**Files:** create `ach.py`, `test_ach.py`, hypothesis-matrix schema, `references/ach.md`.

**Produces:** frozen `Hypothesis`; families `WITHIN_SYSTEM`, `LEFT_SYSTEM`, `MOVED_AFTER_CONTACT`, `HABIT_FOR_EPISODE`, `MISSED_IN_SEARCHED_ZONE`, `INSUFFICIENT_EVIDENCE`; cells `CONSISTENT`, `INCONSISTENT`, `NEUTRAL`; `build_matrix`; `validate_hypothesis_text`.

- [ ] Write RED test that neutral moved-after-contact wording passes.
- [ ] Write RED test that `Муж точно переложил ключи` with known third party `муж` returns `MD_H_THIRD_PARTY_BLAME`.
- [ ] Write RED test that matrix output contains no numeric truth probability.
- [ ] Run RED.
- [ ] Implement explicit cells and transparent `inconsistency_count`; `anchoring_warning` flags underexamined alternatives but never declares a winner.
- [ ] Create schema/reference and run GREEN.
- [ ] Commit `feat: add competing hypothesis matrix`.

---

## Task 7: Safety and fallback-first routing

**Files:** create `redflags.py`, `test_redflags.py`, fallback-plan schema, `references/redflags.md`, `fallback.md`, `safety.md`.

**Produces:** `RiskSignal` values `DISORIENTATION`, `CONFUSION_SAFETY`, `MISSING_PERSON`, `THEFT_MEANINGFUL_HARM`, `CRITICAL_MEDICATION_UNCERTAINTY`, `TIME_CRITICAL_DOCUMENT`, `IMMEDIATE_DANGER`; `Route` values `IN_MOMENT`, `FALLBACK_FIRST`, `EXIT_ROLE`; `RouteDecision`; `route_case(signals)`.

- [ ] Write RED test: `DISORIENTATION` → `EXIT_ROLE` + `MD_RED_FLAG_EXIT`.
- [ ] Write RED test: `TIME_CRITICAL_DOCUMENT` → `FALLBACK_FIRST` + `MD_FALLBACK_FIRST`.
- [ ] Assert there is no age parameter or age-only trigger.
- [ ] Run RED.
- [ ] Implement precedence `EXIT_ROLE > FALLBACK_FIRST > IN_MOMENT`; do not encode jurisdiction-specific passport or medical procedure in Python.
- [ ] Create fallback schema requiring reason codes, contingency categories, search timebox, limitations.
- [ ] Run GREEN.
- [ ] Commit `feat: add safety and fallback routing`.

---

## Task 8: Complete six artifact schemas

**Files:** create case-outcome schema; modify `schemas.py` and `test_schemas.py`; verify all six schema files.

- [ ] Add RED tests for exact schema names: recall transcript, timeline, search plan, hypothesis matrix, fallback plan, case outcome v1.
- [ ] Add RED test that terminal unresolved case `found=false`, mechanism `UNKNOWN` is valid.
- [ ] Run RED.
- [ ] Implement `SCHEMA_REQUIRED_FIELDS` and case-outcome schema; validation returns bounded `MD_SCHEMA_*` errors and never mutates input.
- [ ] Run GREEN.
- [ ] Commit `feat: complete P0 artifact schema contracts`.

---

## Task 9: Production skills and deterministic end-to-end slice

**Files:** create all eight SKILL.md files, `references/interview.md`, `references/mechanisms.md`, `test_end_to_end.py`, plugin README pair.

- [ ] Write RED structural test for every expected skill path, matching frontmatter name, `description` starting `Use when` and length 32–500.
- [ ] Write RED router test for precedence safety → fallback → IN_MOMENT → explicit limitation for LONG_TERM/PROSPECTIVE.
- [ ] Write RED deterministic case test: user recalled statement → timeline → two zones including `UNKNOWN_OR_OUTSIDE` → one search update → unresolved hypothesis matrix; no network or probability claim required.
- [ ] Run RED.
- [ ] Write bounded skills with exact defaults: no unsupported location claim; user-only evidence origins; `UNCALIBRATED` search weights; event boundaries not priors; safety precedence; deferred flows disclosed.
- [ ] `mind-detective-interview` requires candidate utterance submission to `question_lint.py` and states generic-host enforcement limitation.
- [ ] Run all plugin tests + validator; require GREEN.
- [ ] Commit `feat: add P0 detective skill workflow`.

---

## Task 10: Stable requirements, ADRs and SDD/TDD policy

**Files:** create `docs/REQUIREMENTS.md`, `docs/SDD_TDD_WORKFLOW.md`, `AGENTS.md`, `CLAUDE.md`, ADR-001 through ADR-008; extend repository contract tests.

- [ ] Write RED test that every `MD-REQ-*` from design §16 appears exactly once; `CLAUDE.md` references `AGENTS.md`.
- [ ] Run RED.
- [ ] Create ADR decisions exactly from design §26; ADR-004 records miss factors as uncalibrated policy; ADR-008 records P0 non-goals.
- [ ] During this task, mechanically supported requirements may use existing selectors; requirements awaiting Task 12 use `[unenforced: exact traceability added before release]` and Task 12 must eliminate this phrase.
- [ ] Create AGENTS/CLAUDE policy requiring `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY` and prohibiting merge/release claims without current evidence.
- [ ] Run GREEN.
- [ ] Commit `docs: define foundation requirements and ADRs`.

---

## Task 11: Eval contract v2

**Files:** create `docs/EVAL_TOKEN_REGISTRY.json`, plugin `evals/scenarios.json`, `scripts/contract_controls.py`, `tests/test_eval_contract.py`; extend validator.

**Produces:** `validate_eval_file(path, token_registry, skill_root) -> list[str]`; version `2`; outcomes `comply`, `comply_with_limitations`, `refuse`; exact `must_route_to`; registered machine tokens; semantic convey/not-claim fields.

- [ ] Write RED fixtures rejecting legacy `must_refuse`, unknown token, route mismatch, nonexistent skill and invalid outcome.
- [ ] Run RED.
- [ ] Implement structural validator with no live-model execution claim.
- [ ] Add at least 12 adversarial scenarios: direct location demand, habit-as-proof, new location, synonym bypass, blame, repeated quick searches as proof of absence, percentage request, imminent passport, medication uncertainty, disorientation, doorway proof request, unresolved first round.
- [ ] Register exact tokens only where machine vocabulary is required: `MD_Q_NEW_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`, `MD_RED_FLAG_EXIT`, `MD_FALLBACK_FIRST`, `UNCALIBRATED`.
- [ ] Run GREEN.
- [ ] Commit `test: add adversarial eval contract v2`.

---

## Task 12: CONTRACT_MATRIX v2 exact traceability

**Files:** create `docs/CONTRACT_MATRIX.json`, `tests/test_contract_matrix.py`; extend `contract_controls.py`, validator and requirements enforcement labels.

- [ ] Write RED tests for missing selector, typo selector, duplicate matrix ID and statically skipped selector.
- [ ] Run RED.
- [ ] Implement AST selector grammar `path.py::test_function` or `path.py::TestClass::test_method`; parse without importing test modules; reject supported static skips.
- [ ] Document that AST traceability proves target existence, not assertion semantics.
- [ ] Populate high-risk entries for evidence, questions, timeline, search, hypothesis, safety, boundary, eval and release.
- [ ] Replace every `[unenforced: exact traceability added before release]` marker with exact selector or truthful semantic-review-only label.
- [ ] Run GREEN and require `grep -R "exact traceability added before release" docs/REQUIREMENTS.md` to return no match.
- [ ] Commit `test: enforce exact contract traceability`.

---

## Task 13: Transport-free boundary and security

**Files:** create `tests/test_boundaries.py`, security doc pair; extend validator.

**Produces:** `scan_forbidden_imports(root)`; denylist includes `requests`, `httpx`, `urllib.request`, `aiohttp`, `socket`, `selenium`, `playwright`, `boto3`, `google.cloud` and explicitly listed messenger/model SDK namespaces; statically visible subprocess curl/wget is forbidden.

- [ ] Write RED synthetic source `import requests` expecting `BOUNDARY_FORBIDDEN_IMPORT`; verify stdlib `json`, `dataclasses`, `enum`, `re`, `datetime` pass.
- [ ] Run RED.
- [ ] Implement AST scanner and scoped enforcement wording.
- [ ] Add security docs: no credentials, no automatic file crawling, retrieved/user content is data not instructions, no hidden chain-of-thought storage, minimize personal case data.
- [ ] Run GREEN.
- [ ] Commit `security: enforce transport-free P0 boundary`.

---

## Task 14: Methodology, bilingual docs and freshness

**Files:** create root README pair; architecture/plugin-standard/methodology/glossary pairs; privacy/risk docs; `references/sources.md`; bilingual/freshness scripts and tests; extend validator.

**Produces:** reciprocal language links; markers `Verified: YYYY-MM-DD` and `Review-Class: scientific|safety|api`; cadences `365/180/90`; path-aware age failure and strict full check.

- [ ] Write RED bilingual mirror/link tests.
- [ ] Write RED freshness tests: changed stale scientific source fails; untouched stale source does not hard-fail normal mode; future date fails; strict mode fails stale controlled source.
- [ ] Run RED.
- [ ] Write human-first docs: MIND Detective does not know where the item is; Cognitive Interview is transferred methodology; misinformation research motivates anti-leading guards; event-boundary evidence is task-dependent; search theory motivates allocation, not household probabilities; no validated lost-item effect-size claim.
- [ ] Implement bilingual/freshness validators.
- [ ] Run GREEN.
- [ ] Commit `docs: add truthful bilingual methodology contracts`.

---

## Task 15: Changelogs and release manifest governance

**Files:** create repository/plugin changelog pairs, `CONTRIBUTING.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, release-policy pair, `.github/releases/release.json`, `.github/releases/0.1.0.md`, `scripts/release_manifest.py`, release tests; extend bilingual validator.

Target manifest repository entry is version/tag `0.1.0` with notes `.github/releases/0.1.0.md`; plugin entry is name `mind-detective`, version `0.1.0`, tag `mind-detective-v0.1.0`.

- [ ] Write RED tests rejecting repository version/tag mismatch, plugin SSOT mismatch, noncanonical tag, missing notes and duplicate plugin entry; require RU/EN changelog marker parity for `0.1.0`.
- [ ] Run RED.
- [ ] Implement `load_release_manifest(path, root)` and CLI `python scripts/release_manifest.py --check .github/releases/release.json`.
- [ ] Write release policy: repository SemVer distinct from plugin SemVer; P0/P1 are milestones; published tags/releases are immutable history.
- [ ] Run GREEN.
- [ ] Commit `release: stage declarative 0.1.0 contracts`.

---

## Task 16: CI and supply-chain pinning

**Files:** create `.github/workflows/ci.yml`, `reference-freshness.yml`, `.github/dependabot.yml`, PR/issue templates; extend repository contract tests.

- [ ] Write RED test rejecting synthetic `actions/checkout@v5` with `WORKFLOW_MUTABLE_ACTION_REF`; local `uses: ./path` is exempt.
- [ ] Run RED.
- [ ] Add minimal Python `3.10`/`3.13` CI: checkout `fetch-depth: 0`, setup-python, changed-file computation, validator, root/plugin unittest, Ruff, mypy.
- [ ] Add gitleaks job with immutable SHA pin.
- [ ] Add weekly strict freshness command `python scripts/check_reference_freshness.py --strict` and Dependabot for GitHub Actions.
- [ ] Do not add multi-plugin path matrix because one P0 plugin exists.
- [ ] Run locally: root tests, plugin tests, validator, `ruff check .`, `mypy scripts plugins/mind-detective/scripts`; all exit `0`.
- [ ] Commit `ci: add pinned validation and freshness workflows`.

---

## Task 17: Single hardened publisher

**Files:** create `.github/workflows/publish-current-release.yml`; extend release tests/policy when exact executable wording requires it.

**Contract:** exactly one publisher; declarative manifest; no changed-file inference; initial publication requires current successful exact `main` SHA; stale initial run is safe; remote tag absence probe fails closed; standalone/conflicting tag or wrong target fails; rollback exists only during mutable publication window and is disarmed immediately after immutability confirmation.

- [ ] Write RED structural tests for exactly one publisher, manifest path literal, live-main/exact-SHA gate and absence of second release publisher.
- [ ] Run RED.
- [ ] Adapt the current repository-native Yandex publisher pattern; preserve exact-main gate, exact tag-SHA verification, idempotent recovery, fail-closed tag absence, immutability gate and rollback ordering. Do not create a new release framework or copy historical variants.
- [ ] Run GREEN release tests and validator.
- [ ] Commit `release: add single hardened publisher`.

---

## Task 18: Final P0 verification and human gate

**Files:** modify only files implicated by verified failures; create a `docs/reviews/` artifact only when an actual review occurs.

- [ ] Run full deterministic verification: `python -m unittest discover -s tests -v`, plugin unittest discovery, validator, `ruff check .`, `mypy scripts plugins/mind-detective/scripts`; all must exit `0`.
- [ ] Run scope scans: fail if `memory-detective`, `.agents-plugin`, `73%`, `scientifically.*most likely`, or `validated.*lost-item` appears in production docs/code outside historical plan/spec discussion that is explicitly quoted for correction.
- [ ] Verify release surfaces: repository version/tag `0.1.0`, plugin SSOT `0.1.0`, plugin tag `mind-detective-v0.1.0`, one publisher; run release manifest CLI.
- [ ] Push and inspect exact PR-head CI; record exact SHA and verify every required job for that SHA.
- [ ] Run independent/semantic review when available, focused on scientific overclaim, guard bypass, evidence contamination, generic-host overclaim, pseudo-probability, red-flag routing and release state safety. If unavailable, record the limitation.
- [ ] Fix each verified executable finding with its own RED regression test, GREEN implementation and focused commit. Documentation-only semantic corrections get a focused docs commit plus validator/eval update when vocabulary changes.
- [ ] Require clean worktree `git status --short` after final focused commit; do not make an empty final commit.
- [ ] Present exact head SHA, exact-head CI evidence, review evidence/limitations, release manifest and merge/release sequence to human maintainer. Do not merge or publish without explicit authorization.

---

## Post-merge release sequence

1. Merge implementation PR with expected exact head SHA.
2. Resolve new exact `main` SHA.
3. Verify post-merge CI on that exact `main` SHA.
4. Re-confirm declarative release set.
5. Human authorizes repository `0.1.0` + plugin `mind-detective-v0.1.0` publication.
6. Run/allow single publisher.
7. Verify both repository/plugin tags target intended exact release SHA.
8. Verify GitHub Release immutability/state before declaring completion.
9. Never retarget a published tag; correction uses new SemVer.

---

## Plan self-review result

**Spec coverage:** P0/YAGNI → Tasks 1/9/10; evidence → 2; guard → 3/9/11; timeline/event boundary → 4; search/no-zero → 5; hypotheses/no blame → 6; safety/fallback → 7; artifacts → 2/4/5/6/7/8; SDD/TDD/ADRs → 10; eval → 11; exact traceability → 12; transport/security → 13; methodology/bilingual/freshness → 14; version/release manifest → 15; pinned CI → 16; publisher → 17; exact-head/review/human gate → 18.

**Placeholder scan:** no `TBD`, `TODO`, generic “implement later”, angle-bracket file placeholders, or code ellipsis tokens remain. Deferred product capabilities are explicit non-goals.

**Interface consistency:** evidence precedes timeline; guard types precede skills/evals; timeline precedes search orchestration; zone semantics precede docs/evals; risk routing precedes router/evals; `validate_repository` keeps one signature; `contract_controls.py` grows from eval validation to exact traceability; `release_manifest.py` exists before publisher work.

**Mechanical spec correction:** Task 1 changes only `.agents-plugin/plugin.json` to `.codex-plugin/plugin.json`; no approved architecture semantics are changed.