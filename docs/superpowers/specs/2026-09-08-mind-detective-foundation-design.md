# MIND Detective Foundation Design

**Status:** Approved design; implementation plan prepared  
**Date:** 2026-09-08  
**Target repository:** `trafficolog/mind-detective`  
**Target first release:** repository `0.1.0`, plugin `mind-detective-v0.1.0`  
**Development method:** SDD + TDD, Superpowers workflow, DRY/KISS/YAGNI  
**Reference architecture:** behavioral/contracts approach proven in `trafficolog/yandex-ai-plugins-skills`

---

## 1. Executive summary

MIND Detective is an evidence-safe methodology runtime for helping a user search for a misplaced item without pretending that an LLM knows where the item is.

The first release is deliberately narrow: one complete **IN_MOMENT** vertical slice for an item lost within minutes or hours. It combines a conversational skill layer with deterministic helpers for evidence classification, question safety, timeline reconstruction, search allocation, competing hypotheses, safety routing, and case debrief.

The core product claim is **not** “AI finds lost things.” The supported claim is:

> MIND Detective helps a user reconstruct what is supported by their own account, avoid memory-contaminating prompts, allocate search effort explicitly, record what has actually been checked, and choose the next bounded action while preserving uncertainty.

The central safety invariant is analogous to exact-preview write safety in `yandex-ai-plugins-skills`: a consequential action must cross a machine-enforced boundary. Here the highest-risk action is not an API mutation; it is an agent question or claim that can contaminate the user's subsequent recollection or turn an uncalibrated heuristic into a false fact.

Therefore the P0 candidate-utterance boundary is:

```text
candidate agent question/claim
        ↓
conversation stage policy
        ↓
question_lint / claim guard
        ↓
ALLOW or BLOCK(machine code)
        ↓
user-visible output when the host submits the candidate through this path
```

The helper path is fail-closed for candidates submitted to it. A generic Claude Code/Codex skill host cannot mechanically prove that every arbitrary free-form model utterance invoked the helper; mandatory invocation is therefore a skill/eval/review contract in P0 until a dedicated surface with a true pre-send interceptor is separately designed.

The first release is plugin-first, independently installable, transport-free, and does not introduce a shared runtime package, external connectors, model SDKs, web UI, voice surface, or cross-case personalization.

---

## 2. Design principles

### 2.1 Behavioral kernel, not a premature shared library

The repository adopts the same lesson as the current Yandex plugin architecture: common architecture is primarily a **specification, stable requirement IDs, schemas, validators, conformance tests, and exact traceability**.

P0 does **not** create a root `kernel/` runtime dependency consumed by the plugin. Executable code stays inside the independently installable `plugins/mind-detective/` boundary until there is demonstrated reuse plus a defined distribution contract.

This prevents formal DRY from breaking installability.

### 2.2 LLM for dialogue; deterministic code for invariants

The LLM may route to a skill, summarize user-provided statements without inventing new claims, choose among allowed neutral question forms, explain limitations, present deterministic helper output, and formulate hypotheses explicitly as hypotheses.

The LLM must not be the source of truth for evidence-class promotion, whether a submitted candidate utterance passes the guard, timeline consistency, search-weight update math, mechanically detectable red-flag routing, stable machine reason codes, or future persistent-memory mutation.

### 2.3 Progressive disclosure

`SKILL.md` files are short discoverable workflow contracts. Longer methodology, citations, examples, and policy live in `references/`. Executable logic lives in `scripts/`; regression coverage lives in `tests/`; adversarial routing/semantic expectations live in `evals/`.

### 2.4 Truthful confidence

The system distinguishes what the user recalls, what the user says is habitual, what an external source reports, what was actually searched, what deterministic code infers, what remains a hypothesis, and what is merely methodology.

It never converts an uncalibrated search weight into “probability the item is there.”

### 2.5 Safety before optimization

A faster search is not a success if it is achieved by leading the user, inventing a location, making an accusation, or masking a time-critical fallback.

---

## 3. Product scope

### 3.1 P0 / `0.1.0` in scope

```text
router
  → quickcheck
  → interview
  → timeline
  → zones/search allocation
  → first search round
  → hypotheses if unresolved
  → next bounded action or fallback
  → debrief
```

Production skills: `mind-detective`, `mind-detective-quickcheck`, `mind-detective-interview`, `mind-detective-timeline`, `mind-detective-zones`, `mind-detective-hypotheses`, `mind-detective-fallback`, `mind-detective-debrief`.

