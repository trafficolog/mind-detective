# Web Reconstruction 0.4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make reconstruction a first-class deterministic/offline Web workflow from raw free account through uncertainty-preserving timeline and explicit transition to the existing Search/checklist flow.

**Architecture:** Python portable semantics remain authoritative. Add `record_free_account` and `rebuild_timeline` to the portable command surface, regenerate the committed TypeScript executor/conformance corpus, then build focused Vue components that collect inputs and render canonical Case state. AI clarification is not required for 0.4.0 and never mutates memory evidence.

**Tech Stack:** Python 3.10/3.13, stdlib-first domain kernel, deterministic Python→TypeScript generator, Nuxt 4/Vue, TypeScript, IndexedDB, Vitest, Playwright, PWA, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`

## Global Constraints

- Keep `mind-detective-case/v2`; no Case v3.
- No handwritten Web Case reducer or independent timeline semantics.
- Raw free account is verbatim `author=user`, `mode=reconstruction`, `entry_type=free_account`; it is not auto-classified.
- Duplicate free-account recording fails closed with `MD_RECONSTRUCTION_FREE_ACCOUNT_EXISTS`; the gate-opening account is immutable.
- Reconstruction `add_statement` before free account fails with `MD_RECONSTRUCTION_FREE_ACCOUNT_REQUIRED`.
- Assistant output cannot originate recollection/habit/observation or directly mutate canonical Case.
- Preserve unknowns/contradictions; do not resolve by plausibility.
- Do not seed unsupported concrete locations during reconstruction.
- No Bayesian/POD state, calibrated location probabilities, hidden belief weights, cloud Case DB/sync, or cross-case learning.
- Deterministic reconstruction works offline after preload.
- RU/EN copy has exact key parity and equivalent safety/privacy semantics.
- Every active requirement has an exact production-reachability selector in `docs/CONTRACT_MATRIX.json`.
- TDD per task: failing focused test → minimal implementation → focused green → broader regression gate → review/commit.

---

### Task 1: Define executable Web reconstruction contracts

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_contract_reachability.py`

**Interfaces:**
- Consumes: existing `MD-WEB-REQ-*` contract format.
- Produces: stable reconstruction requirement IDs used by all later tasks.

Use exactly:

```text
MD-WEB-REQ-RECONSTRUCT-01 free account precedes structured reconstruction statements
MD-WEB-REQ-RECONSTRUCT-02 raw free account preserves user provenance without auto-classification
MD-WEB-REQ-RECONSTRUCT-03 unsupported concrete locations are not seeded as reconstruction cues
MD-WEB-REQ-RECONSTRUCT-04 timeline preserves unknown intervals and contradictions canonically
MD-WEB-REQ-RECONSTRUCT-05 reconstruction mutation uses generated portable local execution
MD-WEB-REQ-RECONSTRUCT-06 reconstruction and Search remain semantically/visually distinct
MD-WEB-REQ-RECONSTRUCT-07 transition to Search does not promote evidence
MD-WEB-REQ-RECONSTRUCT-08 deterministic reconstruction works offline after preload
MD-WEB-REQ-RECONSTRUCT-09 RU/EN copy has semantic/key parity
MD-WEB-REQ-RECONSTRUCT-10 Case v2 export/import preserves reconstruction state
```

- [ ] **Step 1: Add failing matrix/reachability assertions**

```python
for requirement_id in RECONSTRUCTION_REQUIREMENTS:
    row = matrix[requirement_id]
    self.assertEqual(row["status"], "active")
    self.assertTrue(row["selectors"])
```

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_contract_matrix tests.test_contract_reachability -v
```

Expected: missing reconstruction requirements/selectors.

- [ ] **Step 3: Add requirements and selectors targeting the exact symbols/tests specified in Tasks 2–9**

The implementation branch may remain red until those targets exist; unresolved selectors must be impossible at final merge.

- [ ] **Step 4: Commit the contract delta**

```bash
git add docs/REQUIREMENTS.md docs/CONTRACT_MATRIX.json tests/test_contract_matrix.py tests/test_contract_reachability.py
git commit -m "contract: define web reconstruction requirements"
```

### Task 2: Implement canonical `record_free_account`

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- Produces: command `record_free_account`; `record_free_account_json(case, entry_id, text, now) -> dict[str, object]`; `CaseController.record_free_account(...) -> Case`.

- [ ] **Step 1: Write RED tests for the exact journal shape**

```python
result = record_free_account_json(case_in_reconstruction, "entry-1", "Последний раз помню...", NOW)
entry = result["interaction_journal"][-1]
assert entry["author"] == "user"
assert entry["mode"] == "reconstruction"
assert entry["entry_type"] == "free_account"
assert entry["text"] == "Последний раз помню..."
assert result["statements"] == []
```

Also test empty id/text, wrong mode, paused/terminal Case, duplicate account → `MD_RECONSTRUCTION_FREE_ACCOUNT_EXISTS`, and reconstruction statement before free account → `MD_RECONSTRUCTION_FREE_ACCOUNT_REQUIRED`.

- [ ] **Step 2: Run only the two test files and confirm RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller.py' -v
```

