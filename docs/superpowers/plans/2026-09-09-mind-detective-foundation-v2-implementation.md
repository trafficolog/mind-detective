# MIND Detective Foundation v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build repository `0.1.0` and independently installable plugin `mind-detective-v0.1.0` as a transport-free systematic lost-item search assistant centered on a deterministic Case Controller, uncertainty-preserving reconstruction, a durable physical search log, one-next-action planning, explicit case-local save/resume/delete, and five production skills.

**Architecture:** Repository-level contracts, validators, exact traceability, eval vocabulary, CI and release governance remain modeled after `trafficolog/yandex-ai-plugins-skills`. Runtime behavior stays plugin-local and Python-standard-library-first. The deterministic Case Controller owns state transitions and planning rules; the LLM is limited to dialogue, explanation, neutral reconstruction, and explicitly labeled search suggestions.

**Tech Stack:** Python 3.10 and 3.13; Python standard library for plugin runtime; `unittest`; `ruff`; `mypy`; JSON/Markdown contracts; GitHub Actions with full-SHA pins; gitleaks-compatible repository secret scan; no runtime SDK dependency.

**Spec:** `docs/superpowers/specs/2026-09-09-mind-detective-foundation-v2-design.md`

## Global Constraints

- Canonical namespace is `mind-detective`; `memory-search` is descriptive language only.
- Repository release target is `0.1.0`; plugin tag is `mind-detective-v0.1.0`.
- One plugin exposes exactly five production skills: `mind-detective`, `mind-detective-reconstruct`, `mind-detective-plan`, `mind-detective-resume`, `mind-detective-close`.
- Plugin-local Codex descriptor is `.codex-plugin/plugin.json`; `.agents-plugin/plugin.json` is forbidden.
- Runtime under `plugins/mind-detective/scripts/` is Python standard-library-only.
- P0 has no Web/PWA, voice, messenger, external API connector, ModelAdapter, cloud persistence, Bayesian model, POD, numerical location probability, hidden belief weight, ACH truth score, or cross-case learning.
- `Statement.source` and `Statement.statement_type` are independent fields.
- Assistant-originated `recollection`, `habit`, and `observation` are invalid.
- Vividness, confidence wording, sensory detail, lighting/color and emotional intensity never mechanically promote truth status.
- Reconstruction mode may not introduce unsupported concrete locations as memory-elicitation prompts.
- Search-planning mode may introduce concrete locations only as explicit `search_suggestion` proposals.
- Search history records target, method, result and inaccessible parts; repeated checks remain visible and are never converted into independent probability evidence.
- Planner returns one next action using explicit categorical rule order and no numerical total score.
- Case-local persistence occurs only through explicit save/pause or retain operations; delete removes the local case artifact.
- Saved cases are resumable but are never silently aggregated into user priors or future-case recommendations.
- High-risk forgotten actions such as medication-dose uncertainty do not enter ordinary lost-item reconstruction/search reasoning.
- Close records outcome and user-authored possible causes only; it never diagnoses a forgetting mechanism.
- Generic Claude Code/Codex hosts do not provide a repository-controlled pre-send interceptor; helper tests prove submitted-candidate behavior only.
- High-risk requirements use stable IDs and exact Python test selectors.
- Key public docs are RU-primary with English mirrors.
- One repository SemVer line, independent plugin SemVer, one release manifest and one active publisher govern publication.
- Published tags/releases are immutable.

---

## Locked file map

### Plugin runtime
- `plugins/mind-detective/scripts/statements.py` — statement enums, validation and serialization.
- `plugins/mind-detective/scripts/timeline.py` — timeline events, unknowns and contradictions.
- `plugins/mind-detective/scripts/search_log.py` — physical SearchCheck history and duplicate recognition.
- `plugins/mind-detective/scripts/planner.py` — CandidateCheck and deterministic one-next-action selection.
- `plugins/mind-detective/scripts/guard.py` — reconstruction/search-planning mode rules.
- `plugins/mind-detective/scripts/safety.py` — high-risk forgotten-action routing boundary.
- `plugins/mind-detective/scripts/case.py` — aggregate Case model and lifecycle.
- `plugins/mind-detective/scripts/controller.py` — Case Controller operations.
- `plugins/mind-detective/scripts/store.py` — explicit local save/load/delete.
- `plugins/mind-detective/scripts/schemas.py` — schema names and lightweight artifact validation.

### Plugin skills
- `plugins/mind-detective/skills/mind-detective/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-reconstruct/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-plan/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-resume/SKILL.md`
- `plugins/mind-detective/skills/mind-detective-close/SKILL.md`

