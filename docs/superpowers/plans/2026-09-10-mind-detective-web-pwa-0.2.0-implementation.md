# MIND Detective 0.2.0 Web/PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `0.2.0` mobile-first Web/PWA vertical slice over the released Python Case Controller while preserving one deterministic domain implementation, local case ownership, checklist/AI shell equivalence, and exact release governance.

**Architecture:** Nuxt 4 is a static PWA that stores canonical Case v2 payloads in IndexedDB and never performs domain reduction. A stateless FastAPI adapter receives the current Case plus typed commands, executes the existing Python core, and returns the complete updated Case. Checklist and AI arms share one shell; the only intended experimental difference is the server-side next-proposal engine.

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
- OpenAI is the single live provider implementation in `0.2.0`; `MIND_DETECTIVE_OPENAI_MODEL` and `OPENAI_API_KEY` are required only when assistant proposals are invoked; no provider secret enters Nuxt.
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

### Domain core

- `plugins/mind-detective/scripts/journal.py` — interaction mode and immutable journal-entry types.
- `plugins/mind-detective/scripts/feedback.py` — categorical next-action feedback.
- `plugins/mind-detective/scripts/migrations.py` — deterministic Case v1 → v2 migration.
- `plugins/mind-detective/scripts/case.py` — Case v2 aggregate fields.
- `plugins/mind-detective/scripts/search_log.py` — `reported_check` and check refinement.
- `plugins/mind-detective/scripts/controller.py` — controller-owned journal/mode/feedback/refinement transitions.
- `plugins/mind-detective/scripts/schemas.py` — Case v2 validation contract.
- `plugins/mind-detective/scripts/store.py` — v1/v2 loading and v2 serialization.

### API app

- `apps/api/pyproject.toml` — web-adapter dependencies only.
- `apps/api/run.py` — local ASGI runner with explicit plugin-core import path.
- `apps/api/mind_detective_api/contracts.py` — Pydantic request/response models.
- `apps/api/mind_detective_api/core_bridge.py` — import boundary to existing plugin core.
- `apps/api/mind_detective_api/commands.py` — typed stateless command execution.
- `apps/api/mind_detective_api/checklist.py` — deterministic proposal engine.
- `apps/api/mind_detective_api/openai_provider.py` — single OpenAI structured-proposal implementation.
- `apps/api/mind_detective_api/proposals.py` — common proposal validation, guard and fallback pipeline.
- `apps/api/mind_detective_api/app.py` — four FastAPI endpoints.
- `apps/api/mind_detective_api/privacy_log.py` — metadata-only application logging.

### Web app

- `package.json`, `pnpm-workspace.yaml`, `.node-version` — pinned JS workspace.
- `apps/web/package.json`, `apps/web/nuxt.config.ts` — Nuxt/PWA build.
- `apps/web/app.vue`, `apps/web/pages/index.vue`, `apps/web/pages/cases/[id].vue` — production routes.
- `apps/web/components/case/*` — shared case-state shell.
- `apps/web/components/input/InteractionDock.vue` — identical input placement in B/C.
- `apps/web/composables/useCaseRepository.ts` — local Case persistence API.
- `apps/web/composables/useCommandQueue.ts` — transport-only sequential queue.
- `apps/web/composables/useCaseApi.ts` — typed API client.
- `apps/web/composables/useExperimentalArm.ts` — immutable deployment/test arm config.
- `apps/web/lib/case/derived.ts` — read-only counters/annotations.
- `apps/web/lib/storage/indexeddb.ts` — IndexedDB implementation.
- `apps/web/lib/storage/exportImport.ts` — local JSON export/import.
- `apps/web/lib/eval/log.ts` — privacy-preserving local evaluation events.
- `apps/web/lib/i18n/ru.ts`, `apps/web/lib/i18n/en.ts` — reviewed copy maps.
- `apps/web/assets/css/tokens.css`, `apps/web/assets/css/app.css` — prototype-derived visual system.
- `apps/web/tests/unit/*` — Vitest contracts.
- `apps/web/tests/e2e/*` — Playwright browser workflows.

### Repository contracts

