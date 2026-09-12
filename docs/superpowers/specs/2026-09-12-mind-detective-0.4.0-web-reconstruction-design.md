# MIND Detective 0.4.0 — Post-release governance and Web Reconstruction Foundation

Status: approved design, pre-implementation
Date: 2026-09-12
Base release: `0.3.1`
Base main SHA: `f338f9e6bfca49e01666990bd44109e3a8c34e2d`

## 1. Purpose

`0.3.1` completed the external-review remediation cycle and left the repository with a hardened deterministic local-execution boundary, exact-SHA release publication, explicit product/evaluation limits, and an honest Web/PWA boundary: Web performs physical Search/checklist work while full reconstruction remains available only through the plugin/agent workflow.

The next cycle has two goals that must be completed in order:

1. harden repository governance and remove merged branch residue;
2. make Web reconstruction a first-class local workflow without turning the product into an AI-first chat interface or creating a second domain implementation.

This document is the design contract for post-release governance and the `0.4.0` product/architecture scope. It does not authorize implementation beyond the approved plan that will follow this spec review.

## 2. Decisions carried forward from 0.3.1

The following remain invariants unless a later separately reviewed design explicitly changes them:

- Python portable semantics remain the authoritative deterministic source.
- Web does not maintain a handwritten Case reducer parallel to Python.
- Web canonical Case persistence remains IndexedDB and local-first.
- Deterministic Case mutation remains atomic with an execution receipt and idempotent command semantics.
- Assistant/model execution remains a separate proposal boundary and may not directly mutate canonical Case state.
- `mind-detective-case/v2` remains the Case schema for `0.4.0`; no Case v3 is introduced merely to add the Web reconstruction UI.
- No Bayesian/POD state, calibrated location probabilities, hidden belief weights, cross-case learning, cloud Case database, or background Case synchronization is introduced.
- Reconstruction and Search remain distinct interaction modes and must remain distinguishable without relying on color alone.
- User recollection/habit/observation remains user-originated evidence. Assistant output may not be stored as those statement types.
- Unknowns and contradictions remain explicit; the system does not resolve them by plausibility.
- The B↔C product-evaluation contract remains falsifiable. `0.4.0` does not claim that AI is superior to the deterministic arm without protocol evidence.
- Repository/plugin releases continue to use one declarative release manifest and the hardened repository-native publisher with exact post-merge `main` CI and a human-approved full 40-hex SHA.

## 3. Post-release repository governance

### 3.1 Main protection target

`main` must become a protected integration branch. The intended repository rule is:

- target branch: `main`;
- changes enter through pull requests;
- direct pushes are blocked;
- force pushes are blocked;
- deletion of `main` is blocked;
- required status checks must pass against the current PR head;
- the branch must be up to date with `main` before merge;
- unresolved PR conversations block merge;
- required approval count is `0` while the repository is operated as a single-maintainer project;
- merge commits remain the supported merge strategy;
- linear-history enforcement remains disabled because it conflicts with the repository's merge-commit release ancestry convention;
- signed commits are not a mandatory merge gate in this cycle;
- administrator/emergency bypass, if available in the selected GitHub rule mechanism, is retained only for repository recovery rather than ordinary development.

The required CI contexts are the stable top-level jobs emitted by `.github/workflows/ci.yml`:

- `Validate (Python 3.10)`;
- `Validate (Python 3.13)`;
- `Validate Web`;
- `Secret scan`.

The scheduled `Reference freshness` workflow remains an operational review mechanism rather than a required PR check because it runs independently on a weekly/manual cadence and opens/updates an issue when the strict full-set check requires review.

### 3.2 Merge discipline

For feature, fix, design, and maintenance work after this cycle:

1. branch from the current exact `main` SHA;
2. open a PR;
3. require exact-head CI success;
4. merge using a merge commit unless a separately documented exception exists;
5. require exact-main push CI before any release publication;
6. release only through the canonical publisher.

A green historical PR run is not sufficient if the PR head moved. A release may not target mutable `main`; it must target a human-approved exact 40-hex SHA.

## 4. Branch housekeeping policy

Before this design branch was created, the repository contained 19 non-`main` branches, including historical release-design/feature branches, product-evaluation branches, maintenance work, and nine `review-remediation-task*` branches from the completed 0.3.1 remediation cycle.

Housekeeping is ancestry- and PR-aware, not name-based.

A branch may be deleted when at least one of the following is proven:

- its tip commit is an ancestor of current `main`; or
- its corresponding PR is merged and the merged history contains the intended branch changes.

For historical release branches, the immutable release/tag is the durable archive. The branch does not need to remain solely as a release record.

A branch must be preserved when:

- its tip contains commits not reachable from `main` and no merged PR proves equivalent integration;
- its purpose is still active;
- or its ancestry cannot be determined reliably.

