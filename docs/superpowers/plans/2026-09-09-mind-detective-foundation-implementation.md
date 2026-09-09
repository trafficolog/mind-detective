# MIND Detective Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build repository `0.1.0` and independently installable plugin `mind-detective-v0.1.0` with one complete transport-free IN_MOMENT flow, deterministic evidence/question/timeline/search/hypothesis/safety guards, exact SDD/TDD traceability, adversarial eval fixtures, bilingual documentation, CI, and fail-closed release governance.

**Architecture:** The repository owns contracts, schemas, validators, traceability, eval vocabulary and release governance; executable runtime stays plugin-local under `plugins/mind-detective/`. The LLM owns dialogue/orchestration but deterministic Python helpers own high-risk invariants. P0 has no connector, model SDK, network client, persistent cross-case memory, calibrated probability model, or shared runtime package.

**Tech Stack:** Python 3.10 and 3.13 compatibility; Python standard library for plugin runtime; `unittest` for executable regression tests; `ruff` and `mypy` for development/CI; JSON/Markdown repository contracts; GitHub Actions with immutable full-SHA pins; gitleaks for repository secret scanning.

**Spec:** `docs/superpowers/specs/2026-09-08-mind-detective-foundation-design.md`

## Global Constraints

- Canonical repository/product namespace is `mind-detective`; do not create a second `memory-detective` runtime namespace.
- Correct the approved-spec tree typo during Task 1: plugin-local Codex descriptor is `.codex-plugin/plugin.json`, matching the current reference marketplace; `.agents-plugin/plugin.json` must not be created.
- Repository release target is `0.1.0`; plugin release target/tag is `mind-detective-v0.1.0`.
- Runtime code under `plugins/mind-detective/scripts/` uses Python standard library only.
- Supported Python compatibility floor/ceiling tested in CI is Python 3.10 and Python 3.13.
- P0 remains transport-free: no HTTP/network/browser/cloud/messenger/model-provider SDKs and no credentials.
- No root/shared runtime package is introduced in `0.1.0`.
- No `.mind-detective/` cross-case persistence, personal baseline, LONG_TERM, PROSPECTIVE, connectors, model adapters, web/bot/voice surfaces, or calibrated location probabilities in P0.
- `USER_RECALLED`, `HABITUAL`, and `USER_STATED` may originate only from user-authored case data; agent text cannot create them.
- Sensory/context detail is metadata and never an automatic truth-certification rule.
- Event boundaries are methodology cues and never mechanically boost zone weights.
- Search weights are explicitly `UNCALIBRATED`; user-facing contracts must not present them as location probabilities.
- A failed search may reduce a nonzero zone weight but never zero it by search result alone.
- The generic Claude Code/Codex host cannot prove that every free-form model utterance invoked the linter. P0 mechanically guarantees fail-closed behavior for submitted candidates; host invocation remains skill/eval/review evidence until a dedicated pre-send surface exists.
- High-risk contract tests assert stable machine codes, not only generic exceptions.
- Stable requirement IDs and exact Python test selectors are used from the first release.
- Green CI is mechanical evidence, not proof of scientific validity or live model semantic behavior.
- Key public docs are RU-primary with English mirrors and reciprocal navigation.
- One repository SemVer line, independent plugin SemVer, one declarative release manifest and one active publisher govern future releases.
- Historical release tags/releases, once created, are immutable; fixes use a new version.

---

## File map locked by this plan

### Repository contracts and governance