- `docs/REQUIREMENTS.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json` — Web requirements and exact selectors.
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`, `docs/PRIVACY.md`, `docs/PRODUCT_EVALUATION.md` — Web/API/privacy/research docs.
- `docs/adr/008-web-pwa-domain-boundary.md` — no client reducer/stateless API.
- `docs/adr/009-web-local-persistence.md` — IndexedDB/persist/export.
- `docs/adr/010-web-experiment-shell.md` — one-shell B/C invariant.
- `docs/adr/011-web-model-data-boundary.md` — transient model-provider processing.
- `.github/workflows/ci.yml` — Python + Web + API verification.
- `.github/releases/0.2.0.md`, `.github/releases/release.json` — declared release set.

---

### Task 1: Pin Web/API workspace and extend repository boundaries

**Files:**
- Create: `.node-version`
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `apps/web/package.json`
- Create: `apps/api/pyproject.toml`
- Modify: `tests/test_boundaries.py`
- Modify: `scripts/validate_repo.py`

**Interfaces:**
- Node `24.21.0`, pnpm `12.3.4`.
- API runtime pins `fastapi==0.141.1`, `pydantic==2.13.5`, `uvicorn==0.52.1`, `httpx==0.28.1`, `openai==3.8.0`.
- Web pins Nuxt `4.5.2`, `@vite-pwa/nuxt` `1.1.1`, Vitest `5.0.0`, Playwright `1.63.0`.
- Existing root Python package remains free of Web/API runtime dependencies.

- [ ] **Step 1: Write failing boundary test**

```python
def test_web_workspace_is_pinned_and_core_stays_dependency_free(self):
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

Run: `python -m unittest discover -s tests -p 'test_boundaries.py' -v`

Expected: FAIL because workspace/API files do not exist.

- [ ] **Step 3: Add pinned manifests and validator rules**

Root `package.json`:

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

`apps/api/pyproject.toml`:

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

- [ ] **Step 4: Run GREEN**

Run: `python -m unittest discover -s tests -p 'test_boundaries.py' -v && python scripts/validate_repo.py`

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
- Create: `plugins/mind-detective/tests/test_case_v2.py`

**Interfaces:**
- `InteractionMode`: `unselected`, `reconstruction`, `search`.
- `JournalMode`: `reconstruction`, `search`, `system`.
- `JournalAuthor`: `user`, `assistant`, `system`.
- `JournalEntry`: `id`, `author`, `mode`, `entry_type`, `text`, `created_at`, `statement_ids`, `search_check_ids`.
- `ActionFeedbackReason`: `already_checked`, `impossible_now`, `irrelevant`, `unsafe_or_uncomfortable`, `other`.
- `ActionFeedback`: `id`, `candidate_id`, `reason`, `recorded_at`.
- `CaseController.set_mode(case, mode, now) -> Case`.
- `CaseController.append_journal_entry(case, entry, now) -> Case`.
- `CaseController.record_action_feedback(case, feedback, now) -> Case`.

- [ ] **Step 1: Write RED test**

```python
def test_new_case_is_v2_with_unselected_mode_and_empty_audit_state(self):
    case = CaseController().create_case("c1", "ключи", "2026-09-10T07:00:00Z")
    self.assertEqual(case.schema, "mind-detective-case/v2")
    self.assertEqual(case.current_mode, InteractionMode.UNSELECTED)
    self.assertEqual(case.interaction_journal, ())
    self.assertEqual(case.action_feedback, ())
```

Add tests that all three new controller mutations reject terminal cases with `MD_CASE_TERMINAL`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_case_v2.py' -v`

Expected: FAIL because Case v2 types are missing.

- [ ] **Step 3: Implement immutable dataclasses/enums and controller transitions**

Every transition returns a new frozen Case via `dataclasses.replace`. `record_action_feedback` stores categorical history only and creates no score.

- [ ] **Step 4: Run GREEN**

Run the same discovery command; expected PASS.

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
- Create: `plugins/mind-detective/schemas/mind-detective-case-v2.schema.json`
- Create: `plugins/mind-detective/tests/fixtures/case-v1-active.json`
- Create: `plugins/mind-detective/tests/test_migrations.py`
- Modify: `plugins/mind-detective/tests/test_store.py`

**Interfaces:**
- `migrate_case_payload(data: dict[str, object]) -> dict[str, object]`.
- v1 → v2 adds exactly `current_mode="unselected"`, `interaction_journal=[]`, `action_feedback=[]`, and changes schema id to `mind-detective-case/v2`.
- Migration does not fabricate historical journal entries or reinterpret evidence.
- `case_from_dict()` accepts v1 or v2 and returns Case v2.
- `case_to_dict()` emits v2 only.

- [ ] **Step 1: Write RED migration test**

```python
def test_v1_migration_never_infers_historical_mode(self):
    source = json.loads((FIXTURES / "case-v1-active.json").read_text())
    migrated = migrate_case_payload(source)
    self.assertEqual(migrated["current_mode"], "unselected")
    self.assertEqual(migrated["interaction_journal"], [])
    self.assertEqual(migrated["action_feedback"], [])
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_migrations.py' -v`

