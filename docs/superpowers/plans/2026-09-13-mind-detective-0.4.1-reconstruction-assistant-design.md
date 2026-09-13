# MIND Detective 0.4.1 — Reconstruction Assistant Research / Design Execution Plan

**Status:** companion execution plan for research/design review; no production implementation authorization  
**Date:** 2026-09-13  
**Base release:** `0.4.0`  
**Base main SHA:** `6da587eede2d527f7fdcac7ea8a47df6edf8aa7b`  
**Research spec:** `docs/superpowers/specs/2026-09-13-mind-detective-0.4.1-reconstruction-assistant-research.md`

## 1. Purpose

This plan turns the Reconstruction Assistant research spec into a sequence of reviewable research/design gates.

It is intentionally **not** a production implementation plan. It does not authorize live-model product code, a Case migration, a new portable command, provider credentials in production, a version bump, or publication of `0.4.1`.

The sequence is designed so that work can stop early when deterministic guided clarification is sufficient or the live-model path fails safety/privacy/readiness criteria.

## 2. High-level sequence

```text
0.4.0 immutable release
        ↓
Research contract freeze
        ↓
R0 / R1 / R2 protocol + corpus
        ↓
Deterministic guard + proposal schema design
        ↓
Offline model/provider screening
        ↓
Gate A: eligible for human pilot?
        ↓
Small R0/R1/R2 usability pilot
        ↓
Protocol freeze v1
        ↓
Confirmatory R1 ↔ R2 staged evaluation
        ↓
GO / NO-GO / INCONCLUSIVE
        ↓
GO only → production architecture review
        ↓
GO only → separate implementation plan
```

## 3. Process invariants

Every phase must preserve:

- `mind-detective-case/v2` unless a later separately approved design proves a migration necessary;
- Python as authoritative deterministic Case semantics;
- no handwritten Web domain reducer;
- no assistant-authored recollection/habit/observation;
- no Bayesian/POD/location-probability state;
- no cloud Case database/background Case sync/cross-case learning;
- deterministic Reconstruction as the complete fallback/core path;
- evaluation metadata outside Case;
- local-only evaluation storage by default and explicit export;
- exact requirement/test/traceability only after an implementation slice is approved;
- separate explicit human gates for research implementation, merge, release preparation, and publication.

## 4. Phase 0 — Repository/context reconciliation

### Goal

Prevent future research/implementation agents from using the pre-0.4.0 Web boundary as if it were still current.

### Required work

Before any research-enablement implementation PR:

1. reconcile `AGENTS.md` wording that still describes Web/PWA as Search/checklist-only;
2. review `CLAUDE.md` pointers to old canonical artifacts and update them only where they are demonstrably stale;
3. keep historical specs/plans intact;
4. point development context to the released `0.4.0` Web Reconstruction design/plan and this approved research spec.

### Gate

Docs-only PR, exact-head CI, explicit merge authorization.

This housekeeping is not bundled into the current research-spec PR.

## 5. Phase 1 — Freeze research protocol v1

### Goal

Turn the research spec into machine-checkable vocabulary before comparing models.

### Deliverables

Define/version:

- reconstruction research arms `R0`, `R1`, `R2`;
- clarification reason codes;
- deterministic rejection/guard codes;
- safety annotation codes;
- staged scenario family/variant ids;
- stop reasons;
- technical failure/fallback reasons;
- metric formulas;
- preregistered Go/No-Go thresholds.

### Design constraints

- Do not overload Search evaluation arms `A/B/C`.
- Do not add experiment metadata to `Case v2`.
- No raw model output in evaluation export.
- No user free text in evaluation export.

### Review evidence

A protocol table must show that every decision-gate metric has a privacy-safe source event/field and an explicit denominator.

## 6. Phase 2 — Build the staged scenario corpus design

### Goal

Create reproducible scenarios in which “good clarification” and “forbidden assumption” are knowable.

### Minimum corpus

At least 12 scenario families/variants covering the research spec categories, with RU/EN equivalents where appropriate.

Each fixture must define:

- scenario id/version;
- user-visible initial account;
- latent facts available to the scripted participant;
- genuinely unknown facts;
- contradictions;
- allowed clarification targets;
- forbidden introduced entities/locations/actions;
- expected accepted reason codes;
- critical-violation triggers;
- deterministic stopping/readiness expectations.