- `AGENTS.md` — agent development rules and SDD/TDD/release gates.
- `CLAUDE.md` — concise Claude-specific entrypoint pointing to the same canonical rules; no divergent policy.
- `README.md`, `README.en.md` — human-first product README pair.
- `CHANGELOG.md`, `CHANGELOG.en.md` — repository release history pair.
- `CONTRIBUTING.md` — branch/PR/test/release workflow.
- `SECURITY.md`, `SECURITY.en.md` — reporting, secret and prompt/data-boundary policy.
- `LICENSE` — MIT license.
- `docs/REQUIREMENTS.md` — stable P0 requirement IDs and enforcement labels.
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md` — normative layer/evidence/safety architecture.
- `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md` — installable plugin contract.
- `docs/RELEASE_POLICY.md`, `docs/RELEASE_POLICY.en.md` — repository/plugin SemVer and publication contract.
- `docs/SDD_TDD_WORKFLOW.md` — executable development lifecycle.
- `docs/METHODOLOGY.md`, `docs/METHODOLOGY.en.md` — transferred-methodology posture and source boundaries.
- `docs/PRIVACY.md` — P0 data minimization and deferred persistence boundary.
- `docs/RISK_REGISTER.md` — platform/scientific/product risks and mitigations.
- `docs/GLOSSARY.md`, `docs/GLOSSARY.en.md` — canonical terms.
- `docs/CONTRACT_MATRIX.json` — exact high-risk traceability.
- `docs/EVAL_TOKEN_REGISTRY.json` — exact machine-token allowlist for evals.
- `docs/adr/001-008-*.md` — foundation decisions from the approved design.
- `docs/reviews/` — later review evidence only; no fake review artifact in bootstrap.

### Marketplace/installability

- `.claude-plugin/marketplace.json` — Claude marketplace root.
- `.agents/plugins/marketplace.json` — Agents/Codex marketplace root.
- `plugins/mind-detective/.claude-plugin/plugin.json` — minimal Claude plugin descriptor.
- `plugins/mind-detective/.codex-plugin/plugin.json` — richer Codex plugin descriptor.
- `plugins/mind-detective/README.md`, `README.en.md` — plugin-facing docs.
- `plugins/mind-detective/CHANGELOG.md`, `CHANGELOG.en.md` — plugin SemVer history.
- `plugins/mind-detective/THIRD_PARTY_NOTICES.md` — methodology/repository notices, no vendored runtime dependency claims.

### Plugin runtime

- `plugins/mind-detective/scripts/evidence.py` — evidence classes, normalized statement model, non-promotion/origin validation.
- `plugins/mind-detective/scripts/question_policy.py` — conversation-stage policy and allowed-form metadata.
- `plugins/mind-detective/scripts/question_lint.py` — candidate utterance guard with stable `MD_*` reason codes.
- `plugins/mind-detective/scripts/timeline.py` — supported-contact/loss-window model and contradiction detection.
- `plugins/mind-detective/scripts/zones.py` — uncalibrated zone ranking and multiplicative search update.
- `plugins/mind-detective/scripts/ach.py` — competing-hypothesis matrix and fixation warnings.
- `plugins/mind-detective/scripts/redflags.py` — deterministic safety/fallback routing signals.
- `plugins/mind-detective/scripts/schemas.py` — artifact schema names/required-field contracts and lightweight runtime validation.

### Plugin skills

- `plugins/mind-detective/skills/mind-detective/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-quickcheck/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-interview/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-timeline/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-zones/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-hypotheses/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-fallback/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-debrief/SKILL.md`

### Plugin references

- `plugins/mind-detective/references/safety.md`
- `plugins/mind-detective/references/redflags.md`
- `plugins/mind-detective/references/question-rules.md`
- `plugins/mind-detective/references/interview.md`
- `plugins/mind-detective/references/mechanisms.md`
- `plugins/mind-detective/references/search-allocation.md`
- `plugins/mind-detective/references/ach.md`
- `plugins/mind-detective/references/fallback.md`
- `plugins/mind-detective/references/sources.md`

### Artifact schemas

- `docs/schemas/mind-detective-recall-transcript-v1.schema.json`
- `docs/schemas/mind-detective-timeline-v1.schema.json`
- `docs/schemas/mind-detective-search-plan-v1.schema.json`
- `docs/schemas/mind-detective-hypothesis-matrix-v1.schema.json`
- `docs/schemas/mind-detective-fallback-plan-v1.schema.json`
- `docs/schemas/mind-detective-case-outcome-v1.schema.json`

### Tests/evals/validators

- `plugins/mind-detective/tests/test_evidence.py`
- `plugins/mind-detective/tests/test_question_lint.py`
- `plugins/mind-detective/tests/test_timeline.py`
- `plugins/mind-detective/tests/test_zones.py`
- `plugins/mind-detective/tests/test_ach.py`
- `plugins/mind-detective/tests/test_redflags.py`
- `plugins/mind-detective/tests/test_schemas.py`
- `plugins/mind-detective/tests/test_end_to_end.py`
- `plugins/mind-detective/evals/scenarios.json`
- `scripts/validate_repo.py`
- `scripts/contract_controls.py`
- `scripts/bilingual_docs.py`
- `scripts/check_reference_freshness.py`
- `scripts/release_manifest.py`
- `tests/test_repository_contracts.py`
- `tests/test_boundaries.py`
- `tests/test_contract_matrix.py`
- `tests/test_eval_contract.py`
- `tests/test_bilingual_docs.py`
- `tests/test_reference_freshness.py`
- `tests/test_release_contract.py`

### CI/release

- `.github/workflows/ci.yml`
- `.github/workflows/reference-freshness.yml`
- `.github/workflows/publish-current-release.yml`
- `.github/dependabot.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/releases/release.json`
- `.github/releases/0.1.0.md`

---

## Task 1: Bootstrap repository contracts and installable plugin metadata

**Files:**
- Create: `pyproject.toml`
- Create: `.claude-plugin/marketplace.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/mind-detective/.claude-plugin/plugin.json`
- Create: `plugins/mind-detective/.codex-plugin/plugin.json`
- Create: `scripts/validate_repo.py`
- Create: `tests/test_repository_contracts.py`
- Modify: `docs/superpowers/specs/2026-09-08-mind-detective-foundation-design.md` only to replace `.agents-plugin/plugin.json` with `.codex-plugin/plugin.json`

**Interfaces:**
- Produces `validate_repository(root: Path) -> list[str]` in `scripts/validate_repo.py`; empty list means structurally valid.
- Establishes plugin version SSOT as `plugins/mind-detective/.codex-plugin/plugin.json["version"] == "0.1.0"`; all marketplace/plugin mirrors must match it.
- Marketplace root names are `mind-detective` and display name `MIND Detective`.

- [ ] **Step 1: Write the failing repository metadata test**

```python
# tests/test_repository_contracts.py
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

    def test_deprecated_agents_plugin_descriptor_does_not_exist(self):
        self.assertFalse((ROOT / "plugins/mind-detective/.agents-plugin/plugin.json").exists())
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python -m unittest tests.test_repository_contracts -v`

Expected: FAIL because plugin descriptors/marketplaces do not exist.

- [ ] **Step 3: Create minimal plugin descriptors and marketplace roots**

Use exactly these core values:

```json
// plugins/mind-detective/.claude-plugin/plugin.json
{"name":"mind-detective","version":"0.1.0","skills":"./skills/"}
```

```json
// plugins/mind-detective/.codex-plugin/plugin.json
{
  "name": "mind-detective",
  "description": "Evidence-safe lost-item search methodology with guarded interviewing, timeline reconstruction and uncalibrated search allocation.",
  "version": "0.1.0",
  "author": {"name": "Trafficolog"},
  "license": "MIT",
  "keywords": ["memory", "lost-item", "search", "interview", "evidence", "safety"],
  "skills": "./skills/",
  "interface": {
    "displayName": "MIND Detective",
    "shortDescription": "Evidence-safe help for finding misplaced items.",
    "longDescription": "A transport-free methodology plugin that separates user recall, habit, hypotheses and search evidence while guarding against unsupported location claims and pseudo-probabilities.",
    "developerName": "Trafficolog",
    "category": "Productivity",
    "capabilities": ["Research", "Analysis", "Productivity"]
  }
}
```

`.agents/plugins/marketplace.json` must use local source `./plugins/mind-detective`, `installation: AVAILABLE`, `authentication: ON_USE`, category `Productivity`. Document later that `ON_USE` is schema-compatible metadata, not credential ownership.

- [ ] **Step 4: Create minimal validator interface and pyproject config**

`scripts/validate_repo.py` must expose:

```python
def validate_repository(root: Path) -> list[str]:
    ...

def main() -> int:
    errors = validate_repository(Path(__file__).resolve().parents[1])
    for error in errors:
        print(error)
    return 1 if errors else 0
```

Initial validation covers required descriptor existence, canonical name, exact version parity, and forbidden `.agents-plugin` path. `pyproject.toml` configures Ruff target `py310` and mypy Python `3.10` without runtime dependencies.

- [ ] **Step 5: Correct the approved-spec descriptor typo**

Replace only `.agents-plugin/plugin.json` with `.codex-plugin/plugin.json` in the repository-tree section. Do not alter approved architecture semantics.

- [ ] **Step 6: Run GREEN verification**

Run:

```bash
python -m unittest tests.test_repository_contracts -v
python scripts/validate_repo.py
```

Expected: PASS / exit 0.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .claude-plugin .agents plugins/mind-detective/.claude-plugin plugins/mind-detective/.codex-plugin scripts/validate_repo.py tests/test_repository_contracts.py docs/superpowers/specs/2026-09-08-mind-detective-foundation-design.md
git commit -m "build: bootstrap mind-detective plugin contracts"
```

---

## Task 2: Evidence model and recall-transcript contract

**Files:**
- Create: `plugins/mind-detective/scripts/evidence.py`
- Create: `plugins/mind-detective/tests/test_evidence.py`
- Create: `docs/schemas/mind-detective-recall-transcript-v1.schema.json`
- Create: `plugins/mind-detective/scripts/schemas.py`
- Create: `plugins/mind-detective/tests/test_schemas.py`