Expected: FAIL because migration module is missing.

- [ ] **Step 3: Implement schema dispatch and store integration**

Copy the input dictionary before migration. Reject unknown/future schemas with `MD_STORE_SCHEMA_VERSION`.

- [ ] **Step 4: Run GREEN plus store regression**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_migrations.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_store.py' -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/migrations.py plugins/mind-detective/scripts/schemas.py plugins/mind-detective/scripts/store.py plugins/mind-detective/schemas plugins/mind-detective/tests/fixtures/case-v1-active.json plugins/mind-detective/tests/test_migrations.py plugins/mind-detective/tests/test_store.py
git commit -m "feat: migrate case v1 payloads to v2"
```

---

### Task 4: Add neutral reported checks and explicit quality refinement

**Files:**
- Modify: `plugins/mind-detective/scripts/search_log.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/tests/test_search_log.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- `SearchMethod.REPORTED_CHECK = "reported_check"`.
- Legacy `INACCESSIBLE` remains readable but Web commands never create it.
- `refine_search_check_method(checks, check_id, method) -> tuple[SearchCheck, ...]`.
- `CaseController.refine_search_check(case, check_id, method, inaccessible_parts, now) -> Case`.

- [ ] **Step 1: Write RED test**

```python
def test_refinement_preserves_original_check_identity_and_time(self):
    refined = refine_search_check_method((self.reported,), "check-1", SearchMethod.EMPTY_AND_CHECK)
    self.assertEqual(refined[0].id, "check-1")
    self.assertEqual(refined[0].started_at, self.reported.started_at)
    self.assertEqual(refined[0].method, SearchMethod.EMPTY_AND_CHECK)
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_search_log.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v
```

Expected: FAIL on missing method/refinement.

- [ ] **Step 3: Implement neutral method and refinement**

Reject refinement to `INACCESSIBLE` with `MD_SEARCH_METHOD_INVALID`; inaccessible portions are represented separately.

- [ ] **Step 4: Run GREEN**

Run both commands again; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/search_log.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/tests/test_search_log.py plugins/mind-detective/tests/test_controller.py
git commit -m "feat: support neutral web search checks"
```

---

### Task 5: Define stateless API create/validate contracts and core bridge

**Files:**
- Create: `apps/api/mind_detective_api/__init__.py`
- Create: `apps/api/mind_detective_api/contracts.py`
- Create: `apps/api/mind_detective_api/core_bridge.py`
- Create: `apps/api/mind_detective_api/app.py`
- Create: `apps/api/run.py`
- Create: `apps/api/tests/test_contracts.py`

**Interfaces:**
- `CaseCreateRequest(case_id: str, item_label: str, now: str)`.
- `CaseValidateRequest(case: dict[str, object])`.
- `CaseResponse(case: dict[str, object])`.
- `create_case_payload(case_id, item_label, now) -> dict[str, object]`.
- `validate_or_migrate_case_payload(payload) -> dict[str, object]`.
- Endpoints: `POST /api/v1/case/create`, `POST /api/v1/case/validate`.

- [ ] **Step 1: Write RED API test**

```python
def test_create_returns_case_v2(self):
    response = self.client.post("/api/v1/case/create", json={
        "case_id": "case-1",
        "item_label": "ключи",
        "now": "2026-09-10T07:00:00Z",
    })
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json()["case"]["schema"], "mind-detective-case/v2")
```

Also test v1 validate/migrate and invalid schema 422 response.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -p 'test_contracts.py' -v`

Expected: FAIL because API modules are missing.

- [ ] **Step 3: Implement bridge and endpoints**

`core_bridge.py` resolves repo root from `Path(__file__)`, prepends `plugins/mind-detective` once, then imports `scripts.controller` and `scripts.store`. Domain errors map to HTTP 422 with `{code, message}`. No request body logging.

- [ ] **Step 4: Run GREEN**

Run the same command; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api apps/api/run.py apps/api/tests/test_contracts.py
git commit -m "feat: add stateless case api contracts"
```

---

### Task 6: Implement typed deterministic command execution

**Files:**
- Create: `apps/api/mind_detective_api/commands.py`
- Modify: `apps/api/mind_detective_api/contracts.py`
- Modify: `apps/api/mind_detective_api/app.py`
- Create: `apps/api/tests/test_commands.py`

**Interfaces:**
- `CommandEnvelope`: `command_id`, `expected_updated_at`, `command_type`, `now`, `payload`.
- Allowed command types: `set_mode`, `add_statement`, `record_search_check`, `refine_search_check`, `reject_next_action`, `pause`, `resume`, `close_found`, `close_unresolved`.
- `CaseCommandRequest`: `case`, `command`.
- `execute_command(case_payload, envelope) -> dict[str, object]`.
- `POST /api/v1/case/command`.

- [ ] **Step 1: Write RED tests**

```python
def test_retrying_same_command_against_same_case_is_deterministic(self):
    first = execute_command(self.case_payload, self.command)
    second = execute_command(self.case_payload, self.command)
    self.assertEqual(first, second)
