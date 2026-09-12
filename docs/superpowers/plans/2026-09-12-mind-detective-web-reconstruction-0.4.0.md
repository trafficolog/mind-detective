# MIND Detective 0.4.0 Web Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, offline-capable Web reconstruction workflow that preserves a raw free account, records only user-confirmed structured evidence, derives an uncertainty-preserving timeline through the canonical generated execution path, and transitions explicitly into the existing physical Search workflow.

**Architecture:** Python portable semantics remain authoritative. Two new local commands — `record_free_account` and `rebuild_timeline` — are implemented in the portable kernel, generated into the committed TypeScript executor, persisted atomically with the existing execution-receipt mechanism, and surfaced through focused Vue components rather than a second handwritten domain reducer. Live-model reconstruction is not required for 0.4.0 and may not mutate canonical memory evidence.

**Tech Stack:** Python 3.10/3.13 stdlib-first domain kernel, certified Python→TypeScript generator, Nuxt 4/Vue/TypeScript, IndexedDB, Vitest, Playwright Chromium/WebKit, Ruff, strict Mypy, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`

## Global Constraints

- `mind-detective-case/v2` remains the Case schema for 0.4.0.
- Python portable semantics remain the authoritative deterministic source; no handwritten parallel Web reducer.
- Web canonical persistence remains IndexedDB and local-first.
- Case mutation and execution receipt remain one atomic transaction with idempotent command semantics.
- Raw free account is preserved verbatim as `author=user`, `mode=reconstruction`, `entry_type=free_account`; it is not automatically classified as recollection/habit/observation.
- Structured recollection/habit/observation remains user-originated/user-confirmed only.
- Unknowns and contradictions remain explicit and are not resolved by plausibility.
- New concrete locations may not be seeded as reconstruction cues; user-supplied locations may be clarified, otherwise locations belong to Search proposals.
- `set_mode(search)` is an explicit transition and does not promote evidence.
- No Case v3, Bayesian/POD state, calibrated probabilities, hidden belief weights, cross-case learning, cloud Case DB, or background Case sync.
- Deterministic reconstruction must work after PWA preload without a live model.
- Assistant reconstruction is not a 0.4.0 release blocker and cannot write canonical memory evidence.
- RU/EN copy must have exact key parity and equivalent safety/privacy semantics.
- Every active requirement must have a production path and exact test selector in `docs/CONTRACT_MATRIX.json`.
- Intermediate remote commits must remain CI-valid: requirements are `planned` until their production paths exist, then become `active` in Task 8.
- Historical immutable releases remain unchanged. Version/release publication is a separate human-authorized gate after implementation and exact-main CI.

## Stable 0.4.0 Requirement IDs

```text
MD-WEB-REQ-RECONSTRUCT-01 — raw free account before detailed reconstruction statements
MD-WEB-REQ-RECONSTRUCT-02 — user provenance for recollection/habit/observation
MD-WEB-REQ-RECONSTRUCT-03 — no unsupported location seeding in reconstruction
MD-WEB-REQ-RECONSTRUCT-04 — preserve/render unknowns and contradictions
MD-WEB-REQ-RECONSTRUCT-05 — portable authoritative timeline mutation
MD-WEB-REQ-RECONSTRUCT-06 — semantic/visual distinction of evidence, derived uncertainty, proposals and Search
MD-WEB-REQ-RECONSTRUCT-07 — explicit Search transition without evidence promotion
MD-WEB-REQ-RECONSTRUCT-08 — offline deterministic reconstruction after preload
MD-WEB-REQ-RECONSTRUCT-09 — RU/EN reconstruction semantic parity
MD-WEB-REQ-RECONSTRUCT-10 — Case v2 reconstruction export/import preservation
```

---

### Task 1: Register the reconstruction scope as planned contracts without breaking CI

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_matrix.py`

**Interfaces:**
- Consumes: existing `validate_contract_matrix()` support for `status: planned`.
- Produces: ten stable IDs visible to repository governance but not falsely claimed `active` before implementation.

The matrix planned-task mapping is fixed:

```text
RECONSTRUCT-01 → planned_task 2
RECONSTRUCT-02 → planned_task 2
RECONSTRUCT-03 → planned_task 6
RECONSTRUCT-04 → planned_task 3
RECONSTRUCT-05 → planned_task 3
RECONSTRUCT-06 → planned_task 6
RECONSTRUCT-07 → planned_task 6
RECONSTRUCT-08 → planned_task 7
RECONSTRUCT-09 → planned_task 6
RECONSTRUCT-10 → planned_task 7
```

- [ ] **Step 1: Write a failing contract test**

Extend `ContractMatrixTests` with:

```python
RECONSTRUCTION_REQUIREMENTS = {
    f"MD-WEB-REQ-RECONSTRUCT-{index:02d}" for index in range(1, 11)
}


def test_repository_declares_planned_reconstruction_requirements(self):
    ids, duplicates = collect_requirement_ids(ROOT / "docs/REQUIREMENTS.md")
    self.assertEqual(duplicates, set())
    self.assertTrue(RECONSTRUCTION_REQUIREMENTS.issubset(ids))

    matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
    rows = {
        row["requirement_id"]: row
        for row in matrix["entries"]
        if row["requirement_id"] in RECONSTRUCTION_REQUIREMENTS
    }
    self.assertEqual(set(rows), RECONSTRUCTION_REQUIREMENTS)
    self.assertTrue(all(row["status"] == "planned" for row in rows.values()))
    self.assertTrue(all("test" not in row and "helper" not in row for row in rows.values()))
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
```

Expected: FAIL because the ten IDs do not exist.

- [ ] **Step 3: Add the ten requirements as planned**

Add the exact IDs/semantics above to `docs/REQUIREMENTS.md` with **Status: planned for 0.4.0**.

Add ten `docs/CONTRACT_MATRIX.json` rows shaped exactly as:

```json
{
  "requirement_id": "MD-WEB-REQ-RECONSTRUCT-01",
  "status": "planned",
  "planned_task": 2,
  "reason": "0.4.0 Web Reconstruction Foundation: free-account-first production path is implemented in Task 2"
}
```

Use the task mapping above. Planned rows contain no `skill`, `helper`, `test`, or `reference` fields.

- [ ] **Step 4: Run GREEN and full matrix validation**

```bash
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
python scripts/validate_repo.py
```

Expected: PASS. This commit must remain CI-valid.

- [ ] **Step 5: Commit**

```bash
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json tests/test_contract_matrix.py
git commit -m "docs: register planned web reconstruction contracts"
```

---

### Task 2: Implement canonical `record_free_account` and the free-account-first gate

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/tests/test_portable_contract.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`
- Modify: `plugins/mind-detective/tests/test_controller_portable_parity.py`

**Interfaces:**
- Produces command type: `record_free_account`.
- Payload: `{"entry_id": string, "text": string}`.
- Stable errors: `MD_RECON_MODE_REQUIRED`, `MD_RECON_FREE_ACCOUNT_REQUIRED`, `MD_RECON_FREE_ACCOUNT_EXISTS`; existing malformed-field errors remain `MD_WEB_COMMAND_PAYLOAD`.

Canonical helper signatures:

```python
def has_free_account_json(case: dict[str, object]) -> bool: ...


def record_free_account_json(
    case: dict[str, object],
    entry_id: str,
    text: str,
    now: str,
) -> dict[str, object]: ...
```

Controller adapter:

```python
def record_free_account(
    self,
    case: Case,
    entry_id: str,
    text: str,
    now: str,
) -> Case: ...
```

- [ ] **Step 1: Write failing contract/kernel tests**

Require `record_free_account` in `SUPPORTED_COMMAND_TYPES` and cover:

```text
active + reconstruction → append one verbatim free_account journal entry
unselected/search mode → MD_RECON_MODE_REQUIRED
empty entry_id/text → MD_WEB_COMMAND_PAYLOAD
second distinct free account → MD_RECON_FREE_ACCOUNT_EXISTS
add_statement in reconstruction before free account → MD_RECON_FREE_ACCOUNT_REQUIRED
add_statement in search remains valid without free account
```

Successful journal entry must equal:

```python
{
    "id": "free-1",
    "author": "user",
    "mode": "reconstruction",
    "entry_type": "free_account",
    "text": "Я пришёл домой и положил ключи, но не помню куда.",
    "created_at": now,
    "statement_ids": [],
    "search_check_ids": [],
}
```

and `statements` must remain unchanged.

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_contract.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
```