### Schemas
- `docs/schemas/mind-detective-case-v1.schema.json`
- `docs/schemas/mind-detective-handoff-v1.schema.json`
- `docs/schemas/mind-detective-outcome-v1.schema.json`

### Repository governance
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/mind-detective/.claude-plugin/plugin.json`
- `plugins/mind-detective/.codex-plugin/plugin.json`
- `docs/REQUIREMENTS.md`
- `docs/CONTRACT_MATRIX.json`
- `docs/EVAL_TOKEN_REGISTRY.json`
- `plugins/mind-detective/evals/scenarios.json`
- `scripts/validate_repo.py`
- `scripts/contract_controls.py`
- `scripts/bilingual_docs.py`
- `scripts/check_reference_freshness.py`
- `scripts/release_manifest.py`
- `.github/workflows/ci.yml`
- `.github/workflows/reference-freshness.yml`
- `.github/workflows/publish-current-release.yml`
- `.github/releases/release.json`
- `.github/releases/0.1.0.md`

---

## Task 1: Bootstrap installability and repository validator

**Files:**
- Create: `pyproject.toml`
- Create: `.claude-plugin/marketplace.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/mind-detective/.claude-plugin/plugin.json`
- Create: `plugins/mind-detective/.codex-plugin/plugin.json`
- Create: `scripts/validate_repo.py`
- Create: `tests/test_repository_contracts.py`

**Interfaces:**
- Produces `validate_repository(root: Path) -> list[str]`.
- Plugin version SSOT is `plugins/mind-detective/.codex-plugin/plugin.json["version"]`.
- All marketplace/plugin mirrors must equal `0.1.0`.

- [ ] **Step 1: Write failing installability tests**

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryContractTests(unittest.TestCase):
    def test_marketplace_versions_match_codex_descriptor(self):
        codex = json.loads((ROOT / "plugins/mind-detective/.codex-plugin/plugin.json").read_text())
        claude = json.loads((ROOT / "plugins/mind-detective/.claude-plugin/plugin.json").read_text())
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(codex["version"], "0.1.0")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(agents["plugins"][0]["version"], codex["version"])
        self.assertEqual(market["plugins"][0]["version"], codex["version"])

    def test_only_codex_and_claude_plugin_descriptors_exist(self):
        self.assertFalse((ROOT / "plugins/mind-detective/.agents-plugin/plugin.json").exists())
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_repository_contracts -v`

Expected: FAIL because descriptors do not exist.

- [ ] **Step 3: Create descriptors and marketplaces**

Use plugin name `mind-detective`, version `0.1.0`, skills path `./skills/`, display name `MIND Detective`, category `Productivity`. `.agents/plugins/marketplace.json` uses local source `./plugins/mind-detective`, `installation: AVAILABLE`, `authentication: ON_USE`; docs later state that this metadata does not imply credentials or network ownership.

- [ ] **Step 4: Implement minimal validator**

```python
from pathlib import Path
import json

def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        root / ".claude-plugin/marketplace.json",
        root / ".agents/plugins/marketplace.json",
        root / "plugins/mind-detective/.claude-plugin/plugin.json",
        root / "plugins/mind-detective/.codex-plugin/plugin.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"MD_REPO_MISSING:{path.relative_to(root)}")
    forbidden = root / "plugins/mind-detective/.agents-plugin/plugin.json"
    if forbidden.exists():
        errors.append("MD_REPO_FORBIDDEN:.agents-plugin/plugin.json")
    return errors
```

Extend the function in the same task to parse all four JSON files and assert canonical name/version parity.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest tests.test_repository_contracts -v && python scripts/validate_repo.py`

Expected: PASS and exit 0.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .claude-plugin .agents plugins/mind-detective/.claude-plugin plugins/mind-detective/.codex-plugin scripts/validate_repo.py tests/test_repository_contracts.py
git commit -m "build: bootstrap mind-detective v2 contracts"
```

---

## Task 2: Statement model and origin/type invariants

**Files:**
- Create: `plugins/mind-detective/scripts/statements.py`
- Create: `plugins/mind-detective/tests/test_statements.py`

**Interfaces:**
- `StatementSource`: `user`, `file`, `assistant`.
- `StatementType`: `recollection`, `habit`, `observation`, `hypothesis`, `search_suggestion`.
- `Statement` frozen dataclass fields: `id`, `source`, `statement_type`, `original_text`, `recorded_at`, `event_time`, `user_confirmation`, `supporting_evidence_ids`, `limitations`.
- `StatementError.code` is stable.
- `create_statement(...) -> Statement` enforces allowed source/type matrix.

