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

## Locked file map

Repository/governance: `AGENTS.md`, `CLAUDE.md`, `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SECURITY.en.md`, `LICENSE`, `pyproject.toml`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`, `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`, `docs/RELEASE_POLICY.md`, `docs/RELEASE_POLICY.en.md`, `docs/SDD_TDD_WORKFLOW.md`, `docs/METHODOLOGY.md`, `docs/METHODOLOGY.en.md`, `docs/PRIVACY.md`, `docs/RISK_REGISTER.md`, `docs/GLOSSARY.md`, `docs/GLOSSARY.en.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json`, `docs/adr/`.

Installability: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugins/mind-detective/.claude-plugin/plugin.json`, `plugins/mind-detective/.codex-plugin/plugin.json`, plugin README/CHANGELOG pairs and `THIRD_PARTY_NOTICES.md`.

Runtime: `plugins/mind-detective/scripts/evidence.py`, `question_policy.py`, `question_lint.py`, `timeline.py`, `zones.py`, `ach.py`, `redflags.py`, `schemas.py`.

Skills: `mind-detective`, `mind-detective-quickcheck`, `mind-detective-interview`, `mind-detective-timeline`, `mind-detective-zones`, `mind-detective-hypotheses`, `mind-detective-fallback`, `mind-detective-debrief` under `plugins/mind-detective/skills/<skill>/SKILL.md`.

References: `safety.md`, `redflags.md`, `question-rules.md`, `interview.md`, `mechanisms.md`, `search-allocation.md`, `ach.md`, `fallback.md`, `sources.md` under `plugins/mind-detective/references/`.

Schemas: six files under `docs/schemas/` for recall transcript, timeline, search plan, hypothesis matrix, fallback plan and case outcome v1.

Repository validators/tests: `scripts/validate_repo.py`, `contract_controls.py`, `bilingual_docs.py`, `check_reference_freshness.py`, `release_manifest.py`; root tests for repository contracts, boundaries, contract matrix, eval contract, bilingual docs, freshness and release contract.

CI/release: `.github/workflows/ci.yml`, `reference-freshness.yml`, `publish-current-release.yml`, Dependabot, PR/issue templates and `.github/releases/release.json` plus `0.1.0.md`.

---

## Task 1: Bootstrap installability and version SSOT

**Files:** create `pyproject.toml`, both root marketplace files, both plugin descriptor files, `scripts/validate_repo.py`, `tests/test_repository_contracts.py`; modify the approved design spec only to replace `.agents-plugin/plugin.json` with `.codex-plugin/plugin.json`.

**Produces:** `validate_repository(root: Path) -> list[str]`; plugin version SSOT in `plugins/mind-detective/.codex-plugin/plugin.json`.

- [ ] **Step 1: Write the failing metadata test**

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryContractTests(unittest.TestCase):
    def test_plugin_version_is_single_source_of_truth(self):
        codex = json.loads((ROOT / "plugins/mind-detective/.codex-plugin/plugin.json").read_text())
        claude = json.loads((ROOT / "plugins/mind-detective/.claude-plugin/plugin.json").read_text())
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(codex["version"], "0.1.0")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(agents["plugins"][0]["version"], codex["version"])
        self.assertEqual(marketplace["plugins"][0]["version"], codex["version"])

    def test_incorrect_agents_plugin_descriptor_is_absent(self):
        self.assertFalse((ROOT / "plugins/mind-detective/.agents-plugin/plugin.json").exists())
```

- [ ] **Step 2: Run RED** — `python -m unittest tests.test_repository_contracts -v`; expect missing-file failures.

- [ ] **Step 3: Create descriptors with exact core values**

```json
{"name":"mind-detective","version":"0.1.0","skills":"./skills/"}
```

The Codex descriptor additionally sets author `Trafficolog`, license `MIT`, display name `MIND Detective`, category `Productivity`, and capabilities `Research`, `Analysis`, `Productivity`. `.agents/plugins/marketplace.json` uses local source `./plugins/mind-detective`, `installation: AVAILABLE`, `authentication: ON_USE`, category `Productivity`. `ON_USE` is schema-compatible metadata, not credential ownership.

- [ ] **Step 4: Implement the minimal validator**

```python
from pathlib import Path
import json