### Important distinction

The scenario fixture may contain latent facts because it is a synthetic research instrument. Those latent facts must never be made available to the model question generator. The model receives only the same allowed context class that a product integration would receive.

### Exit criteria

- every guard rejection class has at least two adversarial examples;
- every clarification reason code has at least two positive examples;
- at least one scenario per relevant family has the correct outcome “preserve unknown” rather than “recover more detail”;
- prompt-injection examples exist in both RU and EN.

## 7. Phase 3 — Specify R1 deterministic guided clarification

### Goal

Create a strong non-model comparator so R2 must prove model-specific value rather than merely the value of asking questions.

### R1 design

R1 uses the same clarification taxonomy and stopping policy as R2 but chooses from deterministic question templates/rules.

R1 must:

- inspect only canonical deterministic Reconstruction state;
- select only approved clarification categories;
- never invent new concrete locations/actions/entities;
- produce a stable reason code/target identity;
- support RU/EN parity;
- stop under the same maximum-question / consecutive-skip policy used by R2.

### Comparator fairness

R1 and R2 must share as much downstream behavior as possible:

```text
eligibility/category target
        ↓
question candidate
        ↓
validation / safety boundary
        ↓
state-first UI
        ↓
user answer
        ↓
existing deterministic Case mutation
```

Only candidate-question generation should differ materially.

### Exit criteria

R1 covers every approved question category needed by the corpus or explicitly abstains with a stable reason.

## 8. Phase 4 — Specify R2 proposal schema and deterministic guard

### Goal

Make the live-model capability narrow enough to evaluate safely.

### Proposal schema

Minimum semantic fields:

- `question`;
- `reason_code`;
- `target_ids`.

Unknown fields fail closed unless an approved schema version explicitly adds them.

### Deterministic guard layers

1. parse/schema validation;
2. reason-code allowlist;
3. target-id existence/scope validation;
4. prohibited confidence/diagnosis patterns;
5. introduced-location/action/entity checks where deterministically detectable;
6. leading/forced-resolution heuristics;
7. existing high-risk action/safety ingress where applicable;
8. final abstain/show decision with stable rejection code.

The design may use conservative rejection. False negatives that expose unsafe/leading questions are more costly than occasional abstention during research.

### Exit criteria

The guard has explicit fixture coverage for every rejection code before a live-model pilot is eligible.

## 9. Phase 5 — Context minimization and provider boundary design

### Goal

Define exactly what a live provider can receive before selecting any provider/model.

### Default context contract

Prefer:

- language;
- reason/category candidate;
- targeted timeline/event ids and bounded excerpts needed to ask the question;
- selected user-confirmed statements relevant to that target;
- explicit unknown/contradiction metadata.

Default exclusions:

- full Case payload;
- full interaction journal;
- raw free account;
- unrelated statements;
- evaluation history;
- provider secrets in browser;
- cross-case/profile context.

### Research variants

If a minimized-context R2 cannot ask useful questions, a broader-context variant may be evaluated only after:

1. documenting why the missing context is necessary;
2. adding explicit privacy/retention review;
3. keeping that variant analytically distinct;
4. preserving the same output/guard contract.

### Exit criteria

A context matrix documents each field, why it is needed, whether it is user content, provider retention implications, and whether it appears in any local/export telemetry.

## 10. Phase 6 — Offline model/provider screening

### Goal

Eliminate unsuitable models/prompts without human exposure.

### Candidate comparison

For each approved model/provider configuration, run the fixed corpus at a fixed prompt/schema version and record:

- parse/schema success;
- deterministic guard pass/reject;
- reason-code/category correctness;
- critical violations;
- non-critical safety annotations;
- abstention rate;
- RU/EN parity observations;
- prompt-injection failures;
- latency p50/p95;
- provider errors/retries;
- cost estimate where available.

### Gate A — human-pilot eligibility

A candidate may enter usability pilot only when:

- zero unresolved critical violations in the reviewed corpus;
- structured-output validity after approved retry policy is at least 99%;
- prompt injection does not change system policy/capability contract;
- guard behavior is reproducible;
- privacy/context contract is approved;
- RU and EN both meet minimum qualitative/safety acceptance.

