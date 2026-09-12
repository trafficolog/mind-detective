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
- Historical immutable releases remain unchanged. Version/release publication is a separate human-authorized gate after implementation and exact-main CI.

## File Structure Locked by This Plan

**Canonical semantics and adapters**

- Modify `plugins/mind-detective/scripts/portable_contract.py` — declare the two command names and their portable surface.
- Modify `plugins/mind-detective/scripts/portable_kernel.py` — own free-account gating, canonical journal mutation, timeline validation/derivation, and command dispatch.
- Modify `plugins/mind-detective/scripts/controller.py` — delegate typed free-account/timeline operations to portable semantics.
- Modify `plugins/mind-detective/scripts/timeline.py` only where a typed helper is needed to share canonical timeline construction; do not retain competing mutation semantics.
- Modify `plugins/mind-detective/scripts/conformance_vectors.py` — add reconstruction vectors.

**Contract and generator surface**

- Modify `docs/REQUIREMENTS.md` — add `MD-WEB-REQ-RECONSTRUCT-01` through `MD-WEB-REQ-RECONSTRUCT-10`.
- Modify `docs/CONTRACT_MATRIX.json` — exact selectors for each new requirement.
- Modify `scripts/contract_controls.py` only if production-reachability registration needs new controls.
- Regenerate `apps/web/app/generated/localExecution.ts` and `apps/web/app/generated/localExecution.meta.json` via the existing generator; never hand-edit them.
- Regenerate `conformance/local-execution/v1/manifest.json` and `conformance/local-execution/v1/vectors.json` via the existing corpus generator.

**Web execution and view layer**

- Modify `apps/web/app/lib/api/contracts.ts` — add exact command payload/event/timeline types needed by the UI.
- Modify `apps/web/app/lib/execution/localExecutor.ts` only as the existing persistence/safety wrapper requires; domain rules remain generated.
- Modify `apps/web/app/composables/useLocalExecution.ts` only to expose the existing generic command path if required.
- Create `apps/web/app/composables/useReconstruction.ts` — command construction and reconstruction view-state helpers only; no domain truth calculation.
- Create `apps/web/app/components/reconstruction/ReconstructionPanel.vue` — reconstruction phase orchestration.
- Create `apps/web/app/components/reconstruction/FreeAccountCard.vue` — verbatim free-account capture/display.
- Create `apps/web/app/components/reconstruction/StatementCapture.vue` — explicit user-confirmed statement capture after the gate.
- Create `apps/web/app/components/reconstruction/TimelineEditor.vue` — user-confirmed event/reference inputs only.
- Create `apps/web/app/components/reconstruction/TimelineSummary.vue` — render canonical timeline/unknowns/contradictions.
- Modify `apps/web/app/pages/cases/[id].vue` — replace the reconstruction-unavailable boundary with the new panel and keep Case-level lifecycle orchestration.
- Modify `apps/web/app/lib/i18n/ru.ts` and `apps/web/app/lib/i18n/en.ts` — exact reconstruction copy parity.

**Tests**

- Modify `plugins/mind-detective/tests/test_portable_contract.py`.
- Modify `plugins/mind-detective/tests/test_portable_kernel.py`.
- Modify `plugins/mind-detective/tests/test_controller.py`.
- Modify `plugins/mind-detective/tests/test_controller_portable_parity.py`.
- Modify `tests/test_contract_matrix.py` and `tests/test_contract_reachability.py`.
- Modify `tests/test_local_execution_corpus.py` if vector coverage assertions are enumerated.
- Modify `apps/web/tests/unit/localExecutor.spec.ts` and `apps/web/tests/unit/localExecutionConformance.spec.ts` as needed.
- Create `apps/web/tests/unit/reconstruction.spec.ts` for pure reconstruction command/view-state helpers.
- Create `apps/web/tests/e2e/reconstruction-flow.spec.ts`.
- Create `apps/web/tests/e2e/offline-reconstruction.spec.ts`.
- Extend `apps/web/tests/e2e/storage.spec.ts` or `apps/web/tests/unit/exportImport.spec.ts` for reconstruction import/export preservation.

---