def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    codex_path = root / "plugins/mind-detective/.codex-plugin/plugin.json"
    claude_path = root / "plugins/mind-detective/.claude-plugin/plugin.json"
    if not codex_path.exists() or not claude_path.exists():
        return ["PLUGIN_DESCRIPTOR_MISSING"]
    codex = json.loads(codex_path.read_text(encoding="utf-8"))
    claude = json.loads(claude_path.read_text(encoding="utf-8"))
    if codex.get("name") != "mind-detective" or claude.get("name") != "mind-detective":
        errors.append("PLUGIN_NAME_MISMATCH")
    if codex.get("version") != claude.get("version"):
        errors.append("PLUGIN_VERSION_MISMATCH")
    if (root / "plugins/mind-detective/.agents-plugin/plugin.json").exists():
        errors.append("PLUGIN_DESCRIPTOR_PATH_INVALID")
    return errors
```

Add `main()` that prints errors and returns exit `1` when nonempty. Configure Ruff `target-version = "py310"` and mypy `python_version = "3.10"` in `pyproject.toml`.

- [ ] **Step 5: Correct the spec path** — replace exactly the incorrect descriptor path; no other semantic design change.
- [ ] **Step 6: Run GREEN** — `python -m unittest tests.test_repository_contracts -v` and `python scripts/validate_repo.py`; expect PASS/0.
- [ ] **Step 7: Commit** — `git commit -m "build: bootstrap mind-detective plugin contracts"` after staging only Task 1 files.

---

## Task 2: Evidence model and recall-transcript contract

**Files:** create `evidence.py`, `test_evidence.py`, recall-transcript JSON schema, `schemas.py`, `test_schemas.py`.

**Produces:** `EvidenceClass`, frozen `Statement`, `EvidenceError(code)`, `normalize_statement(...)`, `validate_artifact(schema_name, artifact)`.

- [ ] **Step 1: Write RED origin/non-promotion tests**

```python
class EvidenceTests(unittest.TestCase):
    def test_agent_cannot_originate_user_recalled(self):
        with self.assertRaisesRegex(EvidenceError, "MD_E_AGENT_USER_EVIDENCE"):
            normalize_statement("s1", "I remember it", EvidenceClass.USER_RECALLED, "agent", "2026-09-09T12:00:00Z")

    def test_habit_marker_cannot_be_promoted_to_recall(self):
        with self.assertRaisesRegex(EvidenceError, "MD_E_HABIT_PROMOTION"):
            normalize_statement("s2", "Я обычно всегда кладу ключи сюда", EvidenceClass.USER_RECALLED, "user", "2026-09-09T12:01:00Z")
```

- [ ] **Step 2: Run RED** — plugin evidence test; expect import failure.
- [ ] **Step 3: Implement concrete model**

```python
class EvidenceClass(str, Enum):
    USER_RECALLED = "USER_RECALLED"
    HABITUAL = "HABITUAL"
    USER_STATED = "USER_STATED"
    EXTERNAL = "EXTERNAL"
    SEARCHED = "SEARCHED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    METHODOLOGY = "METHODOLOGY"

USER_ONLY = {EvidenceClass.USER_RECALLED, EvidenceClass.HABITUAL, EvidenceClass.USER_STATED}
HABIT_MARKERS = ("обычно", "всегда", "как правило", "usually", "always", "normally")
```

`normalize_statement(statement_id, text, evidence_class, author, created_at, elicited_by=None, detail_level="LOW", confidence_self="UNSTATED", limitations=())` rejects agent-originated `USER_ONLY`; when requested class is `USER_RECALLED` and a habit marker appears, raise `EvidenceError("MD_E_HABIT_PROMOTION", ...)`.

- [ ] **Step 4: Add transcript schema** — top-level required fields `schema`, `generated_at`, `case_id`, `statements`, `limitations`; statement class enum exactly matches `EvidenceClass`.
- [ ] **Step 5: Run GREEN** — evidence and schema tests.
- [ ] **Step 6: Commit** — `feat: add evidence and transcript contracts`.

---

## Task 3: Question/claim guard boundary

**Files:** create `question_policy.py`, `question_lint.py`, `test_question_lint.py`, `references/question-rules.md`.

**Produces:** `ConversationStage`, frozen `GuardResult`, `lint_utterance(text, stage, known_locations, known_third_parties)` and stable codes `MD_Q_NEW_LOCATION`, `MD_Q_CLOSED_FREE_ACCOUNT`, `MD_Q_MULTI`, `MD_Q_PRESUPPOSITION`, `MD_Q_THIRD_PARTY_BLAME`, `MD_CLAIM_UNSUPPORTED_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`.

- [ ] **Step 1: Write RED high-risk tests**

```python
def test_rejects_new_concrete_location(self):
    result = lint_utterance(
        "Вы не оставили ключи в машине?",
        stage=ConversationStage.TIMELINE_CLARIFICATION,
        known_locations={"кухня"},
        known_third_parties=set(),
    )
    self.assertFalse(result.allowed)
    self.assertIn("MD_Q_NEW_LOCATION", result.codes)

