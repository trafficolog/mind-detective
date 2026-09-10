# MIND Detective 0.2.0 Web/PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `0.2.0` mobile-first Web/PWA vertical slice over the released Python Case Controller while preserving one deterministic domain implementation, local case ownership, checklist/AI shell equivalence, and exact release governance.

**Architecture:** Nuxt 4 is a static mobile-first PWA that stores canonical Case v2 payloads in IndexedDB and never performs domain reduction. A stateless FastAPI adapter receives the current Case plus typed commands, executes the existing Python core, and returns the complete updated Case. Checklist and AI arms share one shell; the only intended experimental difference is the server-side next-proposal engine.

**Tech Stack:** Python 3.10/3.13; FastAPI 0.141.1; Pydantic 2.13.5; Uvicorn 0.52.1; HTTPX 0.28.1; OpenAI Python SDK 3.8.0; Node.js 24.21.0 LTS; pnpm 12.3.4; Nuxt 4.5.2; TypeScript; Vitest 5.0.0; Playwright 1.63.0; `@vite-pwa/nuxt` 1.1.1; IndexedDB; existing stdlib-first plugin runtime.

**Spec:** `docs/superpowers/specs/2026-09-10-mind-detective-web-pwa-0.2.0-design.md`

**UX reference:** `docs/prototypes/2026-09-10-mind-detective-ui-prototype-review.md`

## Global Constraints

- Release target is repository `0.2.0` and plugin `mind-detective 0.2.0`.
- Existing immutable `0.1.0` tags/releases must never be retargeted or edited.
- `plugins/mind-detective/scripts/` remains Python-standard-library-only and transport-free.
- `Case` + `CaseController` remain the only domain source of truth.
- No TypeScript Case reducer, optimistic domain mutation, Bayesian/POD model, numerical location probability, hidden belief weight, or cross-case learning.
- Canonical Web persistence is IndexedDB; no server-side case database, account system, cloud sync, Redis, or Postgres.
- Checklist and assistant arms use one shell, one navigation model, one interaction journal, one input structure, one next-action card, and the same pending/error behavior.
- Experimental arm selection is deployment/test configuration, not a user choice on the first-case screen.
- LLM output is structured proposal data only; it cannot directly set lifecycle, search completion, found outcome, mode labels, timestamps, user confirmation, or UI safety copy.
- Assistant mode may send only the proposal context required for the current request to the configured model provider; privacy copy must distinguish transient model processing from local persistence and must not claim that assistant data never leaves the device.
- OpenAI is the single live provider implementation in `0.2.0`; model name is required through `MIND_DETECTIVE_OPENAI_MODEL`, API key through `OPENAI_API_KEY`, and no provider secret enters Nuxt.
- Reconstruction/search/system provenance is immutable per journal entry and survives reload.
- `case/v1` imports migrate deterministically to `case/v2` with `current_mode=unselected`; migration never invents historical journal entries.
- One-tap `Проверил` records neutral `reported_check`; inaccessible parts are orthogonal to check method.
- State-mutating commands are sequential, retry the same command id/entity ids/timestamps, and mutate canonical local Case only after a validated server response.
- Service worker caches shell/static assets only; API responses, Case JSON, user text, model traffic, command queue payloads, and evaluation exports are excluded.
- RU and EN product/safety copy parity is a CI contract.
- The user-supplied HTML prototype is a visual/scenario reference, not production logic; its engine picker, differing B/C dock, and optimistic demo mutation must not be copied.
- CI retains exact PR-head checkout, Python 3.10/3.13 verification, full-SHA GitHub Actions pins, strict Mypy, Ruff, secret scan, and exact-main release gates.

---

## File Structure

### Domain core changes

- `plugins/mind-detective/scripts/journal.py` — interaction mode and immutable journal-entry types.
- `plugins/mind-detective/scripts/feedback.py` — categorical next-action feedback.
- `plugins/mind-detective/scripts/migrations.py` — deterministic Case v1 → v2 migration.
- `plugins/mind-detective/scripts/case.py` — Case v2 aggregate fields.
- `plugins/mind-detective/scripts/search_log.py` — `reported_check` and check refinement.
- `plugins/mind-detective/scripts/controller.py` — controller-owned journal/mode/feedback/refinement transitions.
- `plugins/mind-detective/scripts/schemas.py` — Case v2 validation contract.
- `plugins/mind-detective/scripts/store.py` — v1/v2 loading and v2 serialization.

### API application

- `apps/api/pyproject.toml` — web-adapter dependencies only.
- `apps/api/mind_detective_api/contracts.py` — Pydantic request/response models.
- `apps/api/mind_detective_api/core_bridge.py` — import boundary to existing plugin core.
- `apps/api/mind_detective_api/commands.py` — typed stateless command execution.
- `apps/api/mind_detective_api/checklist.py` — deterministic proposal engine.
- `apps/api/mind_detective_api/openai_provider.py` — single OpenAI structured-proposal implementation.
- `apps/api/mind_detective_api/proposals.py` — common proposal validation, guard and fallback pipeline.
- `apps/api/mind_detective_api/app.py` — four FastAPI endpoints.
- `apps/api/mind_detective_api/privacy_log.py` — metadata-only application logging helpers.

### Web application