### Task 1: Add the 0.4.0 reconstruction requirements and executable trace contract

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_contract_reachability.py`
- Modify: `scripts/contract_controls.py` only if a new production control resolver is required

**Interfaces:**
- Consumes: current `MD-WEB-REQ-*` contract conventions and exact-selector validation.
- Produces: stable requirement IDs `MD-WEB-REQ-RECONSTRUCT-01` … `MD-WEB-REQ-RECONSTRUCT-10` used by every later task.

Use these exact semantics:

```text
MD-WEB-REQ-RECONSTRUCT-01 — raw free account is required before detailed reconstruction statements.
MD-WEB-REQ-RECONSTRUCT-02 — recollection/habit/observation stored by Web are user-originated/user-confirmed; assistant cannot originate them.
MD-WEB-REQ-RECONSTRUCT-03 — reconstruction does not seed unsupported concrete locations; only user-supplied locations may be clarified.
MD-WEB-REQ-RECONSTRUCT-04 — canonical reconstruction preserves and renders unknown intervals and contradictions.
MD-WEB-REQ-RECONSTRUCT-05 — timeline mutation is executed through portable authoritative semantics and generated Web execution, not a handwritten Web reducer.
MD-WEB-REQ-RECONSTRUCT-06 — raw account, structured evidence, derived uncertainty, assistant proposals, and Search suggestions are semantically/visually distinguishable without color-only cues.
MD-WEB-REQ-RECONSTRUCT-07 — reconstruction→Search is explicit and does not promote evidence or erase uncertainty.
MD-WEB-REQ-RECONSTRUCT-08 — deterministic reconstruction remains usable after PWA preload without a live model.
MD-WEB-REQ-RECONSTRUCT-09 — RU/EN reconstruction copy has exact key parity and equivalent safety/privacy semantics.
MD-WEB-REQ-RECONSTRUCT-10 — Case v2 export/import preserves raw free account, structured evidence, timeline, unknowns, contradictions, and mode without server validation dependency.
```

- [ ] **Step 1: Write failing repository-contract tests for the ten IDs**

Add a test that parses `docs/REQUIREMENTS.md` and `docs/CONTRACT_MATRIX.json` and requires all ten IDs to exist exactly once with non-empty exact selectors.

```python
RECONSTRUCTION_REQUIREMENTS = {
    f"MD-WEB-REQ-RECONSTRUCT-{index:02d}" for index in range(1, 11)
}

self.assertTrue(RECONSTRUCTION_REQUIREMENTS <= requirement_ids)
self.assertTrue(RECONSTRUCTION_REQUIREMENTS <= matrix_ids)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
python -m unittest discover -s tests -p 'test_contract_reachability.py' -v
```

Expected: FAIL because the new requirement IDs/selectors do not yet exist.

- [ ] **Step 3: Add the ten normative requirements and matrix entries**

Add the exact semantics above to `docs/REQUIREMENTS.md`. Add matrix rows with selectors pointing only to tests that later tasks will create; while Task 1 is in progress, selectors may point to the Task 1 contract tests for existence, but before Task 8 the final matrix must point to production-path tests, not existence-only helpers.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the same two commands. Expected: PASS.

- [ ] **Step 5: Commit the contract skeleton**

```bash
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json tests/test_contract_matrix.py tests/test_contract_reachability.py scripts/contract_controls.py
git commit -m "docs: define web reconstruction contracts"
```

---

### Task 2: Implement canonical `record_free_account` semantics

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/tests/test_portable_contract.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`
- Modify: `plugins/mind-detective/tests/test_controller_portable_parity.py`

**Interfaces:**
- Consumes: `Case v2`, `current_mode`, existing `interaction_journal`, command envelope/idempotence path.
- Produces: command type `record_free_account` with payload `{"entry_id": str, "text": str}` and stable errors `MD_RECON_MODE_REQUIRED`, `MD_RECON_FREE_ACCOUNT_REQUIRED`, `MD_RECON_FREE_ACCOUNT_EXISTS`.

Canonical helper signatures to implement:

```python
def record_free_account_json(
    case: dict[str, object],
    entry_id: str,
    text: str,
    now: str,
) -> dict[str, object]: ...


def has_free_account_json(case: dict[str, object]) -> bool: ...
```

Typed controller adapter:

```python
def record_free_account(
    self,
    case: Case,
    entry_id: str,
    text: str,
    now: str,
) -> Case: ...
```