- [ ] **Step 1: Write RED tests**

```python
class StatementTests(unittest.TestCase):
    def test_assistant_cannot_originate_recollection(self):
        with self.assertRaises(StatementError) as ctx:
            create_statement(
                statement_id="s1",
                source=StatementSource.ASSISTANT,
                statement_type=StatementType.RECOLLECTION,
                original_text="Вы положили ключи на стол.",
                recorded_at="2026-09-09T18:00:00Z",
                event_time=None,
                user_confirmation=False,
                supporting_evidence_ids=(),
                limitations=(),
            )
        self.assertEqual(ctx.exception.code, "MD_STMT_ASSISTANT_ORIGIN")

    def test_probability_word_does_not_reclassify_user_statement(self):
        statement = create_statement(
            statement_id="s2",
            source=StatementSource.USER,
            statement_type=StatementType.RECOLLECTION,
            original_text="Наверное, я положил ключи после магазина.",
            recorded_at="2026-09-09T18:01:00Z",
            event_time=None,
            user_confirmation=True,
            supporting_evidence_ids=(),
            limitations=("uncertain wording",),
        )
        self.assertEqual(statement.statement_type, StatementType.RECOLLECTION)
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_statements.py' -v`

- [ ] **Step 3: Implement exact source/type matrix**

```python
ALLOWED_TYPES = {
    StatementSource.USER: frozenset(StatementType),
    StatementSource.FILE: frozenset({StatementType.OBSERVATION}),
    StatementSource.ASSISTANT: frozenset({StatementType.HYPOTHESIS, StatementType.SEARCH_SUGGESTION}),
}
```

Reject invalid pairs with `MD_STMT_ASSISTANT_ORIGIN` for assistant-origin violations and `MD_STMT_SOURCE_TYPE` for all other invalid pairs. Do not inspect vividness, confidence wording, sensory language, lighting or emotional intensity to change `statement_type`.

- [ ] **Step 4: Run GREEN and commit**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_statements.py' -v`

```bash
git add plugins/mind-detective/scripts/statements.py plugins/mind-detective/tests/test_statements.py
git commit -m "feat: add statement provenance contracts"
```

---

## Task 3: Timeline with explicit unknowns and contradictions

**Files:**
- Create: `plugins/mind-detective/scripts/timeline.py`
- Create: `plugins/mind-detective/tests/test_timeline.py`

**Interfaces:**
- `TimelineEvent`: `id`, `label`, `statement_ids`, `event_time`, `time_precision`.
- `Timeline`: `last_supported_interaction_id`, `first_noticed_missing_id`, `events`, `unknown_intervals`, `contradictions`.
- `build_timeline(statements: list[Statement], events: list[TimelineEvent], last_supported_interaction_id: str | None, first_noticed_missing_id: str | None) -> Timeline`.

- [ ] **Step 1: Write RED tests**

Test that `last_supported_interaction_id=None` remains `None`; test that “не помню, выходил ли” is stored as statement text/limitation and never generates an inferred “item stayed inside” event; test explicit timestamp reversal adds `MD_TIME_ORDER_CONTRADICTION` to contradictions.

```python
def test_unknown_last_interaction_remains_unknown(self):
    timeline = build_timeline([], [], None, None)
    self.assertIsNone(timeline.last_supported_interaction_id)
    self.assertEqual(timeline.unknown_intervals, ())
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v`

- [ ] **Step 3: Implement minimal timeline builder**

Only use explicit statement/event timestamps. Preserve unknowns. Contradictions are structured strings/codes and do not auto-resolve one statement in favor of another.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v
git add plugins/mind-detective/scripts/timeline.py plugins/mind-detective/tests/test_timeline.py
git commit -m "feat: preserve uncertainty in case timeline"
```

---

## Task 4: Mode-aware conversational guard

**Files:**
- Create: `plugins/mind-detective/scripts/guard.py`
- Create: `plugins/mind-detective/tests/test_guard.py`
- Create: `plugins/mind-detective/references/guard-rules.md`

**Interfaces:**
- `InteractionMode`: `reconstruction`, `search_planning`.
- `GuardResult`: `allowed`, `codes`, `details`.
- `lint_candidate(text: str, *, mode: InteractionMode, known_locations: set[str]) -> GuardResult`.
- Stable codes: `MD_G_RECON_NEW_LOCATION`, `MD_G_FALSE_MEMORY`, `MD_G_MECHANISM_DIAGNOSIS`, `MD_G_LOCATION_PROBABILITY`, `MD_G_SEARCH_AS_MEMORY`, `MD_G_SUPERFICIAL_PROVES_ABSENCE`.

- [ ] **Step 1: Write RED mode-separation tests**

```python
def test_new_location_blocked_in_reconstruction(self):
    result = lint_candidate("Вы не оставили ключи в машине?", mode=InteractionMode.RECONSTRUCTION, known_locations={"кухня"})
    self.assertFalse(result.allowed)
    self.assertIn("MD_G_RECON_NEW_LOCATION", result.codes)