If no candidate passes, stop. Do not create a product assistant implementation plan.

## 11. Phase 7 — Small R0/R1/R2 usability pilot

### Goal

Validate interaction design, provenance comprehension, and question burden before confirmatory efficacy measurement.

### Suggested protocol

- 18–24 participants;
- within-subject exposure to R0/R1/R2 on isomorphic scenario variants;
- balanced order (Latin-square/counterbalanced assignment);
- no participant receives the same hidden scenario solution twice;
- maximum five shown clarification questions in R1/R2;
- fixed 1–5 task-load, convenience, source-clarity ratings;
- explicit skip / `Не помню` / continue-without-more controls.

### Pilot questions

- Do participants understand that assistant questions are not memories?
- Is five questions too many?
- Is `Не помню` interpreted as a valid endpoint rather than failure?
- Does state-first UI remain primary rather than becoming a chat transcript?
- Are deterministic R1 questions already sufficient?
- Are R2 guard abstentions confusing?
- Does provider latency disrupt the Reconstruction flow?

### Pilot decision

Pilot results may change UI copy, question cap, scenario difficulty, or protocol mechanics **before** confirmatory protocol v1 is frozen. They may not be used as confirmatory GO evidence.

## 12. Phase 8 — Freeze confirmatory protocol

### Goal

Prevent outcome-driven metric/threshold changes.

Before confirmatory sessions begin, freeze/version:

- R1 deterministic generator version;
- R2 model/provider/prompt/schema version;
- guard version;
- scenario/counterbalance table;
- question cap/stopping policy;
- evaluation schema extension;
- primary/secondary metrics;
- Go/No-Go thresholds;
- sample floor;
- analysis method.

Any material change after data collection begins creates a new protocol version and affected sessions remain attributable to their original version.

## 13. Phase 9 — Confirmatory R1 ↔ R2 staged evaluation

### Goal

Answer the only production-AI question: does R2 outperform strong deterministic R1 enough to justify complexity/risk?

### Suggested design

- at least 32 protocol-complete participants;
- paired within-subject/counterbalanced design;
- four tasks per participant, two R1 and two R2;
- isomorphic non-repeated scenario variants;
- intention-to-treat visibility for all assigned/started sessions;
- explicit treatment of provider fallback/abandonment/incomplete participation;
- participant-clustered uncertainty intervals for paired safety/efficacy summaries.

### Primary report

Must include:

- reconstructable evidence coverage R1 vs R2;
- useful clarification rate;
- question efficiency;
- genuine-unknown preservation;
- safety-rate differences and intervals;
- critical violations;
- task load / convenience / source clarity;
- fallback/guard/provider rates;
- result of each preregistered GO condition.

No metric may be substituted after seeing results to rescue a failed primary gate.

## 14. Phase 10 — Decision memo

### Required output

A short immutable decision document records:

- protocol version and exact research implementation/model identifiers;
- sample accounting;
- efficacy result;
- UX result;
- safety/provenance result;
- technical readiness result;
- privacy result;
- decision: `GO`, `NO-GO`, or `INCONCLUSIVE`;
- threshold-by-threshold rationale;
- known limitations;
- next authorized design step.

### Decision consequences

**GO**

- start a separate production architecture review;
- decide whether any temporary proposal persistence is needed;
- decide exact API/provider integration contract;
- activate requirements only with exact selectors/reachability;
- then invoke the repository's normal implementation-planning workflow.

**NO-GO**

- no production live-model Reconstruction assistant;
- optionally promote useful R1 deterministic clarification improvements through a separate design/implementation cycle.

**INCONCLUSIVE**

- retain released `0.4.0` deterministic product truth;
- authorize only research/readiness fixes and protocol rerun.

## 15. Candidate architecture for GO review

This architecture is a research outcome candidate, not a current implementation contract:

```text
Case v2 deterministic Reconstruction
        │
        ├── clarification eligibility / target
        │
        ▼
minimal context builder
        │
        ▼
optional API/provider request
        │
        ▼
structured proposal
        │
        ▼
deterministic validation + guard
        │
        ▼
state-first question card
        │
        ▼
user answer / skip / unknown
        │
        ▼
existing deterministic local Case mutation
```