- [ ] **Step 3: Implement the portable command and mode/gate checks**

Add `record_free_account` to command payload validation/dispatch. `record_free_account_json()` uses the existing portable clone/mutable-case path, requires `current_mode == "reconstruction"`, rejects a second free-account entry, and appends only the canonical journal entry above.

Update reconstruction-mode `add_statement` handling so no detailed statement can be recorded until `has_free_account_json()` is true. Search-mode statement behavior remains unchanged.

- [ ] **Step 4: Add controller safety ingress and adapter**

`CaseController.record_free_account()` must call `_enforce_safe_ingress(text)` before portable mutation, then convert the canonical returned dict through `_from_portable()`.

- [ ] **Step 5: Run GREEN**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_contract.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller_portable_parity.py' -v
```

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/portable_contract.py plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/tests/test_portable_contract.py plugins/mind-detective/tests/test_portable_kernel.py plugins/mind-detective/tests/test_controller.py plugins/mind-detective/tests/test_controller_portable_parity.py
git commit -m "feat: add canonical reconstruction free account"
```

---

### Task 3: Move timeline rebuilding into portable authoritative semantics

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/timeline.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/scripts/plugin_reducer.py`
- Modify: `plugins/mind-detective/tests/test_portable_contract.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`
- Modify: `plugins/mind-detective/tests/test_controller_portable_parity.py`
- Modify: `plugins/mind-detective/tests/test_timeline.py`

**Interfaces:**
- Produces command type: `rebuild_timeline`.
- Stable errors added: `MD_RECON_TIMELINE_EVENT_DUPLICATE`, `MD_RECON_STATEMENT_NOT_FOUND`.
- Reuses `MD_RECON_MODE_REQUIRED`, `MD_RECON_FREE_ACCOUNT_REQUIRED`, `MD_TIME_REFERENCE_MISSING`, `MD_TIME_INVALID_TIMESTAMP`, `MD_TIME_ORDER_CONTRADICTION`.

Exact payload shape:

```json
{
  "events": [
    {
      "id": "event-1",
      "label": "Последний подтверждённый контакт с ключами",
      "statement_ids": ["stmt-1"],
      "event_time": "2026-09-12T08:30:00+03:00",
      "time_precision": "approximate"
    }
  ],
  "last_supported_interaction_id": "stmt-1",
  "first_noticed_missing_id": "stmt-2"
}
```

Canonical helper:

```python
def rebuild_timeline_json(
    case: dict[str, object],
    events: list[dict[str, object]],
    last_supported_interaction_id: str | None,
    first_noticed_missing_id: str | None,
    now: str,
) -> dict[str, object]: ...
```

- [ ] **Step 1: Write failing tests**

Cover:

```text
active reconstruction + free account + valid event refs → canonical timeline
wrong mode → MD_RECON_MODE_REQUIRED
no free account → MD_RECON_FREE_ACCOUNT_REQUIRED
duplicate event id → MD_RECON_TIMELINE_EVENT_DUPLICATE
missing event statement id → MD_RECON_STATEMENT_NOT_FOUND
statement with event_time=None + limitation → unknown_intervals preserved
missing anchor → MD_TIME_REFERENCE_MISSING contradiction
invalid comparable anchor timestamp → MD_TIME_INVALID_TIMESTAMP contradiction
last-supported later than first-missing → MD_TIME_ORDER_CONTRADICTION contradiction
failure → input Case remains unchanged
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
```

- [ ] **Step 3: Implement canonical timeline serialization/mutation**

Validate event structure and references before mutation. Derive canonical `unknown_intervals`/`contradictions` using the existing timeline vocabulary. Store the full serialized timeline under `case["timeline"]` only after validation succeeds.

- [ ] **Step 4: Remove the competing reducer ownership**

`CaseController` timeline mutation must delegate the portable canonical implementation. Remove `reduce_set_timeline` from controller usage. Retain a `plugin_reducer` timeline helper only if an existing compatibility test requires it; if retained, it must delegate canonical semantics rather than mutate independently.

- [ ] **Step 5: Run all plugin tests**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
```

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/portable_contract.py plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/scripts/timeline.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/scripts/plugin_reducer.py plugins/mind-detective/tests
git commit -m "feat: make reconstruction timeline portable"
```

---

### Task 4: Extend certified generation and Python↔TypeScript conformance

**Files:**
- Modify: `plugins/mind-detective/scripts/conformance_vectors.py`
- Regenerate: `apps/web/app/generated/localExecution.ts`
- Regenerate: `apps/web/app/generated/localExecution.meta.json`
- Regenerate: `conformance/local-execution/v1/manifest.json`
- Regenerate: `conformance/local-execution/v1/vectors.json`
- Modify: `tests/test_local_execution_corpus.py`
- Modify: `apps/web/tests/unit/localExecutionConformance.spec.ts`

**Interfaces:**
- Consumes Tasks 2–3 portable functions through the existing generator.
- Produces committed generated execution plus parity vectors for both new commands.

Required vector names:

```text
reconstruction_record_free_account
reconstruction_statement_requires_free_account
reconstruction_rebuild_timeline_unknowns
reconstruction_rebuild_timeline_contradiction
reconstruction_transition_to_search_preserves_evidence
```

- [ ] **Step 1: Add failing corpus coverage assertions**

Extend `tests/test_local_execution_corpus.py` to require the five names above.

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s tests -p 'test_local_execution_corpus.py' -v
```