- `package.json`, `pnpm-workspace.yaml`, `.node-version` — pinned JavaScript workspace.
- `apps/web/package.json`, `apps/web/nuxt.config.ts` — Nuxt/PWA build.
- `apps/web/app.vue`, `apps/web/pages/index.vue`, `apps/web/pages/cases/[id].vue` — create/list/active routes.
- `apps/web/components/case/*` — shared shell components.
- `apps/web/components/input/InteractionDock.vue` — identical input placement in both research arms.
- `apps/web/composables/useCaseRepository.ts` — local Case persistence API.
- `apps/web/composables/useCommandQueue.ts` — transport-only sequential queue.
- `apps/web/composables/useCaseApi.ts` — typed API client.
- `apps/web/composables/useExperimentalArm.ts` — immutable build/test arm config.
- `apps/web/lib/case/derived.ts` — read-only counters/annotations derived from Case.
- `apps/web/lib/storage/indexeddb.ts` — IndexedDB implementation.
- `apps/web/lib/storage/exportImport.ts` — local JSON export/import.
- `apps/web/lib/eval/log.ts` — privacy-preserving local evaluation events.
- `apps/web/lib/i18n/{ru,en}.ts` — reviewed copy maps.
- `apps/web/assets/css/{tokens,app}.css` — prototype-derived visual system.
- `apps/web/tests/unit/*` — Vitest pure/unit contracts.
- `apps/web/tests/e2e/*` — Playwright browser workflows and accessibility/state tests.

### Repository contracts

- `docs/REQUIREMENTS.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json` — Web requirements and exact selectors.
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`, `docs/PRIVACY.md`, `docs/PRODUCT_EVALUATION.md` — Web/API/privacy/research documentation.
- `docs/adr/008-web-pwa-domain-boundary.md` — no client reducer/stateless API decision.
- `docs/adr/009-web-local-persistence.md` — IndexedDB/persist/export decision.
- `docs/adr/010-web-experiment-shell.md` — one-shell B/C research invariant.
- `docs/adr/011-web-model-data-boundary.md` — transient assistant-provider processing boundary.
- `.github/workflows/ci.yml` — Python + Web + API matrix.
- `.github/releases/0.2.0.md`, `.github/releases/release.json` — declared `0.2.0` release set.

---

### Task 1: Pin the Web/API workspace and extend repository boundaries

**Files:**
- Create: `.node-version`
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `apps/web/package.json`
- Create: `apps/api/pyproject.toml`
- Modify: `tests/test_boundaries.py`
- Modify: `scripts/validate_repo.py`

**Interfaces:**
- Produces JavaScript workspace `apps/web` under Node `24.21.0` and pnpm `12.3.4`.
- Produces Python API package `mind_detective_api` with dependencies outside plugin core.
- Repository validator must still reject web/API dependencies imported from `plugins/mind-detective/scripts/`.

- [ ] **Step 1: Write failing repository-boundary tests**

```python
def test_web_workspace_is_pinned_and_plugin_core_stays_dependency_free(self):
    root = Path(__file__).resolve().parents[1]
    package = json.loads((root / "package.json").read_text())
    self.assertEqual(package["packageManager"], "pnpm@12.3.4")
    self.assertEqual((root / ".node-version").read_text().strip(), "24.21.0")
    api_pyproject = (root / "apps/api/pyproject.toml").read_text()
    self.assertIn('fastapi==0.141.1', api_pyproject)
    self.assertIn('openai==3.8.0', api_pyproject)
    self.assertNotIn("fastapi", (root / "pyproject.toml").read_text())
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_boundaries.BoundaryTests.test_web_workspace_is_pinned_and_plugin_core_stays_dependency_free -v`

Expected: FAIL because workspace/API files do not exist.

- [ ] **Step 3: Add the pinned workspace**

Root `package.json` must contain:

```json
{
  "name": "mind-detective-workspace",
  "private": true,
  "packageManager": "pnpm@12.3.4",
  "engines": {"node": "24.21.0"},
  "scripts": {
    "web:test": "pnpm --dir apps/web test",
    "web:build": "pnpm --dir apps/web build",
    "web:e2e": "pnpm --dir apps/web e2e"
  }
}
```

`apps/api/pyproject.toml` runtime pins:

```toml
[project]
name = "mind-detective-api"
version = "0.2.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi==0.141.1",
  "pydantic==2.13.5",
  "uvicorn==0.52.1",
  "httpx==0.28.1",
  "openai==3.8.0",
]
```

`apps/web/package.json` pins Nuxt `4.5.2`, `@vite-pwa/nuxt` `1.1.1`, Vitest `5.0.0`, and `@playwright/test` `1.63.0`.

- [ ] **Step 4: Run GREEN and repository validator**

Run: `python -m unittest tests.test_boundaries -v && python scripts/validate_repo.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .node-version package.json pnpm-workspace.yaml apps/web/package.json apps/api/pyproject.toml tests/test_boundaries.py scripts/validate_repo.py
git commit -m "build: add web and api workspace contracts"
```

---

### Task 2: Introduce canonical Case v2 mode, journal and action feedback

**Files:**
- Create: `plugins/mind-detective/scripts/journal.py`
- Create: `plugins/mind-detective/scripts/feedback.py`
- Modify: `plugins/mind-detective/scripts/case.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Test: `plugins/mind-detective/tests/test_case_v2.py`

**Interfaces:**
- `InteractionMode`: `unselected | reconstruction | search`.
- `JournalMode`: `reconstruction | search | system`.
- `JournalAuthor`: `user | assistant | system`.
- `JournalEntry(id, author, mode, entry_type, text, created_at, statement_ids, search_check_ids)`.
- `ActionFeedbackReason`: `already_checked | impossible_now | irrelevant | unsafe_or_uncomfortable | other`.
- `ActionFeedback(id, candidate_id, reason, recorded_at)`.
- `Case.schema` becomes `mind-detective-case/v2` for newly created cases.

- [ ] **Step 1: Write RED tests**

```python
def test_new_case_is_v2_with_unselected_mode_and_empty_journal(self):
    case = CaseController().create_case("c1", "ключи", "2026-09-10T07:00:00Z")
    self.assertEqual(case.schema, "mind-detective-case/v2")
    self.assertEqual(case.current_mode, InteractionMode.UNSELECTED)
    self.assertEqual(case.interaction_journal, ())
    self.assertEqual(case.action_feedback, ())
```