- [ ] **Step 1: Write failing portable-contract tests**

Require `record_free_account` in `SUPPORTED_COMMAND_TYPES` and exact payload key validation.

```python
self.assertIn("record_free_account", SUPPORTED_COMMAND_TYPES)
```

- [ ] **Step 2: Write failing kernel behavior tests**

Cover these exact cases:

```python
# active + reconstruction => appends one verbatim free_account journal entry
# unselected/search mode => MD_RECON_MODE_REQUIRED
# empty entry_id/text => MD_WEB_COMMAND_PAYLOAD
# second distinct free account => MD_RECON_FREE_ACCOUNT_EXISTS
# add_statement in reconstruction before free account => MD_RECON_FREE_ACCOUNT_REQUIRED
# add_statement in search remains valid without a free account
```

For the successful journal entry assert:

```python
entry == {
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

- [ ] **Step 3: Run focused tests and verify RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_contract.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
```

Expected: FAIL because the command/helper does not exist.

- [ ] **Step 4: Add the command and the kernel-enforced gate**

Implement `record_free_account_json()` so it clones/mutates only through the existing portable primitive-copy rules, requires an active mutable Case in `reconstruction`, rejects a second free-account entry, and appends the exact journal shape above.

Update `add_statement` command application so the free-account gate applies only when `current_mode == "reconstruction"`.

Do not infer statement type from free-account text.

- [ ] **Step 5: Add the typed controller adapter and ingress safety call**

`CaseController.record_free_account()` must call `_enforce_safe_ingress(text)` before delegating to the portable helper, matching other user-authored input paths.

- [ ] **Step 6: Run focused tests and verify GREEN**

Run the same focused tests plus:

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller_portable_parity.py' -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

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
- Modify: `plugins/mind-detective/scripts/plugin_reducer.py` to remove/retire competing timeline mutation if no remaining caller requires it
- Modify: `plugins/mind-detective/tests/test_portable_contract.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`
- Modify: `plugins/mind-detective/tests/test_controller_portable_parity.py`
- Modify: `plugins/mind-detective/tests/test_timeline.py`

**Interfaces:**
- Consumes: free-account gate from Task 2 and current Case statements.
- Produces: command type `rebuild_timeline` with canonical payload and one timeline mutation definition shared by Web/plugin adapters.

Exact command payload:

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

Rules:

```text
events must be an array
id/label/time_precision must be non-empty strings
event_time is string|null
statement_ids is a non-empty array of existing statement ids
duplicate event ids fail MD_RECON_TIMELINE_EVENT_DUPLICATE
missing event statement id fails MD_RECON_STATEMENT_NOT_FOUND
Case must be active reconstruction mode or fail MD_RECON_MODE_REQUIRED
free account must exist or fail MD_RECON_FREE_ACCOUNT_REQUIRED
anchor ids follow existing timeline semantics: missing anchors become MD_TIME_REFERENCE_MISSING contradiction
invalid comparable timestamps preserve MD_TIME_INVALID_TIMESTAMP contradiction
order inversion preserves MD_TIME_ORDER_CONTRADICTION contradiction
failed payload/reference validation does not mutate the Case
```

Canonical helper signature:

```python
def rebuild_timeline_json(
    case: dict[str, object],
    events: list[dict[str, object]],
    last_supported_interaction_id: str | None,
    first_noticed_missing_id: str | None,
    now: str,
) -> dict[str, object]: ...
```

- [ ] **Step 1: Write failing timeline command tests**

Add tests for the success payload plus every rule listed above. Also assert unknown intervals remain derived from statement limitations where `event_time is None`.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
```

Expected: FAIL because `rebuild_timeline` is unsupported.

- [ ] **Step 3: Implement canonical timeline payload validation and derivation**

Reuse the existing `Timeline` semantics rather than inventing a second contradiction vocabulary. The portable function must serialize:

```json
{
  "last_supported_interaction_id": "... or null",
  "first_noticed_missing_id": "... or null",
  "events": [...],
  "unknown_intervals": [...],
  "contradictions": [...]
}
```

into `case["timeline"]` and update `updated_at` only on success.

- [ ] **Step 4: Redirect `CaseController.set_timeline`/new typed rebuild adapter to canonical semantics**

The typed/plugin path must no longer define a competing timeline mutation. If compatibility requires `set_timeline`, make it an adapter that serializes the typed timeline through canonical validation; otherwise expose a typed `rebuild_timeline(...)` and update callers/tests.

- [ ] **Step 5: Run all plugin tests**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts/portable_contract.py plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/scripts/timeline.py plugins/mind-detective/scripts/controller.py plugins/mind-detective/scripts/plugin_reducer.py plugins/mind-detective/tests
git commit -m "feat: make reconstruction timeline portable"
```