- [ ] **Step 3: Add conformance vectors**

Each vector contains canonical input Case, command envelope, and expected output/error. `reconstruction_record_free_account` must prove the raw text appears only in `interaction_journal` and creates no Statement.

- [ ] **Step 4: Regenerate artifacts using the existing certified generator**

```bash
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
```

If the existing AST/certification gate rejects a construct introduced in Tasks 2–3, refactor the portable Python to the already certified subset. Do not broaden the generator surface merely for convenience.

- [ ] **Step 5: Run GREEN and freshness checks**

```bash
python -m unittest discover -s tests -p 'test_local_execution_generator.py' -v
python -m unittest discover -s tests -p 'test_local_execution_emitter.py' -v
python -m unittest discover -s tests -p 'test_local_execution_corpus.py' -v
pnpm --dir apps/web exec vitest run tests/unit/localExecutionConformance.spec.ts
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
```

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/conformance_vectors.py apps/web/app/generated conformance tests/test_local_execution_corpus.py apps/web/tests/unit/localExecutionConformance.spec.ts
git commit -m "test: certify reconstruction local execution"
```

---

### Task 5: Add typed Web command construction without duplicating domain semantics

**Files:**
- Modify: `apps/web/app/lib/api/contracts.ts`
- Create: `apps/web/app/composables/useReconstruction.ts`
- Create: `apps/web/tests/unit/reconstruction.spec.ts`
- Modify: `apps/web/tests/unit/localExecutor.spec.ts`

**Interfaces:**
- Extends `CommandEnvelope['command_type']` with `record_free_account | rebuild_timeline`.
- Reuses existing `TimelineEventV2`; do not create a duplicate timeline-event contract.

Add:

```ts
export type RecordFreeAccountPayload = {
  entry_id: string
  text: string
}

