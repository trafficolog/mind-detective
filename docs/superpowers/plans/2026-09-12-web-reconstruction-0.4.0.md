# Web Reconstruction 0.4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make reconstruction a first-class deterministic/offline Web workflow from raw free account through uncertainty-preserving timeline and explicit transition to the existing Search/checklist flow.

**Architecture:** Keep Python portable semantics authoritative. Add `record_free_account` and `rebuild_timeline` to the portable command surface, regenerate the committed TypeScript executor/conformance corpus, then build focused Vue components that only collect inputs and render canonical Case state. AI clarification is not required for 0.4.0 and may not mutate memory evidence.

**Tech Stack:** Python 3.10/3.13 stdlib-first domain kernel, deterministic Python→TypeScript generator, Nuxt 4/Vue, TypeScript, IndexedDB, Vitest, Playwright, PWA service worker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`

## Global Constraints

- Keep `mind-detective-case/v2`; do not introduce Case v3.
- Python portable semantics remain the authoritative deterministic source.
- No handwritten Web Case reducer or independent timeline semantics.
- Raw free account is stored verbatim as `author=user`, `mode=reconstruction`, `entry_type=free_account`; it is not automatically classified as recollection/habit/observation.
- In reconstruction mode, structured statements are blocked until a free account exists.
- Assistant output may not originate recollection/habit/observation or directly mutate canonical Case.
- Preserve unknowns and contradictions; do not resolve them by plausibility.
- Do not seed unsupported concrete locations during reconstruction.
- No Bayesian/POD state, calibrated location probabilities, hidden belief weights, cloud Case DB/sync, or cross-case learning.
- Deterministic reconstruction must work offline after application preload.
- RU/EN copy must have exact key parity and equivalent safety/privacy semantics.
- Each active requirement must have a production-reachability selector in `docs/CONTRACT_MATRIX.json`.
- Use TDD: failing test → minimal implementation → passing focused tests → broader regression gate → commit/PR review.

---

### Task 1: Add normative Web reconstruction requirements and trace contract

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Test: `tests/test_contract_matrix.py`
- Test: `tests/test_web_contracts.py` or the existing repository contract-test module that owns Web selectors

**Interfaces:**
- Consumes: existing `MD-WEB-REQ-*` contract style.
- Produces: stable IDs used by all subsequent implementation PRs.

Use these requirement IDs:

```text
MD-WEB-REQ-RECONSTRUCT-01 free account precedes structured reconstruction statements
MD-WEB-REQ-RECONSTRUCT-02 raw free account preserves user provenance without auto-classification
MD-WEB-REQ-RECONSTRUCT-03 unsupported concrete locations are not seeded as reconstruction cues
MD-WEB-REQ-RECONSTRUCT-04 timeline preserves/represents unknown intervals and contradictions canonically
MD-WEB-REQ-RECONSTRUCT-05 reconstruction mutation uses generated portable local execution
MD-WEB-REQ-RECONSTRUCT-06 reconstruction and Search remain semantically/visually distinct
MD-WEB-REQ-RECONSTRUCT-07 transition to Search does not promote evidence
MD-WEB-REQ-RECONSTRUCT-08 deterministic reconstruction works offline after preload
MD-WEB-REQ-RECONSTRUCT-09 RU/EN copy has semantic/key parity
MD-WEB-REQ-RECONSTRUCT-10 Case v2 export/import preserves reconstruction state
```

- [ ] **Step 1: Write failing contract tests**

Add assertions that all ten IDs exist, are active, and have non-empty exact selectors that resolve to production paths/tests rather than existence-only helpers.

```python
for requirement_id in RECONSTRUCTION_REQUIREMENTS:
    row = matrix[requirement_id]
    self.assertEqual(row["status"], "active")
    self.assertTrue(row["selectors"])