**Interfaces:**
- `EvidenceClass(str, Enum)` values: `USER_RECALLED`, `HABITUAL`, `USER_STATED`, `EXTERNAL`, `SEARCHED`, `INFERRED`, `HYPOTHESIS`, `METHODOLOGY`.
- `Statement` frozen dataclass fields: `id`, `text`, `evidence_class`, `author`, `created_at`, `elicited_by`, `detail_level`, `confidence_self`, `limitations`.
- `EvidenceError(Exception)` has stable `.code`.
- `normalize_statement(...)->Statement` rejects agent-originated user evidence and rejects obvious habit markers requested as `USER_RECALLED`.
- `validate_artifact(schema_name: str, artifact: dict) -> list[str]` is lightweight runtime validation for schema name and required top-level fields; full schema shape is repository-tested separately.

- [ ] **Step 1: Write RED tests for origin and non-promotion**

```python
class EvidenceTests(unittest.TestCase):
    def test_agent_cannot_originate_user_recalled(self):
        with self.assertRaisesRegex(EvidenceError, "MD_E_AGENT_USER_EVIDENCE"):
            normalize_statement(
                statement_id="s1",
                text="I remember putting it down",
                evidence_class=EvidenceClass.USER_RECALLED,
                author="agent",
                created_at="2026-09-09T12:00:00Z",
            )

    def test_habit_marker_cannot_be_promoted_to_recall(self):
        with self.assertRaisesRegex(EvidenceError, "MD_E_HABIT_PROMOTION"):
            normalize_statement(
                statement_id="s2",
                text="Я обычно всегда кладу ключи сюда",
                evidence_class=EvidenceClass.USER_RECALLED,
                author="user",
                created_at="2026-09-09T12:01:00Z",
            )
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_evidence.py' -v`

Expected: import/module failure.

- [ ] **Step 3: Implement minimal evidence model**

Use explicit RU/EN conservative habit markers such as `обычно`, `всегда`, `как правило`, `usually`, `always`, `normally`. Do not claim exhaustive NLP classification. If requested class is `USER_RECALLED` and a habit marker is detected, fail closed with `MD_E_HABIT_PROMOTION`; caller may re-submit as `HABITUAL`.

`EvidenceError.__str__` must include its code and bounded human-readable message.

- [ ] **Step 4: Add schema contract**

`mind-detective-recall-transcript/v1` requires top-level `schema`, `generated_at`, `case_id`, `statements`, `limitations`; statement items require `id`, `text`, `class`, `author`, `created_at`, `detail_level`, `confidence_self`, `limitations`. `class` enum matches `EvidenceClass` exactly.

- [ ] **Step 5: Run GREEN**

Run:

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_evidence.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_schemas.py' -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/evidence.py plugins/mind-detective/scripts/schemas.py plugins/mind-detective/tests/test_evidence.py plugins/mind-detective/tests/test_schemas.py docs/schemas/mind-detective-recall-transcript-v1.schema.json
git commit -m "feat: add evidence and transcript contracts"
```

---

## Task 3: Question/claim guard boundary

**Files:**
- Create: `plugins/mind-detective/scripts/question_policy.py`
- Create: `plugins/mind-detective/scripts/question_lint.py`
- Create: `plugins/mind-detective/tests/test_question_lint.py`
- Create: `plugins/mind-detective/references/question-rules.md`

**Interfaces:**
- `ConversationStage(str, Enum)`: `FREE_ACCOUNT`, `CONTEXT_RECONSTRUCTION`, `TIMELINE_CLARIFICATION`, `CONTRADICTION_CLARIFICATION`, `SEARCH_FOLLOWUP`.
- `GuardResult` frozen dataclass: `allowed: bool`, `codes: tuple[str, ...]`, `details: tuple[str, ...]`.
- `lint_utterance(text: str, *, stage: ConversationStage, known_locations: set[str], known_third_parties: set[str]) -> GuardResult`.
- Stable codes: `MD_Q_NEW_LOCATION`, `MD_Q_CLOSED_FREE_ACCOUNT`, `MD_Q_MULTI`, `MD_Q_PRESUPPOSITION`, `MD_Q_THIRD_PARTY_BLAME`, `MD_CLAIM_UNSUPPORTED_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`.

- [ ] **Step 1: Write one RED test per high-risk rule plus one synonym bypass case**

Representative tests:

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

Add a synonym bypass test such as `автомобиль` when only `кухня` is known; the repository lexicon must catch both `машина` and `автомобиль` as candidate location/container terms.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_question_lint.py' -v`

Expected: import/module failure.

- [ ] **Step 3: Implement stage policy**

`question_policy.py` defines only structural policy, not scientific claims. `FREE_ACCOUNT` allows open neutral prompts and rejects yes/no-leading templates. Keep rule tables small and explicit.

- [ ] **Step 4: Implement conservative linter**

Use bounded rule/lexicon checks for common RU/EN location/container terms, explicit third-party terms supplied by context, multi-question punctuation/clause patterns, common presupposition verbs, and probability language (`%`, `вероят`, `chance`, `probab`). Return all detected stable codes; never throw traceback for a normal blocked utterance.

Document exact limitation: the linter does not prove all possible suggestive language is caught.

- [ ] **Step 5: Run GREEN and bypass tests**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_question_lint.py' -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/question_policy.py plugins/mind-detective/scripts/question_lint.py plugins/mind-detective/tests/test_question_lint.py plugins/mind-detective/references/question-rules.md
git commit -m "feat: enforce guarded interview utterances"
```

---

## Task 4: Timeline reconstruction and supported-contact semantics

**Files:**
- Create: `plugins/mind-detective/scripts/timeline.py`
- Create: `plugins/mind-detective/tests/test_timeline.py`
- Create: `docs/schemas/mind-detective-timeline-v1.schema.json`

**Interfaces:**
- `TimelineEvent` frozen dataclass: `id`, `time`, `label`, `statement_id`, `boundary`, `limitations`.
- `TimelineFinding` frozen dataclass: `code`, `event_ids`, `message`.
- `build_timeline(*, last_contact: Statement, first_missing: Statement, events: list[TimelineEvent], generated_at: str, case_id: str) -> dict`.
- `TimelineError` stable codes include `MD_T_HABIT_NOT_CONTACT` and `MD_T_ORDER_INVALID`.

- [ ] **Step 1: Write RED tests**

```python
def test_habit_alone_cannot_establish_last_supported_contact(self):
    habitual = make_statement(EvidenceClass.HABITUAL)
    with self.assertRaisesRegex(TimelineError, "MD_T_HABIT_NOT_CONTACT"):
        build_timeline(last_contact=habitual, first_missing=make_missing(), events=[], generated_at=NOW, case_id="c1")