Deterministic helpers: `evidence.py`, `question_policy.py`, `question_lint.py`, `timeline.py`, `zones.py`, `ach.py`, `redflags.py`, `schemas.py`.

Repository enforcement: stable requirement IDs, plugin validator, exact-selector contract matrix, eval contract v2, AST boundary tests, RU-primary + EN mirror key docs, secret scanning, pinned GitHub Actions, declarative release manifest and one hardened publisher.

### 3.2 Explicitly out of scope for `0.1.0`

No `.mind-detective/` cross-case Project Memory, personal priors, `mind-detective-longterm`, prospective-memory workflow, prevention skill, external evidence connectors, MAX/VK/Telegram/voice/web adapters, `ModelAdapter`, model credentials, live multi-model benchmark, calibrated location probabilities, floor-plan modeling, automated private-file ingestion, medical diagnosis/cognitive assessment, or law-enforcement/theft-investigation workflow.

Each deferred capability requires a separate design/spec gate.

---

## 4. Canonical naming

- Repository: `mind-detective`
- Product display name: **MIND Detective / Детектив памяти**
- Plugin: `mind-detective`
- Future privileged connector plugin: `mind-detective-connectors`
- Future local memory root: `.mind-detective/`
- Machine schema prefix: `mind-detective-*`
- Machine reason-code prefix: `MD_`

The earlier working label `memory-detective` is not used as a second runtime namespace.

---

## 5. Repository architecture

```text
mind-detective/
├── .agents/
│   └── plugins/marketplace.json
├── .claude-plugin/
│   └── marketplace.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   ├── releases/
│   │   ├── release.json
│   │   └── 0.1.0.md
│   └── workflows/
│       ├── ci.yml
│       ├── methodology-freshness.yml
│       └── publish-current-release.yml
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── README.en.md
├── CHANGELOG.md
├── CHANGELOG.en.md
├── CONTRIBUTING.md
├── SECURITY.md
├── SECURITY.en.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE.en.md
│   ├── PLUGIN_STANDARD.md
│   ├── PLUGIN_STANDARD.en.md
│   ├── RELEASE_POLICY.md
│   ├── RELEASE_POLICY.en.md
│   ├── GETTING_STARTED.md
│   ├── GETTING_STARTED.en.md
│   ├── METHODOLOGY.md
│   ├── METHODOLOGY.en.md
│   ├── REQUIREMENTS.md
│   ├── SDD_TDD_WORKFLOW.md
│   ├── PRIVACY.md
│   ├── RISK_REGISTER.md
│   ├── GLOSSARY.md
│   ├── GLOSSARY.en.md
│   ├── CONTRACT_MATRIX.json
│   ├── EVAL_TOKEN_REGISTRY.json
│   ├── schemas/
│   ├── adr/
│   ├── reviews/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── plugins/
│   └── mind-detective/
│       ├── .codex-plugin/plugin.json
│       ├── .claude-plugin/plugin.json
│       ├── README.md
│       ├── README.en.md
│       ├── CHANGELOG.md
│       ├── CHANGELOG.en.md
│       ├── THIRD_PARTY_NOTICES.md
│       ├── skills/
│       ├── references/
│       ├── scripts/
│       ├── tests/
│       └── evals/
├── scripts/
│   ├── validate_repo.py
│   ├── contract_controls.py
│   ├── bilingual_docs.py
│   └── release_manifest.py
├── tests/
│   ├── test_boundaries.py
│   ├── test_contract_matrix.py
│   ├── test_eval_contract.py
│   └── test_release_contract.py
└── pyproject.toml
```

P0 may implement the tree incrementally under TDD; no empty directory is required merely to match the diagram.

---

## 6. Layer boundaries

```text
L3  skills / orchestration
    routing, interview stages, presentation, limitation propagation

L2  deterministic domain helpers
    evidence, question guard, timeline, zones, ACH, redflags

L1  repository contracts
    schemas, requirement IDs, validators, contract matrix, eval vocabulary
```

There is no transport layer in P0. `plugins/mind-detective` must not import network SDKs, browser clients, cloud storage clients, messenger clients, model-provider clients, or external connector implementations. AST checks enforce a scoped denylist; they do not claim proof of absence of every possible I/O technique.

---

## 7. Evidence model

Canonical classes: `USER_RECALLED`, `HABITUAL`, `USER_STATED`, `EXTERNAL`, `SEARCHED`, `INFERRED`, `HYPOTHESIS`, `METHODOLOGY`.