Also test that `set_mode`, `append_journal_entry`, and `record_action_feedback` reject terminal cases through `MD_CASE_TERMINAL`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest plugins.mind-detective.tests.test_case_v2 -v`

Expected: FAIL because Case v2 types do not exist.

- [ ] **Step 3: Implement minimal immutable domain types and controller transitions**

Controller signatures:

```python
def set_mode(self, case: Case, mode: InteractionMode, now: str) -> Case: ...
def append_journal_entry(self, case: Case, entry: JournalEntry, now: str) -> Case: ...
def record_action_feedback(self, case: Case, feedback: ActionFeedback, now: str) -> Case: ...
```

`record_action_feedback` must preserve categorical history and must not create a score/weight.

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest plugins.mind-detective.tests.test_case_v2 -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/journal.py plugins/mind-detective/scripts/feedback.py plugins/mind-detective/scripts/case.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/tests/test_case_v2.py
git commit -m "feat: add case v2 interaction state"
```

---

### Task 3: Add deterministic v1 → v2 migration and v2 serialization

**Files:**
- Create: `plugins/mind-detective/scripts/migrations.py`
- Modify: `plugins/mind-detective/scripts/schemas.py`
- Modify: `plugins/mind-detective/scripts/store.py`
- Modify: `plugins/mind-detective/schemas/mind-detective-case-v1.schema.json`
- Create: `plugins/mind-detective/schemas/mind-detective-case-v2.schema.json`
- Test: `plugins/mind-detective/tests/test_migrations.py`
- Modify: `plugins/mind-detective/tests/test_store.py`

**Interfaces:**
- `migrate_case_payload(data: dict[str, object]) -> dict[str, object]`.
- v1 migration sets `schema="mind-detective-case/v2"`, `current_mode="unselected"`, `interaction_journal=[]`, and `action_feedback=[]`.
- v1 migration preserves all existing statements/timeline/search checks/candidates/constraints/outcome byte-semantically after parsing; it does not fabricate journal history.
- `case_from_dict()` accepts v1 or v2 and returns Case v2.
- `case_to_dict()` emits v2 only.

- [ ] **Step 1: Write failing migration test using a complete v1 fixture**

```python
def test_v1_migration_never_infers_historical_mode(self):
    migrated = migrate_case_payload(load_fixture("case-v1-active.json"))
    self.assertEqual(migrated["current_mode"], "unselected")
    self.assertEqual(migrated["interaction_journal"], [])
    self.assertEqual(migrated["action_feedback"], [])
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest plugins.mind-detective.tests.test_migrations -v`

Expected: FAIL because migration module is missing.

- [ ] **Step 3: Implement explicit schema-version dispatch**

Do not mutate the caller's dictionary. Use a copied payload and reject unknown/future schema with `MD_STORE_SCHEMA_VERSION`.

- [ ] **Step 4: Run GREEN plus store regression suite**

Run: `python -m unittest plugins.mind-detective.tests.test_migrations plugins.mind-detective.tests.test_store -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/migrations.py plugins/mind-detective/scripts/schemas.py plugins/mind-detective/scripts/store.py plugins/mind-detective/schemas plugins/mind-detective/tests/test_migrations.py plugins/mind-detective/tests/test_store.py
git commit -m "feat: migrate case v1 payloads to v2"
```

---

### Task 4: Add neutral reported checks and explicit quality refinement

**Files:**
- Modify: `plugins/mind-detective/scripts/search_log.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Test: `plugins/mind-detective/tests/test_search_log.py`
- Test: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- `SearchMethod.REPORTED_CHECK = "reported_check"`.
- Existing `INACCESSIBLE` remains deserializable for v1 compatibility but is not produced by Web commands.
- `refine_search_check_method(checks, check_id, method) -> tuple[SearchCheck, ...]` replaces only the named check while preserving id/timestamps/result/based_on/notes/inaccessible parts.
- `CaseController.refine_search_check(case, check_id, method, inaccessible_parts, now) -> Case`.

- [ ] **Step 1: Write RED tests**

Test one-tap neutral check and refinement preserving check identity.

```python
def test_refinement_preserves_original_check_identity_and_time(self):
    refined = refine_search_check_method((self.reported,), "check-1", SearchMethod.EMPTY_AND_CHECK)
    self.assertEqual(refined[0].id, "check-1")
    self.assertEqual(refined[0].started_at, self.reported.started_at)
    self.assertEqual(refined[0].method, SearchMethod.EMPTY_AND_CHECK)
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest plugins.mind-detective.tests.test_search_log plugins.mind-detective.tests.test_controller -v`

Expected: FAIL on missing enum/method.

- [ ] **Step 3: Implement neutral method and refinement**

Reject refinement to `INACCESSIBLE` with `MD_SEARCH_METHOD_INVALID`; inaccessible portions are supplied separately.

- [ ] **Step 4: Run GREEN**

Run the same two modules; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/search_log.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/tests/test_search_log.py plugins/mind-detective/tests/test_controller.py
git commit -m "feat: support neutral web search checks"
```

---

### Task 5: Define stateless API contracts and core bridge

**Files:**
- Create: `apps/api/mind_detective_api/__init__.py`
- Create: `apps/api/mind_detective_api/contracts.py`
- Create: `apps/api/mind_detective_api/core_bridge.py`
- Create: `apps/api/mind_detective_api/app.py`
- Test: `apps/api/tests/test_contracts.py`

**Interfaces:**

Pydantic models:

```python
class CaseCreateRequest(BaseModel):
    case_id: str
    item_label: str
    now: str

class CaseValidateRequest(BaseModel):
    case: dict[str, object]

class CaseResponse(BaseModel):
    case: dict[str, object]
```