def test_event_boundary_does_not_change_any_search_weight(self):
    artifact = build_timeline(... boundary_event ...)
    self.assertTrue(artifact["events"][0]["boundary"])
    self.assertNotIn("weight", artifact["events"][0])
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v`

- [ ] **Step 3: Implement minimal timeline logic**

Accept `USER_RECALLED` or future `EXTERNAL` as supported contact sources; preserve original evidence class. Parse only explicit RFC3339 timestamps when supplied. Unknown time remains `null`/limitation; never infer a timestamp from event order prose. Detect explicit `first_missing < last_contact` as `MD_T_ORDER_INVALID`.

- [ ] **Step 4: Create timeline JSON schema**

Require `last_supported_contact`, `first_noticed_missing`, `loss_window`, `events`, `gaps`, `contradictions`, `limitations`. `loss_window.precision` must permit `UNKNOWN`.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v`

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/timeline.py plugins/mind-detective/tests/test_timeline.py docs/schemas/mind-detective-timeline-v1.schema.json
git commit -m "feat: add supported-contact timeline reconstruction"
```

---

## Task 5: Uncalibrated search allocation and search-round updates

**Files:**
- Create: `plugins/mind-detective/scripts/zones.py`
- Create: `plugins/mind-detective/tests/test_zones.py`
- Create: `docs/schemas/mind-detective-search-plan-v1.schema.json`
- Create: `plugins/mind-detective/references/search-allocation.md`

**Interfaces:**
- `SearchMethod(str, Enum)`: `GLANCE`, `SYSTEMATIC_VISUAL`, `EMPTY_AND_REPLACE`.
- Operational miss factors (repository policy, not scientific POD): `GLANCE=0.75`, `SYSTEMATIC_VISUAL=0.50`, `EMPTY_AND_REPLACE=0.15`.
- `Zone` frozen dataclass: `id`, `label`, `belief_weight`, `weight_reasons`, `effort`, `calibration_status`, `rounds`.
- `update_after_search(zones: list[Zone], *, zone_id: str, method: SearchMethod, searched_at: str) -> list[Zone]`.
- `rank_zones(zones: list[Zone]) -> list[Zone]` sorts by normalized weight/effort category while keeping explanation explicit.
- `SearchError` codes: `MD_S_ZONE_UNKNOWN`, `MD_S_WEIGHT_INVALID`, `MD_S_ZERO_BY_SEARCH_FORBIDDEN`.

- [ ] **Step 1: Write RED tests for multiplicative reduction, normalization and no-zero rule**

```python
def test_search_reduces_but_does_not_zero_zone(self):
    zones = [zone("desk", 0.6), zone("unknown", 0.4)]
    updated = update_after_search(zones, zone_id="desk", method=SearchMethod.EMPTY_AND_REPLACE, searched_at=NOW)
    desk = next(z for z in updated if z.id == "desk")
    self.assertGreater(desk.belief_weight, 0.0)
    self.assertLess(desk.belief_weight, 0.6)
    self.assertAlmostEqual(sum(z.belief_weight for z in updated), 1.0, places=9)

def test_all_zones_remain_uncalibrated(self):
    self.assertEqual(zone("x", 1.0).calibration_status, "UNCALIBRATED")
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_zones.py' -v`

- [ ] **Step 3: Implement minimal deterministic update**

Compute `raw = old_weight * miss_factor`; keep all other raw weights unchanged; normalize sum to 1. Reject negative/out-of-range initial weights. The helper never emits a field named `probability` or `pod` in P0 artifacts.

- [ ] **Step 4: Create search-plan schema and methodology reference**

Schema requires `calibration_status: "UNCALIBRATED"` for every zone and explicit `UNKNOWN_OR_OUTSIDE` representability. Reference explains that miss factors are operational policy parameters, not measured household detection probabilities.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_zones.py' -v`

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/zones.py plugins/mind-detective/tests/test_zones.py docs/schemas/mind-detective-search-plan-v1.schema.json plugins/mind-detective/references/search-allocation.md
git commit -m "feat: add uncalibrated search allocation"
```

---

## Task 6: Competing hypotheses without blame or opaque scoring

**Files:**
- Create: `plugins/mind-detective/scripts/ach.py`
- Create: `plugins/mind-detective/tests/test_ach.py`
- Create: `docs/schemas/mind-detective-hypothesis-matrix-v1.schema.json`
- Create: `plugins/mind-detective/references/ach.md`

**Interfaces:**
- `Hypothesis` frozen dataclass: `id`, `family`, `text`, `supports`, `weakens`, `status`.
- Allowed P0 families: `WITHIN_SYSTEM`, `LEFT_SYSTEM`, `MOVED_AFTER_CONTACT`, `HABIT_FOR_EPISODE`, `MISSED_IN_SEARCHED_ZONE`, `INSUFFICIENT_EVIDENCE`.
- `build_matrix(hypotheses: list[Hypothesis], evidence_ids: list[str], cells: dict[tuple[str, str], str]) -> dict`.
- Cells enum strings: `CONSISTENT`, `INCONSISTENT`, `NEUTRAL`.
- `validate_hypothesis_text(text: str, known_third_parties: set[str]) -> list[str]` returns `MD_H_THIRD_PARTY_BLAME` when appropriate.

- [ ] **Step 1: Write RED tests**

Test a neutral `MOVED_AFTER_CONTACT` hypothesis passes, while `Муж точно переложил ключи` with `known_third_parties={"муж"}` returns `MD_H_THIRD_PARTY_BLAME`. Test output contains no aggregate numeric “truth score”.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_ach.py' -v`

- [ ] **Step 3: Implement minimal matrix**

Preserve explicit cells and expose `inconsistency_count` only as a transparent count of `INCONSISTENT` cells, not probability/truth ranking. `anchoring_warning` becomes true when one hypothesis has all populated cells `CONSISTENT` and all competitors are unexamined/neutral, signaling review rather than declaring a winner.