def test_same_location_allowed_as_search_proposal(self):
    result = lint_candidate("Предлагаю проверить машину.", mode=InteractionMode.SEARCH_PLANNING, known_locations={"кухня"})
    self.assertTrue(result.allowed)

def test_probability_claim_blocked_in_search_mode(self):
    result = lint_candidate("Вероятность 70%, что ключи в машине.", mode=InteractionMode.SEARCH_PLANNING, known_locations={"машина"})
    self.assertIn("MD_G_LOCATION_PROBABILITY", result.codes)
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_guard.py' -v`

- [ ] **Step 3: Implement bounded RU/EN lexical rules**

Use explicit common location/container lexicon and probability/false-memory/mechanism phrases. The reference file must state that helper coverage is conservative and generic hosts may bypass it because the repository does not control a pre-send hook.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_guard.py' -v
git add plugins/mind-detective/scripts/guard.py plugins/mind-detective/tests/test_guard.py plugins/mind-detective/references/guard-rules.md
git commit -m "feat: separate reconstruction and search guards"
```

---

## Task 5: Physical SearchCheck history and duplicate recognition

**Files:**
- Create: `plugins/mind-detective/scripts/search_log.py`
- Create: `plugins/mind-detective/tests/test_search_log.py`

**Interfaces:**
- `SearchMethod`: `glance`, `visual_systematic`, `empty_and_check`, `tactile`, `inaccessible`.
- `SearchResult`: `found`, `not_found`, `partial`, `inaccessible`.
- `SearchCheck`: `id`, `target`, `method`, `started_at`, `completed_at`, `result`, `inaccessible_parts`, `based_on`, `notes`.
- `normalize_target(text: str) -> tuple[str, ...]`.
- `is_duplicate_target(a: str, b: str) -> bool` returns true for equal normalized token sets or when the smaller normalized token set is a subset of the larger and contains at least two content tokens.
- `SearchLog.add(check: SearchCheck) -> tuple[SearchCheck, ...]` retains all repetitions.

- [ ] **Step 1: Write RED tests**

Test that a `glance/not_found` and later `empty_and_check/not_found` remain two distinct entries; test `"Карманы куртки"` and `"карманы вчерашней куртки"` are recognized as duplicate/near-duplicate; test duplicate detection returns metadata but never suppresses the second entry.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_search_log.py' -v`

- [ ] **Step 3: Implement deterministic normalization**

Normalize lowercase, `ё` to `е`, punctuation to spaces, remove RU/EN stop words `в`, `на`, `из`, `the`, `in`, `on`, and preserve all content tokens. No embedding, fuzzy model or probability is used.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_search_log.py' -v
git add plugins/mind-detective/scripts/search_log.py plugins/mind-detective/tests/test_search_log.py
git commit -m "feat: add durable physical search log"
```

---

## Task 6: Candidate checks and one-next-action planner

**Files:**
- Create: `plugins/mind-detective/scripts/planner.py`
- Create: `plugins/mind-detective/tests/test_planner.py`

**Interfaces:**
- Enums: `RouteRelation(direct, indirect, none)`, `CheckState(unchecked, partial, checked)`, `Effort(low, medium, high)`, `Safety(safe, caution, unsafe)`, `UrgencyRelevance(high, normal)`, `CandidateBasis(episode, habit, generic)`.
- `CandidateCheck`: `id`, `target`, categorical fields above, `based_on`, `rationale`.
- `NextAction`: `candidate_id`, `target`, `rationale_codes`.
- `select_next_action(candidates: list[CandidateCheck]) -> NextAction | None`.

- [ ] **Step 1: Write RED precedence tests**

Test unsafe exclusion; direct episode-linked unchecked candidate beats indirect; partial beats checked when route relation is equal; low effort breaks remaining ties; habit beats generic only after episode-linked candidates are exhausted; urgency-high can outrank continued ordinary checking when candidate represents a recovery/fallback action.

```python
def test_unsafe_candidate_is_never_selected(self):
    action = select_next_action([unsafe_candidate(), safe_candidate()])
    self.assertEqual(action.candidate_id, "safe")
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_planner.py' -v`

- [ ] **Step 3: Implement sequential filtering, not a numerical score**