Endpoints implemented in this task:
- `POST /api/v1/case/create`
- `POST /api/v1/case/validate`

`core_bridge.py` exposes `create_case_payload(...)` and `validate_or_migrate_case_payload(...)` by importing the existing plugin runtime; it must not copy domain rules.

- [ ] **Step 1: Write failing API contract tests**

Use `fastapi.testclient.TestClient` and assert create returns Case v2 with no journal history and validate migrates a v1 fixture.

- [ ] **Step 2: Run RED**

Run from repo root with plugin root on `PYTHONPATH`:

`PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -p 'test_contracts.py' -v`

Expected: FAIL because API modules are absent.

- [ ] **Step 3: Implement the two endpoints**

Map domain `StoreError`/`CaseError` codes to HTTP 422 with body `{"code": <machine-code>, "message": <safe-message>}`. Do not log request bodies.

- [ ] **Step 4: Run GREEN**

Run the same command; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api apps/api/tests/test_contracts.py
git commit -m "feat: add stateless case api contracts"
```

---

### Task 6: Implement typed sequential command execution on the server

**Files:**
- Create: `apps/api/mind_detective_api/commands.py`
- Modify: `apps/api/mind_detective_api/contracts.py`
- Modify: `apps/api/mind_detective_api/app.py`
- Test: `apps/api/tests/test_commands.py`

**Interfaces:**

```python
class CommandEnvelope(BaseModel):
    command_id: str
    expected_updated_at: str
    command_type: Literal[
        "set_mode", "add_statement", "record_search_check", "refine_search_check",
        "reject_next_action", "pause", "resume", "close_found", "close_unresolved"
    ]
    now: str
    payload: dict[str, object]

class CaseCommandRequest(BaseModel):
    case: dict[str, object]
    command: CommandEnvelope
```

`execute_command(case_payload, envelope) -> dict[str, object]` must first require `case.updated_at == expected_updated_at`; mismatch returns `MD_WEB_STALE_COMMAND`.

- [ ] **Step 1: Write RED tests**

Cover:
- retrying the same command with the same input Case produces byte-equivalent output;
- stale `expected_updated_at` fails closed;
- `record_search_check` creates `reported_check` when no method is supplied;
- `reject_next_action` appends categorical ActionFeedback;
- no command accepts a probability field.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest apps.api.tests.test_commands -v`

Expected: FAIL.

- [ ] **Step 3: Implement command dispatch without server state**

All entity IDs and timestamps that affect output must come from the command payload/envelope so a retry is deterministic. Never generate a second id/time during retry.

- [ ] **Step 4: Run GREEN**

Run the same module; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/commands.py apps/api/mind_detective_api/contracts.py apps/api/mind_detective_api/app.py apps/api/tests/test_commands.py
git commit -m "feat: execute deterministic web commands"
```

---

### Task 7: Add deterministic checklist proposals and explicit empty-planner state

**Files:**
- Create: `apps/api/mind_detective_api/checklist.py`
- Create: `apps/api/mind_detective_api/proposals.py`
- Modify: `apps/api/mind_detective_api/contracts.py`
- Modify: `apps/api/mind_detective_api/app.py`
- Test: `apps/api/tests/test_checklist_proposals.py`

**Interfaces:**

```python
class Proposal(BaseModel):
    kind: Literal["next_action", "clarification", "need_more_information", "fallback"]
    candidate_id: str | None = None
    target: str | None = None
    copy_key: str
    rationale_codes: list[str] = []
    related_statement_ids: list[str] = []

class ProposalRequest(BaseModel):
    case: dict[str, object]
    mode: Literal["reconstruction", "search"]
    locale: Literal["ru", "en"]
    experimental_arm: Literal["checklist", "assistant"]
```

Checklist engine rules use the existing planner/case state. If no safe candidate exists, return `need_more_information` with reviewed `copy_key`; do not invent a location.

- [ ] **Step 1: Write RED tests**

Assert empty candidates never produce `target`, and an existing `case.next_action` is rendered as structured proposal without new probability metadata.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest apps.api.tests.test_checklist_proposals -v`

Expected: FAIL.

- [ ] **Step 3: Implement checklist proposal engine and `POST /api/v1/proposal/next` for checklist arm**

`copy_key` values are identifiers such as `next_action.check_target`, `empty.clarify_last_supported_interaction`, and `empty.resolve_partial_check`; no arbitrary final prose is returned.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/checklist.py apps/api/mind_detective_api/proposals.py apps/api/mind_detective_api/contracts.py apps/api/mind_detective_api/app.py apps/api/tests/test_checklist_proposals.py
git commit -m "feat: add deterministic checklist proposals"
```

---

### Task 8: Add the single OpenAI structured-proposal provider and guard fallback

**Files:**
- Create: `apps/api/mind_detective_api/openai_provider.py`
- Create: `apps/api/mind_detective_api/privacy_log.py`
- Modify: `apps/api/mind_detective_api/proposals.py`
- Test: `apps/api/tests/test_assistant_proposals.py`

**Interfaces:**

```python
class OpenAIProposalClient:
    async def propose(self, case: dict[str, object], mode: str) -> Proposal: ...
```

Configuration:
- `OPENAI_API_KEY` required only when assistant engine is invoked.
- `MIND_DETECTIVE_OPENAI_MODEL` required only when assistant engine is invoked.
- Responses API uses strict JSON Schema matching the `Proposal` contract.

- [ ] **Step 1: Write RED tests with a fake OpenAI client**

Cover:
- assistant proposal is structured, not display prose;
- reconstruction proposal that injects a new location is blocked;
- percentage/location-probability claim is blocked;
- blocked proposal creates a `system` journal event with a machine reason code and returns deterministic fallback;
- raw rejected proposal text never enters the Case or privacy log.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest apps.api.tests.test_assistant_proposals -v`