export type RebuildTimelinePayload = {
  events: TimelineEventV2[]
  last_supported_interaction_id: string | null
  first_noticed_missing_id: string | null
}
```

`useReconstruction.ts` exposes UI/view helpers only:

```ts
hasFreeAccount(caseValue: CaseV2): boolean
freeAccountText(caseValue: CaseV2): string | null
buildRecordFreeAccountPayload(entryId: string, text: string): RecordFreeAccountPayload
buildRebuildTimelinePayload(
  events: TimelineEventV2[],
  lastSupportedInteractionId: string | null,
  firstNoticedMissingId: string | null,
): RebuildTimelinePayload
```

- [ ] **Step 1: Write failing Vitest tests**

Test that free-account detection requires `author=user`, `mode=reconstruction`, `entry_type=free_account`, preserves text verbatim, and payload builders never calculate unknowns/contradictions.

- [ ] **Step 2: Run RED**

```bash
pnpm --dir apps/web exec vitest run tests/unit/reconstruction.spec.ts tests/unit/localExecutor.spec.ts
```

- [ ] **Step 3: Implement exact types/helpers**

Use existing generic local command execution. Do not add a Web-only reducer or a second timeline validator.

- [ ] **Step 4: Run GREEN**

```bash
pnpm --dir apps/web exec vitest run tests/unit/reconstruction.spec.ts tests/unit/localExecutor.spec.ts
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/lib/api/contracts.ts apps/web/app/composables/useReconstruction.ts apps/web/tests/unit/reconstruction.spec.ts apps/web/tests/unit/localExecutor.spec.ts
git commit -m "feat: add typed web reconstruction commands"
```

---

### Task 6: Build the state-first reconstruction UI and explicit Search transition

**Files:**
- Create: `apps/web/app/components/reconstruction/ReconstructionPanel.vue`
- Create: `apps/web/app/components/reconstruction/FreeAccountCard.vue`
- Create: `apps/web/app/components/reconstruction/StatementCapture.vue`
- Create: `apps/web/app/components/reconstruction/TimelineEditor.vue`
- Create: `apps/web/app/components/reconstruction/TimelineSummary.vue`
- Modify: `apps/web/app/pages/cases/[id].vue`
- Modify: `apps/web/app/lib/i18n/ru.ts`
- Modify: `apps/web/app/lib/i18n/en.ts`
- Modify: `apps/web/tests/unit/i18n.spec.ts`
- Create: `apps/web/tests/e2e/reconstruction-flow.spec.ts`

**Interfaces:**
- Components emit user input/payloads upward; `[id].vue` uses the existing `runCommand()` boundary.
- Reconstruction core does not call `api.nextProposal()`.

Required component responsibilities:

```text
ReconstructionPanel — phase orchestration and canonical state display
FreeAccountCard — raw account capture/read-only saved display
StatementCapture — one explicit user-confirmed statement after the gate
TimelineEditor — event grouping/reference input only
TimelineSummary — read-only canonical timeline/unknowns/contradictions
```

Required copy keys:

```text
reconstruction.title
reconstruction.free_account.title
reconstruction.free_account.prompt
reconstruction.free_account.submit
reconstruction.free_account.saved
reconstruction.statement.title
reconstruction.statement.type
reconstruction.statement.text
reconstruction.statement.event_time
reconstruction.statement.unknown_time
reconstruction.timeline.title
reconstruction.timeline.rebuild
reconstruction.timeline.unknowns
reconstruction.timeline.contradictions
reconstruction.to_search
reconstruction.mode_label
```

- [ ] **Step 1: Write the failing canonical Playwright journey**

`reconstruction-flow.spec.ts` must cover:

```text
create Case
→ enter reconstruction
→ detailed statement controls unavailable before free account
→ submit raw free account
→ verbatim account appears and is not presented as recollection
→ add explicit user-confirmed structured statements
→ rebuild timeline
→ canonical unknown/contradiction sections render
→ explicit switch to Search
→ reconstruction evidence remains preserved
→ existing Search/checklist UI activates
```

Also assert no unsupported concrete location is presented by reconstruction UI unless already present in user-authored input.

- [ ] **Step 2: Run RED**

```bash
pnpm --dir apps/web exec playwright test tests/e2e/reconstruction-flow.spec.ts --project=chromium
```

Expected: fail at the current reconstruction-unavailable boundary.

- [ ] **Step 3: Add RU/EN copy with exact key parity**

Copy must explain that reconstruction structures the user's account and does not establish the item's actual location. Distinctions must use labels/iconography/typography, not color alone.

- [ ] **Step 4: Build the five focused components**

Event surface:

```ts
emit('record-free-account', text)
emit('add-statement', payload)
emit('rebuild-timeline', payload)
emit('switch-to-search')
```

Components do not write IndexedDB or calculate domain truth.

- [ ] **Step 5: Integrate into `[id].vue`**

Replace `web-reconstruction-unavailable` with `ReconstructionPanel` for active reconstruction cases. Construct these exact command envelopes through the existing command helper:

```text
record_free_account
add_statement
rebuild_timeline
set_mode(search)
```

Existing pause/resume/close/local-retry behavior remains Case-level page orchestration.

- [ ] **Step 6: Run GREEN**

```bash
pnpm --dir apps/web exec vitest run tests/unit/i18n.spec.ts tests/unit/reconstruction.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/reconstruction-flow.spec.ts --project=chromium
```

- [ ] **Step 7: Commit**

```bash
git add apps/web/app/components/reconstruction apps/web/app/pages/cases/'[id].vue' apps/web/app/lib/i18n/ru.ts apps/web/app/lib/i18n/en.ts apps/web/tests/unit/i18n.spec.ts apps/web/tests/e2e/reconstruction-flow.spec.ts
git commit -m "feat: add state-first web reconstruction ui"
```

---

### Task 7: Prove offline operation, persistence, retry, and Case v2 portability

**Files:**
- Create: `apps/web/tests/e2e/offline-reconstruction.spec.ts`
- Modify: `apps/web/tests/e2e/storage.spec.ts`
- Modify: `apps/web/tests/unit/exportImport.spec.ts`
- Modify only when a failing test proves a defect: `apps/web/app/lib/storage/caseImport.ts`, `apps/web/app/lib/storage/exportImport.ts`, `apps/web/app/lib/storage/indexeddb.ts`

**Interfaces:**
- Produces executable proof that deterministic reconstruction remains local-first and reconstructive state round-trips under Case v2.

- [ ] **Step 1: Write the offline E2E test**

Canonical flow:

```text
preload app online
create Case → reconstruction → free account
set browser offline
reload
resume same Case from IndexedDB
add confirmed statement
rebuild timeline
switch to Search
record physical check
```

Assert deterministic mutations complete without successful Case API calls.

- [ ] **Step 2: Extend export/import unit coverage**

Round-trip a Case v2 containing:

```text
free_account journal entry
recollection statement
habit/observation statement
timeline event
unknown interval
contradiction
current_mode=reconstruction
```

Assert deep equality of those canonical fields after local export/import.

- [ ] **Step 3: Run RED/GREEN cycle**

```bash
pnpm --dir apps/web exec vitest run tests/unit/exportImport.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/offline-reconstruction.spec.ts tests/e2e/storage.spec.ts --project=chromium
```

If failures expose dropped fields, fix only the local Case v2 import/export/storage path; do not add schema migration or server validation.

- [ ] **Step 4: Commit**

```bash
git add apps/web/tests/e2e/offline-reconstruction.spec.ts apps/web/tests/e2e/storage.spec.ts apps/web/tests/unit/exportImport.spec.ts apps/web/app/lib/storage
git commit -m "test: prove reconstruction offline persistence"
```

---

### Task 8: Activate the ten requirements with exact production-reachability selectors

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_contract_reachability.py`
- Modify: `tests/test_web_pwa_contract.py`
- Modify: `scripts/contract_controls.py`