Apply the spec rule order as successive filters. Do not construct or expose a sum, weighted tuple, probability or `belief_weight`. `rationale_codes` records the winning categorical reasons, for example `MD_PLAN_DIRECT_ROUTE`, `MD_PLAN_UNCHECKED`, `MD_PLAN_LOW_EFFORT`.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_planner.py' -v
git add plugins/mind-detective/scripts/planner.py plugins/mind-detective/tests/test_planner.py
git commit -m "feat: select one explicit next search action"
```

---

## Task 7: High-risk forgotten-action safety boundary

**Files:**
- Create: `plugins/mind-detective/scripts/safety.py`
- Create: `plugins/mind-detective/tests/test_safety.py`
- Create: `plugins/mind-detective/references/safety.md`

**Interfaces:**
- `SafetyRoute`: `ordinary_search`, `limit_and_escalate`.
- `SafetyDecision`: `route`, `codes`, `message_key`.
- `classify_request(text: str) -> SafetyDecision`.
- Codes include `MD_SAFE_MEDICATION_ACTION`, `MD_SAFE_HAZARDOUS_ACTION`, `MD_SAFE_SECURITY_ACTION`.

- [ ] **Step 1: Write RED distinction tests**

`"Где упаковка лекарства?"` routes to ordinary search. `"Я уже принял таблетку?"` routes to `limit_and_escalate`. Security-critical forgotten action and hazardous equipment-state examples also exit ordinary reasoning.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_safety.py' -v`

- [ ] **Step 3: Implement conservative phrase rules**

Rules identify action uncertainty, not merely presence of words such as medicine or key. The reference must prohibit guessing whether the action occurred or recommending repetition solely from uncertain memory.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_safety.py' -v
git add plugins/mind-detective/scripts/safety.py plugins/mind-detective/tests/test_safety.py plugins/mind-detective/references/safety.md
git commit -m "feat: route high-risk forgotten actions safely"
```

---

## Task 8: Canonical Case aggregate and Case Controller lifecycle

**Files:**
- Create: `plugins/mind-detective/scripts/case.py`
- Create: `plugins/mind-detective/scripts/controller.py`
- Create: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- `CaseLifecycle`: `active`, `paused`, `closed_found`, `closed_unresolved`, `deleted`.
- `Case`: `schema`, `case_id`, `item_label`, `created_at`, `updated_at`, `lifecycle`, `statements`, `timeline`, `search_checks`, `candidates`, `next_action`, `constraints`, `outcome`.
- `CaseController.create_case(case_id: str, item_label: str, now: str) -> Case`.
- `add_statement`, `record_search_check`, `replace_candidates`, `refresh_next_action`, `pause`, `resume`, `close_found`, `close_unresolved` operate on one Case and update `updated_at`.

- [ ] **Step 1: Write RED lifecycle tests**

Create → active; pause → paused; resume → active; close_found → closed_found; closed cases reject further search mutation with `MD_CASE_TERMINAL`; deleted is terminal.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v`

- [ ] **Step 3: Implement minimal aggregate controller**

The controller delegates provenance validation to `statements.py`, search history to `search_log.py`, planning to `planner.py`, and never duplicates those rules.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v
git add plugins/mind-detective/scripts/case.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/tests/test_controller.py
git commit -m "feat: add canonical case controller"
```

---

## Task 9: Case schema and explicit local persistence

**Files:**
- Create: `plugins/mind-detective/scripts/schemas.py`
- Create: `plugins/mind-detective/scripts/store.py`
- Create: `plugins/mind-detective/tests/test_store.py`
- Create: `docs/schemas/mind-detective-case-v1.schema.json`

**Interfaces:**
- Case schema name is `mind-detective-case/v1`.
- `case_to_dict(case: Case) -> dict[str, object]` and `case_from_dict(data: dict[str, object]) -> Case`.
- `save_case(case: Case, root: Path) -> Path` writes `<root>/.mind-detective/cases/<case-id>/case.json` atomically through a temporary sibling file plus `Path.replace`.
- `load_case(case_id: str, root: Path) -> Case` validates schema before returning.
- `delete_case(case_id: str, root: Path) -> bool` removes the case directory only; it never scans or aggregates sibling cases.

- [ ] **Step 1: Write RED round-trip/privacy tests**

Test save/load exact preservation of statements/search history; test no profile/index file is created; test delete removes only selected case; test unsupported schema returns `MD_STORE_SCHEMA_VERSION`; test artifact contains no field named `chain_of_thought`, `belief_weight`, `probability`, `pod` or `user_profile`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_store.py' -v`