Expected: FAIL.

- [ ] **Step 3: Implement provider and guard pipeline**

The OpenAI request contains only the current typed Case data required to choose/clarify the next proposal. `privacy_log.py` may log event name, request id, arm, outcome code, latency bucket and model identifier; it must not log item label, user text, target text, full Case JSON, or raw model output.

- [ ] **Step 4: Run GREEN**

Expected PASS without a live API key because tests inject the fake client.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/openai_provider.py apps/api/mind_detective_api/privacy_log.py apps/api/mind_detective_api/proposals.py apps/api/tests/test_assistant_proposals.py
git commit -m "feat: add guarded assistant proposal engine"
```

---

### Task 9: Bootstrap Nuxt and enforce a read-only Case view model

**Files:**
- Create: `apps/web/nuxt.config.ts`
- Create: `apps/web/app.vue`
- Create: `apps/web/lib/api/contracts.ts`
- Create: `apps/web/lib/case/derived.ts`
- Create: `apps/web/composables/useExperimentalArm.ts`
- Create: `apps/web/tests/unit/derived.spec.ts`
- Create: `apps/web/vitest.config.ts`

**Interfaces:**
- `CaseV2` TypeScript interface mirrors serialized Python fields only.
- `deriveProgress(case) -> { checked: number; remaining: number; inaccessible: number }` reads state only.
- `derivePriorCheckAnnotation(case, candidateId) -> PriorCheckAnnotation | null` reads history only.
- No exported function accepts `CaseV2` and returns mutated `CaseV2`.
- `useExperimentalArm()` reads `runtimeConfig.public.experimentalArm` and returns readonly `checklist | assistant`.

- [ ] **Step 1: Write RED unit tests**

```ts
it('derives progress without changing the case', () => {
  const before = structuredClone(caseFixture)
  expect(deriveProgress(caseFixture)).toEqual({ checked: 4, remaining: 3, inaccessible: 1 })
  expect(caseFixture).toEqual(before)
})
```

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web vitest run tests/unit/derived.spec.ts`

Expected: FAIL because modules are missing.

- [ ] **Step 3: Implement Nuxt base and read-only derivations**

Set `ssr: false`. Default experiment arm is configured through `NUXT_PUBLIC_MIND_DETECTIVE_ARM`; do not render an end-user engine picker.

- [ ] **Step 4: Run GREEN and build**

Run: `pnpm --dir apps/web vitest run && pnpm --dir apps/web build`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/nuxt.config.ts apps/web/app.vue apps/web/lib apps/web/composables/useExperimentalArm.ts apps/web/tests/unit apps/web/vitest.config.ts
git commit -m "feat: bootstrap read-only web case model"
```

---

### Task 10: Implement IndexedDB repository, persistence capability and local export/import

**Files:**
- Create: `apps/web/lib/storage/indexeddb.ts`
- Create: `apps/web/lib/storage/exportImport.ts`
- Create: `apps/web/composables/useCaseRepository.ts`
- Create: `apps/web/tests/e2e/storage.spec.ts`

**Interfaces:**

```ts
interface CaseRepository {
  list(): Promise<CaseV2[]>
  get(caseId: string): Promise<CaseV2 | null>
  put(caseValue: CaseV2): Promise<void>
  delete(caseId: string): Promise<void>
}

async function requestPersistentStorage(): Promise<'granted' | 'denied' | 'unsupported'>
async function exportCase(caseValue: CaseV2): Promise<Blob>
async function importCase(file: File, validate: (payload: unknown) => Promise<CaseV2>): Promise<CaseV2>
```

IndexedDB database: `mind-detective`, object store `cases`, key path `case_id`.

- [ ] **Step 1: Write RED Playwright storage tests**

Test create/put/reload/list, delete isolation, valid export, v1 import sent through `/case/validate`, invalid/future schema rejection, and storage capability copy for denied/unsupported states.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web playwright test tests/e2e/storage.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement storage without localStorage Case copies**

Only non-sensitive UI preferences/capability state may use localStorage. Case payloads and evaluation payloads must remain outside Cache Storage.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/storage apps/web/composables/useCaseRepository.ts apps/web/tests/e2e/storage.spec.ts
git commit -m "feat: add local case persistence and export"
```

---

### Task 11: Implement the transport-only command queue with no optimistic reducer

**Files:**
- Create: `apps/web/composables/useCaseApi.ts`
- Create: `apps/web/composables/useCommandQueue.ts`
- Create: `apps/web/tests/unit/commandQueue.spec.ts`

**Interfaces:**

```ts
interface PendingCommand {
  command_id: string
  case_id: string
  command_type: CommandType
  expected_updated_at: string
  now: string
  payload: Record<string, unknown>
  status: 'pending' | 'retrying' | 'failed'
  attempt_count: number
}

function enqueue(caseValue: CaseV2, command: PendingCommand): Promise<CaseV2>
function retry(commandId: string): Promise<CaseV2>
```

- [ ] **Step 1: Write RED tests with a fake API transport**

Assert:
- Case ref remains unchanged while request is pending;
- two commands for one case are sent sequentially;
- retry sends byte-equivalent command envelope;
- failed validation does not mutate Case;
- successful response replaces local canonical Case and only then persists it.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web vitest run tests/unit/commandQueue.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement queue and API client**