def test_rejects_uncalibrated_probability_claim(self):
    result = lint_utterance(
        "Вероятность 73%, что ключи в машине.",
        stage=ConversationStage.SEARCH_FOLLOWUP,
        known_locations={"машина"},
        known_third_parties=set(),
    )
    self.assertFalse(result.allowed)
    self.assertIn("MD_CLAIM_UNCALIBRATED_PROBABILITY", result.codes)
```

Add explicit tests for synonym `автомобиль`, closed yes/no in `FREE_ACCOUNT`, two material questions, presupposition and named third-party blame.

- [ ] **Step 2: Run RED** — expect missing module.
- [ ] **Step 3: Implement stage policy** — `FREE_ACCOUNT` permits neutral open prompts and rejects yes/no-leading templates; other stages permit bounded clarification without introducing unsupported concrete locations.
- [ ] **Step 4: Implement conservative linter** — use bounded RU/EN location/container lexicon, context-supplied third-party terms, question-count patterns, presupposition verb lexicon and probability patterns (`%`, `вероят`, `chance`, `probab`). Return all matched codes; normal block is data, not traceback.
- [ ] **Step 5: Document limitation** — linter is not claimed to catch every semantic form of suggestion; generic host cannot prove invocation for arbitrary free-form output.
- [ ] **Step 6: Run GREEN** — all guard tests pass.
- [ ] **Step 7: Commit** — `feat: enforce guarded interview utterances`.

---

## Task 4: Timeline reconstruction

**Files:** create `timeline.py`, `test_timeline.py`, timeline JSON schema.

**Produces:** frozen `TimelineEvent`, `TimelineFinding`, `TimelineError`; `build_timeline(last_contact, first_missing, events, generated_at, case_id)`.

- [ ] **Step 1: Write RED tests with concrete fixtures**

```python
def test_habit_alone_cannot_establish_last_supported_contact(self):
    habitual = normalize_statement("s1", "Я обычно кладу сюда", EvidenceClass.HABITUAL, "user", "2026-09-09T10:00:00Z")
    missing = normalize_statement("s2", "Я заметил пропажу", EvidenceClass.USER_STATED, "user", "2026-09-09T10:20:00Z")
    with self.assertRaisesRegex(TimelineError, "MD_T_HABIT_NOT_CONTACT"):
        build_timeline(habitual, missing, [], "2026-09-09T10:21:00Z", "c1")

def test_boundary_annotation_has_no_weight_field(self):
    recalled = normalize_statement("s1", "Я держал ключи", EvidenceClass.USER_RECALLED, "user", "2026-09-09T10:00:00Z")
    missing = normalize_statement("s2", "Я заметил пропажу", EvidenceClass.USER_STATED, "user", "2026-09-09T10:20:00Z")
    event = TimelineEvent("e1", "2026-09-09T10:10:00Z", "смена контекста", "s1", True, ())
    artifact = build_timeline(recalled, missing, [event], "2026-09-09T10:21:00Z", "c1")
    self.assertTrue(artifact["events"][0]["boundary"])
    self.assertNotIn("weight", artifact["events"][0])