```

- [ ] **Step 2: Run the focused repository contract test**

Run:

```bash
python -m unittest tests.test_contract_matrix -v
```

Expected: FAIL because the ten IDs do not yet exist.

- [ ] **Step 3: Add requirements and provisional selectors**

Selectors may reference the tests/files introduced by later tasks, but the final repository gate must reject unresolved selectors before merge.

- [ ] **Step 4: Run the contract tests**

Expected: selectors are syntactically valid; any selector that requires later code remains intentionally red on the implementation branch until its task lands.

- [ ] **Step 5: Commit**

```bash
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json tests/
git commit -m "contract: define web reconstruction requirements"
```

### Task 2: Add portable `record_free_account` semantics

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Test: `plugins/mind-detective/tests/test_portable_kernel.py`
- Test: `plugins/mind-detective/tests/test_controller.py`
- Test: `tests/test_web_contracts.py`

**Interfaces:**
- Consumes: `Case v2`, `interaction_journal`, `InteractionMode.RECONSTRUCTION`.
- Produces: command type `record_free_account`; kernel function `record_free_account_json(case, entry_id, text, now) -> dict[str, object]`; controller method `record_free_account(case, entry_id, text, now) -> Case`.

- [ ] **Step 1: Write failing portable-kernel tests**

Test successful shape:

```python
result = record_free_account_json(case_in_reconstruction, "entry-1", "Последний раз помню...", NOW)
entry = result["interaction_journal"][-1]
assert entry == {
    "id": "entry-1",
    "author": "user",
    "mode": "reconstruction",
    "entry_type": "free_account",
    "text": "Последний раз помню...",
    "created_at": NOW,
    "statement_ids": [],
    "search_check_ids": [],
}
assert result["statements"] == []
```

Also fail on empty text/id, wrong mode, paused/terminal Case, duplicate `free_account` rewrite attempt if the contract chooses one immutable gate-opening entry, and probabilistic forbidden fields.

- [ ] **Step 2: Run focused tests and confirm RED**

```bash
python -m unittest plugins.mind-detective.tests.test_portable_kernel -v
```

Expected: missing command/function failures.

- [ ] **Step 3: Extend the command contract**

Add:

```python
SUPPORTED_COMMAND_TYPES = (..., "record_free_account", ...)
```

and payload allowlist:

```python
"record_free_account": frozenset({"entry_id", "text"})
```

- [ ] **Step 4: Implement minimal canonical mutation**

`record_free_account_json` must call the same `_primitive_copy` lifecycle/shape guard, require reconstruction mode, preserve verbatim text, and append exactly one journal entry without creating a statement.

- [ ] **Step 5: Enforce free-account-first in reconstruction `add_statement`**

Before accepting an `add_statement` command while `current_mode == "reconstruction"`, require a journal entry where:

```text
author == user
mode == reconstruction
entry_type == free_account
```

Fail with stable code:

```text
MD_RECONSTRUCTION_FREE_ACCOUNT_REQUIRED
```

Search-mode `add_statement` remains unchanged.

- [ ] **Step 6: Add controller adapter and safety-ingress coverage**

Controller method:

```python
def record_free_account(self, case: Case, entry_id: str, text: str, now: str) -> Case:
    self._enforce_safe_ingress(text)
    ...
```

- [ ] **Step 7: Run focused + repository/plugin tests**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
python -m unittest discover -s tests -v
```

- [ ] **Step 8: Commit**

```bash
git add plugins/mind-detective/scripts plugins/mind-detective/tests tests
git commit -m "feat: add canonical free account command"
```

### Task 3: Move timeline mutation into the portable canonical boundary

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/timeline.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify only as needed: `plugins/mind-detective/scripts/plugin_reducer.py`
- Test: `plugins/mind-detective/tests/test_timeline.py`
- Test: `plugins/mind-detective/tests/test_portable_kernel.py`
- Test: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- Consumes: current Case statements and user-confirmed event/reference payload.
- Produces: command `rebuild_timeline`; kernel function `rebuild_timeline_json(case, payload, now) -> dict[str, object]` and a typed adapter used by `CaseController.set_timeline`/replacement method.

Canonical payload shape:

```json
{
  "events": [
    {
      "id": "event-1",
      "label": "Вышел из машины",
      "statement_ids": ["statement-1"],
      "event_time": null,
      "time_precision": "unknown"
    }
  ],
  "last_supported_interaction_id": "statement-1",
  "first_noticed_missing_id": "statement-2"
}
```