The nine completed remediation branches are expected deletion candidates after ancestry verification:

- `review-remediation-task1-safety`
- `review-remediation-task2-checklist`
- `review-remediation-task3-reachability`
- `review-remediation-task4-eval-events`
- `review-remediation-task5-local-import`
- `review-remediation-task6-reconstruction-boundary`
- `review-remediation-task7-semantic-eval-governance`
- `review-remediation-task8-web-contract-pwa`
- `review-remediation-task9-portability-docs-release`

The post-housekeeping target is simple: retain `main` plus only branches representing active, unmerged work. Git history, merged PRs, release tags, and immutable GitHub Releases remain the historical record.

## 5. Product scope for 0.4.0

### 5.1 Release theme

`0.4.0` is **Web Reconstruction Foundation**.

The release closes the largest product-surface gap left intentionally by `0.3.1`: a user should be able to start a Case in Web, provide a neutral free account, structure supported evidence, see an uncertainty-preserving timeline, and explicitly transition into physical Search without requiring the plugin/agent surface.

The release is not an AI-chat release. A fully useful deterministic reconstruction path must exist without a live model.

### 5.2 Canonical user journey

```text
Create Case
   ↓
FREE ACCOUNT
user records their own account before detailed prompts
   ↓
STRUCTURE
user-originated recollection / habit / observation
+ explicit limitations / unknowns
   ↓
TIMELINE
supported events + unknown intervals + contradictions
   ↓
READY FOR SEARCH
explicit transition
   ↓
PLAN / CHECKLIST
   ↓
physical checks
   ↓
found / unresolved
```

The application remains state-first. Chat history is not the primary navigation or state model.

### 5.3 Required 0.4.0 capabilities

`0.4.0` must provide:

1. an explicit Web transition into `reconstruction` mode for a new/eligible active Case;
2. free-account-first capture before detailed clarification;
3. local creation of user-originated statements using the existing Case v2 statement model;
4. explicit distinction between recollection, habit, observation, hypothesis/search suggestion semantics already represented by the current model, while preventing assistant-originated recollection/habit/observation;
5. optional event-time/precision inputs without requiring false precision;
6. deterministic timeline rebuild that preserves unknown intervals and contradictions;
7. a readable timeline/uncertainty view derived from canonical Case state;
8. an explicit `reconstruction → search` transition;
9. continuation of the existing Search/checklist workflow without evidence promotion at the transition;
10. RU/EN key parity and equivalent safety/privacy semantics;
11. offline operation after application preload for the deterministic reconstruction path;
12. full export/import preservation of reconstruction state through the existing versioned Case v2 contract.

### 5.4 Non-goals for 0.4.0

The release does not include:

- Case v3;
- autonomous memory inference;
- model-authored recollection/habit/observation;
- location-probability scores;
- Bayesian/POD estimation;
- cross-case personalization or hidden aggregation;
- cloud Case persistence/sync;
- background Case sync;
- retrospective replay of assistant requests after reconnect;
- a general-purpose chat surface;
- a claim that the assistant evaluation arm is superior to the deterministic arm;
- new production skills unrelated to the reconstruction workflow.

## 6. Current architecture facts relevant to 0.4.0

The current `Case` already contains the reconstruction data needed for this release:

- `statements`;
- optional `timeline`;
- `current_mode` including `reconstruction`;
- `interaction_journal`;
- existing lifecycle/search state.

Therefore a schema migration is not required solely to expose reconstruction in Web.

The current portable command contract already includes `set_mode` and `add_statement`, and Web executes them through the generated local executor. However timeline mutation is currently outside the portable command set: `CaseController.set_timeline()` delegates to the plugin reducer, and `SUPPORTED_COMMAND_TYPES` does not include a timeline command. That is the principal deterministic-boundary gap `0.4.0` must close for Web reconstruction.

The current Web Case page intentionally renders a `web-reconstruction-unavailable` boundary and allows switching such a Case directly to physical Search. `0.4.0` replaces that unavailable-state treatment with a real reconstruction surface while retaining the explicit Search transition.

## 7. Deterministic reconstruction architecture

### 7.1 Principle

Web receives reconstruction semantics through the same generated portable-execution path used for existing deterministic commands. It does not reproduce timeline/reconstruction rules in Vue/TypeScript by hand.

```text
Python authoritative semantics
        │
        ├── statement mutation
        ├── timeline derivation/validation
        ├── reconstruction/search mode transition
        │
        ▼
restricted portable kernel
        │
        ├── certified generator
        ▼
committed generated TypeScript executor
        │
        ▼
Web local executor
        │
        ▼
IndexedDB atomic Case + execution receipt
```

### 7.2 Portable timeline command