```

Also cover stale `expected_updated_at -> MD_WEB_STALE_COMMAND`, neutral `reported_check`, categorical rejection feedback, and command payload allowlists rejecting `probability`.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -p 'test_commands.py' -v`

Expected: FAIL.

- [ ] **Step 3: Implement dispatch**

IDs and timestamps that affect output come from the envelope/payload so retries are deterministic. The server stores no command history.

- [ ] **Step 4: Run GREEN**

Run the same command; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/commands.py apps/api/mind_detective_api/contracts.py apps/api/mind_detective_api/app.py apps/api/tests/test_commands.py
git commit -m "feat: execute deterministic web commands"
```

---

### Task 7: Add deterministic checklist proposals and empty-planner state

**Files:**
- Create: `apps/api/mind_detective_api/checklist.py`
- Create: `apps/api/mind_detective_api/proposals.py`
- Modify: `apps/api/mind_detective_api/contracts.py`
- Modify: `apps/api/mind_detective_api/app.py`
- Create: `apps/api/tests/test_checklist_proposals.py`

**Interfaces:**
- `Proposal.kind`: `next_action`, `clarification`, `need_more_information`, `fallback`.
- Proposal fields: `candidate_id`, `target`, `copy_key`, `rationale_codes`, `related_statement_ids`.
- `ProposalRequest`: `case`, `mode`, `locale`, `experimental_arm`.
- `POST /api/v1/proposal/next`.
- Checklist engine never invents a target when no safe candidate exists.

- [ ] **Step 1: Write RED tests**

```python
def test_empty_case_returns_information_needed_without_location(self):
    proposal = build_checklist_proposal(self.empty_case, "reconstruction")
    self.assertEqual(proposal.kind, "need_more_information")
    self.assertIsNone(proposal.target)
```

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -p 'test_checklist_proposals.py' -v`

Expected: FAIL.

- [ ] **Step 3: Implement deterministic proposal selection**

Use existing `case.next_action`, timeline unknowns, partial/inaccessible checks and urgency constraints. Final display text is represented by reviewed localization `copy_key` values.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/checklist.py apps/api/mind_detective_api/proposals.py apps/api/mind_detective_api/contracts.py apps/api/mind_detective_api/app.py apps/api/tests/test_checklist_proposals.py
git commit -m "feat: add deterministic checklist proposals"
```

---

### Task 8: Add OpenAI Responses structured proposals, guard fallback and privacy logging

**Files:**
- Create: `apps/api/mind_detective_api/openai_provider.py`
- Create: `apps/api/mind_detective_api/privacy_log.py`
- Modify: `apps/api/mind_detective_api/proposals.py`
- Create: `apps/api/tests/test_assistant_proposals.py`

**Interfaces:**
- `OpenAIProposalClient.propose(case: dict[str, object], mode: str) -> Proposal` is asynchronous.
- Uses `AsyncOpenAI.responses.parse(model=model_name, input=model_input, text_format=ProposalModel)`.
- `OPENAI_API_KEY` and `MIND_DETECTIVE_OPENAI_MODEL` are read server-side only.
- Blocked proposals never enter user-facing journal text; a reviewed system event plus deterministic fallback is returned.

- [ ] **Step 1: Write RED tests with injected fake provider**

```python
async def test_reconstruction_location_injection_is_blocked(self):
    fake = FakeProposalClient(ProposalModel(
        kind="next_action",
        candidate_id="candidate-car",
        target="машина",
        copy_key="next_action.check_target",
        rationale_codes=[],
        related_statement_ids=[],
    ))
    result = await build_assistant_proposal(self.case_without_car, "reconstruction", fake)
    self.assertEqual(result.proposal.kind, "fallback")
    self.assertEqual(result.guard_code, "MD_G_RECON_NEW_LOCATION")
```

Add tests for percentage claims, raw rejected text exclusion, and privacy log allowlist.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -p 'test_assistant_proposals.py' -v`

Expected: FAIL.

- [ ] **Step 3: Implement provider and guarded proposal pipeline**