- [ ] **Step 3: Extend portable contract**

```python
SUPPORTED_COMMAND_TYPES = (..., "record_free_account", ...)
```

and:

```python
"record_free_account": frozenset({"entry_id", "text"})
```

- [ ] **Step 4: Implement canonical mutation and free-account-first guard**

Use `_primitive_copy`, require active reconstruction mode, append one immutable journal entry, create no Statement, and gate reconstruction-mode `add_statement`. Search-mode `add_statement` remains unchanged.

- [ ] **Step 5: Add controller safety ingress**

```python
def record_free_account(self, case: Case, entry_id: str, text: str, now: str) -> Case:
    self._enforce_safe_ingress(text)
    ...
```

- [ ] **Step 6: Run plugin + repository regressions**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
python -m unittest discover -s tests -v
```

- [ ] **Step 7: Commit**

```bash
git add plugins/mind-detective/scripts plugins/mind-detective/tests
git commit -m "feat: add canonical free account command"
```

### Task 3: Make timeline rebuild portable and canonical

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_contract.py`
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/timeline.py`
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/tests/test_timeline.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`

**Interfaces:**
- Produces: `rebuild_timeline`; `rebuild_timeline_json(case, payload, now) -> dict[str, object]`; typed controller delegation to the same semantics.

Canonical payload:

```json
{
  "events": [{
    "id": "event-1",
    "label": "Вышел из машины",
    "statement_ids": ["statement-1"],
    "event_time": null,
    "time_precision": "unknown"
  }],
  "last_supported_interaction_id": "statement-1",
  "first_noticed_missing_id": "statement-2"
}
```

- [ ] **Step 1: Add RED tests**

Cover success, missing statement refs, duplicate event ids, free-account requirement, wrong mode/lifecycle, unknown intervals, time-order contradiction, invalid timestamps, and atomic failure.

- [ ] **Step 2: Confirm RED**

```bash
python -m unittest discover -s plugins/mind-detective/tests -p 'test_timeline.py' -v
python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v
```

- [ ] **Step 3: Add command allowlist**

```python
"rebuild_timeline": frozenset({"events", "last_supported_interaction_id", "first_noticed_missing_id"})
```

- [ ] **Step 4: Reuse/refactor `build_timeline()` for canonical derivation**

The browser must never own contradiction/unknown inference.

- [ ] **Step 5: Move `CaseController` timeline mutation onto the portable function**

Remove the separate reducer mutation as the authoritative path; adapters may remain only if they delegate the same semantics.

- [ ] **Step 6: Run all plugin tests and commit**

```bash
python -m unittest discover -s plugins/mind-detective/tests -v
git add plugins/mind-detective/scripts plugins/mind-detective/tests
git commit -m "feat: make timeline rebuild portable and canonical"
```

### Task 4: Regenerate executor and add differential conformance

**Files:**
- Modify: `plugins/mind-detective/scripts/conformance_vectors.py`
- Modify exact generator/certifier files only if new Python constructs require certified support
- Regenerate: `apps/web/app/generated/localExecution.ts`
- Regenerate: `apps/web/app/generated/localExecution.meta.json`
- Regenerate: `conformance/local-execution/v1/manifest.json`
- Regenerate: `conformance/local-execution/v1/vectors.json`
- Modify: `apps/web/tests/unit/localExecutionConformance.spec.ts`
- Modify as required: `tests/test_local_execution_generator.py`, `tests/test_local_execution_emitter.py`, `tests/test_local_execution_corpus.py`

**Interfaces:**
- Produces: Python↔generated-TypeScript parity for both commands and their stable failures.

