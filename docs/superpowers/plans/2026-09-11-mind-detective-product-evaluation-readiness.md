# Product Evaluation Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an explicit, privacy-safe evaluation mode that can run the approved staged B↔C crossover and real-pilot assignment, export analyzable local data, and reconstruct every decision-gate metric without changing `Case v2` or deterministic kernel semantics.

**Architecture:** Keep evaluation as a sibling subsystem to the Case/kernel path. A versioned IndexedDB evaluation store owns participants, immutable assignments, sessions, and privacy-filtered events; the normal product arm remains build-configured unless an explicit evaluation session is bound to a Case. Browser instrumentation produces only categorical/identifier/timing data, while a stdlib-only Python analysis CLI validates exports and computes reproducible metrics; arm A remains external and enters only through the common analysis contract.

**Tech Stack:** Nuxt 4.5.2, Vue 3.5.38, IndexedDB, Vitest 5, Playwright 1.63, Python 3.10/3.13 stdlib, `unittest`, Ruff, Mypy.

**Spec:** `docs/superpowers/specs/2026-09-11-mind-detective-product-evaluation-design.md`

## Global Constraints

- `Case` schema remains exactly `mind-detective-case/v2`; no Case migration is introduced.
- Portable Python kernel and generated TypeScript executor semantics remain unchanged.
- Evaluation contract is `mind-detective-evaluation/v1` and is stored separately from Case data.
- Evaluation mode is explicit and disabled by default; ordinary users are never silently randomized.
- Arm A remains external to the Web/PWA; no fake A application route is created.
- Staged assignments use the corrected four-cell matrix in the spec; every participant receives two B and two C tasks and each family receives all four arm×variant combinations across cells.
- Real-pilot B/C assignment is 1:1, case-level, immutable, and never reclassified after fallback.
- Evaluation data is local-only by default; export is an explicit action.
- Evaluation data must reject item/location text, Case payloads, journal/statement/user text, evaluator free text, and raw model output.
- No Bayesian/POD/location probability state is introduced.
- No release manifest/version/tag/release change is part of this plan.

---

## File structure to create or modify

### Evaluation domain

- Create `apps/web/app/lib/eval/contracts.ts` — versioned participant/session/event/export types and bounded metadata validators.
- Create `apps/web/app/lib/eval/store.ts` — IndexedDB v2 persistence for participants, sessions, and events with immutable-assignment guards.
- Modify `apps/web/app/lib/eval/log.ts` — delegate persistence/validation to the new contract/store and require an evaluation session for new evaluation events.
- Create `apps/web/app/lib/eval/assignment.ts` — staged counterbalance and real 1:1 assignment engine.
- Create `apps/web/app/composables/useEvaluationSession.ts` — explicit evaluation context, Case binding, and effective B/C arm resolution.

### Evaluation UI

- Modify `apps/web/nuxt.config.ts` — add disabled-by-default `mindDetectiveEvaluationEnabled` public config.
- Create `apps/web/app/pages/evaluation/index.vue` — evaluator dashboard / staged or real session start / explicit export.
- Create `apps/web/app/pages/evaluation/observer/[sessionId].vue` — staged proposal annotation and S4 rubric console.
- Create `apps/web/app/components/evaluation/EvaluationStartPanel.vue` — participant/session start controls.
- Create `apps/web/app/components/evaluation/EvaluationPostCaseRatings.vue` — fixed 1–5 task-load/convenience form.
- Create `apps/web/app/components/evaluation/EvaluationAbandonAction.vue` — evaluation-only abandonment without changing Case lifecycle.
- Create `apps/web/app/components/evaluation/EvaluationExportActions.vue` — explicit privacy-safe JSON/CSV export.
- Modify `apps/web/app/components/case/CreateCaseForm.vue` — optionally bind a pre-created evaluation session after canonical Case creation.
- Modify `apps/web/app/pages/cases/[id].vue` — resolve evaluation arm and emit session-scoped instrumentation.

### Analysis and protocol

- Create `scripts/analyze_evaluation.py` — stdlib-only export validation, session reconstruction, RMTUA, clustered bootstrap, safety/readiness/sample summaries.
- Create `tests/test_evaluation_analysis.py` — deterministic analysis fixtures and gate-input tests.
- Create `tests/fixtures/evaluation/staged-v1.json` — privacy-safe staged fixture including completed, abandoned, fallback, and incomplete-protocol data.
- Create `tests/fixtures/evaluation/external-a-v1.json` — external A input example using the common export shape.
- Update `docs/PRODUCT_EVALUATION.md` — point to the executable protocol and clarify engineering-vs-causal evidence.
- Create `docs/evaluation/STAGED_PROTOCOL.md` — physical/evaluator procedure for S1–S4 and enrollment slot assignment.
- Create `docs/evaluation/REAL_PILOT_PROTOCOL.md` — eligibility/exclusion/consent and analytic separation.
- Create `docs/evaluation/EXTERNAL_A_PROTOCOL.md` — ordinary-search baseline procedure and common input fields.
- Create `docs/evaluation/ANALYSIS.md` — CLI usage and interpretation rules.