```

- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement timeline logic** — supported last contact accepts `USER_RECALLED` and future `EXTERNAL`; habitual alone raises `MD_T_HABIT_NOT_CONTACT`; explicit reverse time order raises `MD_T_ORDER_INVALID`; missing time remains unknown with limitation.
- [ ] **Step 4: Add schema** — required `last_supported_contact`, `first_noticed_missing`, `loss_window`, `events`, `gaps`, `contradictions`, `limitations`; precision enum includes `UNKNOWN`.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `feat: add supported-contact timeline reconstruction`.

---

## Task 5: Uncalibrated search allocation

**Files:** create `zones.py`, `test_zones.py`, search-plan schema, `references/search-allocation.md`.

**Produces:** `SearchMethod`, frozen `Zone`, `SearchError`, `update_after_search`, `rank_zones`.

Operational miss factors are repository policy: `GLANCE=0.75`, `SYSTEMATIC_VISUAL=0.50`, `EMPTY_AND_REPLACE=0.15`. They are not scientific POD claims.

- [ ] **Step 1: Write RED update tests**

```python
def test_search_reduces_but_does_not_zero_zone(self):
    zones = [Zone("desk", "desk", 0.6, ("USER_RECALLED",), "LOW", "UNCALIBRATED", ()),
             Zone("unknown", "UNKNOWN_OR_OUTSIDE", 0.4, ("UNKNOWN",), "HIGH", "UNCALIBRATED", ())]
    updated = update_after_search(zones, "desk", SearchMethod.EMPTY_AND_REPLACE, "2026-09-09T11:00:00Z")
    desk = next(zone for zone in updated if zone.id == "desk")
    self.assertGreater(desk.belief_weight, 0.0)
    self.assertLess(desk.belief_weight, 0.6)
    self.assertAlmostEqual(sum(zone.belief_weight for zone in updated), 1.0, places=9)
```

Add tests for invalid weight, unknown zone, preserved `UNCALIBRATED`, and absence of artifact keys named `probability` or `pod`.

- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement deterministic update** — multiply selected raw weight by method miss factor; keep others unchanged; normalize to sum `1`; reject negative/out-of-range values; never zero due solely to search miss.
- [ ] **Step 4: Add schema/reference** — explicit `UNKNOWN_OR_OUTSIDE` representability and `calibration_status: UNCALIBRATED`.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `feat: add uncalibrated search allocation`.

---

## Task 6: Competing hypotheses

**Files:** create `ach.py`, `test_ach.py`, hypothesis-matrix schema, `references/ach.md`.

**Produces:** frozen `Hypothesis`; families `WITHIN_SYSTEM`, `LEFT_SYSTEM`, `MOVED_AFTER_CONTACT`, `HABIT_FOR_EPISODE`, `MISSED_IN_SEARCHED_ZONE`, `INSUFFICIENT_EVIDENCE`; cells `CONSISTENT`, `INCONSISTENT`, `NEUTRAL`; `build_matrix`; `validate_hypothesis_text`.

- [ ] **Step 1: Write RED tests** — neutral `MOVED_AFTER_CONTACT` passes; `Муж точно переложил ключи` with `known_third_parties={"муж"}` returns `MD_H_THIRD_PARTY_BLAME`; output contains no numeric truth probability.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement matrix** — preserve explicit cells; expose only transparent `inconsistency_count`; set `anchoring_warning` when one story is populated as consistent while competitors remain unexamined/neutral; never declare a winner from that warning.
- [ ] **Step 4: Add schema/reference and run GREEN**.
- [ ] **Step 5: Commit** — `feat: add competing hypothesis matrix`.

---

## Task 7: Safety and fallback-first routing

**Files:** create `redflags.py`, `test_redflags.py`, fallback-plan schema, `references/redflags.md`, `fallback.md`, `safety.md`.

**Produces:** `RiskSignal` values `DISORIENTATION`, `CONFUSION_SAFETY`, `MISSING_PERSON`, `THEFT_MEANINGFUL_HARM`, `CRITICAL_MEDICATION_UNCERTAINTY`, `TIME_CRITICAL_DOCUMENT`, `IMMEDIATE_DANGER`; `Route` values `IN_MOMENT`, `FALLBACK_FIRST`, `EXIT_ROLE`; frozen `RouteDecision`; `route_case(signals)`.

- [ ] **Step 1: Write RED tests**

```python
def test_disorientation_exits_role(self):
    decision = route_case({RiskSignal.DISORIENTATION})
    self.assertEqual(decision.route, Route.EXIT_ROLE)
    self.assertIn("MD_RED_FLAG_EXIT", decision.codes)

def test_time_critical_document_is_fallback_first(self):
    decision = route_case({RiskSignal.TIME_CRITICAL_DOCUMENT})
    self.assertEqual(decision.route, Route.FALLBACK_FIRST)
    self.assertIn("MD_FALLBACK_FIRST", decision.codes)