Normalized statement metadata includes `id`, `text`, `class`, `author`, `created_at`, `elicited_by`, `detail_level`, `confidence_self`, `limitations`. `confidence_self` is user self-report, not probability of truth.

Non-promotion invariants:

1. Agent cannot originate `USER_RECALLED`, `HABITUAL`, or `USER_STATED` on the user's behalf.
2. `HABITUAL` cannot become `USER_RECALLED` because it is repeated, plausible or high-confidence.
3. Sensory/context detail is metadata, not mechanical truth certification.
4. Absence of recall is not negative evidence by default.
5. `METHODOLOGY` cannot satisfy a case-specific evidence requirement.
6. `HYPOTHESIS` remains a hypothesis until supported evidence/rule changes state.

---

## 8. Interview and contamination boundary

The project uses Cognitive Interview principles as **transferred methodology**, not proof that a forensic protocol has validated household lost-item recovery.

Stages: `FREE_ACCOUNT`, `CONTEXT_RECONSTRUCTION`, `TIMELINE_CLARIFICATION`, `CONTRADICTION_CLARIFICATION`, `SEARCH_FOLLOWUP`.

`question_policy.py` defines stage-aware structural constraints. `question_lint.py` returns `GuardResult` with `allowed`, stable `codes`, and bounded `details`.

P0 stable guard codes include `MD_Q_NEW_LOCATION`, `MD_Q_CLOSED_FREE_ACCOUNT`, `MD_Q_MULTI`, `MD_Q_PRESUPPOSITION`, `MD_Q_THIRD_PARTY_BLAME`, `MD_CLAIM_UNSUPPORTED_LOCATION`, `MD_CLAIM_UNCALIBRATED_PROBABILITY`.

The linter is intentionally conservative. Semantic edge cases remain covered by evals/review; documentation must not claim total prevention of suggestive questioning.

---

## 9. Timeline

The artifact uses **last supported contact**, not “last confirmed contact”, because user recollection is not independent verification. Habit alone cannot establish last supported contact; missing timestamps remain unknown; contradictions remain explicit; event boundaries may be annotated but do not change search weights; impossible explicit ordering produces structured error/finding rather than traceback.

Normative artifact: `mind-detective-timeline/v1`.

---

## 10. Event-boundary discipline

```text
event_boundary
  → METHODOLOGY cue
  → may motivate a neutral reconstruction question
  → may contribute to a HYPOTHESIS reason
  → does NOT automatically increase a zone weight
```

No code path implements `doorway => +X%` or equivalent.

---

## 11. Search allocation

The search helper allocates effort; it does not predict the true location. Normative artifact: `mind-detective-search-plan/v1`.

Zone fields include `id`, user-derived label, `belief_weight`, reasons, effort, rounds, and `calibration_status: UNCALIBRATED`. An explicit `UNKNOWN_OR_OUTSIDE` remainder is representable.

P0 weights may derive from user recall, capped/weak habitual context, physical/logical containment supported by timeline facts, search status and explicit unknown remainder. Population statistics are not presented as personalized probability.

Search update:

```text
weight_after_raw = weight_before × miss_factor(search_method)
normalize(all zone weights + UNKNOWN_OR_OUTSIDE)
```

`miss_factor` is operational search-coverage policy, not validated household POD. A failed search alone never zeroes a nonzero zone.

---

## 12. Competing hypotheses

P0 families include: item remains within current system; item left the system; item was moved after last supported contact; habitual sequence substituted for episode; item remains in searched zone but was missed; evidence insufficient.

Third-party hypotheses remain non-accusatory. The system does not turn “item may have been moved” into blame toward spouse/child/colleague without user-supplied specific evidence, and even then remains evidence-focused.

---

## 13. Safety and fallback-first

Functional/safety signals rather than age drive routing: disorientation, safety-impacting confusion, missing person, theft with meaningful harm, critical medication uncertainty, time-critical identity/travel/legal documents, immediate danger.

High-consequence/time-critical cases run fallback before extended search. P0 does not hard-code jurisdiction-specific medical/legal instructions without separately controlled current sources.

---

## 14. Skill contracts

Router order: safety/red flag → high-consequence fallback → IN_MOMENT support → truthful limitation for deferred workflow.

Quickcheck is bounded and generic. Interview is free-account first and guarded clarification second. Timeline preserves provenance/gaps/contradictions. Zones create/update uncalibrated search allocation. Hypotheses are required after unresolved first structured round or fixation. Fallback produces parallel contingency categories. Debrief records current-session outcome only; P0 does not persist cross-case baselines.