### Tests

- Create `apps/web/tests/unit/evaluationContracts.spec.ts`.
- Extend `apps/web/tests/unit/evalLog.spec.ts`.
- Create `apps/web/tests/unit/evaluationAssignment.spec.ts`.
- Create `apps/web/tests/unit/evaluationStore.spec.ts`.
- Create `apps/web/tests/e2e/evaluation-flow.spec.ts`.
- Create `apps/web/tests/e2e/evaluation-privacy.spec.ts`.
- Modify `apps/web/tests/e2e/helpers.ts` — seed/read evaluation IndexedDB stores for deterministic browser tests.

No `.github/workflows/ci.yml` change is required: existing Web/unit/e2e and Python unittest/compile/Ruff/Mypy jobs automatically include these files.

---

### Task 1: Versioned evaluation contract and fail-closed local store

**Files:**
- Create: `apps/web/app/lib/eval/contracts.ts`
- Create: `apps/web/app/lib/eval/store.ts`
- Modify: `apps/web/app/lib/eval/log.ts`
- Create: `apps/web/tests/unit/evaluationContracts.spec.ts`
- Create: `apps/web/tests/unit/evaluationStore.spec.ts`
- Modify: `apps/web/tests/unit/evalLog.spec.ts`

**Interfaces:**
- Produces `EvaluationParticipantV1`, `EvaluationSessionV1`, `EvaluationEventV1`, `EvaluationExportV1`.
- Produces `createEvaluationParticipant()`, `createEvaluationSession()`, `bindEvaluationSessionCase()`, `completeEvaluationSession()`, `getEvaluationSessionByCaseId()`, `appendEvaluationEvent()`, `buildEvaluationExport()`.
- Later tasks consume only these APIs; they do not open evaluation IndexedDB directly.

- [ ] **Step 1: Write contract tests for bounded values and sensitive-field rejection**

Add cases equivalent to:

```ts
expect(validateRating(1)).toBe(1)
expect(validateRating(5)).toBe(5)
expect(() => validateRating(0)).toThrow('MD_WEB_EVAL_RATING')
expect(() => validateEventMetadata('next_action_shown', { target: 'рюкзак' }))
  .toThrow('MD_WEB_EVAL_SENSITIVE_FIELD')
expect(() => validateEventMetadata('next_action_shown', { unknown: true }))
  .toThrow('MD_WEB_EVAL_FIELD')
```

Run:

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationContracts.spec.ts
```

Expected: FAIL because `contracts.ts` does not exist.

- [ ] **Step 2: Implement explicit v1 domain types and per-event metadata allowlists**

Use exact core unions:

```ts
export type EvaluationProtocol = 'staged' | 'real' | 'external_a'
export type EvaluationArm = 'A' | 'B' | 'C'
export type EvaluationOutcome = 'found' | 'unresolved' | 'abandoned'
export type ScenarioFamily = 'S1' | 'S2' | 'S3' | 'S4'
export type ScenarioVariant = 'A' | 'B'
export type CounterbalanceCell = 1 | 2 | 3 | 4
export const EVALUATION_SCHEMA = 'mind-detective-evaluation/v1' as const
export const EVALUATION_EXPORT_SCHEMA = 'mind-detective-evaluation-export/v1' as const
```

`EvaluationSessionV1` must keep assignment fields immutable and mutable completion fields separate:

```ts
export interface EvaluationSessionV1 {
  evaluation_schema: typeof EVALUATION_SCHEMA
  evaluation_session_id: string
  participant_id: string
  protocol: EvaluationProtocol
  arm: EvaluationArm
  assignment_version: 'eval-assignment/v1'
  counterbalance_cell: CounterbalanceCell | null
  scenario_family: ScenarioFamily | null
  scenario_variant: ScenarioVariant | null
  order_position: 1 | 2 | 3 | 4 | null
  case_id: string | null
  started_at: string | null
  ended_at: string | null
  outcome: EvaluationOutcome | null
}
```

Event metadata must be validated against an event-specific key map, not one global permissive set. Include only keys required by the spec: `case_id`, `candidate_id`, `proposal_id`, `mode`, `reason_code`, `guard_code`, `command_id`, `outcome_code`, `found_context`, `task_load`, `convenience`, the seven staged safety booleans, four handoff booleans, and `handoff_score`.

- [ ] **Step 3: Write IndexedDB migration/immutability tests**

Test that version 2 creates `participants`, `sessions`, and `events`, preserves an existing legacy `events` store, and refuses a second session create with the same id or any assignment-field mutation.

Expected immutable error code:

```ts
'MD_WEB_EVAL_ASSIGNMENT_IMMUTABLE'
```

Run:

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationStore.spec.ts
```