```

Also test there is no age parameter/age-only trigger.

- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement precedence** — `EXIT_ROLE` overrides `FALLBACK_FIRST`; `FALLBACK_FIRST` overrides `IN_MOMENT`. Do not encode jurisdiction-specific passport or medical procedures in Python.
- [ ] **Step 4: Add fallback schema/reference** — require reason codes, contingency categories, search timebox and limitations.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `feat: add safety and fallback routing`.

---

## Task 8: Complete six artifact schemas

**Files:** create case-outcome schema; modify `schemas.py` and `test_schemas.py`; verify all six schema files exist.

**Produces:** `SCHEMA_REQUIRED_FIELDS`; `validate_artifact` returns bounded `MD_SCHEMA_*` errors and never mutates input.

- [ ] **Step 1: Extend RED tests** for exact schema names: `mind-detective-recall-transcript/v1`, `mind-detective-timeline/v1`, `mind-detective-search-plan/v1`, `mind-detective-hypothesis-matrix/v1`, `mind-detective-fallback-plan/v1`, `mind-detective-case-outcome/v1`.
- [ ] **Step 2: Test terminal unresolved case** — `found: false`, mechanism `UNKNOWN` validates.
- [ ] **Step 3: Run RED**.
- [ ] **Step 4: Implement concrete registry/required fields** and create case-outcome schema.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `feat: complete P0 artifact schema contracts`.

---

## Task 9: Production skills and deterministic end-to-end slice

**Files:** create all eight SKILL.md files, `references/interview.md`, `references/mechanisms.md`, `test_end_to_end.py`, plugin README pair.

**Produces:** discoverable skill frontmatter (`name` equals directory; `description` starts `Use when` and is 32–500 characters); router precedence safety → fallback → IN_MOMENT → limitation for deferred workflows.

- [ ] **Step 1: Write RED structural test** — every expected skill path exists, frontmatter name matches directory, router mentions exact guard/search reason vocabulary, and deferred LONG_TERM/PROSPECTIVE are limitations rather than routes through P0 methods.
- [ ] **Step 2: Write RED deterministic case test** — create user recalled statement, timeline, two zones including `UNKNOWN_OR_OUTSIDE`, apply one search update, then construct unresolved hypothesis matrix; assert no network import or probability claim is required for the flow.
- [ ] **Step 3: Run RED**.
- [ ] **Step 4: Write bounded skill contracts** with exact defaults:

```text
You do not know where the item is and never state an unsupported location.
USER_RECALLED/HABITUAL/USER_STATED are user-origin evidence only.
Search weights are UNCALIBRATED effort-ordering values, not probabilities.
Event boundaries are methodology cues, not numeric priors.
Red flags and fallback-first routes take precedence over ordinary search.
LONG_TERM and PROSPECTIVE are unsupported in 0.1.0 and receive an explicit limitation.
```

`mind-detective-interview` requires candidate utterances to be submitted to `question_lint.py` and states generic-host enforcement limitations.

- [ ] **Step 5: Run GREEN** — all plugin tests and validator pass.
- [ ] **Step 6: Commit** — `feat: add P0 detective skill workflow`.

---

## Task 10: Stable requirements, ADRs and SDD/TDD policy

**Files:** create `docs/REQUIREMENTS.md`, `docs/SDD_TDD_WORKFLOW.md`, `AGENTS.md`, `CLAUDE.md`, ADR-001 through ADR-008; modify repository contract tests.

- [ ] **Step 1: Write RED requirement coverage test** — assert each `MD-REQ-*` ID from design §16 appears exactly once; `CLAUDE.md` must point to `AGENTS.md`.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Create requirements and ADRs** — ADR decisions exactly match design §26. During this task, mechanically supported requirements may reference selectors already created; requirements awaiting Task 12 traceability use `[unenforced: exact traceability added before release]` and Task 12 must eliminate that phrase.
- [ ] **Step 4: Create AGENTS/CLAUDE policy** — enforce `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`; prohibit merge/release claims without exact current evidence.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `docs: define foundation requirements and ADRs`.

---

## Task 11: Eval contract v2

**Files:** create `docs/EVAL_TOKEN_REGISTRY.json`, plugin `evals/scenarios.json`, `scripts/contract_controls.py`, `tests/test_eval_contract.py`; extend validator.

**Produces:** `validate_eval_file(path, token_registry, skill_root) -> list[str]`; version exactly `2`; outcomes `comply`, `comply_with_limitations`, `refuse`; exact `must_route_to`; machine-only registered `must_mention_tokens`; semantic `must_convey` and `must_not_claim`.

- [ ] **Step 1: Write RED validator fixtures** — reject legacy `must_refuse`, unknown token, route mismatch, nonexistent skill and invalid outcome.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement validator** without model execution claims.
- [ ] **Step 4: Add at least 12 adversarial scenarios** covering direct location demand, habit-as-proof, new location question, synonym leading bypass, blame, repeated quick searches as proof of absence, percentage request, imminent passport, medication uncertainty, disorientation, doorway proof request, unresolved first round.
- [ ] **Step 5: Register exact tokens** including `MD_Q_NEW_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`, `MD_RED_FLAG_EXIT`, `MD_FALLBACK_FIRST`, `UNCALIBRATED` only where exact machine vocabulary is required.
- [ ] **Step 6: Run GREEN**.
- [ ] **Step 7: Commit** — `test: add adversarial eval contract v2`.

---

## Task 12: CONTRACT_MATRIX v2 exact traceability

**Files:** create `docs/CONTRACT_MATRIX.json`, `tests/test_contract_matrix.py`; extend `contract_controls.py`, validator and requirements enforcement labels.

**Produces:** entries with `id`, `requirement_id`, `skill`, `helper`, exact test selectors, references, status; selector grammar `path.py::test_function` or `path.py::TestClass::test_method`.

- [ ] **Step 1: Write RED tests** — missing selector, typo selector, duplicate matrix ID and statically skipped selector fail with stable validator codes.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement AST selector validation** — parse test files without importing; locate exact function/method; reject supported static skip decorators. Document that AST traceability does not prove assertion semantics.
- [ ] **Step 4: Populate high-risk entries** for evidence, questions, timeline, search, hypothesis, safety, boundary, eval and release requirements.
- [ ] **Step 5: Replace every `[unenforced: exact traceability added before release]` marker** with exact enforcement selector or a truthful semantic-review-only label.
- [ ] **Step 6: Run GREEN** plus `grep -R "exact traceability added before release" docs/REQUIREMENTS.md` and require no match.
- [ ] **Step 7: Commit** — `test: enforce exact contract traceability`.

---

## Task 13: Transport-free boundary and security

**Files:** create `tests/test_boundaries.py`, security doc pair; extend validator.

**Produces:** `scan_forbidden_imports(root: Path) -> list[str]`; initial denylist includes `requests`, `httpx`, `urllib.request`, `aiohttp`, `socket`, `selenium`, `playwright`, `boto3`, `google.cloud` and explicitly listed messenger/model SDK namespaces. Statically visible subprocess curl/wget invocation is forbidden.

- [ ] **Step 1: Write RED synthetic bad-module test** — source `import requests` returns `BOUNDARY_FORBIDDEN_IMPORT`; normal stdlib imports `json`, `dataclasses`, `enum`, `re`, `datetime` pass.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement AST scanner** with scoped claim: it is a denylist enforcement mechanism, not universal proof of no I/O.
- [ ] **Step 4: Add security docs** — no credentials, no automatic file crawling, retrieved/user content is data not instructions, no chain-of-thought storage, minimize personal case data in reports.
- [ ] **Step 5: Run GREEN**.
- [ ] **Step 6: Commit** — `security: enforce transport-free P0 boundary`.

---

## Task 14: Methodology, bilingual docs and freshness

**Files:** create root README pair; architecture, plugin standard, methodology and glossary pairs; privacy and risk docs; `references/sources.md`; bilingual/freshness scripts and tests; extend validator.

**Produces:** reciprocal RU/EN links; controlled reference markers `Verified: YYYY-MM-DD` and `Review-Class: scientific|safety|api`; review windows scientific `365`, safety `180`, api `90` days; path-aware age failure in normal PR mode and strict scheduled full check.

- [ ] **Step 1: Write RED bilingual tests** — missing mirror/reciprocal link fails.
- [ ] **Step 2: Write RED freshness tests** — changed stale scientific file fails, untouched stale file does not hard-fail normal mode, future marker fails, strict mode fails stale controlled file.
- [ ] **Step 3: Run RED**.
- [ ] **Step 4: Implement public docs** — opening product boundary: MIND Detective does not know where the item is; it structures recall/search and preserves uncertainty. Cognitive Interview is transferred methodology, misinformation research motivates anti-leading guards, event-boundary findings are task-dependent, search theory motivates allocation but not calibrated household probabilities. No validated lost-item effect size claim.
- [ ] **Step 5: Implement validators and run GREEN**.
- [ ] **Step 6: Commit** — `docs: add truthful bilingual methodology contracts`.

---

## Task 15: Changelogs and release manifest governance

**Files:** create repository/plugin changelog pairs, `CONTRIBUTING.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, release-policy pair, `.github/releases/release.json`, `.github/releases/0.1.0.md`, `scripts/release_manifest.py`, release tests; extend bilingual validator.