Do not expose a `reduceCase`, `applyCommandLocally`, or equivalent domain mutation helper.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/composables/useCaseApi.ts apps/web/composables/useCommandQueue.ts apps/web/tests/unit/commandQueue.spec.ts
git commit -m "feat: add pending web command queue"
```

---

### Task 12: Build first-case creation and local case-list/resume screens

**Files:**
- Create: `apps/web/pages/index.vue`
- Create: `apps/web/components/case/CaseList.vue`
- Create: `apps/web/components/case/CreateCaseForm.vue`
- Create: `apps/web/tests/e2e/create-resume.spec.ts`

**Interfaces:**
- Empty/new flow has exactly one user-input field `item_label` and one primary `Start search` action.
- Engine arm is absent from production creation UI.
- Case list sorts active/paused cases by `updated_at` descending and shows item label, lifecycle, derived compact summary and local update time.

- [ ] **Step 1: Write RED E2E tests**

Assert no engine picker exists; create calls `/case/create`, persists returned Case only after response, then navigates to `/cases/<id>`; paused case resumes exact stored Case without strengthening statements/checks.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web playwright test tests/e2e/create-resume.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement screens using prototype density/visual direction**

Keep storage warning and export/install education contextual after meaningful engagement, not as a pre-creation gate.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/pages/index.vue apps/web/components/case/CaseList.vue apps/web/components/case/CreateCaseForm.vue apps/web/tests/e2e/create-resume.spec.ts
git commit -m "feat: add web case creation and resume"
```

---

### Task 13: Build the one-shell active case UI and immutable journal mode presentation

**Files:**
- Create: `apps/web/pages/cases/[id].vue`
- Create: `apps/web/components/case/CaseShell.vue`
- Create: `apps/web/components/case/ModeBanner.vue`
- Create: `apps/web/components/case/NextActionCard.vue`
- Create: `apps/web/components/case/ProgressStrip.vue`
- Create: `apps/web/components/case/InteractionJournal.vue`
- Create: `apps/web/components/input/InteractionDock.vue`
- Create: `apps/web/assets/css/tokens.css`
- Create: `apps/web/assets/css/app.css`
- Test: `apps/web/tests/e2e/shell-equivalence.spec.ts`

**Interfaces:**
- `CaseShell` receives `caseValue`, `experimentalArm`, `pendingState`, and emitted structured actions.
- Checklist and assistant arms render the same component tree for shell, journal and input dock.
- Journal entry mode is rendered from persisted `entry.mode`; current screen mode never rewrites historical tags.
- Mode representation includes text label + SVG icon + distinct type treatment; color is optional redundancy.

- [ ] **Step 1: Write RED equivalence tests**

Render identical Case fixture under both arms and assert identical landmark/component test IDs. Allow only proposal-source metadata to differ; do not hide the journal or replace the dock.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web playwright test tests/e2e/shell-equivalence.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement the shared shell using prototype tokens**

Use the supplied prototype's 4px spacing scale, 44px minimum targets, safe-area handling, system font stack, glass/readability floors, reduced-motion and increased-contrast fallbacks. Do not include the external control rail in production.

- [ ] **Step 4: Run GREEN at 320px, 405px and desktop viewport widths**

Expected: PASS with no horizontal overflow.

- [ ] **Step 5: Commit**

```bash
git add apps/web/pages/cases apps/web/components apps/web/assets/css apps/web/tests/e2e/shell-equivalence.spec.ts
git commit -m "feat: build unified mobile case shell"
```

---

### Task 14: Wire one-tap checks, inaccessible state and delayed quality clarification

**Files:**
- Create: `apps/web/components/case/CheckQualityDialog.vue`
- Modify: `apps/web/components/case/NextActionCard.vue`
- Modify: `apps/web/pages/cases/[id].vue`
- Test: `apps/web/tests/e2e/check-flow.spec.ts`

**Interfaces:**
- `Проверил` enqueues `record_search_check` with `reported_check` and never opens quality dialog merely because the first check completed.
- Quality dialog appears only when returned proposal/controller state marks prior quality as decision-relevant.
- `inaccessible_parts` is a separate checkbox/list input, never a method radio value.

- [ ] **Step 1: Write RED tests**

Cover pending spinner/`aria-busy`, no counter change before API response, returned Case updates progress, delayed quality clarification, and refinement preserving original check id.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web playwright test tests/e2e/check-flow.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement flow through command queue only**

The progress strip always derives values from the returned/persisted Case; never increment a local `done` variable as the prototype demo does.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/CheckQualityDialog.vue apps/web/components/case/NextActionCard.vue apps/web/pages/cases/[id].vue apps/web/tests/e2e/check-flow.spec.ts
git commit -m "feat: add one-tap web check flow"
```

---

### Task 15: Add empty-planner, visible guard block and next-action rejection UX

**Files:**
- Create: `apps/web/components/case/SystemJournalEvent.vue`
- Create: `apps/web/components/case/ActionRejectDialog.vue`
- Modify: `apps/web/components/case/NextActionCard.vue`
- Modify: `apps/web/pages/cases/[id].vue`
- Test: `apps/web/tests/e2e/proposal-states.spec.ts`

**Interfaces:**
- `need_more_information` proposal renders a neutral non-location card.
- `ai_guard_blocked` returns a system journal event using reviewed copy key plus deterministic fallback; rejected raw proposal is never rendered.
- `Not suitable` enqueues `reject_next_action` with one categorical reason.
- Planner must not immediately return the rejected candidate unless new evidence or an explicit reset changes the Case.

- [ ] **Step 1: Write RED tests for all three states**

Also assert `Delete case` is absent from the primary next-action button group.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web playwright test tests/e2e/proposal-states.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement reviewed state components**

Machine guard codes may appear only in a details/diagnostic affordance, not as primary UX copy.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/SystemJournalEvent.vue apps/web/components/case/ActionRejectDialog.vue apps/web/components/case/NextActionCard.vue apps/web/pages/cases/[id].vue apps/web/tests/e2e/proposal-states.spec.ts
git commit -m "feat: surface proposal safety states"
```

---

### Task 16: Implement found/unresolved closing and privacy-preserving evaluation log