Expected: FAIL before `store.ts` exists.

- [ ] **Step 4: Implement IndexedDB v2 store with narrow mutation methods**

Use:

```ts
const DB_NAME = 'mind-detective-evaluation'
const DB_VERSION = 2
const PARTICIPANTS = 'participants'
const SESSIONS = 'sessions'
const EVENTS = 'events'
```

Create sessions with `add`, never `put`. Permit only these later mutations:

```ts
bindEvaluationSessionCase(sessionId, caseId, startedAt)
completeEvaluationSession(sessionId, outcome, endedAt)
```

`bindEvaluationSessionCase` may set `case_id`/`started_at` only once; repeating the same values is idempotent, different values fail closed.

Add an index on `sessions.case_id` (`unique: true`) for resume lookup and an index on `events.evaluation_session_id` (`unique: false`).

- [ ] **Step 5: Refactor `log.ts` onto the new store without preserving unrestricted ordinary logging**

Expose:

```ts
export function appendEvalEvent(
  evaluationSessionId: string,
  event: EvalEventName,
  metadata: Record<string, unknown> = {},
): Promise<void>
```

and explicit export helpers:

```ts
export async function buildEvaluationExport(): Promise<EvaluationExportV1>
export function exportEvalJson(bundle: EvaluationExportV1): Blob
export function exportEvalCsv(bundle: EvaluationExportV1): Blob
```

CSV must use one row per session/event record with a `record_type` column and JSON-encoded primitive metadata; it must never flatten Case content because Case data is absent from the bundle.

- [ ] **Step 6: Run focused and full Web unit tests**

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationContracts.spec.ts tests/unit/evaluationStore.spec.ts tests/unit/evalLog.spec.ts
pnpm --dir apps/web test
```

Expected: PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add apps/web/app/lib/eval apps/web/tests/unit/evaluationContracts.spec.ts apps/web/tests/unit/evaluationStore.spec.ts apps/web/tests/unit/evalLog.spec.ts
git commit -m "feat: add evaluation data contract and store"
```

---

### Task 2: Deterministic staged counterbalance and immutable real assignment

**Files:**
- Create: `apps/web/app/lib/eval/assignment.ts`
- Create: `apps/web/tests/unit/evaluationAssignment.spec.ts`

**Interfaces:**
- Consumes `EvaluationParticipantV1`, `EvaluationSessionV1`, `CounterbalanceCell`, `ScenarioFamily`, `ScenarioVariant`, `EvaluationArm` from Task 1.
- Produces `cellForEnrollmentSlot()`, `createStagedParticipantRecord()`, `nextStagedAssignment()`, `assignRealArm()`.

- [ ] **Step 1: Encode invariant tests before the table**

The test must prove all four invariants, not compare only a snapshot:

```ts
for (const cell of [1, 2, 3, 4] as const) {
  const assignments = STAGED_CELLS[cell]
  expect(assignments.filter(x => x.arm === 'B')).toHaveLength(2)
  expect(assignments.filter(x => x.arm === 'C')).toHaveLength(2)
}

for (const family of ['S1', 'S2', 'S3', 'S4'] as const) {
  const combinations = new Set(allAssignmentsFor(family).map(x => `${x.arm}/${x.variant}`))
  expect(combinations).toEqual(new Set(['B/A', 'B/B', 'C/A', 'C/B']))
}
```

Also assert first-arm balance: cells 1–2 begin with B; cells 3–4 begin with C.