---

## 15. Artifact contracts

P0 schemas:

1. `mind-detective-recall-transcript/v1`
2. `mind-detective-timeline/v1`
3. `mind-detective-search-plan/v1`
4. `mind-detective-hypothesis-matrix/v1`
5. `mind-detective-fallback-plan/v1`
6. `mind-detective-case-outcome/v1`

Every artifact has schema, generated timestamp, case-local ID, provenance references where applicable, limitations, no secrets, and no hidden chain-of-thought. Rationale is concise structured reason codes, not private model reasoning.

---

## 16. Stable P0 requirements

- `MD-REQ-EVIDENCE-01` Agent cannot originate a user recollection.
- `MD-REQ-EVIDENCE-02` `HABITUAL` never promotes to `USER_RECALLED`.
- `MD-REQ-EVIDENCE-03` Missing recall is not negative evidence by default.
- `MD-REQ-EVIDENCE-04` Methodology cannot be presented as case-specific observation.
- `MD-REQ-QUESTION-01` Production skill contract requires submitted interview candidates to cross guard boundary before display; generic-host invocation enforcement is explicitly limited.
- `MD-REQ-QUESTION-02` Unsupported concrete locations are not introduced by guarded questions/claims.
- `MD-REQ-QUESTION-03` Free-account stage rejects closed leading collection patterns.
- `MD-REQ-QUESTION-04` Named third-party blame is not generated as investigative hypothesis.
- `MD-REQ-TIMELINE-01` Last supported contact preserves evidence class and cannot be established by habit alone.
- `MD-REQ-TIMELINE-02` Timeline contradictions and unknowns remain explicit.
- `MD-REQ-SEARCH-01` Search miss reduces rather than zeroes a nonzero zone weight.
- `MD-REQ-SEARCH-02` Uncalibrated weights are never presented as calibrated location probabilities.
- `MD-REQ-SEARCH-03` Unknown/outside remainder remains representable.
- `MD-REQ-SEARCH-04` Event boundary alone does not mechanically boost zone weight.
- `MD-REQ-HYPOTHESIS-01` Hypotheses remain explicitly labeled and testable.
- `MD-REQ-SAFETY-01` Supported red flags exit/limit ordinary flow.
- `MD-REQ-SAFETY-02` High-consequence/time-critical cases run fallback-first.
- `MD-REQ-BOUNDARY-01` P0 core remains transport/connector-free.
- `MD-REQ-EVAL-01` High-risk contracts have exact test traceability and adversarial eval coverage.
- `MD-REQ-DOCS-01` Key public docs are RU-primary with EN mirror and reciprocal navigation.
- `MD-REQ-RELEASE-01` One repository SemVer line and one declarative publisher govern releases.

Normative MUST/never in production docs is mechanically traced or explicitly labeled semantic-review/policy-only.

---

## 17. Contract matrix

`docs/CONTRACT_MATRIX.json` starts at exact-function traceability. Each high-risk entry links stable requirement → owning SKILL.md → helper → exact Python test selector → relevant reference. Repository validation checks structural traceability and exact selector existence through AST, not semantic quality of assertions.

---

## 18. Eval contract

P0 uses `scenarios.json` version 2 with exact route, outcome enum, registered machine tokens, semantic `must_convey`, and semantic `must_not_claim`. Initial adversarial coverage includes direct location demand, habit-as-proof, new location, synonymous leading phrasing, third-party blame, repeated quick searches as proof of absence, percentage request, imminent passport, medication uncertainty, disorientation, event-boundary-as-proof, and unresolved first round.

Green fixture validation is not a claim that a live model semantically passed.

---

## 19. SDD + TDD

```text
SPEC
  ↓
RED
  ↓
GREEN
  ↓
REFACTOR
  ↓
TRACE
  ↓
EVAL
  ↓
VERIFY
```

Executable high-risk behavior starts with failing regression tests. Guards have normal and bypass/adversarial tests. Stable machine errors are asserted. Documentation cannot claim stronger enforcement than code/CI provides.

---

## 20. CI

Initial CI covers Python syntax/compile, Ruff, mypy, unittest suites, repository validator, skill/plugin metadata, schemas, contract matrix, eval vocabulary, AST boundaries, bilingual/changelog parity, secret scan, release manifest, and full-SHA action pinning.

---

## 21. Methodology freshness