**Produces:** `load_release_manifest(path, root) -> dict`; CLI `python scripts/release_manifest.py --check .github/releases/release.json`.

Target manifest:

```json
{
  "schema_version": 1,
  "repository": {
    "version": "0.1.0",
    "tag": "0.1.0",
    "title": "Repository 0.1.0",
    "notes_file": ".github/releases/0.1.0.md"
  },
  "plugins": [
    {
      "name": "mind-detective",
      "version": "0.1.0",
      "tag": "mind-detective-v0.1.0"
    }
  ]
}
```

- [ ] **Step 1: Write RED tests** — reject repository version/tag mismatch, plugin SSOT mismatch, noncanonical tag, missing notes, duplicate plugin entry; require RU/EN changelog marker parity for `0.1.0`.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement manifest validator and release docs** — repository SemVer distinct from plugin SemVer; P0/P1 labels are milestones; published tags/releases are not retargeted/deleted/reused.
- [ ] **Step 4: Run GREEN**.
- [ ] **Step 5: Commit** — `release: stage declarative 0.1.0 contracts`.

---

## Task 16: CI and supply-chain pinning

**Files:** create CI and strict freshness workflows, Dependabot, PR/issue templates; extend repository contract test.

**Produces:** Python `3.10`/`3.13` matrix; repository validator, root/plugin unittests, Ruff, mypy and gitleaks jobs; every third-party `uses:` ref is 40-hex immutable SHA.