Run and expect FAIL:

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationAssignment.spec.ts
```

- [ ] **Step 2: Implement the exact approved matrix**

Represent each cell in execution order:

```ts
export const STAGED_CELLS = {
  1: [
    { family: 'S1', arm: 'B', variant: 'A' },
    { family: 'S2', arm: 'C', variant: 'A' },
    { family: 'S3', arm: 'B', variant: 'A' },
    { family: 'S4', arm: 'C', variant: 'A' },
  ],
  2: [
    { family: 'S2', arm: 'B', variant: 'B' },
    { family: 'S3', arm: 'C', variant: 'B' },
    { family: 'S4', arm: 'B', variant: 'B' },
    { family: 'S1', arm: 'C', variant: 'A' },
  ],
  3: [
    { family: 'S3', arm: 'C', variant: 'A' },
    { family: 'S4', arm: 'B', variant: 'A' },
    { family: 'S1', arm: 'C', variant: 'B' },
    { family: 'S2', arm: 'B', variant: 'A' },
  ],
  4: [
    { family: 'S4', arm: 'C', variant: 'B' },
    { family: 'S1', arm: 'B', variant: 'B' },
    { family: 'S2', arm: 'C', variant: 'B' },
    { family: 'S3', arm: 'B', variant: 'B' },
  ],
} as const
```

- [ ] **Step 3: Implement enrollment-slot and next-session functions**

Use preassigned enrollment slot rather than evaluator-selected arm:

```ts
export function cellForEnrollmentSlot(slot: number): CounterbalanceCell {
  if (!Number.isInteger(slot) || slot < 1) throw new Error('MD_WEB_EVAL_ENROLLMENT_SLOT')
  return (((slot - 1) % 4) + 1) as CounterbalanceCell
}
```

`nextStagedAssignment(participant, existingSessions)` returns the first order position 1–4 for which no session record exists. It returns `null` after all four assignments have been created.

- [ ] **Step 4: Implement real assignment with injectable entropy for deterministic tests**

```ts
export function assignRealArm(randomByte?: number): 'B' | 'C' {
  const byte = randomByte ?? crypto.getRandomValues(new Uint8Array(1))[0]!
  return byte % 2 === 0 ? 'B' : 'C'
}
```

Test even→B, odd→C, and that assignment is stored once by Task 1 rather than recomputed on resume.

- [ ] **Step 5: Run focused/full unit tests and commit**

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationAssignment.spec.ts
pnpm --dir apps/web test
git add apps/web/app/lib/eval/assignment.ts apps/web/tests/unit/evaluationAssignment.spec.ts
git commit -m "feat: add evaluation assignment engine"
```

---

### Task 3: Explicit evaluation entry and Case-bound arm resolution

**Files:**
- Modify: `apps/web/nuxt.config.ts`
- Create: `apps/web/app/composables/useEvaluationSession.ts`
- Create: `apps/web/app/pages/evaluation/index.vue`
- Create: `apps/web/app/components/evaluation/EvaluationStartPanel.vue`
- Modify: `apps/web/app/components/case/CreateCaseForm.vue`
- Modify: `apps/web/app/pages/cases/[id].vue`
- Create: `apps/web/tests/e2e/evaluation-flow.spec.ts`
- Modify: `apps/web/tests/e2e/helpers.ts`

**Interfaces:**
- Consumes Tasks 1–2 store/assignment APIs.
- Produces `useEvaluationSession()` with `session`, `loadForCase()`, `effectiveProductArm()`, `startStagedSession()`, `startRealSession()`.
- Maps B→`checklist`, C→`assistant`; A is rejected as an application arm.

- [ ] **Step 1: Add failing browser tests proving evaluation is disabled by default**

Test normal `/` remains unchanged and `/evaluation` renders an unavailable message unless `NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION=1` is set in the evaluation Playwright webServer environment.

Do not add any random assignment to `/` or `CreateCaseForm` when no evaluation session id is supplied.

Run:

```bash
pnpm --dir apps/web exec playwright test tests/e2e/evaluation-flow.spec.ts --project=chromium
```

Expected: FAIL before route/config exists.

- [ ] **Step 2: Add disabled-by-default public config**

```ts
mindDetectiveEvaluationEnabled: process.env.NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION === '1',
```

The default remains `false`.

- [ ] **Step 3: Implement the evaluation context composable**

Core arm mapping:

```ts
function productArmForSession(session: EvaluationSessionV1): ExperimentalArm {
  if (session.arm === 'B') return 'checklist'
  if (session.arm === 'C') return 'assistant'
  throw new Error('MD_WEB_EVAL_EXTERNAL_ARM')
}
```

`loadForCase(caseId)` calls only `getEvaluationSessionByCaseId`; no randomization occurs on Case-page load.

- [ ] **Step 4: Build explicit start page**

Staged flow:

1. evaluator enters integer `enrollment_slot`;
2. create/reuse one pseudonymous staged participant record;
3. derive cell from slot;
4. create the next immutable session from `STAGED_CELLS`;
5. render family/variant/arm code for the evaluator;
6. render `CreateCaseForm` with `evaluation-session-id`.

Real flow:

1. create pseudonymous participant id;
2. call `assignRealArm()` once;
3. persist session;
4. render `CreateCaseForm` with that session id.

- [ ] **Step 5: Bind Case only after canonical local creation succeeds**

Add optional prop:

```ts
evaluationSessionId?: string | null
```

After `localExecution.createCase(...)` succeeds, call:

```ts
await bindEvaluationSessionCase(sessionId, caseValue.case_id, now)
await appendEvalEvent(sessionId, 'case_started', { case_id: caseValue.case_id })
```

If binding fails, do not emit `created`; show an evaluation binding error so an unbound Case is not analyzed as an assigned session.

- [ ] **Step 6: Resolve arm in the Case page without changing ordinary behavior**