---

### Task 4: Extend certified generation and Python↔TypeScript conformance

**Files:**
- Modify: `plugins/mind-detective/scripts/conformance_vectors.py`
- Modify only if required by supported AST/call surface: `scripts/generate_local_execution.py`, `scripts/generate_local_execution_certified.py`, `scripts/local_execution_ast.py`
- Regenerate: `apps/web/app/generated/localExecution.ts`
- Regenerate: `apps/web/app/generated/localExecution.meta.json`
- Regenerate: `conformance/local-execution/v1/manifest.json`
- Regenerate: `conformance/local-execution/v1/vectors.json`
- Modify: `tests/test_local_execution_corpus.py`
- Modify: `apps/web/tests/unit/localExecutionConformance.spec.ts`

**Interfaces:**
- Consumes: `record_free_account` and `rebuild_timeline` from Tasks 2–3.
- Produces: generated TypeScript functions/dispatch and committed conformance vectors proving observable parity for both new commands.

- [ ] **Step 1: Add failing corpus coverage assertions**

Require vector names equivalent to:

```text
reconstruction_record_free_account
reconstruction_statement_requires_free_account
reconstruction_rebuild_timeline_unknowns
reconstruction_rebuild_timeline_contradiction
reconstruction_transition_to_search_preserves_evidence
```

- [ ] **Step 2: Run corpus tests and verify RED**

```bash
python -m unittest discover -s tests -p 'test_local_execution_corpus.py' -v
```

Expected: FAIL because the vectors do not exist.

- [ ] **Step 3: Add conformance vectors using the exact portable command envelopes**

Each vector must include the canonical input Case, command envelope, and expected output/error. At least one vector must prove raw free-account text remains journal-only and does not create a statement.

- [ ] **Step 4: Regenerate executor and corpus**

```bash
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
```

Do not edit generated files by hand.

- [ ] **Step 5: Run generator/corpus tests and Web conformance**

```bash
python -m unittest discover -s tests -p 'test_local_execution_generator.py' -v
python -m unittest discover -s tests -p 'test_local_execution_emitter.py' -v
python -m unittest discover -s tests -p 'test_local_execution_corpus.py' -v
pnpm --dir apps/web exec vitest run tests/unit/localExecutionConformance.spec.ts
```

Expected: PASS.

- [ ] **Step 6: Prove committed artifacts are fresh**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
```

Expected: no diff.

- [ ] **Step 7: Commit**

```bash
git add plugins/mind-detective/scripts/conformance_vectors.py scripts apps/web/app/generated conformance tests/test_local_execution_corpus.py apps/web/tests/unit/localExecutionConformance.spec.ts
git commit -m "test: certify reconstruction local execution"
```

---

### Task 5: Add typed Web reconstruction command construction without duplicating domain semantics

**Files:**
- Modify: `apps/web/app/lib/api/contracts.ts`
- Modify: `apps/web/app/lib/execution/localExecutor.ts`
- Modify: `apps/web/app/composables/useLocalExecution.ts`
- Create: `apps/web/app/composables/useReconstruction.ts`
- Create: `apps/web/tests/unit/reconstruction.spec.ts`
- Modify: `apps/web/tests/unit/localExecutor.spec.ts`

**Interfaces:**
- Consumes: generated command names/payload rules from Task 4.
- Produces: typed UI helper methods that create command envelopes only; canonical validation/derivation remains generated.

Add these TypeScript payload types:

```ts
export type RecordFreeAccountPayload = {
  entry_id: string
  text: string
}

export type ReconstructionTimelineEventInput = {
  id: string
  label: string
  statement_ids: string[]
  event_time: string | null
  time_precision: string
}