- [ ] **Step 4: Create schema/reference and run GREEN**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_ach.py' -v`

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/ach.py plugins/mind-detective/tests/test_ach.py docs/schemas/mind-detective-hypothesis-matrix-v1.schema.json plugins/mind-detective/references/ach.md
git commit -m "feat: add competing hypothesis matrix"
```

---

## Task 7: Safety routing and fallback-first decision contract

**Files:**
- Create: `plugins/mind-detective/scripts/redflags.py`
- Create: `plugins/mind-detective/tests/test_redflags.py`
- Create: `docs/schemas/mind-detective-fallback-plan-v1.schema.json`
- Create: `plugins/mind-detective/references/redflags.md`
- Create: `plugins/mind-detective/references/fallback.md`
- Create: `plugins/mind-detective/references/safety.md`

**Interfaces:**
- `RiskSignal(str, Enum)`: `DISORIENTATION`, `CONFUSION_SAFETY`, `MISSING_PERSON`, `THEFT_MEANINGFUL_HARM`, `CRITICAL_MEDICATION_UNCERTAINTY`, `TIME_CRITICAL_DOCUMENT`, `IMMEDIATE_DANGER`.
- `Route(str, Enum)`: `IN_MOMENT`, `FALLBACK_FIRST`, `EXIT_ROLE`.
- `RouteDecision` frozen dataclass: `route`, `codes`, `limitations`.
- `route_case(signals: set[RiskSignal]) -> RouteDecision`.
- Stable codes include `MD_RED_FLAG_EXIT`, `MD_FALLBACK_FIRST`.

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

Also test that age alone is not an input or trigger.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_redflags.py' -v`

- [ ] **Step 3: Implement deterministic precedence**

`EXIT_ROLE` signals override `FALLBACK_FIRST`; `FALLBACK_FIRST` overrides ordinary `IN_MOMENT`. Do not encode jurisdiction-specific passport/medical procedures in Python.

- [ ] **Step 4: Create fallback schema and references**

Fallback artifact requires `schema`, `generated_at`, `case_id`, `reason_codes`, `contingency_categories`, `search_timebox`, `limitations`. Content references must state that current medical/legal/jurisdictional details require separately verified sources outside P0 static methodology.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_redflags.py' -v
git add plugins/mind-detective/scripts/redflags.py plugins/mind-detective/tests/test_redflags.py docs/schemas/mind-detective-fallback-plan-v1.schema.json plugins/mind-detective/references/redflags.md plugins/mind-detective/references/fallback.md plugins/mind-detective/references/safety.md
git commit -m "feat: add safety and fallback routing"
```

---

## Task 8: Complete artifact schema set and case-outcome contract

**Files:**
- Create: `docs/schemas/mind-detective-case-outcome-v1.schema.json`
- Modify: `plugins/mind-detective/scripts/schemas.py`
- Modify: `plugins/mind-detective/tests/test_schemas.py`

**Interfaces:**
- `SCHEMA_REQUIRED_FIELDS: dict[str, frozenset[str]]` contains all six P0 schema names.
- `validate_artifact` returns bounded error strings prefixed `MD_SCHEMA_`; it never mutates artifacts.

- [ ] **Step 1: Extend RED tests to require all six schemas**

Test exact names:

```text
mind-detective-recall-transcript/v1
mind-detective-timeline/v1
mind-detective-search-plan/v1
mind-detective-hypothesis-matrix/v1
mind-detective-fallback-plan/v1
mind-detective-case-outcome/v1
```

Test `case-outcome/v1` supports `found: false` and mechanism `UNKNOWN`; giving up without finding the item is a valid terminal case state.

- [ ] **Step 2: Run RED, implement minimum registry, run GREEN**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_schemas.py' -v`

- [ ] **Step 3: Commit**

```bash
git add docs/schemas plugins/mind-detective/scripts/schemas.py plugins/mind-detective/tests/test_schemas.py
git commit -m "feat: complete P0 artifact schema contracts"
```

---

## Task 9: Production skill set and end-to-end IN_MOMENT orchestration contract

**Files:**
- Create all eight `plugins/mind-detective/skills/*/SKILL.md` files listed in the file map.
- Create: `plugins/mind-detective/references/interview.md`
- Create: `plugins/mind-detective/references/mechanisms.md`
- Create: `plugins/mind-detective/tests/test_end_to_end.py`
- Create: `plugins/mind-detective/README.md`
- Create: `plugins/mind-detective/README.en.md`

**Interfaces:**
- Skill frontmatter: `name` equals directory name; `description` starts with `Use when` and stays 32–500 characters.
- Router order: red flag → fallback-first → IN_MOMENT → truthful limitation for deferred LONG_TERM/PROSPECTIVE.
- Every skill names exact helper it delegates deterministic work to.
- `mind-detective-interview` explicitly says candidate questions must be submitted to `question_lint.py`; it also states the generic-host limitation that the plugin cannot prove arbitrary host text passed the helper.

- [ ] **Step 1: Write RED structural/end-to-end tests before skills exist**

`test_end_to_end.py` loads skill files and asserts required route names/guard vocabulary exist. Add one deterministic synthetic case test that calls evidence → timeline → zones → search update → hypotheses using helper APIs without network access.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_end_to_end.py' -v`

- [ ] **Step 3: Write bounded SKILL.md contracts**

Each SKILL body should fit one workflow. Do not duplicate long methodology; link only needed references. Required router defaults:

```text
- You do not know where the item is and never state an unsupported location.
- USER_RECALLED/HABITUAL/USER_STATED are user-origin evidence only.
- Search weights are UNCALIBRATED effort-ordering values, not probabilities.
- Event boundaries are methodology cues, not numeric priors.
- Red flags/fallback-first routes take precedence over ordinary search.
- LONG_TERM and PROSPECTIVE are deferred in 0.1.0; disclose limitation instead of improvising them.
```

- [ ] **Step 4: Run GREEN**

Run:

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
python scripts/validate_repo.py
```

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/skills plugins/mind-detective/references/interview.md plugins/mind-detective/references/mechanisms.md plugins/mind-detective/tests/test_end_to_end.py plugins/mind-detective/README.md plugins/mind-detective/README.en.md
git commit -m "feat: add P0 detective skill workflow"
```

---

## Task 10: Stable requirements, ADRs and SDD/TDD policy

**Files:**
- Create: `docs/REQUIREMENTS.md`
- Create: `docs/SDD_TDD_WORKFLOW.md`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Create ADR-001 through ADR-008 under `docs/adr/`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- Every requirement ID from approved design §16 appears exactly once in `docs/REQUIREMENTS.md`.
- Normative `MUST`/`never` statements use `[enforced: path::selector]` or `[unenforced: semantic review/policy reason]` once corresponding selectors exist; requirements not yet traced during this task may be `[unenforced: trace added in Task 12]` only inside this plan branch and must be eliminated before Task 12 GREEN.
- `AGENTS.md` requires SDD → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY and prohibits release/merge claims without current evidence.
- `CLAUDE.md` points to `AGENTS.md` and does not fork policy.

- [ ] **Step 1: Write RED test for requirement coverage and forbidden duplicate policy sources**

Test all `MD-REQ-*` IDs expected from design exist once. Test `CLAUDE.md` contains `AGENTS.md` reference.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_repository_contracts -v`

- [ ] **Step 3: Create docs and ADRs**

ADR titles/decisions exactly follow approved design §26. ADR-004 explicitly records operational miss factors as uncalibrated repository policy, not scientific effect sizes. ADR-008 lists P0 non-goals.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_repository_contracts -v
git add docs/REQUIREMENTS.md docs/SDD_TDD_WORKFLOW.md docs/adr AGENTS.md CLAUDE.md tests/test_repository_contracts.py
git commit -m "docs: define foundation requirements and ADRs"
```