**Interfaces:**
- Consumes production code/tests from Tasks 2–7.
- Produces `status: active` rows with real `skill`, `helper`, `test`, `reference` fields and exact test selectors.

Required trace targets:

```text
01 → record_free_account + reconstruction add_statement gate
02 → user-only statement source enforcement
03 → reconstruction location-seeding guard/UI contract
04 → rebuild_timeline + TimelineSummary
05 → portable timeline command + generated conformance
06 → reconstruction-flow semantic distinction assertions
07 → explicit set_mode(search) transition test
08 → offline-reconstruction E2E
09 → i18n parity test
10 → export/import reconstruction round-trip
```

- [ ] **Step 1: Write/extend reachability tests before activating rows**

Tests must reject existence-only helpers and require the new Web components/composable to be reachable from `apps/web/app/pages/cases/[id].vue` or another production surface.

- [ ] **Step 2: Run reachability tests while rows are still planned**

```bash
python -m unittest discover -s tests -p 'test_contract_reachability.py' -v
python -m unittest discover -s tests -p 'test_web_pwa_contract.py' -v
```

Expected: PASS for existing contracts; new reachability helper assertions should pass against Tasks 2–7 production code.

- [ ] **Step 3: Change all ten requirement statuses from planned to active**

Update `docs/REQUIREMENTS.md` to **Status: active** and replace each planned matrix row with the full active row. Each exact selector must already exist before this edit.