- [ ] **Step 3: Implement serialization and atomic local store**

Use `json.dumps(..., ensure_ascii=False, indent=2, sort_keys=True)` and standard library only. Saving happens only when the caller invokes `save_case`; case creation does not persist automatically.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_store.py' -v
git add plugins/mind-detective/scripts/schemas.py plugins/mind-detective/scripts/store.py plugins/mind-detective/tests/test_store.py docs/schemas/mind-detective-case-v1.schema.json
git commit -m "feat: add explicit resumable case storage"
```

---

## Task 10: Resume/handoff and close/outcome artifacts

**Files:**
- Create: `plugins/mind-detective/scripts/artifacts.py`
- Create: `plugins/mind-detective/tests/test_artifacts.py`
- Create: `docs/schemas/mind-detective-handoff-v1.schema.json`
- Create: `docs/schemas/mind-detective-outcome-v1.schema.json`

**Interfaces:**
- `build_handoff(case: Case) -> dict[str, object]` outputs supported state, timeline unknowns/contradictions, search history with methods, inaccessible parts, next action, constraints.
- `build_outcome(case: Case) -> dict[str, object]` outputs `found | unresolved | abandoned`, user-reported found location, immediately preceding search check id when known, user-authored possible cause, prevention note, retain/delete decision.

- [ ] **Step 1: Write RED artifact tests**

Assert handoff preserves search methods and does not strengthen old statements; assert outcome has no `forgetting_mechanism`; assert user-authored possible cause references a user statement id; assert no private model reasoning field is emitted.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_artifacts.py' -v`

- [ ] **Step 3: Implement concise serializers and schemas**

Handoff is a derived read artifact, not a second source of truth. Outcome is either embedded in Case or exported independently with schema `mind-detective-outcome/v1`.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_artifacts.py' -v
git add plugins/mind-detective/scripts/artifacts.py plugins/mind-detective/tests/test_artifacts.py docs/schemas/mind-detective-handoff-v1.schema.json docs/schemas/mind-detective-outcome-v1.schema.json
git commit -m "feat: add resume handoff and close artifacts"
```

---

## Task 11: Five production skills and end-to-end workflow

**Files:**
- Create the five `SKILL.md` paths locked above.
- Create: `plugins/mind-detective/tests/test_end_to_end.py`
- Create: `plugins/mind-detective/references/reconstruction.md`
- Create: `plugins/mind-detective/references/search-planning.md`
- Create: `plugins/mind-detective/references/resume-close.md`

**Interfaces:**
- Router skill always checks safety before ordinary routing.
- Reconstruct skill uses free account first and guard in reconstruction mode.
- Plan skill records SearchCheck before choosing another action and uses search-planning guard for model-formulated proposals.
- Resume skill only resumes an explicitly supplied/saved case.
- Close skill records outcome and honors retain/delete choice.

- [ ] **Step 1: Write RED repository tests for exact five skills**

Test the plugin exposes exactly the five approved skill directories and no v1 `quickcheck`, `zones`, `hypotheses`, `fallback`, `debrief` skill directories.

- [ ] **Step 2: Add RED end-to-end deterministic scenario**

Create case → add recollection → timeline → add two candidates → select one action → record `glance/not_found` → planner chooses a different/partial unresolved action → pause/save → load/resume → record `found` → close_found → build outcome. Assert no numerical probability field appears anywhere in serialized case.

- [ ] **Step 3: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -v`

- [ ] **Step 4: Write the five skills and references**

Each `SKILL.md` must state inputs, deterministic helper calls, outputs, limitations, and explicit mode transition. No skill may claim memory restoration, mechanism diagnosis, calibrated location likelihood or guaranteed guard interception.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
git add plugins/mind-detective/skills plugins/mind-detective/references plugins/mind-detective/tests/test_end_to_end.py
git commit -m "feat: add five-skill lost-item workflow"
```

---

## Task 12: Stable requirements, exact CONTRACT_MATRIX and adversarial eval v2

**Files:**
- Create: `docs/REQUIREMENTS.md`
- Create: `docs/CONTRACT_MATRIX.json`
- Create: `docs/EVAL_TOKEN_REGISTRY.json`
- Create: `plugins/mind-detective/evals/scenarios.json`
- Create: `scripts/contract_controls.py`
- Create: `tests/test_contract_matrix.py`
- Create: `tests/test_eval_contract.py`

**Interfaces:**
- Formalize all `MD-REQ-*` IDs from v2 spec section 19.
- Every high-risk requirement links to owning SKILL, helper path, exact unittest selector and reference.
- Eval v2 fields: `must_route_to`, `outcome`, `must_mention_tokens`, `must_convey`, `must_not_claim`.

- [ ] **Step 1: Write RED validation tests**

Require exact selector existence by AST; reject unknown token; reject non-approved outcome; reject missing route; reject duplicate requirement ids.

- [ ] **Step 2: Create initial adversarial scenarios**

Include at least: unsupported concrete location during reconstruction; same location as allowed search proposal; “70% chance”; repeated glances treated as proof; medication-dose uncertainty; physical medicine-package search; resume preserving prior history; assistant-originated recollection; mechanism-diagnosis request; unresolved case close; explicit delete; PWA request receiving limitation for `0.1.0`.

- [ ] **Step 3: Run RED then implement validators**

Run: `python -m unittest tests.test_contract_matrix tests.test_eval_contract -v`

Implement JSON/AST validators with standard library only.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_contract_matrix tests.test_eval_contract -v
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json docs/EVAL_TOKEN_REGISTRY.json plugins/mind-detective/evals scripts/contract_controls.py tests/test_contract_matrix.py tests/test_eval_contract.py
git commit -m "test: trace v2 safety contracts and evals"
```