Add one reconstruction-focused portable command, tentatively named `rebuild_timeline`.

The command payload contains only user/UI selections required to define event grouping and references, for example:

- event ids;
- labels supplied or confirmed by the user;
- referenced statement ids;
- optional event time and time precision;
- optional `last_supported_interaction_id`;
- optional `first_noticed_missing_id`.

The portable kernel derives canonical timeline output from the current Case statements plus that payload. In particular, it owns:

- reference validation;
- unknown-interval derivation;
- timestamp/order contradiction detection;
- duplicate/reference consistency checks;
- canonical timeline serialization;
- Case mutation and `updated_at` semantics.

The browser may collect inputs and render canonical output, but it may not independently calculate the authoritative contradiction/unknown result.

The typed/plugin timeline path should delegate to the same canonical semantics or an adapter around it, rather than creating a second definition of timeline truth.

### 7.3 Statement capture

The existing `add_statement` command remains the mutation path. Web commands must remain user-originated.

Free account is recorded before detailed clarification. The initial free account may be stored as one or more user-confirmed statements according to the implementation design, but the system must not silently split model text into purported memories. Any structured statement written into Case must correspond to user-authored or user-confirmed material and preserve the original user text needed by the current Case contract.

### 7.4 Transition to Search

`set_mode(search)` remains the explicit deterministic transition. The transition itself does not:

- strengthen evidence;
- convert hypotheses into recollections;
- eliminate contradictions;
- assign probabilities;
- or imply that the reconstruction is complete or correct.

Search planning uses the Case state under its existing contracts.

## 8. Web component design

The existing `apps/web/app/pages/cases/[id].vue` is already a large orchestration page. `0.4.0` should avoid adding the reconstruction UI directly as another large inline block.

Introduce focused components/composables with narrow responsibilities, for example:

- `ReconstructionPanel` — phase orchestration and canonical state display;
- `FreeAccountCard` — initial free-account capture;
- `StatementCapture` — explicit user statement capture/classification inputs;
- `TimelineEditor` — event/reference inputs that produce a `rebuild_timeline` command;
- `TimelineSummary` — read-only canonical events/unknowns/contradictions;
- a reconstruction-specific composable for command construction/view state where useful.

Names may change during the implementation plan, but responsibilities must remain separated. The page continues to own Case-level lifecycle/orchestration, while domain semantics stay in the generated executor.

The reconstruction UI must visually distinguish:

- user evidence;
- system-derived unknowns/contradictions;
- optional assistant proposals;
- Search suggestions/checks.

No visual state may rely only on color.

## 9. Assistant boundary

### 9.1 0.4.0 default

Live-model reconstruction is not required for the 0.4.0 Definition of Done.

The deterministic reconstruction path is the product core. If assistant clarification support is added within the release, it remains optional and cannot become a dependency for progressing from free account to Search.

### 9.2 Optional clarification proposal

If implemented, assistant flow is:

```text
minimal reconstruction context
        ↓
assistant proposal boundary
        ↓
RECONSTRUCTION guard
        ↓
safe candidate clarification
        ↓
UI question
        ↓
user response
        ↓
user-confirmed deterministic statement command
```

The assistant proposes a question; it does not write memory evidence into Case.

Blocked raw assistant output is not later revealed. Transport failure does not replay a stale question after reconnect. Existing execution-identity skew protection remains applicable to any online assistant call.

A stronger assistant-reconstruction experience is preferably evaluated as a follow-up `0.4.x` change rather than made a release blocker for the deterministic foundation.

## 10. Requirements delta

Add a dedicated Web reconstruction contract family in `docs/REQUIREMENTS.md` and exact trace selectors in `docs/CONTRACT_MATRIX.json`.

The implementation plan must assign stable identifiers, covering at minimum:

- free-account-first interaction;
- user-only provenance for recollection/habit/observation;
- no unsupported location seeding during reconstruction;
- explicit preservation/rendering of unknowns and contradictions;
- canonical portable timeline mutation;
- visual/semantic distinction between reconstruction evidence and Search suggestions;
- explicit transition to Search without evidence promotion;
- offline deterministic reconstruction after preload;
- RU/EN semantic parity;
- export/import preservation;
- assistant proposal non-mutation and guard path if assistant clarification is included.

Every active requirement must have a production path and exact test selector. Existence-only helper tests are insufficient.

## 11. Evaluation implications

The existing B↔C evaluation protocol remains valid for Search/checklist assistant lift and must not be silently reinterpreted as evidence about reconstruction.

`0.4.0` therefore separates two questions:

1. can deterministic Web reconstruction be completed safely and coherently? — release engineering/product readiness question;
2. does live-model clarification add practical value over deterministic reconstruction? — future evaluation question requiring its own reviewed protocol/extension if pursued.