- [ ] **Step 1: Write failing timeline command tests**

Cover valid rebuild, missing statement references, free-account requirement, wrong mode/lifecycle, unknown interval preservation, time-order contradiction, invalid timestamp handling, duplicate event ids, and no partial mutation on failure.

- [ ] **Step 2: Confirm RED**

```bash
python -m unittest plugins.mind-detective.tests.test_timeline plugins.mind-detective.tests.test_portable_kernel -v
```

- [ ] **Step 3: Add `rebuild_timeline` to portable command allowlists**

```python
"rebuild_timeline": frozenset({"events", "last_supported_interaction_id", "first_noticed_missing_id"})
```

- [ ] **Step 4: Implement canonical parsing/validation**

Keep timeline truth in Python. Reuse/refactor `build_timeline()` rather than duplicating contradiction logic inside the command dispatcher.

- [ ] **Step 5: Make the typed controller delegate canonical semantics**

Do not leave `CaseController.set_timeline()` mutating through a separate reducer path. The typed path must serialize to the same portable function and deserialize the resulting Case.

- [ ] **Step 6: Run plugin tests**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
```

- [ ] **Step 7: Commit**

```bash
git add plugins/mind-detective/scripts plugins/mind-detective/tests
git commit -m "feat: make timeline rebuild portable and canonical"
```

### Task 4: Extend generated execution and differential conformance

**Files:**
- Modify: `plugins/mind-detective/scripts/conformance_vectors.py`
- Modify as required: generator/certifier modules under `scripts/` and `plugins/mind-detective/scripts/`
- Regenerate: `apps/web/app/generated/localExecution.ts`
- Regenerate: `apps/web/app/generated/localExecution.meta.json`
- Regenerate: `conformance/local-execution/v1/manifest.json`
- Regenerate: `conformance/local-execution/v1/vectors.json`
- Test: `apps/web/tests/unit/localExecutionConformance.spec.ts`
- Test: Python generator/certification tests under `tests/`

**Interfaces:**
- Consumes: Task 2/3 portable functions.
- Produces: generated TypeScript support for `record_free_account` and `rebuild_timeline`, with Python↔TS observable parity vectors.

- [ ] **Step 1: Add failing conformance vectors**

Vectors must include at least:

```text
record_free_account success
record_free_account wrong mode
add_statement before free account -> MD_RECONSTRUCTION_FREE_ACCOUNT_REQUIRED
rebuild_timeline success
rebuild_timeline unknown interval
rebuild_timeline time-order contradiction
rebuild_timeline missing reference failure
```

- [ ] **Step 2: Run generator/conformance tests before regeneration**

```bash
python -m scripts.generate_local_execution_corpus
pnpm --dir apps/web exec vitest run apps/web/tests/unit/localExecutionConformance.spec.ts
```

Expected: generated artifact/corpus mismatch or unsupported-call failure before generator support is complete.

- [ ] **Step 3: Extend restricted generator/certified surface minimally**

Do not loosen the AST whitelist globally to make one function compile. Add only the exact constructs/intrinsics required by the new canonical functions.

- [ ] **Step 4: Regenerate committed artifacts**

```bash
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
```

- [ ] **Step 5: Verify reproducibility and TypeScript parity**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
pnpm --dir apps/web exec vitest run apps/web/tests/unit/localExecutionConformance.spec.ts
```

- [ ] **Step 6: Commit**

```bash
git add plugins/mind-detective/scripts scripts apps/web/app/generated conformance apps/web/tests/unit/localExecutionConformance.spec.ts tests
git commit -m "feat: generate reconstruction execution semantics"
```

### Task 5: Extend Web command types/local executor without new domain logic

**Files:**
- Modify: `apps/web/app/lib/api/contracts.ts`
- Modify: `apps/web/app/lib/execution/localExecutor.ts`
- Modify: `apps/web/app/composables/useLocalExecution.ts` if command typing lives there
- Test: `apps/web/tests/unit/localExecutor.spec.ts`
- Test: `apps/web/tests/unit/localStorageContract.spec.ts`