---

## Task 13: Human docs, methodology, privacy, product evaluation and ADRs

**Files:**
- Create/update root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`, `SECURITY.md`, `SECURITY.en.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `LICENSE`.
- Create RU/EN: `docs/ARCHITECTURE`, `GETTING_STARTED`, `METHODOLOGY`, `PLUGIN_STANDARD`, `RELEASE_POLICY`, `GLOSSARY`.
- Create: `docs/PRIVACY.md`, `docs/RISK_REGISTER.md`, `docs/PRODUCT_EVALUATION.md`, `docs/SDD_TDD_WORKFLOW.md`.
- Create ADRs for Case Controller, statement provenance, mode-aware guard, no numerical search model, case-local persistence, five-skill scope, PWA deferment, release governance.
- Create plugin README/CHANGELOG RU/EN and `THIRD_PARTY_NOTICES.md`.
- Create: `scripts/bilingual_docs.py`, `tests/test_bilingual_docs.py`.

**Interfaces:**
- RU is primary public language; reciprocal language links required.
- Product positioning uses “помощник систематического поиска потерянных вещей”.
- Product evaluation defines A ordinary search, B structured checklist/search log, C checklist/search log + conversational AI and metrics from v2 section 20.

- [ ] **Step 1: Write RED bilingual/claim tests**

Test required RU/EN pairs exist; test README does not contain forbidden claims equivalent to “restores memory”, “determines forgetting mechanism”, or calibrated location percentages; test `PRODUCT_EVALUATION.md` includes all three comparison arms and unresolved/abandoned reporting.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_bilingual_docs -v`

- [ ] **Step 3: Write docs and validator**

Methodology must distinguish direct memory-research evidence from product transfer. Privacy must state explicit case-local save/delete and no cross-case indexing. PWA must be described only as `0.2.0` candidate, with no frontend scaffold.

- [ ] **Step 4: Run GREEN and commit**

```bash
python -m unittest tests.test_bilingual_docs -v
git add README.md README.en.md CHANGELOG.md CHANGELOG.en.md SECURITY.md SECURITY.en.md CONTRIBUTING.md AGENTS.md CLAUDE.md LICENSE docs plugins/mind-detective/README.md plugins/mind-detective/README.en.md plugins/mind-detective/CHANGELOG.md plugins/mind-detective/CHANGELOG.en.md plugins/mind-detective/THIRD_PARTY_NOTICES.md scripts/bilingual_docs.py tests/test_bilingual_docs.py
git commit -m "docs: document simplified lost-item search product"
```

---

## Task 14: Static boundaries, freshness and CI

**Files:**
- Create: `tests/test_boundaries.py`
- Create: `scripts/check_reference_freshness.py`
- Create: `tests/test_reference_freshness.py`
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/reference-freshness.yml`
- Create: `.github/dependabot.yml`
- Create: `.github/pull_request_template.md`

**Interfaces:**
- AST denylist blocks imports such as `requests`, `httpx`, `aiohttp`, `boto3`, `google.cloud`, `openai`, messenger SDKs and browser automation from plugin runtime.
- Also fail if P0 runtime contains modules/files named `zones.py`, `ach.py`, `model_adapter.py` or frontend manifests.
- Scientific methodology freshness 365 days; safety guidance 180 days; future external-platform facts 90 days.

- [ ] **Step 1: Write RED boundary/freshness tests**