**Files:**
- Create: `apps/web/components/case/CloseCaseDialog.vue`
- Create: `apps/web/components/case/CaseOutcome.vue`
- Create: `apps/web/lib/eval/log.ts`
- Create: `apps/web/tests/unit/evalLog.spec.ts`
- Create: `apps/web/tests/e2e/close-flow.spec.ts`

**Interfaces:**
- `found_context`: `current_suggested_action | elsewhere_unplanned | after_previous_check | unknown`.
- Local evaluation events include `case_started`, `next_action_shown`, `next_action_started`, `next_action_rejected`, `check_started`, `check_finished`, `duplicate_check_detected`, `check_quality_clarified`, `ai_guard_blocked`, `pending_command_started`, `pending_command_retried`, `pending_command_failed`, `pause`, `resume`, `found`, `case_closed_unresolved`, `case_abandoned`, `found_context_recorded`.
- Event payload allowlist excludes item label, location/target text, journal text, statement text, raw model text and complete Case payload.

- [ ] **Step 1: Write RED privacy tests**

```ts
it('rejects sensitive evaluation keys', () => {
  expect(() => appendEvalEvent('found', { item_label: 'ключи' } as never)).toThrow('MD_WEB_EVAL_SENSITIVE_FIELD')
})
```

E2E must distinguish found-on-current-action from found-elsewhere/unplanned and unresolved close.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web vitest run tests/unit/evalLog.spec.ts && pnpm --dir apps/web playwright test tests/e2e/close-flow.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement close flow and local JSON/CSV evaluation export**

Evaluation export is explicit user action and never background-uploaded.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/CloseCaseDialog.vue apps/web/components/case/CaseOutcome.vue apps/web/lib/eval apps/web/tests/unit/evalLog.spec.ts apps/web/tests/e2e/close-flow.spec.ts
git commit -m "feat: add outcome and local evaluation flow"
```

---

### Task 17: Add PWA shell caching, offline behavior, install education and storage-loss copy

**Files:**
- Modify: `apps/web/nuxt.config.ts`
- Create: `apps/web/public/manifest.webmanifest`
- Create: `apps/web/components/storage/StorageNotice.vue`
- Create: `apps/web/components/storage/InstallEducation.vue`
- Test: `apps/web/tests/e2e/pwa-storage.spec.ts`

**Interfaces:**
- Service worker precaches shell/static assets only.
- Runtime caching has no route for `/api/`.
- No background sync plugin is enabled.
- Offline mutation stays queued/failed visibly and canonical Case remains unchanged.
- Storage copy says cases are local, cloud backup is absent, site-data clearing can delete cases, persistence is not a backup, export is the recovery path.

- [ ] **Step 1: Write RED PWA tests**

Inspect generated service worker/Workbox manifest and assert API patterns, Case JSON routes and background sync are absent. Simulate offline check action and assert no progress change before reconnection/retry.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web build && pnpm --dir apps/web playwright test tests/e2e/pwa-storage.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Configure `@vite-pwa/nuxt` 1.1.1 and storage UX**

Call `navigator.storage.persisted()` then `persist()` after first meaningful case interaction. Show capability state honestly.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/nuxt.config.ts apps/web/public apps/web/components/storage apps/web/tests/e2e/pwa-storage.spec.ts
git commit -m "feat: add privacy-safe pwa behavior"
```

---

### Task 18: Lock RU/EN copy, accessibility and the prototype scenario matrix

**Files:**
- Create: `apps/web/lib/i18n/ru.ts`
- Create: `apps/web/lib/i18n/en.ts`
- Create: `apps/web/lib/i18n/index.ts`
- Create: `apps/web/tests/unit/i18n.spec.ts`
- Create: `apps/web/tests/e2e/accessibility.spec.ts`
- Create: `apps/web/tests/e2e/scenario-matrix.spec.ts`

**Interfaces:**
- Locale keys cover mode labels, guard/safety states, empty planner, storage warnings, pending/retry/error states, create/resume/close, check quality, export/import and assistant-provider privacy disclosure.
- Both locale maps have identical key sets.
- No keyboard autofocus on active-case load.
- Dialogs trap focus, close on Escape, restore trigger focus and mark background inert.
- Minimum interactive hit area is 44px.

- [ ] **Step 1: Write RED parity/accessibility/scenario tests**

Scenario matrix must cover the 20 states in `docs/prototypes/2026-09-10-mind-detective-ui-prototype-review.md`, including both arms, both phases, pending/retry, guard block, partial/inaccessible, quality clarification, planner empty, rejection, pause, both found contexts, unresolved, persistence states, v1 migration, invalid import, light/dark/reduced-motion/increased-contrast.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web vitest run tests/unit/i18n.spec.ts && pnpm --dir apps/web playwright test tests/e2e/accessibility.spec.ts tests/e2e/scenario-matrix.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement complete reviewed RU/EN resources and accessibility fixes**