---

## Task 11: Eval contract v2 and adversarial fixtures

**Files:**
- Create: `docs/EVAL_TOKEN_REGISTRY.json`
- Create: `plugins/mind-detective/evals/scenarios.json`
- Create: `scripts/contract_controls.py`
- Create: `tests/test_eval_contract.py`
- Modify: `scripts/validate_repo.py`

**Interfaces:**
- `validate_eval_file(path: Path, token_registry: dict, skill_root: Path) -> list[str]`.
- Eval file `version` is exactly `2`.
- Allowed `outcome`: `comply`, `comply_with_limitations`, `refuse`.
- `must_mention_tokens` may contain only registered exact machine vocabulary; prose belongs in `must_convey`.
- `must_route_to` must equal scenario `skill` and referenced `SKILL.md` must exist.

- [ ] **Step 1: Write RED validator tests using one valid and several invalid inline fixtures**

Reject legacy `must_refuse`, unknown token, missing skill, outcome outside enum, and route mismatch.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_eval_contract -v`

- [ ] **Step 3: Implement validator and 12+ adversarial scenarios**

Required scenarios from design: direct location demand; habit-as-proof; new location question; synonym-leading bypass; third-party blame; repeated quick searches as proof of absence; percentage probability request; imminent passport; medication uncertainty; disorientation; doorway/event-boundary proof request; unresolved first round requiring hypotheses.

Register machine tokens only where exact code matters, including `MD_Q_NEW_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`, `MD_RED_FLAG_EXIT`, `MD_FALLBACK_FIRST`, `UNCALIBRATED`.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_eval_contract -v
python scripts/validate_repo.py
```

- [ ] **Step 5: Commit**

```bash
git add docs/EVAL_TOKEN_REGISTRY.json plugins/mind-detective/evals/scenarios.json scripts/contract_controls.py scripts/validate_repo.py tests/test_eval_contract.py
git commit -m "test: add adversarial eval contract v2"
```

---

## Task 12: Exact CONTRACT_MATRIX v2 traceability

**Files:**
- Create: `docs/CONTRACT_MATRIX.json`
- Create: `tests/test_contract_matrix.py`
- Modify: `scripts/contract_controls.py`
- Modify: `scripts/validate_repo.py`
- Modify: `docs/REQUIREMENTS.md` to replace any temporary unenforced trace markers with exact enforcement selectors where mechanically supported.

**Interfaces:**
- Matrix entries contain stable `id`, `requirement_id`, `skill`, `helper`, `tests` exact selectors, `references`, and `status`.
- Exact selector grammar: `path.py::test_function` or `path.py::TestClass::test_method`.
- Validator parses test files with Python `ast`, verifies exact function/method existence and rejects supported static `@skip`/`@skipIf(True, ...)` cases.

- [ ] **Step 1: Write RED tests for missing selector, typo selector and duplicate matrix ID**

Use a temporary matrix fixture in `tests/test_contract_matrix.py`; assert machine-coded validator messages such as `CONTRACT_TEST_SELECTOR_MISSING`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_contract_matrix -v`

- [ ] **Step 3: Implement AST selector validation**

Do not import test modules. Static AST inspection is traceability evidence only; docs must explicitly state it does not prove assertion semantics.

- [ ] **Step 4: Populate high-risk matrix**

At minimum trace every `MD-REQ-EVIDENCE-*`, `MD-REQ-QUESTION-*`, `MD-REQ-TIMELINE-*`, `MD-REQ-SEARCH-*`, `MD-REQ-HYPOTHESIS-01`, `MD-REQ-SAFETY-*`, `MD-REQ-BOUNDARY-01`, `MD-REQ-EVAL-01`, and `MD-REQ-RELEASE-01` to exact tests.

- [ ] **Step 5: Run GREEN and scan requirements for stale temporary markers**

Run:

```bash
python -m unittest tests.test_contract_matrix -v
python scripts/validate_repo.py
grep -R "trace added in Task 12" docs/REQUIREMENTS.md && exit 1 || true
```

- [ ] **Step 6: Commit**

```bash
git add docs/CONTRACT_MATRIX.json docs/REQUIREMENTS.md scripts/contract_controls.py scripts/validate_repo.py tests/test_contract_matrix.py
git commit -m "test: enforce exact contract traceability"
```

---

## Task 13: Transport-free AST boundary and repository security checks

**Files:**
- Create: `tests/test_boundaries.py`
- Modify: `scripts/validate_repo.py`
- Create: `SECURITY.md`
- Create: `SECURITY.en.md`

**Interfaces:**
- `scan_forbidden_imports(root: Path) -> list[str]` walks all plugin `*.py` by AST.
- Initial denylist includes `requests`, `httpx`, `urllib.request`, `aiohttp`, `socket`, `selenium`, `playwright`, `boto3`, `google.cloud`, messenger/provider SDK namespaces and direct subprocess-based curl/wget patterns where statically visible.
- The boundary check is explicitly scoped; it does not claim universal proof of no I/O.

- [ ] **Step 1: Write RED boundary tests with synthetic bad module**

Create temporary Python source `import requests` and verify scanner returns `BOUNDARY_FORBIDDEN_IMPORT`. Verify normal stdlib `json`, `dataclasses`, `enum`, `re`, `datetime` pass.

- [ ] **Step 2: Run RED, implement scanner, run GREEN**

Run: `python -m unittest tests.test_boundaries -v`

- [ ] **Step 3: Add security docs**

State: no credentials, retrieved/user content is data not instructions, no automatic file crawling, no hidden chain-of-thought artifact storage, security reports must not include live personal case data unnecessarily.

- [ ] **Step 4: Commit**

```bash
git add tests/test_boundaries.py scripts/validate_repo.py SECURITY.md SECURITY.en.md
git commit -m "security: enforce transport-free P0 boundary"
```

---

## Task 14: Methodology, freshness, bilingual documentation and public truthfulness

**Files:**
- Create: `README.md`, `README.en.md`
- Create: `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`
- Create: `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`
- Create: `docs/METHODOLOGY.md`, `docs/METHODOLOGY.en.md`
- Create: `docs/PRIVACY.md`
- Create: `docs/RISK_REGISTER.md`
- Create: `docs/GLOSSARY.md`, `docs/GLOSSARY.en.md`
- Create: `plugins/mind-detective/references/sources.md`
- Create: `scripts/bilingual_docs.py`
- Create: `scripts/check_reference_freshness.py`
- Create: `tests/test_bilingual_docs.py`
- Create: `tests/test_reference_freshness.py`
- Modify: `scripts/validate_repo.py`

**Interfaces:**
- Key RU/EN pairs must contain reciprocal language links.
- Changelog parity is implemented in Task 15 when changelogs exist.
- Controlled reference marker format is exactly `Verified: YYYY-MM-DD` and `Review-Class: scientific|safety|api`.
- Cadence days: scientific `365`, safety `180`, api `90`.
- PR validation treats age as hard-fail only for changed controlled files; missing/malformed/future marker always fails. Scheduled strict mode checks all controlled files.

- [ ] **Step 1: Write RED tests for bilingual pairs and freshness behavior**

Test missing English mirror fails; changed stale scientific reference fails; unchanged stale reference is warning/non-failure in normal mode; future date fails; strict mode fails stale controlled source.

- [ ] **Step 2: Run RED**

Run:

```bash
python -m unittest tests.test_bilingual_docs -v
python -m unittest tests.test_reference_freshness -v
```

- [ ] **Step 3: Implement docs and truthful methodology posture**

README must open with direct product boundary: MIND Detective does not know where the item is; it structures recall/search and preserves uncertainty. Methodology docs classify Cognitive Interview principles as transferred methodology for this product, misinformation literature as rationale for non-leading guard design, event-boundary research as task-dependent, and search theory as rationale for effort allocation—not household calibrated probabilities.

Do not claim validated lost-item recovery effect size.

- [ ] **Step 4: Implement bilingual/freshness validators and run GREEN**

Run:

```bash
python -m unittest tests.test_bilingual_docs -v
python -m unittest tests.test_reference_freshness -v
python scripts/validate_repo.py
```

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md docs plugins/mind-detective/references/sources.md scripts/bilingual_docs.py scripts/check_reference_freshness.py scripts/validate_repo.py tests/test_bilingual_docs.py tests/test_reference_freshness.py
git commit -m "docs: add truthful bilingual methodology contracts"
```