- [ ] **Step 1: Add vectors for free-account success/wrong-mode/duplicate/gate and timeline success/unknown/contradiction/missing-ref**
- [ ] **Step 2: Run Python generator/corpus tests and verify initial RED where unsupported**

```bash
python -m unittest tests.test_local_execution_generator tests.test_local_execution_emitter tests.test_local_execution_corpus -v
```

- [ ] **Step 3: Extend the certified generator minimally; do not globally relax AST restrictions**
- [ ] **Step 4: Regenerate artifacts**

```bash
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
```

- [ ] **Step 5: Verify reproducibility and TS parity**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
pnpm --dir apps/web exec vitest run apps/web/tests/unit/localExecutionConformance.spec.ts
```

- [ ] **Step 6: Commit generated and source changes together**

### Task 5: Extend typed Web local execution

**Files:**
- Modify: `apps/web/app/lib/api/contracts.ts`
- Modify: `apps/web/app/lib/execution/localExecutor.ts`
- Modify: `apps/web/app/composables/useLocalExecution.ts`
- Modify: `apps/web/tests/unit/localExecutor.spec.ts`
- Modify: `apps/web/tests/unit/localStorageContract.spec.ts`

**Interfaces:**
- Produces typed `record_free_account` and `rebuild_timeline` envelopes through the existing atomic IndexedDB/receipt path.

- [ ] **Step 1: Add RED tests for command execution, atomic persistence, idempotent retry, and command-id conflict**
- [ ] **Step 2: Confirm RED**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/localExecutor.spec.ts apps/web/tests/unit/localStorageContract.spec.ts
```

- [ ] **Step 3: Extend `CommandEnvelope` command union/payload types in `contracts.ts`**
- [ ] **Step 4: Pass both commands through existing `localExecutor.ts`/`useLocalExecution.ts`; add no handwritten reconstruction reducer**
- [ ] **Step 5: Run focused tests and commit**

### Task 6: Add reconstruction presentation/view-model helpers

**Files:**
- Create: `apps/web/app/lib/case/reconstruction.ts`
- Create: `apps/web/app/composables/useReconstruction.ts`
- Create: `apps/web/tests/unit/reconstruction.spec.ts`

**Interfaces:**
- Produces only pure derivations and command builders.

Required pure functions:

```ts
export function freeAccountEntry(caseValue: CaseV2): JournalEntryV2 | null
export function hasFreeAccount(caseValue: CaseV2): boolean
export function reconstructionStatements(caseValue: CaseV2): StatementV2[]
export function timelineView(caseValue: CaseV2): TimelineV2 | null
```