Inject fixture source strings with forbidden imports and verify exact machine code; verify no production runtime imports network/provider SDKs; verify malformed/future freshness marker fails; verify untouched aging methodology can be scheduled-warning rather than unrelated-PR hard failure.

- [ ] **Step 2: Implement checks**

CI runs Python 3.10 and 3.13, `ruff`, `mypy`, repository validator, all repository/plugin unittests, contract/eval checks, boundary checks, bilingual checks, freshness path-aware checks, secret scan, release-manifest checks. Pin `actions/checkout` and `actions/setup-python` to the immutable full SHAs already used by the current reference repository; any additional third-party Action must also use a 40-hex commit SHA.

- [ ] **Step 3: Run local verification**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
ruff check .
mypy plugins/mind-detective/scripts scripts
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_boundaries.py scripts/check_reference_freshness.py tests/test_reference_freshness.py .github/workflows/ci.yml .github/workflows/reference-freshness.yml .github/dependabot.yml .github/pull_request_template.md
git commit -m "ci: enforce v2 boundaries and quality gates"
```

---

## Task 15: Declarative release path and exact-head release readiness

**Files:**
- Create: `.github/releases/release.json`
- Create: `.github/releases/0.1.0.md`
- Create: `scripts/release_manifest.py`
- Create: `tests/test_release_contract.py`
- Create: `.github/workflows/publish-current-release.yml`
- Update changelogs/version surfaces only if final verification reveals mismatch.

**Interfaces:**
- Repository release: `0.1.0`, tag `0.1.0`.
- Plugin release: `mind-detective-v0.1.0` pointing to the same approved exact main SHA unless the manifest explicitly declares otherwise.
- One active publisher reads `.github/releases/release.json`.
- Publisher refuses stale main, conflicting tag SHA, mutable recovery target, ambiguous existing release state and non-40-hex recovery SHA.

- [ ] **Step 1: Write RED release tests**

Test exact version parity, exactly one active publisher, manifest notes file existence, exact plugin tag format, 40-hex recovery SHA validation, fail-closed conflicting tag state and idempotent same-SHA recovery.

- [ ] **Step 2: Implement manifest/parser and publisher**

Mirror the current repository-native hardened publisher pattern from `trafficolog/yandex-ai-plugins-skills`; do not introduce a new shared publishing framework or second checkout/state machine.

- [ ] **Step 3: Run full verification**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
ruff check .
mypy plugins/mind-detective/scripts scripts
```

Expected: all PASS before pushing final implementation head.

- [ ] **Step 4: Push implementation PR and require exact-head CI**

The implementation PR must target `main`, preserve human merge authorization, and record exact PR head SHA plus all required successful workflow runs. Do not publish or merge merely because local tests pass.

- [ ] **Step 5: Post-merge release gate**

After human-authorized exact-head merge, require CI green on the exact new `main` SHA. Only then may the human-approved release manifest be published. Verify repository tag `0.1.0` and plugin tag `mind-detective-v0.1.0` resolve to the intended exact SHA; never retarget a published tag.

- [ ] **Step 6: Commit release preparation**

```bash
git add .github/releases scripts/release_manifest.py tests/test_release_contract.py .github/workflows/publish-current-release.yml CHANGELOG.md CHANGELOG.en.md plugins/mind-detective/CHANGELOG.md plugins/mind-detective/CHANGELOG.en.md
git commit -m "release: prepare mind-detective 0.1.0"
```

---

## Self-review checklist completed for this plan

- **Spec coverage:** all v2 sections 1–25 map to Tasks 1–15; PWA remains explicitly outside implementation.
- **Domain simplification:** no v1 zones, ACH, Bayesian, POD, belief-weight, forgetting-mechanism or eight-skill decomposition remains.
- **Persistence consistency:** `resume` is backed by explicit case-local `case.json`; no cross-case index/profile is created.
- **Guard consistency:** concrete locations are blocked only as unsupported memory elicitation and allowed as explicit search proposals.
- **Type consistency:** `Statement`, `Timeline`, `SearchCheck`, `CandidateCheck`, `NextAction`, `Case`, `CaseController` and store/artifact interfaces are defined once and consumed by later tasks with the same names.
- **Placeholder scan:** this plan contains no `TBD`, `TODO`, empty implementation marker, placeholder SHA token or deferred-code instruction.
- **Release truthfulness:** green fixture/CI evidence is not described as scientific validation or live-model semantic proof.

## Execution handoff

Implementation must occur in a separate implementation branch/PR. The documentation PR remains architecture evidence and must not receive production code.

Preferred execution mode: **Superpowers subagent-driven development** — one fresh worker per Task 1–15 with task-spec review and code-quality review before advancing.