Use production helpers/references appropriate to each requirement; do not point active rows to the design spec or an existence-only test as the implementation control.

- [ ] **Step 4: Run full contract validation**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
python -m unittest discover -s tests -p 'test_contract_reachability.py' -v
python -m unittest discover -s tests -p 'test_web_pwa_contract.py' -v
```

Expected: PASS with no `MD_CONTRACT_*` errors.

- [ ] **Step 5: Commit**

```bash
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json tests/test_contract_matrix.py tests/test_contract_reachability.py tests/test_web_pwa_contract.py scripts/contract_controls.py
git commit -m "test: activate web reconstruction contracts"
```

---

### Task 9: Reconcile architecture, privacy, evaluation, and user-facing docs

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `docs/PRIVACY.md`
- Modify: `docs/PRODUCT_EVALUATION.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/GETTING_STARTED.en.md`
- Create: `docs/adr/015-web-reconstruction-portable-boundary.md`
- Modify: `tests/test_bilingual_docs.py`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- Produces documentation matching the actual deterministic 0.4.0 behavior without claiming assistant efficacy.

ADR 015 decision text must establish:

```text
Web reconstruction uses portable authoritative commands (`record_free_account`, `rebuild_timeline`) and generated local execution. Vue components collect/render state but do not own reconstruction truth. Live-model clarification is not a dependency of the 0.4.0 core path.
```

- [ ] **Step 1: Add failing doc assertions**

Require public docs to stop saying Web reconstruction is unavailable and require the phrases/semantics: verbatim free account, user-confirmed structured evidence, explicit unknowns/contradictions, local deterministic reconstruction, Case v2 unchanged.

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s tests -p 'test_bilingual_docs.py' -v
python -m unittest discover -s tests -p 'test_repository_contracts.py' -v
```

- [ ] **Step 3: Update RU-primary docs and EN mirrors plus ADR 015**

`docs/PRODUCT_EVALUATION.md` must preserve the current Search B↔C scope and explicitly say it is not evidence that live-model reconstruction adds value.

- [ ] **Step 4: Run GREEN**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_bilingual_docs.py' -v
python -m unittest discover -s tests -p 'test_repository_contracts.py' -v
```

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md docs tests/test_bilingual_docs.py tests/test_repository_contracts.py
git commit -m "docs: document web reconstruction boundary"
```

---

### Task 10: Run full verification and prepare the implementation PR

**Files:**
- No planned feature files are added here; only fix failures proven by the complete verification suite.
- Do not change version/release surfaces.

**Interfaces:**
- Produces exact-head green implementation evidence; does not publish 0.4.0.

- [ ] **Step 1: Prove generated artifacts/corpus are fresh**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
```

- [ ] **Step 2: Run full Python/repository gates**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py --strict
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
python -m compileall -q plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
ruff check .
MYPYPATH=plugins/mind-detective:apps/api mypy --explicit-package-bases plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
```

- [ ] **Step 3: Run full Web gates**

```bash
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

- [ ] **Step 4: Scope audit**

Fail review if the diff introduces:

```text
mind-detective-case/v3
probability/pod/belief_weight/posterior domain fields
cloud Case persistence or background Case sync
assistant-authored recollection/habit/observation
a handwritten Web timeline/reconstruction reducer
release/tag publication
```

- [ ] **Step 5: Require exact-head GitHub CI**

Record the full 40-hex implementation head. All four top-level PR checks on that exact SHA must succeed:

```text
Validate (Python 3.10)
Validate (Python 3.13)
Validate Web
Secret scan
```

- [ ] **Step 6: Keep release preparation behind a separate gate**

Do not modify `.github/releases/release.json`, version surfaces, create tags, or publish `0.4.0` until the implementation PR is reviewed/merged, exact-main push CI succeeds, and the user separately authorizes release preparation/publication.