export type RebuildTimelinePayload = {
  events: ReconstructionTimelineEventInput[]
  last_supported_interaction_id: string | null
  first_noticed_missing_id: string | null
}
```

`CommandEnvelope['command_type']` must include:

```text
record_free_account
rebuild_timeline
```

`useReconstruction.ts` may expose only UI-safe helpers such as:

```ts
hasFreeAccount(caseValue: CaseV2): boolean
freeAccountText(caseValue: CaseV2): string | null
buildRecordFreeAccountPayload(text: string): RecordFreeAccountPayload
buildRebuildTimelinePayload(input: ReconstructionTimelineDraft): RebuildTimelinePayload
```

`hasFreeAccount`/`freeAccountText` inspect canonical journal state; they do not infer memory truth or timeline contradictions.

- [ ] **Step 1: Write failing Vitest tests for typed helper behavior**

Test that free-account detection requires exactly `author=user`, `mode=reconstruction`, `entry_type=free_account`, and that payload builders preserve text verbatim except for UI rejection of all-whitespace input before sending.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
pnpm --dir apps/web exec vitest run tests/unit/reconstruction.spec.ts tests/unit/localExecutor.spec.ts
```

Expected: FAIL because the types/composable do not exist.

- [ ] **Step 3: Implement the types and composable**

Keep UUID/timestamp creation at the existing page/command-envelope boundary. Do not calculate `unknown_intervals` or `contradictions` in TypeScript helper code.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the same Vitest command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/lib/api/contracts.ts apps/web/app/lib/execution/localExecutor.ts apps/web/app/composables/useLocalExecution.ts apps/web/app/composables/useReconstruction.ts apps/web/tests/unit/reconstruction.spec.ts apps/web/tests/unit/localExecutor.spec.ts
git commit -m "feat: add typed web reconstruction commands"
```

---

### Task 6: Build the state-first reconstruction UI

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
- Consumes: typed command builders from Task 5 and canonical Case v2 returned by local execution.
- Produces: complete deterministic reconstruction UI from free account through explicit Search transition.

Component responsibilities are fixed:

```text
ReconstructionPanel
  owns phase orchestration/events; receives canonical Case and pending state
FreeAccountCard
  captures/displays verbatim raw account; no statement classification
StatementCapture
  captures one explicit user-confirmed statement after free-account gate
TimelineEditor
  collects event grouping/refs and emits RebuildTimelinePayload
TimelineSummary
  read-only rendering of canonical events/unknown_intervals/contradictions