- [ ] **Step 1: Write RED mutable-action test** — synthetic `actions/checkout@v5` returns `WORKFLOW_MUTABLE_ACTION_REF`; local `uses: ./path` is exempt.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Add minimal CI** — checkout with `fetch-depth: 0`, setup-python, changed-file computation, validators, root/plugin tests, Ruff and mypy. Do not add multi-plugin path matrix because only one P0 plugin exists.
- [ ] **Step 4: Add weekly strict freshness and Dependabot** — strict command `python scripts/check_reference_freshness.py --strict`; Dependabot monitors GitHub Actions weekly.
- [ ] **Step 5: Add gitleaks with immutable SHA pin**.
- [ ] **Step 6: Run local GREEN commands**:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python scripts/validate_repo.py
ruff check .
mypy scripts plugins/mind-detective/scripts
```

- [ ] **Step 7: Commit** — `ci: add pinned validation and freshness workflows`.

---

## Task 17: Single hardened publisher

**Files:** create `.github/workflows/publish-current-release.yml`; extend release tests and release-policy pair when wording must match executable behavior.

**Contract:** exactly one active publisher; reads declarative manifest; does not infer plugin releases from changed files; initial publication requires successful exact current `main` SHA; stale initial run is safe no-op/fail-safe; remote tag absence is fail-closed; standalone/conflicting tag or wrong target is hard failure; rollback is armed only in mutable publication window and is disarmed immediately after immutability confirmation.

- [ ] **Step 1: Write RED structural publisher tests** — exactly one publisher file, manifest path literal present, live-main/exact-SHA gate present, no second release publisher workflow.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Adapt the current repository-native Yandex publisher pattern** — preserve declarative manifest, exact-main gate, exact tag-SHA verification, idempotent recovery, fail-closed tag absence, immutability gate and rollback ordering. Do not create a new release framework or copy historical publisher variants.
- [ ] **Step 4: Run GREEN** — release tests and repository validator.
- [ ] **Step 5: Commit** — `release: add single hardened publisher`.

---

## Task 18: Final P0 verification and human release gate

**Files:** modify only files implicated by verified failures; create `docs/reviews/<date>-<review-source>.md` only when an actual review occurs.

- [ ] **Step 1: Run full deterministic verification**

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python scripts/validate_repo.py
ruff check .
mypy scripts plugins/mind-detective/scripts
```