Expected isolation boundaries:

- **eligibility selector:** determines whether a clarification opportunity exists; no model dependency;
- **R1 generator:** deterministic comparator;
- **context builder:** minimizes provider payload;
- **R2 client/boundary:** transport only, no Case mutation;
- **proposal validator/guard:** deterministic allow/reject;
- **question UI:** renders provenance and controls;
- **user-answer adapter:** converts explicit user answer into existing canonical command payloads;
- **research instrumentation:** separate from Case and fail-closed for raw content.

## 16. Anticipated research-enablement implementation slices

These slices are listed to bound future planning; they are not authorized by this document.

1. repository-context housekeeping (`AGENTS.md` / relevant development context);
2. reconstruction research schema/enums and privacy-safe evaluation extension;
3. staged scenario corpus/fixtures;
4. R1 deterministic clarification prototype;
5. R2 proposal schema/context builder/provider research adapter;
6. deterministic guard and adversarial fixture suite;
7. explicit evaluation-only R0/R1/R2 UI controls;
8. offline benchmark runner/report format;
9. small pilot instrumentation;
10. confirmatory assignment/counterbalance and analysis tooling;
11. decision memo template and verification checklist.

Each slice requires its own RED→GREEN evidence if/when implementation is authorized.

## 17. Testing/research verification strategy

Future research-enablement implementation must separate deterministic tests from live-model evidence.

### Deterministic tests

- schema validation;
- category/rejection allowlists;
- guard fixtures;
- prompt/context serialization without secrets;
- evaluation privacy allowlist/fail-closed behavior;
- R1 deterministic outputs;
- stop policy;
- assignment/counterbalance;
- metric reconstruction;
- Case non-mutation by proposal path;
- offline/degraded fallback.

### Semantic/adversarial evaluation

- leading-suggestion corpus;
- introduced-location/action corpus;
- contradiction handling;
- genuine-unknown preservation;
- prompt injection;
- RU/EN parity;
- provider malformed/timeout/error behavior.

### Live-model evidence

Live-model corpus/pilot results are research evidence only. They must record model/provider/prompt/schema versions and must not be represented as deterministic unit-test guarantees.

## 18. Traceability strategy after GO

If production implementation is authorized, every activated `MD-WEB-REQ-RECON-ASSIST-*` requirement must receive:

- exact production helper/component/endpoint ownership;
- exact deterministic selector(s);
- relevant adversarial/semantic scenario ids;
- privacy/safety reference where applicable;
- production reachability from Web/API roots;
- explicit offline/degraded behavior where applicable.

Until GO + approved implementation plan, the proposed requirement family remains inactive research design.

## 19. Release/version policy

This research cycle does not automatically create `0.4.1`.

- `0.4.0` remains the published product truth during research.
- A GO result authorizes only production design/planning, not publication.
- A NO-GO result may lead to a deterministic clarification release or no release.
- An INCONCLUSIVE result authorizes research fixes, not a product-direction release.
- Version surfaces and `.github/releases/release.json` remain unchanged until a separately approved release-preparation phase.

## 20. Definition of Done for the research/design cycle

This cycle is complete when:

1. the research spec and this execution plan are human-approved and merged;
2. repository-context drift that would misstate the 0.4.0 Web boundary is reconciled before implementation;
3. research-enablement implementation receives a separate approved plan;
4. protocol v1, corpus, R1, R2 schema/guard, context/privacy contract, and offline benchmark exist;
5. an eligible R2 candidate passes Gate A or the cycle terminates NO-GO early;
6. pilot findings are resolved before confirmatory freeze;
7. confirmatory R1↔R2 study reaches a valid decision or is explicitly inconclusive;
8. decision memo records `GO`, `NO-GO`, or `INCONCLUSIVE` without post-hoc metric substitution;
9. only a `GO` result proceeds to a separate production implementation plan.

## 21. Current authorization boundary

The current approved action is limited to **writing/reviewing these research/design artifacts**.

No live-model production code, research harness implementation, requirement activation, Case schema change, release preparation, tag, or publication is authorized by this plan.