**Interfaces:**
- Consumes: generated executor from Task 4.
- Produces: typed command envelopes for `record_free_account` and `rebuild_timeline`; IndexedDB atomic persistence and receipts remain unchanged.

- [ ] **Step 1: Write failing unit tests for the two command envelopes**

Assert that commands pass through generated execution, persist Case+receipt atomically, and idempotent retry returns the stored canonical result.

- [ ] **Step 2: Confirm RED**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/localExecutor.spec.ts apps/web/tests/unit/localStorageContract.spec.ts
```

- [ ] **Step 3: Extend TypeScript union types**

Add the exact command names and payload types; do not add handwritten reconstruction state transformation.

- [ ] **Step 4: Pass commands through the existing local executor path**

No special persistence transaction is introduced for reconstruction.

- [ ] **Step 5: Run unit tests**

Expected: PASS, including existing Search command regressions.

- [ ] **Step 6: Commit**

```bash
git add apps/web/app/lib/api apps/web/app/lib/execution apps/web/app/composables apps/web/tests/unit
git commit -m "feat: expose reconstruction commands to web executor"
```

### Task 6: Add a reconstruction view-model/composable boundary

**Files:**
- Create: `apps/web/app/lib/case/reconstruction.ts`
- Create: `apps/web/app/composables/useReconstruction.ts`
- Test: `apps/web/tests/unit/reconstruction.spec.ts`

**Interfaces:**
- Consumes: canonical `CaseV2`, `CommandEnvelope` constructor callback.
- Produces: presentation-only derivations and command builders; no canonical domain mutation.

Define pure derivations such as:

```ts
export function freeAccountEntry(caseValue: CaseV2): JournalEntryV2 | null
export function hasFreeAccount(caseValue: CaseV2): boolean
export function reconstructionStatements(caseValue: CaseV2): StatementV2[]
export function timelineView(caseValue: CaseV2): TimelineV2 | null
```

`useReconstruction` may construct envelopes:

```ts
recordFreeAccount(text: string): Promise<CaseV2 | null>
addConfirmedStatement(input: ConfirmedStatementInput): Promise<CaseV2 | null>
rebuildTimeline(input: TimelineInput): Promise<CaseV2 | null>
switchToSearch(): Promise<CaseV2 | null>
```

but delegates execution to the existing page/local-execution callback.

- [ ] **Step 1: Write failing pure-function tests**

Include free-account detection, statement filtering, timeline passthrough, and no inference from raw journal text.

- [ ] **Step 2: Implement pure derivations**

Do not parse raw free-account prose into memories.

- [ ] **Step 3: Write composable command-builder tests**

Assert exact command names/payloads and that original text remains verbatim.

- [ ] **Step 4: Implement minimal composable**

- [ ] **Step 5: Run unit tests**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/reconstruction.spec.ts
```

- [ ] **Step 6: Commit**

```bash
git add apps/web/app/lib/case/reconstruction.ts apps/web/app/composables/useReconstruction.ts apps/web/tests/unit/reconstruction.spec.ts
git commit -m "feat: add reconstruction web view model"
```

### Task 7: Build focused reconstruction UI components

**Files:**
- Create: `apps/web/app/components/ReconstructionPanel.vue`
- Create: `apps/web/app/components/FreeAccountCard.vue`
- Create: `apps/web/app/components/StatementCapture.vue`
- Create: `apps/web/app/components/TimelineEditor.vue`
- Create: `apps/web/app/components/TimelineSummary.vue`
- Modify: `apps/web/app/lib/i18n/ru.ts`
- Modify: `apps/web/app/lib/i18n/en.ts`
- Test: `apps/web/tests/unit/i18n.spec.ts`
- Test: component/reconstruction unit tests under `apps/web/tests/unit/`

**Interfaces:**
- Consumes: canonical Case/read-only timeline view and event callbacks.
- Produces: semantic UI events only: `record-free-account`, `add-statement`, `rebuild-timeline`, `switch-to-search`.

- [ ] **Step 1: Add RU/EN copy keys and failing parity assertions**

Required concepts include:

```text
reconstruction.title
reconstruction.free_account.title
reconstruction.free_account.prompt
reconstruction.free_account.saved
reconstruction.statement.type.recollection
reconstruction.statement.type.habit
reconstruction.statement.type.observation
reconstruction.timeline.title
reconstruction.timeline.unknowns
reconstruction.timeline.contradictions
reconstruction.to_search
reconstruction.free_account_required
```

- [ ] **Step 2: Build `FreeAccountCard`**

The prompt must remain neutral and must not list candidate rooms/containers/actions. Once saved, display the original free account read-only; later corrections go through structured statements rather than overwriting it.

- [ ] **Step 3: Build `StatementCapture`**

Only enable after `hasFreeAccount`. Require the user to choose/confirm statement type. Do not expose assistant as a source option.

- [ ] **Step 4: Build `TimelineEditor` and `TimelineSummary`**

Editor submits user-confirmed event/reference structure; Summary renders canonical `events`, `unknown_intervals`, and `contradictions`. No browser-side contradiction inference.

- [ ] **Step 5: Build `ReconstructionPanel` orchestration**

Panel remains state-first: free account → structured evidence → timeline → explicit Search transition. It is not a chat transcript UI.

- [ ] **Step 6: Verify keyboard/semantic accessibility in component tests where practical**

Use labels, headings, `aria-live` only for state updates that need announcement, and text/icon/treatment—not color alone—to identify reconstruction vs Search.

- [ ] **Step 7: Run unit/i18n tests**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/i18n.spec.ts apps/web/tests/unit/reconstruction.spec.ts
```

- [ ] **Step 8: Commit**

```bash
git add apps/web/app/components apps/web/app/lib/i18n apps/web/tests/unit
git commit -m "feat: add deterministic reconstruction interface"
```

### Task 8: Integrate reconstruction into the Case page without expanding page-domain logic

**Files:**
- Modify: `apps/web/app/pages/cases/[id].vue`
- Modify if needed: `apps/web/app/components/CaseShell.vue`
- Test: `apps/web/tests/e2e/reconstruction-flow.spec.ts`
- Test: `apps/web/tests/e2e/accessibility.spec.ts`

**Interfaces:**
- Consumes: `ReconstructionPanel`, existing `runCommand`, `CaseV2` lifecycle/state.
- Produces: real Web reconstruction instead of `web-reconstruction-unavailable` placeholder.

- [ ] **Step 1: Add failing browser test for entering reconstruction**

The test should create/open an active Case, select reconstruction, see the neutral free-account UI, and confirm no Search proposal is requested while reconstruction is active.

- [ ] **Step 2: Replace the unavailable boundary**

For active `current_mode === 'reconstruction'`, mount `ReconstructionPanel` instead of `web-reconstruction-unavailable`.

For `unselected`, offer an explicit mode choice that includes reconstruction and Search; selecting reconstruction sends `set_mode(reconstruction)`.

- [ ] **Step 3: Wire panel events to canonical commands**

Use the same immutable command envelope/retry semantics as Search. Do not create a second command execution helper that bypasses `runCommand`/local execution receipts.

- [ ] **Step 4: Keep Search proposal behavior strictly mode-gated**

`refreshProposal()` remains Search-only. Reconstruction does not accidentally call live assistant proposal endpoints in 0.4.0 core.

- [ ] **Step 5: Run browser tests**

```bash
pnpm --dir apps/web exec playwright test apps/web/tests/e2e/reconstruction-flow.spec.ts apps/web/tests/e2e/accessibility.spec.ts
```

- [ ] **Step 6: Commit**

```bash
git add apps/web/app/pages/cases/'[id].vue' apps/web/app/components apps/web/tests/e2e
git commit -m "feat: enable reconstruction in web cases"
```

### Task 9: Verify Case v2 export/import, reload/resume, and offline reconstruction

**Files:**
- Modify tests as required: `apps/web/tests/unit/exportImport.spec.ts`
- Create/modify: `apps/web/tests/e2e/reconstruction-offline.spec.ts`
- Modify: `apps/web/tests/e2e/helpers.ts` only for reusable setup helpers
- Production storage/export code only if a failing test proves a gap.

**Interfaces:**
- Consumes: existing Case v2 export/import and IndexedDB repository.
- Produces: evidence that reconstruction state survives portability/offline boundaries without schema change.

- [ ] **Step 1: Add export/import round-trip test**

Fixture must include:

```text
free_account journal entry
user statements
canonical timeline with unknown_intervals/contradictions
current_mode=reconstruction
```

Expected imported object: semantically/exactly preserved under Case v2 validation.

- [ ] **Step 2: Add reload/resume Playwright test**

Record free account + statement + timeline, reload, and assert the same canonical state renders from IndexedDB.

- [ ] **Step 3: Add preload→offline reconstruction vertical slice**

Canonical path:

```text
online preload
create/open Case
enter reconstruction
browser context offline
record free account
add confirmed statement
rebuild timeline
switch to Search
add/check a deterministic target
close or leave resumable
```

No Case API network request may be required for deterministic mutations.

- [ ] **Step 4: Run focused tests**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/exportImport.spec.ts
pnpm --dir apps/web exec playwright test apps/web/tests/e2e/reconstruction-offline.spec.ts
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/tests apps/web/app/lib/storage apps/web/app/composables
git commit -m "test: prove reconstruction portability and offline continuity"
```