No new reconstruction assistant metric is added merely because instrumentation is technically easy. Events must exist only when they support a defined decision.

Manual plugin semantic scenario governance remains manual unless a separately reviewed semantic runner is introduced.

## 12. Error handling and safety

Reconstruction commands use the existing fail-closed local execution model:

- command id and expected Case timestamp are immutable per attempt;
- retry after persistence failure repeats the byte-equivalent Case snapshot and command envelope;
- conflicting command-id reuse fails closed;
- terminal/paused lifecycle rules remain enforced by canonical semantics;
- high-risk action uncertainty is blocked before Case mutation;
- invalid timeline references fail with stable machine-readable error codes;
- a failed timeline command must not partially update canonical Case;
- assistant/model transport failure never blocks deterministic local reconstruction.

## 13. Testing strategy

### 13.1 Python/kernel

Add deterministic tests for:

- `rebuild_timeline` command payload validation;
- missing statement references;
- unknown-interval preservation;
- time-order contradictions;
- invalid timestamp handling;
- lifecycle/mode constraints where applicable;
- user provenance restrictions;
- idempotent command replay;
- forbidden probabilistic fields.

### 13.2 Conformance

Extend the committed Python↔generated-TypeScript conformance corpus with reconstruction/timeline vectors. CI must regenerate artifacts/corpus and require no diff.

### 13.3 Web unit tests

Cover:

- free-account-first state transitions;
- statement command construction;
- canonical timeline rendering;
- unknown/contradiction presentation;
- reconstruction/Search visual distinction;
- assistant-disabled/offline progression;
- RU/EN key parity.

### 13.4 Browser tests

Playwright must include a canonical offline-capable journey:

`create → reconstruction → free account → structured evidence → timeline → switch to Search → check → close`

Also test reload/resume from IndexedDB during reconstruction and imported Case v2 reconstruction state.

### 13.5 Regression gates

Existing Python 3.10/3.13, Web, secret scan, strict typing/linting, PWA build, browser matrix, release-contract, and reference controls remain in force.

## 14. Definition of Done for 0.4.0

`0.4.0` is ready only when all of the following are true:

- repository governance for `main` is applied or, if platform permission prevents automated application, the exact required rule is documented and verified after manual application;
- merged branch residue has been ancestry-audited and safe deletion candidates removed;
- no active/unmerged branch was deleted by assumption;
- a Web user can create a Case and enter reconstruction mode;
- free account precedes detailed clarification;
- user-originated evidence can be stored locally through canonical deterministic commands;
- canonical timeline unknowns/contradictions are generated through portable semantics, not handwritten Web rules;
- reconstruction survives reload/resume through IndexedDB;
- the user can explicitly transition to Search and finish the existing search workflow;
- deterministic reconstruction works without a live model after preload;
- Case schema remains `mind-detective-case/v2` unless implementation discovers a concrete incompatible requirement and triggers a new design review;
- all new active contracts have exact production-reachability selectors;
- exact-head CI is green before merge;
- exact-main CI is green after merge;
- release publication, when separately authorized, uses only the canonical exact-SHA publisher.

## 15. Implementation staging

The implementation plan should preserve these review boundaries:

**Phase 0 — Governance and housekeeping**

Apply/verify `main` protection and perform ancestry-safe branch cleanup. No product behavior changes.

**Phase 1 — Reconstruction contract and portable timeline semantics**

Requirements/contract matrix first, then failing tests, portable command/kernel/adapters, generated artifact and conformance vectors.

**Phase 2 — Web reconstruction UX**

Add focused components and local command flows. Replace the `web-reconstruction-unavailable` state with real reconstruction while preserving mode distinction.

**Phase 3 — Offline/PWA and end-to-end readiness**

Offline/reload/import browser journeys, accessibility, i18n parity, privacy/safety regression checks.

**Phase 4 — Optional assistant clarification**

Only if it can be added without becoming a dependency for the deterministic Definition of Done and without widening the release beyond this design. Otherwise defer it to `0.4.x` with a separate evaluation/design review.

**Phase 5 — Release readiness**

Documentation/version/release-manifest updates, exact-head CI, merge authorization, exact-main CI, then a separate human publication gate.

## 16. Review triggers that require a new design decision

Implementation must stop and return to architecture/product review if any of these become necessary:

- Case v3 or incompatible Case migration;
- storing assistant text as recollection/habit/observation;
- a second handwritten Web domain reducer;
- cloud Case persistence/sync;
- background Case synchronization;
- calibrated probability/belief state;
- cross-case learning;
- making a live model mandatory for reconstruction completion;
- changing the primary B↔C evaluation decision without a protocol review;
- bypassing exact-SHA merge/release governance.

These are architecture changes, not implementation details.