The scenario controls are test fixtures/developer tooling only; no production engine picker/control rail is introduced.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/i18n apps/web/tests/unit/i18n.spec.ts apps/web/tests/e2e/accessibility.spec.ts apps/web/tests/e2e/scenario-matrix.spec.ts
git commit -m "test: lock web copy and scenario accessibility"
```

---

### Task 19: Trace requirements, extend CI/docs, prepare and verify the 0.2.0 release set

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `docs/EVAL_TOKEN_REGISTRY.json`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `docs/PRIVACY.md`
- Modify: `docs/PRODUCT_EVALUATION.md`
- Create: `docs/adr/008-web-pwa-domain-boundary.md`
- Create: `docs/adr/009-web-local-persistence.md`
- Create: `docs/adr/010-web-experiment-shell.md`
- Create: `docs/adr/011-web-model-data-boundary.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Modify: `.github/workflows/ci.yml`
- Create: `.github/releases/0.2.0.md`
- Modify: `.github/releases/release.json`
- Modify: plugin descriptors/marketplace version fields for `0.2.0`
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_release_contract.py`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- Activate all `MD-WEB-REQ-*` IDs from the spec with exact test selectors.
- Add explicit privacy requirement that assistant arm transiently sends minimal proposal context to the configured model provider while local persistence remains browser-only.
- CI jobs:
  - Python 3.10/3.13 existing core/repo/API tests;
  - pinned Node 24.21.0 + pnpm 12.3.4 install with frozen lockfile;
  - Web Vitest;
  - Nuxt build;
  - Playwright Chromium + WebKit mobile-critical suite;
  - existing Ruff, strict Mypy, freshness, boundaries, bilingual contracts, secret scan and release checks.
- Release manifest declares exactly repository tag `0.2.0` and plugin tag `mind-detective-v0.2.0`.
- Existing `publish-current-release.yml` remains the only active publisher and keeps manual full-40-hex `target_sha`, exact-main CI, detached-worktree, immutable release and tag-SHA checks.

- [ ] **Step 1: Write RED contract/release tests first**

Add selectors for every `MD-WEB-REQ-*` requirement and assert manifest/descriptors still show `0.1.0` before release preparation, causing the new version-parity test to fail.

- [ ] **Step 2: Run RED**

Run:

```bash
python -m unittest tests.test_contract_matrix tests.test_release_contract tests.test_repository_contracts -v
```

Expected: FAIL on missing Web requirements/version `0.2.0`.

- [ ] **Step 3: Update requirements, docs, CI, descriptors and declarative release manifest**

Release JSON must normalize to exactly:

```json
{
  "schema_version": 1,
  "repository": {
    "version": "0.2.0",
    "tag": "0.2.0",
    "title": "MIND Detective repository 0.2.0",
    "notes_file": ".github/releases/0.2.0.md"
  },
  "plugins": [
    {
      "plugin": "mind-detective",
      "version": "0.2.0",
      "tag": "mind-detective-v0.2.0",
      "title": "MIND Detective plugin 0.2.0",
      "notes_file": ".github/releases/0.2.0.md"
    }
  ]
}
```

Do not edit `.github/releases/0.1.0.md`, tag `0.1.0`, or tag `mind-detective-v0.1.0`.

- [ ] **Step 4: Run the complete local verification set**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py --strict
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
ruff check .
mypy --strict scripts tests plugins/mind-detective/scripts plugins/mind-detective/tests apps/api/mind_detective_api apps/api/tests
pnpm install --frozen-lockfile
pnpm --dir apps/web vitest run
pnpm --dir apps/web build
pnpm --dir apps/web playwright test
```

Expected: all PASS.

- [ ] **Step 5: Commit release-ready implementation**

```bash
git add docs README.md README.en.md CHANGELOG.md CHANGELOG.en.md .github apps plugins tests scripts package.json pnpm-workspace.yaml pnpm-lock.yaml .node-version
git commit -m "release: prepare MIND Detective 0.2.0"
```

- [ ] **Step 6: Integration and publication gates**

1. Push implementation branch and open a separate implementation PR against the approved documentation/design base or `main`, depending on whether the docs PR has already merged.
2. Require exact PR-head CI success.
3. Obtain explicit human authorization before merge.
4. Merge with expected-head protection.
5. Require exact post-merge `main` push CI success.
6. Obtain separate explicit human authorization for publication at the full 40-hex `main` SHA.
7. Run only `publish-current-release.yml` with that SHA.
8. Verify both `0.2.0` and `mind-detective-v0.2.0` are non-draft, immutable, and their tag refs resolve to the exact approved release SHA.

---

## Plan Self-Review

### Spec coverage

- One shell / one navigation / same input structure: Tasks 9, 13, 18.
- Message-level mode provenance and app-owned mode banner: Tasks 2, 3, 13.
- No client reducer / pending sequential retry: Tasks 6, 11, 14.
- One-tap neutral check / delayed refinement / orthogonal inaccessible state: Tasks 4, 14.
- Persistent progress and prior-check context: Tasks 9, 13, 14.
- First create / local cases / resume: Tasks 10, 12.
- Empty planner / visible guard block / action rejection: Tasks 7, 8, 15.
- Found-context and unresolved close: Task 16.
- IndexedDB, `persist()`, install education, export/import: Tasks 10, 17.
- Service-worker privacy boundary: Task 17.
- RU/EN copy, accessibility and scenario harness: Task 18.
- Checklist-vs-AI research validity and local evaluation metrics: Tasks 7, 8, 13, 16, 18.
- Existing Python core reuse and stdlib boundary: Tasks 1, 5, 19.
- Assistant-provider transient data boundary: Tasks 8, 18, 19.
- Exact release governance and immutable `0.1.0`: Task 19.

### Placeholder scan

No `TBD`, `TODO`, deferred implementation placeholders, undefined function names, or unspecified test steps are present. Features explicitly outside `0.2.0` remain outside the plan rather than appearing as future-work steps.

### Type consistency

- Python Case v2 types originate in Tasks 2–4 and are serialized/migrated in Task 3 before API use.
- API contracts in Tasks 5–8 return the same full Case v2 payload consumed by the Web interfaces introduced in Task 9.
- Pending command fields are identical between server `CommandEnvelope` in Task 6 and client `PendingCommand` in Task 11.
- Proposal kinds defined in Task 7 are the same states rendered in Tasks 13 and 15.
- `found_context` values in Task 16 match the canonical spec.

## Execution Handoff

Implementation must occur on a separate production branch/PR; the documentation/design branch remains the reviewed specification/plan artifact. At execution time create an isolated worktree using `superpowers:using-git-worktrees`, then execute this plan with `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`. No implementation merge or release is authorized by approval of this plan.