Reference classes: scientific methodology `365` days, safety/high-consequence guidance `180`, future external API/platform fact `90`. Age hard-fails in ordinary PR validation only for changed controlled files; malformed/missing/future markers always fail. Scheduled strict workflow checks the whole controlled set and opens/updates freshness issue behavior rather than causing unrelated PR time bombs.

Initial sources include Fisher/Geiselman/Amador on Cognitive Interview, Loftus on misinformation, contemporary misinformation replication work, event-boundary studies, and Koopman search theory; product docs must distinguish direct evidence from transferred methodology and must not infer a household effect size.

---

## 22. Privacy

P0 is text-only and transport-free. No credentials, automatic file crawling, hidden connector access, floor-plan/value-inventory requirement, or chain-of-thought artifact storage. Artifacts minimize identifying detail where unnecessary. Cross-case persistence is deferred because it creates a new contamination/privacy/write boundary.

---

## 23. Project Memory direction

A future separately designed P1 may add `.mind-detective/profile.yaml`, case artifacts and baselines. Cross-case profile/baseline mutation is consequential because incorrect persistence can bias future cases; future design therefore requires preview → explicit approval → persistence. No P1 compatibility abstraction exists in P0.

---

## 24. Release architecture

Repository SemVer and plugin SemVer are independent. P0/P1 labels are milestones, not version schemes. Human-approved release intent lives in `.github/releases/release.json`. Changed files do not authorize plugin publication. The only active publisher is `.github/workflows/publish-current-release.yml`.

Publication gates: exact-head CI → semantic/review evidence → human merge → post-merge exact-main CI → human-approved release intent → publisher → exact tag-SHA validation → immutable GitHub Release. Conflicting/ambiguous tag/release state fails closed; published history is not retargeted.

---

## 25. Planned release sequence

`0.1.0` — P0 Core Detective. Candidate `0.2.0` — P1 Case Memory only if P0 demonstrates value. Candidate `0.3.0` — long-term workflow only after separate methodology review. Subsequent candidates may include executable benchmark, opt-in connectors and product surfaces. `1.0.0` is reserved for stabilized contracts supported by pilot evidence.

---

## 26. ADR foundation set

1. ADR-001 Behavioral kernel and plugin-local runtime.
2. ADR-002 Evidence classes and non-promotion.
3. ADR-003 Question/claim guard as primary safety boundary, with truthful generic-host enforcement limitation.
4. ADR-004 Uncalibrated search allocation.
5. ADR-005 Transport-free P0 and deferred connectors.
6. ADR-006 SDD/TDD exact traceability.
7. ADR-007 Release governance.
8. ADR-008 P0 YAGNI non-goals.

---

## 27. Acceptance criteria

Release review requires: end-to-end IN_MOMENT installed-plugin flow without network dependency; guarded candidate path with negative tests; truthful generic-host limitation; evidence non-promotion; explicit timeline unknowns/contradictions; search update never zeroes by failed search alone; no user-facing calibrated probability; event boundaries do not alter weights; safety/fallback scenarios route correctly; exact contract selectors exist/run; eval v2 fixtures validate; AST boundary passes; RU/EN parity passes; actions pinned; one declarative release path; exact PR-head CI green; review evidence separates mechanical from semantic/scientific validation; human authorization required before merge/publication.

---

## 28. Risks

Key risks and mitigations: memory contamination → guard + evals; linter false confidence → scoped enforcement wording; pseudo-scientific percentages → `UNCALIBRATED`; doorway cargo-cult → no weight effect; habit/episode confusion → non-promotion; blame fixation → neutral hypotheses; endless search → bounded next actions/fallback; framework overbuilding → one plugin/no shared runtime; future persistence contamination → separate P1 gate; CI/release drift → stable requirements/traceability/manifest/publisher.

---

## 29. Final P0 decisions

Python helper language; independently installable transport-free plugin; no root shared runtime; agent cannot create user recall; sensory detail is metadata; last supported contact terminology; event boundaries are cues not priors; search weights are uncalibrated; failed search uses multiplicative reduction and does not zero by itself; no persistent cross-case baseline; no connector/model/surface abstraction; exact-function traceability from first release; one manifest + one publisher.

---

## 30. Implementation transition

Canonical implementation plan: `docs/superpowers/plans/2026-09-09-mind-detective-foundation-implementation.md`. Production implementation follows that task-by-task TDD plan using Superpowers execution skills; no release publication occurs before exact-head/post-merge gates and explicit human authorization.