Tests must not require a live API key. Application metadata logs may contain request id, arm, outcome code, latency bucket and configured model id; they must not contain item label, user text, target text, full Case JSON, or raw model output.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/mind_detective_api/openai_provider.py apps/api/mind_detective_api/privacy_log.py apps/api/mind_detective_api/proposals.py apps/api/tests/test_assistant_proposals.py
git commit -m "feat: add guarded assistant proposal engine"
```

---

### Task 9: Bootstrap Nuxt, typed Case contracts and read-only derived state

**Files:**
- Create: `apps/web/nuxt.config.ts`
- Create: `apps/web/app.vue`
- Create: `apps/web/lib/api/contracts.ts`
- Create: `apps/web/lib/case/derived.ts`
- Create: `apps/web/composables/useExperimentalArm.ts`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/tests/unit/derived.spec.ts`

**Interfaces:**
- `CaseV2` mirrors serialized Python Case v2.
- `deriveProgress(caseValue) -> {checked, remaining, inaccessible}`.
- `derivePriorCheckAnnotation(caseValue, candidateId) -> PriorCheckAnnotation | null`.
- `useExperimentalArm()` returns readonly `checklist | assistant` from `NUXT_PUBLIC_MIND_DETECTIVE_ARM`.
- No client function accepts a Case and returns a domain-mutated Case.

- [ ] **Step 1: Write RED unit test**

```ts
it('derives progress without mutating the case', () => {
  const before = structuredClone(caseFixture)
  expect(deriveProgress(caseFixture)).toEqual({ checked: 4, remaining: 3, inaccessible: 1 })
  expect(caseFixture).toEqual(before)
})
```

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec vitest run tests/unit/derived.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement Nuxt base and test runners**

Set `ssr: false`. Playwright starts API with `python ../api/run.py` and Nuxt dev server on `127.0.0.1:3000`. No engine picker is present in production pages.

- [ ] **Step 4: Run GREEN and build**

```bash
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/nuxt.config.ts apps/web/app.vue apps/web/lib apps/web/composables/useExperimentalArm.ts apps/web/vitest.config.ts apps/web/playwright.config.ts apps/web/tests/unit/derived.spec.ts
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
- IndexedDB database `mind-detective`, store `cases`, key path `case_id`.
- `CaseRepository.list/get/put/delete`.
- `requestPersistentStorage() -> granted | denied | unsupported`.
- `exportCase(caseValue) -> Blob`.
- `importCase(file, validate) -> CaseV2`.

- [ ] **Step 1: Write RED browser test**

Test put/reload/list, delete isolation, valid export, v1 import through `/case/validate`, invalid/future schema rejection, and denied/unsupported persistence states.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/storage.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement storage**

Case payloads never go into localStorage or Cache Storage. localStorage may contain only non-sensitive presentation/capability flags.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/storage apps/web/composables/useCaseRepository.ts apps/web/tests/e2e/storage.spec.ts
git commit -m "feat: add local case persistence and export"
```

---

### Task 11: Implement transport-only sequential command queue

**Files:**
- Create: `apps/web/composables/useCaseApi.ts`
- Create: `apps/web/composables/useCommandQueue.ts`
- Create: `apps/web/tests/unit/commandQueue.spec.ts`

**Interfaces:**
- `PendingCommand`: `command_id`, `case_id`, `command_type`, `expected_updated_at`, `now`, `payload`, `status`, `attempt_count`.
- `enqueue(caseValue, command) -> Promise<CaseV2>`.
- `retry(commandId) -> Promise<CaseV2>`.
- Queue is transport state only and never feeds planner logic.

- [ ] **Step 1: Write RED tests**

```ts
it('does not mutate canonical case while request is pending', async () => {
  const api = deferredApi()
  const queue = makeCommandQueue(api, repository)
  const pending = queue.enqueue(caseFixture, commandFixture)
  expect(repository.current()).toEqual(caseFixture)
  api.resolve(updatedCaseFixture)
  await pending
  expect(repository.current()).toEqual(updatedCaseFixture)
})
```

Also assert sequential send order, byte-equivalent retry envelope, and no mutation after validation failure.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec vitest run tests/unit/commandQueue.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement queue and API client**