Keep `useExperimentalArm()` as the ordinary build-level default. Add:

```ts
const defaultArm = useExperimentalArm()
const evaluation = useEvaluationSession()
const effectiveArm = computed(() => evaluation.session.value
  ? evaluation.effectiveProductArm(evaluation.session.value)
  : defaultArm.value)
```

Replace proposal calls/provider disclosure checks to use `effectiveArm`. A reload calls `loadForCase(caseId)` and therefore restores stored assignment instead of recomputing it.

- [ ] **Step 7: Extend Playwright helpers to seed evaluation DB v2**

Add `seedEvaluationParticipant`, `seedEvaluationSession`, `storedEvaluationSession`, opening `mind-detective-evaluation` version 2 with the same stores/indexes as production.

- [ ] **Step 8: Prove assignment persistence in Chromium and WebKit**

Browser test must create one staged session, reload Case route, and assert the stored arm/session id remains identical. Add a C session that goes offline and assert it remains C after deterministic fallback.

Run:

```bash
pnpm --dir apps/web exec playwright test tests/e2e/evaluation-flow.spec.ts
```

Expected: PASS.

- [ ] **Step 9: Commit Task 3**

```bash
git add apps/web/nuxt.config.ts apps/web/app/composables/useEvaluationSession.ts apps/web/app/pages/evaluation apps/web/app/components/evaluation/EvaluationStartPanel.vue apps/web/app/components/case/CreateCaseForm.vue apps/web/app/pages/cases/[id].vue apps/web/tests/e2e/evaluation-flow.spec.ts apps/web/tests/e2e/helpers.ts
git commit -m "feat: add explicit evaluation session entry"
```

---

### Task 4: Reproducible instrumentation for useful action, duplicates, fallback, and outcomes

**Files:**
- Modify: `apps/web/app/pages/cases/[id].vue`
- Modify: `apps/web/app/lib/eval/contracts.ts`
- Modify: `apps/web/tests/unit/evaluationContracts.spec.ts`
- Extend: `apps/web/tests/e2e/evaluation-flow.spec.ts`

**Interfaces:**
- Consumes session-scoped `appendEvalEvent()`.
- Produces proposal linkage via random `proposal_id`; analysis later joins `next_action_shown` → rejection/check events without proposal text.

- [ ] **Step 1: Write e2e assertions for exact event sequence**

For an evaluation B Case:

```text
case_started
next_action_shown(proposal_id, candidate_id)
check_started(proposal_id, candidate_id)
check_finished(proposal_id, candidate_id)
found | case_closed_unresolved
```

For a prior-checked candidate, assert `duplicate_check_detected` is emitted after the repeated check completes.

For a C transport failure, assert `assistant_offline_fallback` exists while session arm remains C.

- [ ] **Step 2: Gate all Case-page evaluation logging on a bound evaluation session**

Replace fire-and-forget ordinary logging with:

```ts
function logEvaluationEvent(event: EvalEventName, metadata: Record<string, unknown> = {}): void {
  const sessionId = evaluation.session.value?.evaluation_session_id
  if (!sessionId) return
  void appendEvalEvent(sessionId, event, metadata).catch(() => undefined)
}
```

This ensures ordinary product use is not silently enrolled.

- [ ] **Step 3: Add proposal identity without storing target/copy**

Whenever a visible `next_action` is set, generate:

```ts
const proposalId = crypto.randomUUID()
currentProposalId.value = proposalId
logEvaluationEvent('next_action_shown', {
  case_id: current.case_id,
  candidate_id: next.candidate_id,
  proposal_id: proposalId,
  mode: current.current_mode,
})
```

Reject/check events reuse `currentProposalId`. Never persist `proposal.target`, `copy_key`, rationale text, or model output in evaluation metadata.

- [ ] **Step 4: Detect duplicates from canonical Case evidence before writing the new check**

Before `record_search_check`, compute:

```ts
const duplicate = current.search_checks.some(check =>
  check.completed_at !== null
  && action.candidate_id !== null
  && check.based_on.includes(action.candidate_id),
)
```

After successful command, emit `duplicate_check_detected` only when `duplicate` is true.

- [ ] **Step 5: Complete evaluation outcome with the Case close action**

After successful `close_found`:

```ts
await completeEvaluationSession(sessionId, 'found', new Date().toISOString())
```

After successful `close_unresolved`, use `unresolved`. Event and session completion must agree; unit/e2e tests assert mismatch attempts fail closed.

- [ ] **Step 6: Run focused browser/unit tests and commit**

```bash
pnpm --dir apps/web exec vitest run tests/unit/evaluationContracts.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/evaluation-flow.spec.ts
pnpm --dir apps/web test
git add apps/web/app/pages/cases/[id].vue apps/web/app/lib/eval/contracts.ts apps/web/tests/unit/evaluationContracts.spec.ts apps/web/tests/e2e/evaluation-flow.spec.ts
git commit -m "feat: instrument evaluation sessions"
```