---

## Task 15: Changelogs, contribution docs and release governance

**Files:**
- Create: `CHANGELOG.md`, `CHANGELOG.en.md`
- Create: `plugins/mind-detective/CHANGELOG.md`, `plugins/mind-detective/CHANGELOG.en.md`
- Create: `CONTRIBUTING.md`
- Create: `LICENSE`
- Create: `plugins/mind-detective/THIRD_PARTY_NOTICES.md`
- Create: `docs/RELEASE_POLICY.md`, `docs/RELEASE_POLICY.en.md`
- Create: `.github/releases/release.json`
- Create: `.github/releases/0.1.0.md`
- Create: `scripts/release_manifest.py`
- Create: `tests/test_release_contract.py`
- Modify: `scripts/bilingual_docs.py`
- Modify: `scripts/validate_repo.py`

**Interfaces:**
- `load_release_manifest(path: Path, root: Path) -> dict` validates schema/version/tag/notes/plugin list.
- Repository `release.json` target:

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

- Release validator cross-checks plugin version SSOT and canonical tag exactly.

- [ ] **Step 1: Write RED tests**

Reject repository tag/version mismatch, plugin manifest version mismatch, noncanonical plugin tag, missing notes file, duplicate plugin entry. Test RU/EN changelog release-marker parity for `0.1.0`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_release_contract -v`

- [ ] **Step 3: Implement release manifest validator and release docs**

Release policy must separate repository SemVer from plugin SemVer, state that `P0/P1/...` are milestones only, and prohibit retarget/delete/rewrite of published release history.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_release_contract -v
python -m unittest tests.test_bilingual_docs -v
python scripts/validate_repo.py
```

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md CHANGELOG.en.md plugins/mind-detective/CHANGELOG.md plugins/mind-detective/CHANGELOG.en.md CONTRIBUTING.md LICENSE plugins/mind-detective/THIRD_PARTY_NOTICES.md docs/RELEASE_POLICY.md docs/RELEASE_POLICY.en.md .github/releases scripts/release_manifest.py scripts/bilingual_docs.py scripts/validate_repo.py tests/test_release_contract.py
git commit -m "release: stage declarative 0.1.0 contracts"
```

---

## Task 16: GitHub CI, scheduled freshness and supply-chain pinning

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/reference-freshness.yml`
- Create: `.github/dependabot.yml`
- Create: `.github/pull_request_template.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- CI matrix runs Python `3.10` and `3.13` for repository validation/tests.
- Third-party action `uses:` references are immutable 40-hex SHAs; comments may record human-readable major version.
- CI runs repository validators, root tests, plugin tests, `ruff`, and `mypy`.
- gitleaks runs as a separate job/action pinned to immutable SHA.

- [ ] **Step 1: Write RED test that rejects mutable Action refs**

Test every active workflow `uses:` line against `@[0-9a-f]{40}` except local `./` actions. Include a synthetic `actions/checkout@v5` fixture that must fail with `WORKFLOW_MUTABLE_ACTION_REF`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_repository_contracts -v`

- [ ] **Step 3: Add CI using full-SHA pins**

Mirror the reference repository's minimal proven pattern: checkout with `fetch-depth: 0`; setup-python; compute changed files; `python scripts/validate_repo.py`; root `unittest`; plugin `unittest`; `ruff check`; `mypy` for plugin scripts and repository scripts. Do not add path-aware multi-plugin complexity because this repository has one P0 plugin (YAGNI).

- [ ] **Step 4: Add weekly strict freshness workflow and Dependabot**

Scheduled freshness runs `python scripts/check_reference_freshness.py --strict`. Dependabot monitors GitHub Actions weekly; generated update PRs still must preserve full-SHA pinning after review.

- [ ] **Step 5: Run local GREEN checks**

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python scripts/validate_repo.py
ruff check .
mypy scripts plugins/mind-detective/scripts
```

- [ ] **Step 6: Commit**

```bash
git add .github tests/test_repository_contracts.py
git commit -m "ci: add pinned validation and freshness workflows"
```

---

## Task 17: Single hardened publisher contract

**Files:**
- Create: `.github/workflows/publish-current-release.yml`
- Modify: `tests/test_release_contract.py`
- Modify: `docs/RELEASE_POLICY.md`, `docs/RELEASE_POLICY.en.md` if exact workflow details require clarification.

**Interfaces:**
- Only one active workflow filename matches release publication intent: `publish-current-release.yml`.
- Publisher reads `.github/releases/release.json`; it does not infer plugin release entries from changed files.
- Initial publication requires current successful CI target to still equal live `main` exact SHA; stale initial run is verified no-op/failure-safe.
- Remote tag absence probe is fail-closed: probe/auth/transport error is not interpreted as absent.
- Conflicting standalone tag, wrong target SHA, mutable published release conflict or ambiguous recovery is hard failure.
- Rollback applies only in mutable publication window; immutable release is never deleted by rollback.

- [ ] **Step 1: Add RED structural tests before workflow exists**

Test exactly one publisher workflow, manifest path literal present, `github.sha`/live-main exact check vocabulary present, canonical plugin tag sourced from manifest/validator, and no second `publish-*release*.yml` file.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_release_contract -v`