Do not create `reduceCase`, `applyCommandLocally`, or equivalent mutation helper.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/composables/useCaseApi.ts apps/web/composables/useCommandQueue.ts apps/web/tests/unit/commandQueue.spec.ts
git commit -m "feat: add pending web command queue"
```

---

### Task 12: Build one-field case creation and local case list/resume

**Files:**
- Create: `apps/web/pages/index.vue`
- Create: `apps/web/components/case/CaseList.vue`
- Create: `apps/web/components/case/CreateCaseForm.vue`
- Create: `apps/web/tests/e2e/create-resume.spec.ts`

**Interfaces:**
- First-case flow has one `item_label` field and one primary Start action.
- Engine arm is absent from user-facing creation UI.
- Active/paused cases sort by `updated_at` descending.

- [ ] **Step 1: Write RED E2E test**

Assert no engine picker, create waits for `/case/create`, persists returned Case, navigates to `/cases/<id>`, and paused resume preserves exact statements/checks.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/create-resume.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement screens using prototype density**

Storage/install education appears after meaningful engagement, not as an onboarding gate.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/pages/index.vue apps/web/components/case/CaseList.vue apps/web/components/case/CreateCaseForm.vue apps/web/tests/e2e/create-resume.spec.ts
git commit -m "feat: add web case creation and resume"
```

---

### Task 13: Build the unified active-case shell and immutable mode-marked journal

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
- Create: `apps/web/tests/e2e/shell-equivalence.spec.ts`

**Interfaces:**
- `CaseShell` receives canonical Case, experimental arm and pending state; it emits typed UI intents only.
- B/C render the same shell/journal/input component tree.
- Historical entry tag comes only from `entry.mode`.
- Mode uses label + SVG icon + typography; color is redundant.

- [ ] **Step 1: Write RED equivalence test**

Render the same Case fixture under checklist and assistant deployments and compare stable landmark/test-id sets. Journal and `InteractionDock` must exist in both.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/shell-equivalence.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement shared shell and prototype-derived tokens**

Carry forward 4px spacing, 44px minimum hit targets, safe-area handling, system font stack, readable glass floors, reduced-motion and increased-contrast fallbacks. Do not ship the prototype control rail.

- [ ] **Step 4: Run GREEN at 320px, 405px and desktop widths**

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
- Create: `apps/web/tests/e2e/check-flow.spec.ts`

**Interfaces:**
- `Проверил` enqueues `record_search_check` with `reported_check`.
- No progress counter changes before canonical API response.
- Quality dialog appears only when returned state says prior method quality is decision-relevant.
- `inaccessible_parts` is separate from method choice.

- [ ] **Step 1: Write RED E2E test**

Cover `aria-busy`, unchanged counters during pending state, returned Case progress, no immediate quality dialog, later refinement, and preserved check id.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/check-flow.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement through command queue only**

Progress always comes from `deriveProgress(returnedCase)`; never increment a demo-local `done` variable.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/CheckQualityDialog.vue apps/web/components/case/NextActionCard.vue apps/web/pages/cases/[id].vue apps/web/tests/e2e/check-flow.spec.ts
git commit -m "feat: add one-tap web check flow"
```

---

### Task 15: Add empty planner, visible guard block and next-action rejection

**Files:**
- Create: `apps/web/components/case/SystemJournalEvent.vue`
- Create: `apps/web/components/case/ActionRejectDialog.vue`
- Modify: `apps/web/components/case/NextActionCard.vue`
- Modify: `apps/web/pages/cases/[id].vue`
- Create: `apps/web/tests/e2e/proposal-states.spec.ts`

**Interfaces:**
- `need_more_information` is a non-location card.
- Guard block renders reviewed system copy plus deterministic fallback; raw rejected proposal is absent.
- `Not suitable` enqueues `reject_next_action` with one categorical reason.
- Delete remains outside primary search actions.

- [ ] **Step 1: Write RED state tests**

Test empty planner, guard block, rejected candidate non-repeat, and primary-action delete absence.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/proposal-states.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Implement reviewed states**

Machine guard code may appear only in optional details, never as primary UX copy.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/SystemJournalEvent.vue apps/web/components/case/ActionRejectDialog.vue apps/web/components/case/NextActionCard.vue apps/web/pages/cases/[id].vue apps/web/tests/e2e/proposal-states.spec.ts
git commit -m "feat: surface proposal safety states"
```

---

### Task 16: Implement close outcomes and privacy-preserving local evaluation log

**Files:**
- Create: `apps/web/components/case/CloseCaseDialog.vue`
- Create: `apps/web/components/case/CaseOutcome.vue`
- Create: `apps/web/lib/eval/log.ts`
- Create: `apps/web/tests/unit/evalLog.spec.ts`
- Create: `apps/web/tests/e2e/close-flow.spec.ts`