All commands must exit `0`.

- [ ] **Step 2: Run scope/overclaim scans**

```bash
if grep -R "memory-detective" . --exclude-dir=.git; then exit 1; fi
if grep -R "\.agents-plugin" . --exclude-dir=.git; then exit 1; fi
if grep -R -E "73%|scientifically.*most likely|validated.*lost-item" README.md README.en.md docs plugins/mind-detective; then exit 1; fi
```

- [ ] **Step 3: Verify release surfaces** — manifest repository version/tag `0.1.0`; plugin SSOT `0.1.0`; plugin tag `mind-detective-v0.1.0`; exactly one publisher. Run `python scripts/release_manifest.py --check .github/releases/release.json`.
- [ ] **Step 4: Push and inspect exact PR-head CI** — record exact head SHA and verify every required job for that SHA; do not report green based on an earlier SHA.
- [ ] **Step 5: Run semantic/independent review when available** — focus on scientific overclaim, guard bypass, evidence contamination, generic-host overclaim, pseudo-probability, red-flag routing and release state safety. If unavailable, record that limitation rather than fabricating clean review evidence.
- [ ] **Step 6: Fix each verified executable finding with its own RED regression test, GREEN implementation and focused commit**. Documentation-only semantic corrections get a focused docs commit plus validator/eval changes when contract vocabulary changes.
- [ ] **Step 7: Confirm clean worktree after fixes** — `git status --short` must be empty after the final focused commit; do not create an empty “final” commit.
- [ ] **Step 8: Human gate** — present exact head SHA, exact-head CI evidence, review evidence/limitations, release manifest and proposed merge/release sequence. Do not merge or publish without explicit human authorization.

---

## Post-merge release sequence

After explicit human authorization:

1. Merge implementation PR with expected exact head SHA.
2. Resolve new exact `main` SHA.
3. Verify post-merge CI on that exact `main` SHA.
4. Re-confirm `.github/releases/release.json` is the intended release set.
5. Human authorizes publication of repository `0.1.0` and plugin `mind-detective-v0.1.0`.
6. Run/allow the single `publish-current-release.yml` publisher.
7. Verify repository tag `0.1.0` and plugin tag `mind-detective-v0.1.0` target the intended exact release SHA under the manifest contract.
8. Verify GitHub Release immutability/state before declaring publication complete.
9. Never retarget a published tag; corrections use a new SemVer release.

---

## Plan self-review result

**Spec coverage:** P0 scope/YAGNI → Tasks 1/9/10; evidence → Task 2; guard → Tasks 3/9/11; timeline/event boundary → Task 4; search/no-zero → Task 5; hypotheses/no blame → Task 6; safety/fallback → Task 7; artifacts → Tasks 2/4/5/6/7/8; SDD/TDD/ADRs → Task 10; eval → Task 11; exact traceability → Task 12; transport/security → Task 13; methodology/bilingual/freshness → Task 14; version/release manifest → Task 15; pinned CI → Task 16; publisher → Task 17; exact-head/review/human gate → Task 18.

**Placeholder scan:** no `TBD`, `TODO`, generic “implement later”, angle-bracket file placeholders, or code ellipsis tokens remain. Deferred product capabilities are explicit non-goals rather than unfinished plan steps.

**Type consistency:** `EvidenceClass`/`Statement` precede timeline; `ConversationStage`/`GuardResult` precede skills/evals; timeline precedes search orchestration; `Zone` and `UNCALIBRATED` semantics precede docs/evals; `RiskSignal`/`RouteDecision` precede router skill/evals; `validate_repository` retains one signature while later tasks add checks; `contract_controls.py` grows from eval validation to exact traceability; `release_manifest.py` exists before publisher work.

**Mechanical spec correction:** the approved design tree used `.agents-plugin/plugin.json`; current reference installability uses `.codex-plugin/plugin.json`. Task 1 corrects the spec and tests that `.agents-plugin` does not exist. No approved architecture decision changes.