- [ ] **Step 3: Implement publisher by adapting the current repository-native Yandex publisher pattern, not inventing a new state machine**

Preserve repository-native semantics: declarative manifest, exact-main gate, exact tag-SHA verification, idempotent recovery, fail-closed tag absence, immutable release check, rollback disarmed immediately after immutability is confirmed. Do not copy historical publisher variants or create reusable release frameworks.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_release_contract -v
python scripts/validate_repo.py
```

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/publish-current-release.yml tests/test_release_contract.py docs/RELEASE_POLICY.md docs/RELEASE_POLICY.en.md
git commit -m "release: add single hardened publisher"
```

---

## Task 18: Final P0 verification, review evidence and release-readiness gate

**Files:**
- Modify only files required to fix verified defects found by final checks.
- Create a review artifact under `docs/reviews/` only when an actual review has occurred; filename includes date and reviewer/source.

**Interfaces:**
- Final local verification command set is fixed below.
- No tag/release publication occurs in this task. Publication is a separate human-authorized post-merge action after exact-main CI.

- [ ] **Step 1: Run the complete deterministic test suite**

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python scripts/validate_repo.py
ruff check .
mypy scripts plugins/mind-detective/scripts
```

Expected: all PASS, validator exit 0, Ruff/mypy exit 0.

- [ ] **Step 2: Run explicit scope scans**

```bash
grep -R "memory-detective" . --exclude-dir=.git && exit 1 || true
grep -R "\.agents-plugin" . --exclude-dir=.git && exit 1 || true
grep -R -E "(73%|scientifically.*most likely|validated.*lost-item)" README.md README.en.md docs plugins/mind-detective && exit 1 || true
find plugins/mind-detective -type f -name '*.py' -print
```

Expected: no deprecated namespace/path or forbidden overclaim; Python files limited to intended helpers/tests.

- [ ] **Step 3: Verify release/version surfaces**

Confirm exact values:

```text
repository manifest version/tag: 0.1.0 / 0.1.0
plugin SSOT: 0.1.0
plugin tag: mind-detective-v0.1.0
one publisher workflow only
```

Run: `python scripts/release_manifest.py --check .github/releases/release.json` (provide this CLI in Task 15).

- [ ] **Step 4: Verify PR exact-head CI after push**

After commits are pushed, record the exact PR head SHA and inspect the GitHub Actions run for that SHA. Do not say “CI passed” unless every required job on that exact SHA is successful.

- [ ] **Step 5: Run independent/semantic review when available**

Review focus: unsupported scientific claims, guard bypass semantics, evidence-class contamination, generic-host overclaim, search-weight pseudo-probability, red-flag routing, release/publisher state safety. If independent review is unavailable, state that limitation explicitly; do not fabricate clean review evidence.

- [ ] **Step 6: Fix only verified findings under TDD**

Each executable fix starts with a failing regression test and gets its own commit. Documentation-only semantic corrections get a focused commit and corresponding validator/eval update when enforcement vocabulary changes.

- [ ] **Step 7: Final implementation commit only if needed**

Example only when there are final verified fixes:

```bash
git add <verified-fix-files>
git commit -m "fix: close 0.1.0 release review findings"
```

- [ ] **Step 8: Human gate**

Do not merge or publish automatically. Present exact head SHA, CI run evidence, review evidence/limitations, release manifest contents and proposed merge/release sequence to the human maintainer.

---

## Post-merge release sequence (not implementation work)

After explicit human authorization:

1. Merge implementation PR with expected exact head SHA.
2. Resolve new exact `main` SHA.
3. Wait for/check post-merge CI on that exact `main` SHA.
4. Re-confirm `.github/releases/release.json` is the intended release set.
5. Human authorizes publication of repository `0.1.0` + plugin `mind-detective-v0.1.0`.
6. Run/allow the single `publish-current-release.yml` publisher.
7. Verify repository tag `0.1.0` and plugin tag `mind-detective-v0.1.0` both target the intended exact release SHA according to the release-set contract.
8. Verify GitHub Release immutability/state before declaring publication complete.
9. Never retarget an existing published tag; any correction becomes a new SemVer release.

---

## Plan self-review result

### Spec coverage

- P0 scope and YAGNI boundary: Tasks 1, 9, 10.
- Evidence/non-promotion: Task 2.
- Guard boundary and generic-host truthfulness: Tasks 3, 9, 11.
- Timeline and event-boundary discipline: Task 4.
- Uncalibrated search allocation/no-zero rule: Task 5.
- Competing hypotheses/no blame: Task 6.
- Safety/fallback-first: Task 7.
- Six artifact contracts: Tasks 2, 4, 5, 6, 7, 8.
- Stable requirements/ADRs/SDD-TDD: Task 10.
- Eval v2: Task 11.
- Exact contract traceability: Task 12.
- Transport-free boundary/privacy/security: Tasks 13, 14.
- Bilingual docs/methodology/freshness: Task 14.
- Versioning/release manifest/changelog parity: Task 15.
- Pinned CI/supply chain: Task 16.
- One hardened publisher/immutable history: Task 17.
- Exact-head verification and truthful review evidence: Task 18.

### Placeholder scan

No `TBD`, `TODO`, “implement later”, “add appropriate validation”, or unnamed “write tests” steps are permitted. Deferred product capabilities are explicitly out of P0 scope rather than placeholders.

### Type/interface consistency

- Evidence enum and `Statement` are introduced in Task 2 and consumed by Timeline Task 4.
- `ConversationStage`/`GuardResult` are introduced in Task 3 and referenced by skills/evals in Tasks 9/11.
- Timeline artifact is produced before Zones consumes supported timeline context.
- Zone `UNCALIBRATED` semantics and operational miss-factor interface are fixed in Task 5 and reused by docs/evals.
- `RiskSignal`/`RouteDecision` are introduced in Task 7 before router skills/evals consume them.
- `validate_repository` begins in Task 1 and is incrementally extended by later repository-contract tasks without changing its public signature.
- `contract_controls.py` begins with eval validation in Task 11 and extends to matrix validation in Task 12.
- `release_manifest.py` is introduced before publisher Task 17 and is the publisher's canonical manifest interpreter.

### Scope correction discovered during planning

The approved design tree contained `.agents-plugin/plugin.json`; the current reference repository uses plugin-local `.codex-plugin/plugin.json`. This plan treats that as a mechanical spec correction in Task 1 and explicitly tests that the deprecated/incorrect `.agents-plugin` path does not exist. No other approved architecture decision is changed.