### Task 10: Close production reachability and regression gates

**Files:**
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify tests: repository contract/reachability modules under `tests/`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/GETTING_STARTED.en.md`

**Interfaces:**
- Consumes: Tasks 1–9 production paths.
- Produces: exact requirement→production→test trace and accurate RU/EN public documentation.

- [ ] **Step 1: Replace provisional reconstruction selectors with exact production/test selectors**

Every `MD-WEB-REQ-RECONSTRUCT-*` row must point to actual symbols/components/tests now present.

- [ ] **Step 2: Add/extend reachability tests**

A helper existing in a file is insufficient; tests must prove the command/component is used by the production flow.

- [ ] **Step 3: Update architecture/public docs**

Remove the statement that Web reconstruction is unavailable. Describe raw-free-account provenance, canonical timeline execution, offline reconstruction, and explicit transition to Search. Preserve all non-goals.

- [ ] **Step 4: Run the complete local gate**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py --changed-files-file /tmp/changed-files.txt
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
python -m compileall -q plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
ruff check .
MYPYPATH=plugins/mind-detective:apps/api mypy --explicit-package-bases plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all green; generated artifacts/corpus clean after regeneration.

- [ ] **Step 5: Commit**

```bash
git add docs README.md README.en.md tests
git commit -m "docs: document web reconstruction contract"
```

### Task 11: Prepare 0.4.0 version/release declaration only after implementation is green

**Files:**
- Modify version surfaces validated by `scripts/validate_repo.py`
- Create: `.github/releases/0.4.0.md`
- Modify: `.github/releases/release.json`
- Modify RU/EN CHANGELOG/version docs if present in current repository policy
- Test: repository release/version contract tests under `tests/`

**Interfaces:**
- Consumes: fully green implementation head.
- Produces: declarative `0.4.0` repository/plugin release intent; publication remains a separate human authorization gate.

- [ ] **Step 1: Write failing version/release contract test for 0.4.0 surfaces**

Expected tags:

```text
repository: 0.4.0
plugin: mind-detective-v0.4.0
```

- [ ] **Step 2: Update all version SSOT/dependent surfaces consistently**

Do not hardcode historical/current version assertions in generic validators where SSOT lookup is appropriate.

- [ ] **Step 3: Write release notes that state actual delivered scope**

Include deterministic Web reconstruction, free-account provenance, canonical timeline, offline continuity, and retained non-goals. Do not claim assistant reconstruction superiority.

- [ ] **Step 4: Run complete CI-equivalent gate again**

Use the commands from Task 10.

- [ ] **Step 5: Open final implementation PR and require exact-head CI**

Do not merge until exact-head CI is successful.

- [ ] **Step 6: After explicit merge authorization, merge using merge commit and require exact-main CI**

- [ ] **Step 7: Stop at release authorization gate**

Do not dispatch `Publish current declared release` until the user separately authorizes publication of exact verified `main` SHA.