- [ ] **Step 1: Test free-account detection and prove raw prose is never parsed into Statements**
- [ ] **Step 2: Implement pure derivations**
- [ ] **Step 3: Test exact command builders for `record_free_account`, `add_statement`, `rebuild_timeline`, `set_mode(search)`**
- [ ] **Step 4: Implement `useReconstruction` as a thin envelope/event helper; execution remains owned by existing Case-page/local execution path**
- [ ] **Step 5: Run**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/reconstruction.spec.ts
```

### Task 7: Build focused reconstruction components and bilingual copy

**Files:**
- Create: `apps/web/app/components/ReconstructionPanel.vue`
- Create: `apps/web/app/components/FreeAccountCard.vue`
- Create: `apps/web/app/components/StatementCapture.vue`
- Create: `apps/web/app/components/TimelineEditor.vue`
- Create: `apps/web/app/components/TimelineSummary.vue`
- Modify: `apps/web/app/lib/i18n/ru.ts`
- Modify: `apps/web/app/lib/i18n/en.ts`
- Modify: `apps/web/tests/unit/i18n.spec.ts`
- Modify: `apps/web/tests/unit/reconstruction.spec.ts`

**Interfaces:**
- Emits semantic events only: `record-free-account`, `add-statement`, `rebuild-timeline`, `switch-to-search`.

Required copy keys include:

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

- [ ] **Step 1: Add RU/EN parity tests and copy keys**
- [ ] **Step 2: Implement neutral `FreeAccountCard`; no candidate rooms/containers/actions in its prompt**
- [ ] **Step 3: Implement `StatementCapture`, disabled until free account exists; source is always user**
- [ ] **Step 4: Implement `TimelineEditor` input only and `TimelineSummary` canonical output only**
- [ ] **Step 5: Implement state-first `ReconstructionPanel`; no chat-first transcript architecture**
- [ ] **Step 6: Verify reconstruction/Search distinction uses text/icon/structure, not color alone**
- [ ] **Step 7: Run unit/i18n tests and commit**

### Task 8: Integrate the real reconstruction flow into Case page

**Files:**
- Modify: `apps/web/app/pages/cases/[id].vue`
- Create: `apps/web/tests/e2e/reconstruction-flow.spec.ts`
- Modify: `apps/web/tests/e2e/accessibility.spec.ts`

**Interfaces:**
- Replaces `web-reconstruction-unavailable` with `ReconstructionPanel`; reuses existing `runCommand` retry/receipt behavior.

- [ ] **Step 1: Add RED browser journey: select reconstruction → free account UI → no Search proposal call**
- [ ] **Step 2: For `unselected`, present explicit reconstruction/Search mode choice**
- [ ] **Step 3: For active reconstruction mode, mount `ReconstructionPanel` and wire emitted events to canonical local commands**
- [ ] **Step 4: Keep `refreshProposal()` strictly Search-only**
- [ ] **Step 5: Run**

```bash
pnpm --dir apps/web exec playwright test apps/web/tests/e2e/reconstruction-flow.spec.ts apps/web/tests/e2e/accessibility.spec.ts
```

- [ ] **Step 6: Commit**

### Task 9: Prove Case v2 portability, reload/resume, and offline reconstruction

**Files:**
- Modify: `apps/web/tests/unit/exportImport.spec.ts`
- Create: `apps/web/tests/e2e/reconstruction-offline.spec.ts`
- Modify: `apps/web/tests/e2e/helpers.ts` only for reusable setup
- Modify production storage/export code only if a RED test demonstrates a real gap

- [ ] **Step 1: Round-trip Case v2 fixture containing free account, statements, timeline unknowns/contradictions, and `current_mode=reconstruction`**
- [ ] **Step 2: Reload after free account + statement + timeline and assert identical canonical IndexedDB state renders**
- [ ] **Step 3: Preload online, go offline, then run `record free account → add statement → rebuild timeline → switch to Search → deterministic check` with no Case API mutation dependency**
- [ ] **Step 4: Run**

```bash
pnpm --dir apps/web exec vitest run apps/web/tests/unit/exportImport.spec.ts
pnpm --dir apps/web exec playwright test apps/web/tests/e2e/reconstruction-offline.spec.ts
```

### Task 10: Close reachability, docs, and full regression gates

**Files:**
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_contract_reachability.py`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/GETTING_STARTED.en.md`

- [ ] **Step 1: Replace all provisional reconstruction selectors with exact production/test selectors**
- [ ] **Step 2: Add reachability assertions proving commands/components are in the production path**
- [ ] **Step 3: Update RU/EN docs: Web reconstruction is now available; raw free-account provenance, portable timeline, offline boundary, and retained non-goals must be explicit**
- [ ] **Step 4: Build changed-files input and run full CI-equivalent gate**

```bash
git diff --name-only main...HEAD > /tmp/changed-files.txt
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

Expected: all green and generated artifacts/corpus clean.

### Task 11: Declare 0.4.0 only after implementation is green

**Files:**
- Modify version SSOT/dependent surfaces enforced by `scripts/validate_repo.py`
- Create: `.github/releases/0.4.0.md`
- Modify: `.github/releases/release.json`
- Modify: `tests/test_release_contract.py`
- Modify RU/EN release/version docs required by current policy

**Interfaces:**
- Produces declarative repository tag `0.4.0` and plugin tag `mind-detective-v0.4.0`; publication remains a separate human authorization gate.

- [ ] **Step 1: Add RED release-contract assertions for 0.4.0 declaration**
- [ ] **Step 2: Update version surfaces consistently; validators should derive current version from SSOT rather than hardcode history**
- [ ] **Step 3: Write release notes describing only delivered scope and retained non-goals**
- [ ] **Step 4: Re-run Task 10 full gate**
- [ ] **Step 5: Open implementation PR and require exact-head CI**
- [ ] **Step 6: Merge only after explicit merge authorization, then require exact-main CI**
- [ ] **Step 7: Stop at a separate release authorization gate; do not dispatch the canonical publisher without explicit approval of the exact verified main SHA**