```

- [ ] **Step 1: Write the RED canonical browser journey**

Create Playwright test `reconstruction-flow.spec.ts` for:

```text
create Case
→ enter reconstruction
→ verify detailed statement controls unavailable before free account
→ submit free account
→ verify verbatim journal/account display
→ add confirmed recollection and habit/observation examples
→ rebuild timeline
→ verify unknown/contradiction sections render canonical values
→ switch explicitly to Search
→ verify reconstruction evidence remains visible/preserved and Search UI activates
```

The test must assert semantic labels/text and `data-testid` boundaries, not color values.

- [ ] **Step 2: Run the new E2E test and verify RED**

```bash
pnpm --dir apps/web exec playwright test tests/e2e/reconstruction-flow.spec.ts --project=chromium
```

Expected: FAIL at the current `web-reconstruction-unavailable` boundary.

- [ ] **Step 3: Add reconstruction copy keys in RU and EN**

Use one-to-one keys for:

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

Copy must state that the timeline structures the user's account and does not prove the item's location.

- [ ] **Step 4: Build focused components with event-only mutation interfaces**

Components emit data upward. They do not import generated domain functions directly and do not mutate IndexedDB themselves.

Example event shapes:

```ts
emit('record-free-account', text)
emit('add-statement', payload)
emit('rebuild-timeline', payload)
emit('switch-to-search')
```

- [ ] **Step 5: Integrate `ReconstructionPanel` in `[id].vue`**

Replace the `web-reconstruction-unavailable`/search-only boundary for active reconstruction cases. Case-level page code should construct command envelopes and use the existing `runCommand()` retry/atomicity path.

Add exact command handlers:

```ts
record_free_account
add_statement
rebuild_timeline
set_mode(search)
```

Do not request an assistant proposal while `current_mode === 'reconstruction'` in 0.4.0 core flow.

- [ ] **Step 6: Run i18n and browser tests**

```bash
pnpm --dir apps/web exec vitest run tests/unit/i18n.spec.ts tests/unit/reconstruction.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/reconstruction-flow.spec.ts --project=chromium
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/web/app/components/reconstruction apps/web/app/pages/cases/'[id].vue' apps/web/app/lib/i18n apps/web/tests/unit/i18n.spec.ts apps/web/tests/e2e/reconstruction-flow.spec.ts
git commit -m "feat: add state-first web reconstruction ui"
```

---

### Task 7: Prove offline, persistence, retry, and Case v2 import/export behavior

**Files:**
- Create: `apps/web/tests/e2e/offline-reconstruction.spec.ts`
- Modify: `apps/web/tests/e2e/storage.spec.ts`
- Modify: `apps/web/tests/unit/exportImport.spec.ts`
- Modify only if a bug is exposed: `apps/web/app/lib/storage/caseImport.ts`, `apps/web/app/lib/storage/exportImport.ts`, `apps/web/app/lib/storage/indexeddb.ts`

**Interfaces:**
- Consumes: complete deterministic reconstruction flow from Task 6.
- Produces: evidence that reconstruction is local-first, reload-safe, retry-safe, and preserved by Case v2 portability.

- [ ] **Step 1: Write an offline reconstruction E2E test**

Test sequence:

```text
load/precache app online
create Case and enter reconstruction
record free account
set browser context offline
reload
resume the same Case from IndexedDB
add a user-confirmed statement
rebuild timeline
switch to Search
record one physical check
```

Assert no deterministic Case mutation requires `/api/v1/case/*` network success.

- [ ] **Step 2: Write export/import preservation tests**

Construct a Case v2 fixture with:

```text
free_account journal entry
recollection statement
habit statement
timeline event
unknown interval
contradiction
current_mode=reconstruction
```

Export then import locally and assert deep canonical equality for those fields.

- [ ] **Step 3: Run focused tests and verify failures if current storage code drops any field**

```bash
pnpm --dir apps/web exec vitest run tests/unit/exportImport.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/offline-reconstruction.spec.ts tests/e2e/storage.spec.ts --project=chromium
```

- [ ] **Step 4: Make only the minimal storage/import fixes exposed by the tests**

Do not introduce a schema migration or server validation call. Preserve `mind-detective-case/v2`.

- [ ] **Step 5: Re-run focused tests and verify GREEN**

Run the same commands. Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/web/tests/e2e/offline-reconstruction.spec.ts apps/web/tests/e2e/storage.spec.ts apps/web/tests/unit/exportImport.spec.ts apps/web/app/lib/storage
git commit -m "test: prove reconstruction offline persistence"
```

---

### Task 8: Replace provisional trace selectors with production-reachability selectors

**Files:**
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_reachability.py`
- Modify: `tests/test_web_pwa_contract.py`
- Modify: `scripts/contract_controls.py` if needed

**Interfaces:**
- Consumes: production code and tests from Tasks 2–7.
- Produces: exact requirement→production-path→test-selector trace for all ten reconstruction requirements.

- [ ] **Step 1: Write/extend reachability tests that reject existence-only controls**

Each requirement must resolve to a production symbol/path exercised by an exact test selector. In particular:

```text
RECONSTRUCT-01 → record_free_account + reconstruction add_statement gate
RECONSTRUCT-02 → user-only statement source enforcement
RECONSTRUCT-03 → reconstruction UI/guard contract forbidding seeded new locations
RECONSTRUCT-04 → rebuild_timeline unknowns/contradictions + TimelineSummary
RECONSTRUCT-05 → portable command + generated executor/conformance
RECONSTRUCT-06 → reconstruction E2E semantic mode/evidence labels
RECONSTRUCT-07 → explicit set_mode(search) transition test
RECONSTRUCT-08 → offline-reconstruction E2E
RECONSTRUCT-09 → i18n parity test
RECONSTRUCT-10 → export/import preservation test
```

- [ ] **Step 2: Run reachability tests and verify RED against provisional selectors**

```bash
python -m unittest discover -s tests -p 'test_contract_reachability.py' -v
python -m unittest discover -s tests -p 'test_web_pwa_contract.py' -v
```

- [ ] **Step 3: Update matrix selectors to exact final test methods**

Use selector syntax already accepted by repository validation. Do not point to broad files when an exact test method is available.

- [ ] **Step 4: Run repository contract validation**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
python -m unittest discover -s tests -p 'test_contract_reachability.py' -v
python -m unittest discover -s tests -p 'test_web_pwa_contract.py' -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/CONTRACT_MATRIX.json tests/test_contract_reachability.py tests/test_web_pwa_contract.py scripts/contract_controls.py
git commit -m "test: trace web reconstruction production contracts"
```

---

### Task 9: Update architecture, privacy, evaluation, and user-facing documentation

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
- Modify bilingual-doc tests if they enumerate mirrors

**Interfaces:**
- Consumes: final implemented 0.4.0 behavior.
- Produces: documentation that describes actual behavior without claiming assistant efficacy or a Case v3 migration.

- [ ] **Step 1: Add a failing repository-doc assertion for the new Web boundary wording if current tests do not cover it**

The public docs must no longer say Web reconstruction is unavailable. They must state that deterministic reconstruction is local-first and assistant reconstruction is not required for the core flow.

- [ ] **Step 2: Update RU-primary docs and EN mirrors**

Document:

```text
free account is verbatim journal evidence, not auto-classified memory
structured evidence is user-confirmed
unknowns/contradictions remain explicit
portable Python semantics own timeline mutation
Web deterministic reconstruction works offline after preload
AI remains optional proposal boundary
Case v2 remains current
```

`docs/PRODUCT_EVALUATION.md` must explicitly preserve the existing Search B↔C interpretation and state that it is not evidence for reconstruction assistant value.

- [ ] **Step 3: Add ADR 015**

ADR decision:

```text
Use portable authoritative reconstruction commands (`record_free_account`, `rebuild_timeline`) and generated Web execution; do not implement reconstruction truth logic in Vue and do not make live-model clarification a dependency for 0.4.0.
```

Consequences must include generator/conformance expansion, unchanged Case v2, and optional future assistant-evaluation work.

- [ ] **Step 4: Run doc/repository tests**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_bilingual_docs.py' -v
python -m unittest discover -s tests -p 'test_repository_contracts.py' -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md docs/ARCHITECTURE.md docs/ARCHITECTURE.en.md docs/PRIVACY.md docs/PRODUCT_EVALUATION.md docs/GETTING_STARTED.md docs/GETTING_STARTED.en.md docs/adr/015-web-reconstruction-portable-boundary.md tests
git commit -m "docs: document web reconstruction boundary"
```

---

### Task 10: Run full verification and prepare the implementation PR for review

**Files:**
- Modify only files required by failures proven in this task.
- Do not change release manifest/version surfaces in this task.

**Interfaces:**
- Consumes: all Tasks 1–9.
- Produces: exact-head green CI-ready implementation branch; no release publication.

- [ ] **Step 1: Regenerate and prove artifact freshness**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
```

Expected: no diff.

- [ ] **Step 2: Run full Python/repository quality gates**

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

Expected: all PASS.

- [ ] **Step 3: Run full Web gates**

```bash
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all PASS in the configured browser matrix.

- [ ] **Step 4: Inspect git diff for scope violations**

Reject the branch if the diff introduces any of:

```text
mind-detective-case/v3
probability/pod/belief_weight/posterior fields
cloud Case persistence
background Case sync
assistant-authored recollection/habit/observation
a handwritten Web timeline reducer
release/tag publication
```

- [ ] **Step 5: Push the exact implementation head and require exact-head CI**

Record the full 40-hex branch head and wait for the PR-triggered `CI` workflow on that exact SHA. All four top-level checks must succeed:

```text
Validate (Python 3.10)
Validate (Python 3.13)
Validate Web
Secret scan
```

- [ ] **Step 6: Keep release preparation separate**

Do not change `.github/releases/release.json`, version surfaces, create tags, or publish `0.4.0` until the implementation PR is reviewed, merged, exact-main CI succeeds, and the user separately authorizes release preparation/publication.

At this point the implementation is ready for code review/merge governance, not release publication.