**Interfaces:**
- `found_context`: `current_suggested_action`, `elsewhere_unplanned`, `after_previous_check`, `unknown`.
- Required events: `case_started`, `next_action_shown`, `next_action_started`, `next_action_rejected`, `check_started`, `check_finished`, `duplicate_check_detected`, `check_quality_clarified`, `ai_guard_blocked`, `pending_command_started`, `pending_command_retried`, `pending_command_failed`, `pause`, `resume`, `found`, `case_closed_unresolved`, `case_abandoned`, `found_context_recorded`.
- Evaluation allowlist excludes item/location/journal/statement/model text and full Case payload.

- [ ] **Step 1: Write RED privacy test**

```ts
it('rejects sensitive evaluation keys', () => {
  expect(() => appendEvalEvent('found', { item_label: 'ключи' } as never))
    .toThrow('MD_WEB_EVAL_SENSITIVE_FIELD')
})
```

E2E covers found on current action, found elsewhere/unplanned and unresolved close.

- [ ] **Step 2: Run RED**

```bash
pnpm --dir apps/web exec vitest run tests/unit/evalLog.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/close-flow.spec.ts
```

Expected: FAIL.

- [ ] **Step 3: Implement close and explicit JSON/CSV evaluation export**

No background telemetry upload exists.

- [ ] **Step 4: Run GREEN**

Run both commands again; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/case/CloseCaseDialog.vue apps/web/components/case/CaseOutcome.vue apps/web/lib/eval apps/web/tests/unit/evalLog.spec.ts apps/web/tests/e2e/close-flow.spec.ts
git commit -m "feat: add outcome and local evaluation flow"
```

---

### Task 17: Add PWA shell caching, offline behavior and durability UX

**Files:**
- Modify: `apps/web/nuxt.config.ts`
- Create: `apps/web/public/manifest.webmanifest`
- Create: `apps/web/components/storage/StorageNotice.vue`
- Create: `apps/web/components/storage/InstallEducation.vue`
- Create: `apps/web/tests/e2e/pwa-storage.spec.ts`

**Interfaces:**
- Service worker precaches shell/static assets only.
- No `/api/` runtime cache.
- No background sync.
- Offline mutation remains visibly pending/failed and canonical Case remains unchanged.
- Storage copy explains local-only cases, no cloud backup, possible site-data loss, persistence limits and export recovery.

- [ ] **Step 1: Write RED PWA tests**

Inspect generated worker/manifest and assert no API route, Case payload route or background sync registration. Simulate offline check and assert no progress mutation before retry succeeds.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web build && pnpm --dir apps/web exec playwright test tests/e2e/pwa-storage.spec.ts`

Expected: FAIL.

- [ ] **Step 3: Configure `@vite-pwa/nuxt` and durability UX**

After first meaningful case interaction, call `navigator.storage.persisted()` and then `navigator.storage.persist()` when needed. Render granted/denied/unsupported honestly.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/nuxt.config.ts apps/web/public apps/web/components/storage apps/web/tests/e2e/pwa-storage.spec.ts
git commit -m "feat: add privacy-safe pwa behavior"
```

---

### Task 18: Lock RU/EN copy, accessibility and prototype scenario coverage

**Files:**
- Create: `apps/web/lib/i18n/ru.ts`
- Create: `apps/web/lib/i18n/en.ts`
- Create: `apps/web/lib/i18n/index.ts`
- Create: `apps/web/tests/unit/i18n.spec.ts`
- Create: `apps/web/tests/e2e/accessibility.spec.ts`
- Create: `apps/web/tests/e2e/scenario-matrix.spec.ts`

**Interfaces:**
- Locale keys cover mode labels, guard/safety, empty planner, storage warnings, pending/retry/error, create/resume/close, check quality, export/import and assistant-provider privacy disclosure.
- RU/EN key sets are identical.
- No keyboard autofocus on active-case load.
- Dialogs trap focus, close on Escape, restore trigger focus and make background inert.
- Minimum interactive hit area is 44px.

- [ ] **Step 1: Write RED tests**

Scenario matrix must cover all 20 states in `docs/prototypes/2026-09-10-mind-detective-ui-prototype-review.md`, including both arms/phases, pending/retry, guard block, partial/inaccessible, quality clarification, planner empty, rejection, pause, both found contexts, unresolved, persistence states, v1 migration, invalid import, light/dark/reduced-motion/increased-contrast.

- [ ] **Step 2: Run RED**

```bash
pnpm --dir apps/web exec vitest run tests/unit/i18n.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/accessibility.spec.ts tests/e2e/scenario-matrix.spec.ts
```

Expected: FAIL.

- [ ] **Step 3: Implement reviewed locale maps and accessibility behavior**

Prototype scenario controls remain test/developer fixtures only; production gets no control rail or engine chooser.

- [ ] **Step 4: Run GREEN**

Expected PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/i18n apps/web/tests/unit/i18n.spec.ts apps/web/tests/e2e/accessibility.spec.ts apps/web/tests/e2e/scenario-matrix.spec.ts
git commit -m "test: lock web copy and scenario accessibility"
```