---

### Task 5: Ratings, abandonment, staged observer rubric, and explicit export UI

**Files:**
- Create: `apps/web/app/components/evaluation/EvaluationPostCaseRatings.vue`
- Create: `apps/web/app/components/evaluation/EvaluationAbandonAction.vue`
- Create: `apps/web/app/components/evaluation/EvaluationExportActions.vue`
- Create: `apps/web/app/pages/evaluation/observer/[sessionId].vue`
- Modify: `apps/web/app/pages/evaluation/index.vue`
- Modify: `apps/web/app/pages/cases/[id].vue`
- Create: `apps/web/tests/e2e/evaluation-privacy.spec.ts`

**Interfaces:**
- Uses `post_case_rating`, `proposal_safety_annotation`, `handoff_rubric`, and `case_abandoned` events.
- Safety annotation is linked by `proposal_id`; no proposal text is copied into evaluation storage.

- [ ] **Step 1: Add failing privacy/evaluation UI browser tests**

Cover:

- ratings accept only integers 1–5;
- abandon marks evaluation outcome `abandoned` but leaves Case lifecycle unchanged;
- staged observer can annotate a proposal with booleans only;
- S4 observer can store exactly four booleans plus derived 0–4 score;
- export contains no item label, target string, journal text, user text, model text, or Case object;
- no network request is issued by append/store/export actions.

Run and expect FAIL:

```bash
pnpm --dir apps/web exec playwright test tests/e2e/evaluation-privacy.spec.ts --project=chromium
```

- [ ] **Step 2: Implement fixed post-case ratings**

Component emits:

```ts
{ taskLoad: 1 | 2 | 3 | 4 | 5, convenience: 1 | 2 | 3 | 4 | 5 }
```

Persist one event:

```ts
appendEvalEvent(sessionId, 'post_case_rating', {
  task_load: taskLoad,
  convenience,
})
```

Do not render a text area or notes field.

- [ ] **Step 3: Implement evaluation-only abandonment**

`EvaluationAbandonAction` calls:

```ts
await completeEvaluationSession(sessionId, 'abandoned', now)
await appendEvalEvent(sessionId, 'case_abandoned', { case_id })
```

It does not call a Case command and therefore does not add a new Case lifecycle state. Navigate back to `/evaluation` after success.

- [ ] **Step 4: Implement staged observer safety booleans**

For each unannotated `next_action_shown` proposal id, store exactly these booleans:

```ts
unsupported_fact
leading_suggestion
false_confidence
critical_location_assertion
critical_invented_recollection
critical_forgetting_diagnosis
critical_unsafe_action
```

`critical_violation` is derived in analysis as OR of the four critical booleans; it is not entered as free text.

- [ ] **Step 5: Implement S4 handoff rubric**

Fields:

```ts
mode_restored
prior_checks_preserved
journal_continuity
next_action_coherent
```

Store `handoff_score` as the integer sum 0–4. Reject the rubric event for any non-S4 staged session.

- [ ] **Step 6: Implement explicit evaluation exports on the dashboard**

Use `buildEvaluationExport()` only after button click. Download names:

```text
mind-detective-evaluation-<ISO-date>.json
mind-detective-evaluation-<ISO-date>.csv
```

Normal `CaseDataActions` remains unchanged and does not include evaluation data.

- [ ] **Step 7: Run browser privacy tests and all Web tests**

```bash
pnpm --dir apps/web exec playwright test tests/e2e/evaluation-privacy.spec.ts
pnpm --dir apps/web test
pnpm --dir apps/web exec playwright test
```

Expected: PASS.

- [ ] **Step 8: Commit Task 5**

```bash
git add apps/web/app/components/evaluation apps/web/app/pages/evaluation apps/web/app/pages/cases/[id].vue apps/web/tests/e2e/evaluation-privacy.spec.ts
git commit -m "feat: add evaluation measures and export"
```

---

### Task 6: Stdlib-only analysis pipeline and deterministic fixtures

**Files:**
- Create: `scripts/analyze_evaluation.py`
- Create: `tests/test_evaluation_analysis.py`
- Create: `tests/fixtures/evaluation/staged-v1.json`
- Create: `tests/fixtures/evaluation/external-a-v1.json`

**Interfaces:**
- CLI: `python -m scripts.analyze_evaluation INPUT.json [--external-a FILE.json] [--seed 1729] [--bootstrap 2000] [--json-out FILE]`.
- Produces privacy-safe aggregate JSON/report; it never reads Case files.

- [ ] **Step 1: Write failing schema and reconstruction tests**

Fixtures must include:

- at least two staged participants with both B/C sessions;
- one `abandoned` session;
- one C session with pre-useful-action fallback;
- one participant with incomplete protocol participation;
- one duplicate check;
- staged safety annotations;
- one S4 handoff rubric;
- an external A record.

Tests assert that all these sessions remain visible in ITT and denominator counts.

Run:

```bash
python -m unittest tests.test_evaluation_analysis -v
```

Expected: FAIL before the script exists.

- [ ] **Step 2: Implement strict export validation**

Use dataclasses/typed dictionaries from stdlib only. Reject:

- wrong export/evaluation schema;
- duplicate participant/session/event ids;
- event session id not present in sessions;
- staged B/C session missing cell/family/variant/order;
- `external_a` with arm other than A;
- application session with arm A;
- ratings outside 1–5;
- handoff score inconsistent with booleans;
- unknown event metadata keys.

Do not accept or inspect `item_label`, target, journal, user text, or raw model output fields.

- [ ] **Step 3: Reconstruct the first useful action deterministically**

For each session:

1. sort events by `(at, event_id)`;
2. start at `case_started`;
3. collect `next_action_shown` by `proposal_id`/`candidate_id`;
4. mark a proposal rejected if a matching rejection precedes its check completion;
5. first shown proposal that later reaches matching `check_finished` without prior rejection is the event time;
6. otherwise censor at terminal event or 600 seconds, whichever occurs first.

Expose:

```py
@dataclass(frozen=True)
class TimeObservation:
    seconds: float
    event_observed: bool
```

- [ ] **Step 4: Implement 10-minute Kaplan–Meier restricted mean**

Implement survival-step integration without third-party libraries:

```py
def restricted_mean_time(observations: Sequence[TimeObservation], horizon: float = 600.0) -> float:
    ...
```

Unit tests use hand-calculated fixtures, including all-censored and immediate-event cases.

- [ ] **Step 5: Implement participant-clustered bootstrap**

Sample participant ids with replacement; include all of each sampled participant’s staged sessions each draw. Recompute B and C RMTUA and rate differences. Use deterministic `random.Random(seed)` and percentile two-sided 95% intervals.

CLI default is `--bootstrap 2000`; unit tests use 100 draws and a fixed seed for speed.

- [ ] **Step 6: Compute explicit gate inputs without pretending ambiguous review is automatic**

The report must include:

```text
sample.protocol_complete_participants
sample.participants_per_cell
primary.rmtua_B_seconds
primary.rmtua_C_seconds
primary.percent_change_C_vs_B
primary.bootstrap_95_interval
secondary.task_load_difference
secondary.convenience_difference
secondary.duplicate_check_difference
outcomes.found/unresolved/abandoned_by_arm
safety.rate_differences_and_95_intervals
safety.critical_violation_count
readiness.pre_useful_fallback_rate_C
readiness.execution_contract_failure_count
```

Classify only rules with exact thresholds as `pass`/`fail`/`inconclusive`. Terminal-outcome imbalance remains a visible review flag because the approved spec deliberately does not invent a numeric staged threshold for “could plausibly explain the time effect”. Overall product direction therefore remains a reviewed conclusion, not a one-line automated claim.

- [ ] **Step 7: Prove arm A stays contextual**

With `--external-a`, include A summaries under `contextual_external_a`; never use A values in the C-vs-B efficacy/safety decision calculations.

- [ ] **Step 8: Run Python quality gates and commit**

```bash
python -m unittest tests.test_evaluation_analysis -v
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
ruff check scripts/analyze_evaluation.py tests/test_evaluation_analysis.py
mypy --explicit-package-bases scripts tests/test_evaluation_analysis.py
git add scripts/analyze_evaluation.py tests/test_evaluation_analysis.py tests/fixtures/evaluation
git commit -m "feat: add evaluation analysis pipeline"
```

---

### Task 7: Executable staged, real, external-A, and analysis protocol documentation

**Files:**
- Modify: `docs/PRODUCT_EVALUATION.md`
- Create: `docs/evaluation/STAGED_PROTOCOL.md`
- Create: `docs/evaluation/REAL_PILOT_PROTOCOL.md`
- Create: `docs/evaluation/EXTERNAL_A_PROTOCOL.md`
- Create: `docs/evaluation/ANALYSIS.md`
- Modify or create repository contract tests only if `scripts/validate_repo.py` requires references for new normative docs.

**Interfaces:**
- Documents the exact operator steps implemented in Tasks 1–6.
- Does not redefine thresholds independently from the approved spec.

- [ ] **Step 1: Write `STAGED_PROTOCOL.md` from the corrected matrix**

It must specify:

- enrollment slot is assigned before case content is viewed;
- `cell = ((slot - 1) mod 4) + 1`;
- exact four-cell order/arm/variant table from the spec;
- S1–S4 physical setup principles;
- fixed 10-minute observation horizon;
- observer annotation timing;
- terminal outcomes and ratings;
- incomplete/abandoned participation remains analyzable.

No participant-identifying field is requested.

- [ ] **Step 2: Write real-pilot eligibility/exclusion procedure**

Include explicit low-risk examples as categories rather than personal examples, high-stakes exclusions, immutable 1:1 assignment, and the rule that fallback remains C.

- [ ] **Step 3: Write external-A procedure**

Use the same staged family framing where applicable, but no application route and no hidden structured assistance. Document the JSON template fields accepted by `--external-a`.

- [ ] **Step 4: Write analysis runbook**

Commands:

```bash
python -m scripts.analyze_evaluation export.json --seed 1729 --bootstrap 2000 --json-out summary.json
python -m scripts.analyze_evaluation export.json --external-a external-a.json --json-out summary-with-a.json
```

State prominently: green fixtures prove machinery/reproducibility, not causal lift or scientific validity.

- [ ] **Step 5: Update `docs/PRODUCT_EVALUATION.md`**

Keep it short and canonical: link the approved design, four protocol docs, and analysis CLI; preserve the falsifiable “simplify if C does not lift over B” rule.

- [ ] **Step 6: Run repository validation and commit**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py
python -m unittest discover -s tests -v
git add docs/PRODUCT_EVALUATION.md docs/evaluation
git commit -m "docs: add Product Evaluation runbooks"
```

---

### Task 8: Full vertical verification and implementation-PR preparation

**Files:**
- Modify only files revealed by failing verification; no unrelated refactor.
- Update implementation PR body/checklist, not release files.

**Interfaces:**
- Verifies every `MD-EVAL-REQ-*` requirement against tests or a documented operator step.

- [ ] **Step 1: Run generated-artifact freshness gates before full test suite**

```bash
python -m scripts.write_local_execution_artifacts
git diff --exit-code -- apps/web/app/generated/localExecution.ts apps/web/app/generated/localExecution.meta.json
python -m scripts.generate_local_execution_corpus
git diff --exit-code -- conformance/local-execution/v1/manifest.json conformance/local-execution/v1/vectors.json
```

Expected: no diff, proving evaluation work did not alter kernel/generated semantics.

- [ ] **Step 2: Run full Python repository/API/plugin gates**

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py
python -m unittest discover -s tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python -m compileall -q plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
ruff check .
MYPYPATH=plugins/mind-detective:apps/api mypy --explicit-package-bases plugins/mind-detective/scripts scripts apps/api/mind_detective_api apps/api/tests
```

Expected: all green.

- [ ] **Step 3: Run full Web/PWA gates**

```bash
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all green in Chromium and WebKit.

- [ ] **Step 4: Run privacy grep against evaluation implementation/export fixtures**

```bash
grep -RInE 'item_label|raw_model_output|journal_text|statement_text|user_text|model_text' \
  apps/web/app/lib/eval tests/fixtures/evaluation
```

Expected: matches are limited to explicit denylist/test assertions, never exported fixture payload values. Manually inspect each match before accepting the gate.

- [ ] **Step 5: Map requirements to evidence in the implementation PR**

PR body must list all requirements from `MD-EVAL-REQ-BOUNDARY-01` through `MD-EVAL-REQ-RELEASE-01` and point to exact tests/docs. It must explicitly state:

```text
No release/version publication is requested by this implementation PR.
Engineering-green does not imply Product Evaluation lift.
```

- [ ] **Step 6: Verify exact implementation head CI before requesting merge authorization**

Record exact branch head SHA and require the pull-request CI run for that SHA to be completed/success across Python 3.10, Python 3.13, Web, and Secret scan.

Do not merge in this step. Merge requires a separate explicit user authorization after review.

- [ ] **Step 7: Commit any verification-only documentation changes**

```bash
git add docs
# Only if Task 8 produced documentation/evidence-map changes:
git commit -m "docs: record evaluation readiness verification"
```

If there is no Task-8 file change, do not create an empty commit.

---

## Implementation completion gate

The implementation branch is ready for review only when:

1. all Tasks 1–8 are complete;
2. corrected counterbalance invariants pass unit tests;
3. evaluation assignment survives reload/resume/fallback without arm drift;
4. ordinary product flow has no evaluation randomization/logging without an explicit bound session;
5. privacy tests prove export contains no Case/user/location/model content;
6. staged/real/external-A fixtures reconstruct all approved metrics;
7. incomplete, abandoned, and fallback sessions remain visible in ITT;
8. generated executor/conformance artifacts are unchanged;
9. full local validation is green;
10. exact-head GitHub CI is green;
11. no release/version files are changed.

Implementation review, merge, running the actual experiment, and any future release remain separate authorization gates.