---

### Task 19: Trace requirements, extend CI/docs and prepare the 0.2.0 release set

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
- Modify: plugin descriptor and marketplace version fields
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_release_contract.py`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- Every `MD-WEB-REQ-*` requirement in the approved spec maps to an exact selector, including `MD-WEB-REQ-PRIVACY-01`.
- Add explicit privacy requirement for transient assistant-provider processing while persistence remains browser-local.
- CI adds pinned Node/pnpm install, Vitest, Nuxt build, Playwright Chromium + WebKit, and API tests while retaining all existing Python/core/release gates.
- Release manifest declares exactly repository `0.2.0` and plugin `mind-detective-v0.2.0`.
- `publish-current-release.yml` remains the only publisher and is not replaced by a second release framework.

- [ ] **Step 1: Write RED contract/version tests**

Add Web selectors first and a version-parity assertion expecting `0.2.0`; current descriptors/manifest must fail before release preparation.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s tests -p 'test_contract_matrix.py' -v && python -m unittest discover -s tests -p 'test_release_contract.py' -v && python -m unittest discover -s tests -p 'test_repository_contracts.py' -v`

Expected: FAIL on missing Web requirements/version `0.2.0`.

- [ ] **Step 3: Update contracts/docs/CI/descriptors/release manifest**

`release.json` must normalize to exactly:

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

Do not edit `.github/releases/0.1.0.md` or any published `0.1.0` tag/release.

- [ ] **Step 4: Run complete verification**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py --strict
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
ruff check .
mypy --strict scripts tests plugins/mind-detective/scripts plugins/mind-detective/tests apps/api/mind_detective_api apps/api/tests
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all PASS.

- [ ] **Step 5: Commit release-ready implementation**

```bash
git add docs README.md README.en.md CHANGELOG.md CHANGELOG.en.md .github apps plugins tests scripts package.json pnpm-workspace.yaml pnpm-lock.yaml .node-version
git commit -m "release: prepare MIND Detective 0.2.0"
```

- [ ] **Step 6: Preserve human integration/release gates**

1. Push a separate implementation branch and open an implementation PR.
2. Require exact PR-head CI success.
3. Obtain explicit human authorization before merge.
4. Merge with expected-head protection.
5. Require exact post-merge `main` push CI success.
6. Obtain separate explicit human authorization for publication at the full 40-hex `main` SHA.
7. Run only `publish-current-release.yml` with that SHA.
8. Verify `0.2.0` and `mind-detective-v0.2.0` are non-draft, immutable, and both tag refs resolve to the exact approved release SHA.

---

## Plan Self-Review

### Spec coverage

- Same B/C shell and input structure: Tasks 9, 13, 18.
- Message-level mode provenance: Tasks 2, 3, 13.
- No client reducer and sequential pending queue: Tasks 6, 11, 14.
- One-tap neutral check and delayed refinement: Tasks 4, 14.
- Persistent progress/prior-check context: Tasks 9, 13, 14.
- Create/list/resume: Tasks 10, 12.
- Empty planner, guard block and action rejection: Tasks 7, 8, 15.
- Found context/unresolved close and evaluation events: Task 16.
- IndexedDB, persistence request, install education and export/import: Tasks 10, 17.
- Service-worker data boundary: Task 17.
- RU/EN, accessibility and prototype state coverage: Task 18.
- Existing Python core reuse/stdlib boundary: Tasks 1, 5, 19.
- Assistant-provider privacy boundary: Tasks 8, 18, 19.
- Exact immutable release governance: Task 19.

### Placeholder scan

The plan contains no `TBD`, `TODO`, implementation-later markers, Python Ellipsis placeholders, undefined command names, or invalid dotted test-module paths through `mind-detective`.

### Type consistency

- Case v2 types originate in Tasks 2–4 and serialize/migrate before API use.
- API Tasks 5–8 return the same full Case v2 payload consumed by Web Task 9.
- Server CommandEnvelope fields match client PendingCommand fields introduced in Task 11.
- Proposal kinds from Task 7 are exactly the states rendered in Tasks 13 and 15.
- `found_context` values in Task 16 match the approved spec.

## Execution Handoff

Production implementation must happen on a separate branch/PR. At execution time create an isolated worktree using `superpowers:using-git-worktrees`, then execute task-by-task with `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`. Approval of this plan does not authorize implementation merge or release publication.
