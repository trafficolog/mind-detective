# MIND Detective Foundation Design

**Status:** Self-reviewed; written-spec human review pending  
**Date:** 2026-09-08  
**Target repository:** `trafficolog/mind-detective`  
**Target first release:** repository `0.1.0`, plugin `mind-detective-v0.1.0`  
**Development method:** SDD + TDD, Superpowers workflow, DRY/KISS/YAGNI  
**Reference architecture:** behavioral/contracts approach proven in `trafficolog/yandex-ai-plugins-skills`

---

## 1. Executive summary

MIND Detective is an evidence-safe methodology runtime for helping a user search for a misplaced item without pretending that an LLM knows where the item is.

The first release is deliberately narrow: one complete **IN_MOMENT** vertical slice for an item lost within minutes or hours. It combines a conversational skill layer with deterministic helpers for evidence classification, utterance safety, timeline reconstruction, search allocation, competing hypotheses, safety routing, and case debrief.

The supported product claim is not “AI finds lost things.” It is:

> MIND Detective helps a user reconstruct what is supported by their own account, avoid memory-contaminating prompts, allocate search effort explicitly, record what has actually been checked, and choose the next bounded action while preserving uncertainty.

The highest-risk interaction is an agent utterance that can contaminate the user's later recollection, assign blame, introduce an unsupported location, or turn an uncalibrated heuristic into a false fact.

P0 therefore defines a deterministic guard contract:

```text
candidate structured utterance
        ↓
conversation-stage policy
        ↓
utterance_lint
        ↓
ALLOW or BLOCK(machine code)
        ↓
allowed candidate for user-visible output
```

**Enforcement boundary:** the helper path is fail-closed for candidates submitted to it. Production skills MUST route investigative questions/claims through that path. Generic skill hosts such as Claude Code/Codex do not provide this repository with a pre-send interception hook, so P0 cannot mechanically prove that an arbitrary host/model never bypasses the helper. Host-level compliance is therefore covered by skill contract + adversarial eval + review. A future dedicated bot/web/voice surface may make end-to-end interception mechanically enforceable. The repository must state this limitation explicitly and never equate green helper tests with proof that every model utterance was guarded.

The first release is plugin-first, independently installable, transport-free, and does not introduce a shared runtime package, external connectors, model SDKs, web UI, voice surface, or cross-case personalization.

---

## 2. Design principles

### 2.1 Behavioral kernel, not a premature shared library

The repository adopts the same lesson as the current Yandex plugin architecture: common architecture is primarily a **specification, stable requirement IDs, schemas, validators, conformance tests, and exact traceability**.

P0 does **not** create a root `kernel/` runtime dependency consumed by the plugin. Executable code stays inside the independently installable `plugins/mind-detective/` boundary until there is demonstrated reuse plus a defined distribution contract.

This prevents formal DRY from breaking installability.

### 2.2 LLM for dialogue; deterministic code for invariants

The LLM may route, summarize user-provided statements without inventing claims, select allowed neutral question forms, explain limitations, present helper output, and formulate explicitly labeled hypotheses.

The LLM is not the source of truth for evidence-class promotion, guard result codes, timeline consistency, search-weight update math, or deterministic red-flag rules.

### 2.3 Progressive disclosure

`SKILL.md` files are short discoverable workflow contracts. Longer methodology, citations, examples, and policy live in `references/`. Executable logic lives in `scripts/`; regression coverage lives in `tests/`; adversarial routing/semantic expectations live in `evals/`.

### 2.4 Truthful confidence

The system distinguishes user recall, habit, user-stated context, searched observations, deterministic inference, hypotheses, and methodology. It never converts an uncalibrated search weight into “probability the item is there.”

### 2.5 Safety before optimization

A faster search is not a success if it is achieved by leading the user, inventing a location, making an accusation, masking a time-critical fallback, or overstating enforcement.

---

## 3. Product scope

### 3.1 P0 / `0.1.0` in scope

One complete **IN_MOMENT** flow:

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

Production skills:

1. `mind-detective` — router and safety triage.
2. `mind-detective-quickcheck` — short high-value pre-interview checks.
3. `mind-detective-interview` — free account followed by neutral clarification.
4. `mind-detective-timeline` — reconstruct supported sequence and loss window.
5. `mind-detective-zones` — search allocation and round updates.
6. `mind-detective-hypotheses` — competing-hypothesis matrix after unresolved first round or fixation.
7. `mind-detective-fallback` — time-critical/high-consequence parallel recovery plan.
8. `mind-detective-debrief` — current-session outcome; no cross-case baseline mutation in P0.

Deterministic helpers:

- `evidence.py`
- `utterance_policy.py`
- `utterance_lint.py`
- `timeline.py`
- `zones.py`
- `ach.py`
- `redflags.py`
- `schemas.py`

Repository-level enforcement:

- stable requirement IDs;
- plugin validator;
- exact-selector contract matrix;
- eval contract v2;
- AST boundary tests;
- RU-primary + EN mirror key docs;
- secret scanning;
- pinned GitHub Actions;
- declarative release manifest;
- one hardened publisher.

### 3.2 Explicitly out of scope for `0.1.0`

The following are intentionally deferred rather than scaffolded as empty abstractions:

- `.mind-detective/` cross-case Project Memory;
- personal priors or learned household base rates;
- long-term recall workflow;
- prospective-memory workflow (“did I lock/take/send?”);
- prevention/habit redesign as a separate skill;
- external evidence connectors (EXIF, calendar, messages, cloud APIs);
- MAX/VK/Telegram/voice/web adapters;
- `ModelAdapter` provider abstraction;
- model API credentials;
- live multi-model benchmark;
- calibrated location probabilities;
- floor-plan modeling;
- automatic private-file ingestion;
- medical diagnosis or cognitive assessment;
- law-enforcement or theft investigation workflow.

Each deferred capability requires a separate design/spec gate.

---

## 4. Canonical naming

- Repository: `mind-detective`
- Product display name: **MIND Detective / Детектив памяти**
- Plugin: `mind-detective`
- Future privileged connector plugin: `mind-detective-connectors`
- Future local memory root: `.mind-detective/`
- Schema prefix: `mind-detective-*`
- Machine reason-code prefix: `MD_`

The earlier working label `memory-detective` is not used as a second runtime namespace.

---

## 5. Repository architecture

Target shape after P0 implementation:

```text
mind-detective/
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
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
│   └── superpowers/{specs,plans}/
├── plugins/mind-detective/
│   ├── .agents-plugin/plugin.json
│   ├── .claude-plugin/plugin.json
│   ├── README.md
│   ├── README.en.md
│   ├── CHANGELOG.md
│   ├── CHANGELOG.en.md
│   ├── THIRD_PARTY_NOTICES.md
│   ├── skills/
│   ├── references/
│   ├── scripts/
│   ├── tests/
│   └── evals/
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

P0 implements the tree incrementally under TDD; no empty directory is required merely to match the diagram.

---

## 6. Layer boundaries

```text
L3  skills / orchestration
    routing, interview stages, presentation, limitation propagation

L2  deterministic domain helpers
    evidence, utterance guard, timeline, zones, ACH, redflags

L1  repository contracts
    schemas, requirement IDs, validators, contract matrix, eval vocabulary
```

There is intentionally no transport layer in P0.

`plugins/mind-detective` must not import network SDKs, browser clients, cloud storage clients, messenger clients, or external connector implementations. Repository AST tests enforce a bounded denylist appropriate to the Python codebase. This proves only the supported static boundary, not the absence of every conceivable form of I/O.

A future `mind-detective-connectors` plugin will be separately installable and will emit structured `EXTERNAL` evidence with provenance.

---

## 7. Evidence model

### 7.1 Classes

| Class | Meaning | Allowed origin |
|---|---|---|
| `USER_RECALLED` | User reports an episodic memory/recollection | user statement only |
| `HABITUAL` | User reports a routine/usual placement/schema | user statement only |
| `USER_STATED` | User supplies context such as item properties, deadline, constraints | user statement only |
| `EXTERNAL` | Evidence from a future external connector/parser | not produced by P0 core |
| `SEARCHED` | User confirms a search action/method/result | user-confirmed action |
| `INFERRED` | Deterministic conclusion from supported inputs and a named rule | helper only |
| `HYPOTHESIS` | Testable explanation that remains unconfirmed | agent or user, explicitly labeled |
| `METHODOLOGY` | General research/methodological principle, never a fact about this case | references/methodology |

### 7.2 Statement metadata

```json
{
  "id": "stmt-...",
  "text": "...",
  "class": "USER_RECALLED",
  "author": "user",
  "created_at": "RFC3339 timestamp",
  "elicited_by": "utterance-id or null",
  "detail_level": "LOW|MEDIUM|HIGH",
  "confidence_self": "LOW|MEDIUM|HIGH|UNSTATED",
  "limitations": []
}
```

`confidence_self` is the user's self-report, not an estimated probability of truth.

### 7.3 Non-promotion invariants

1. The agent cannot originate `USER_RECALLED`, `HABITUAL`, or `USER_STATED` on the user's behalf.
2. `HABITUAL` cannot be promoted to `USER_RECALLED` because it is repeated, plausible, detailed, or high-confidence.
3. Sensory/contextual detail is metadata and does not mechanically certify truth.
4. Absence of recall does not become evidence that an event did not happen.
5. `METHODOLOGY` cannot satisfy a case-specific evidence requirement.
6. `HYPOTHESIS` remains a hypothesis until supported by a separately defined rule/evidence change.

---

## 8. Interview and memory-contamination guard

### 8.1 Scientific posture

The project uses cognitive-interview principles as **transferred methodology**, not as proof that a forensic protocol has been validated for household lost-item recovery.

Design implications:

- obtain a free account before detailed clarification;
- reinstate context in neutral terms;
- encourage retrieval without rewarding a particular answer;
- avoid misleading post-event information;
- preserve provenance of how a statement was elicited.

The repository must not claim a validated household lost-item effect size unless direct evidence is later obtained.

### 8.2 Conversation stages

1. `FREE_ACCOUNT`
2. `CONTEXT_RECONSTRUCTION`
3. `TIMELINE_CLARIFICATION`
4. `CONTRADICTION_CLARIFICATION`
5. `SEARCH_FOLLOWUP`

### 8.3 Guard interface

`utterance_policy.py` defines stage-aware rules. `utterance_lint.py` validates a structured candidate:

```json
{
  "kind": "QUESTION",
  "text": "...",
  "stage": "FREE_ACCOUNT",
  "known_entities": [],
  "known_locations": []
}
```

and returns:

```json
{
  "allowed": false,
  "codes": ["MD_Q_NEW_LOCATION"],
  "details": []
}
```

A submitted candidate that is blocked is never returned as allowed. Production skill contracts require reformulation rather than bypass.

### 8.4 Codes

| Code | Invariant |
|---|---|
| `MD_Q_NEW_LOCATION` | Question introduces a concrete location/container not supplied by the user as case data. |
| `MD_Q_CLOSED_FREE_ACCOUNT` | Closed yes/no collection pattern during free account when an open neutral prompt is required. |
| `MD_Q_MULTI` | More than one material question in a candidate. |
| `MD_Q_PRESUPPOSITION` | Unsupported action, location, cause, or person is presupposed. |
| `MD_Q_THIRD_PARTY_BLAME` | Named/role-based accusation is introduced as a hypothesis. |
| `MD_CLAIM_UNSUPPORTED_LOCATION` | Candidate claim states/implies a specific unsupported location. |
| `MD_CLAIM_UNCALIBRATED_PROBABILITY` | Candidate claim presents search weight as calibrated probability. |

### 8.5 Truthful enforcement statement

- **Mechanically enforced:** submitted candidate parsing, rule checks, machine codes, fail-closed result, negative tests, exact traceability.
- **Skill/eval/review enforced:** that a generic LLM host invokes the helper for every investigative utterance before showing it.
- **Deferred mechanical end-to-end enforcement:** a dedicated surface adapter with a mandatory pre-send guard hook.

The project will not claim “all model outputs are technically intercepted” in P0.

---

## 9. Timeline model

The timeline reconstructs the smallest supported sequence between the **last supported contact** with the item and the first supported observation that it was missing. “Supported” is used instead of “confirmed” because a user's recollection is evidence supplied by the user, not independently verified fact.

Normative artifact: `mind-detective-timeline/v1`.

Core fields:

```json
{
  "schema": "mind-detective-timeline/v1",
  "last_supported_contact": {"statement_id": "...", "class": "USER_RECALLED"},
  "first_noticed_missing": {"statement_id": "..."},
  "loss_window": {"start": "...", "end": "...", "precision": "..."},
  "events": [],
  "gaps": [],
  "contradictions": [],
  "limitations": []
}
```

Invariants:

- habit alone cannot establish `last_supported_contact`;
- missing timestamps remain unknown;
- contradictions are surfaced rather than silently resolved;
- event boundaries may be annotated but do not change a location weight by themselves;
- impossible ordering detected from explicit times returns a structured finding/code, not an unbounded traceback.

---

## 10. Event boundaries and methodology discipline

The project distinguishes **event segmentation** from a simplistic “doorway = forgetting” rule.

Research supports the broader proposition that event boundaries can affect memory organization/accessibility, while physical-doorway effects depend on task and experimental conditions. This does not justify a universal household-search prior.

P0 rule:

```text
event_boundary
  → METHODOLOGY cue
  → may motivate a neutral reconstruction question
  → may contribute to a HYPOTHESIS reason
  → does NOT automatically increase a search-zone weight
```

No code path implements `doorway => +X%` or an equivalent hidden rule.

---

## 11. Search allocation model

### 11.1 Purpose

The search helper allocates attention among candidate zones; it does not predict the item's true location.

Normative artifact: `mind-detective-search-plan/v1`.

```json
{
  "id": "zone-...",
  "label": "user-derived categorical label",
  "belief_weight": 0.0,
  "weight_reasons": [],
  "effort": "LOW|MEDIUM|HIGH",
  "rounds": [],
  "calibration_status": "UNCALIBRATED"
}
```

The plan includes `UNKNOWN_OR_OUTSIDE` where appropriate.

### 11.2 Initial weights

Transparent rules may use:

- user-recalled interactions;
- user-stated habitual placement, capped as weaker evidence;
- physical/logical containment from supported timeline facts;
- search status;
- explicit unknown remainder.

P0 does not use population statistics as personalized probability. Numeric constants are operational policy parameters labeled uncalibrated, not scientific facts.

### 11.3 Search-round update

Search theory motivates the principle that a failed search reduces but does not necessarily eliminate belief in a searched area.

P0 uses:

```text
weight_after_raw = weight_before × miss_factor(search_method)
normalize(all zone weights + UNKNOWN_OR_OUTSIDE)
```

`miss_factor` is an operational coverage parameter, not a validated household probability of detection.

For P0, a nonzero searched-zone weight is **never set to zero solely because a search round failed**. No “impossibility exception” is included in `0.1.0`; such a rule would require its own explicit future contract.

### 11.4 User-facing semantics

Allowed:

- “this zone remains higher priority because…”;
- “a quick glance should reduce priority less than a systematic search”;
- “this is an uncalibrated search weight used to order effort.”

Forbidden:

- “73% chance your keys are there”;
- “scientifically, this location is most likely”;
- “three searches prove it is not there.”

---

## 12. Competing hypotheses

The hypothesis matrix exists to reduce fixation after an unsuccessful first structured round or explicit fixation on one story.

P0 categorical families include:

- item remained within the current closed system;
- item left the current system during the loss window;
- item was moved after the last supported contact;
- user recalled a habitual sequence rather than the actual episode;
- item remains in an already searched zone but was missed;
- current evidence is insufficient.

A case-specific hypothesis must stay labeled `HYPOTHESIS` and state what would support or weaken it.

The system does not transform “someone may have moved it” into “your spouse/child/colleague moved it.” User-supplied evidence about another person may be recorded neutrally, but MIND Detective does not assign blame.

Normative artifact: `mind-detective-hypothesis-matrix/v1`.

---

## 13. Safety routing and fallback-first behavior

### 13.1 Red-flag categories

Routing is based on functional/safety signals, not age alone:

- disorientation or inability to account for how the user arrived somewhere;
- sudden/progressive confusion materially affecting safety;
- a missing person;
- suspected theft with meaningful safety/financial/legal harm;
- uncertainty around critical medication use where guessing/re-dosing may be unsafe;
- time-critical identity/travel/legal documents;
- immediate physical danger.

The tool does not diagnose a medical condition or adjudicate a crime.

### 13.2 Fallback-first

High-consequence/time-critical cases activate a parallel contingency **before** extended searching.

P0 fallback remains generic and safe: it tells the user to use the relevant current authoritative/official/medical channel and keeps the search bounded. Detailed jurisdiction-specific or medication-specific instructions are not hard-coded without current authoritative sourcing and freshness control.

Examples:

- passport + imminent travel → official/current document contingency first, bounded search in parallel;
- medication uncertainty → contact an appropriate medical/pharmacy/poison-control-type authority rather than infer dosing from memory;
- vehicle/house keys with security exposure → consider the relevant current security contingency in parallel with search.

Normative artifact: `mind-detective-fallback-plan/v1`.

---

## 14. Skill contracts

### Router — `mind-detective`

Routing order:

1. safety/red flag;
2. fallback-first requirement;
3. supported IN_MOMENT flow;
4. truthful limitation for deferred LONG_TERM/PROSPECTIVE flows.

### Quickcheck

A bounded pre-interview step. It may use generic current-state self-checks (for example, whether the item is on the user's person or already in active use) without turning them into recollection claims. It does not enumerate a long list of household locations.

### Interview

Free account first; neutral clarification second. Skill contract requires each investigative candidate utterance to be submitted to the guard. Output: `mind-detective-recall-transcript/v1`.

### Timeline

Consumes transcript evidence, preserves provenance, surfaces gaps/contradictions. Output: `mind-detective-timeline/v1`.

### Zones

Consumes supported timeline + user evidence + search rounds. Produces/updates uncalibrated search allocation. Output: `mind-detective-search-plan/v1`.

### Hypotheses

Used after unresolved first structured round or fixation. Output: `mind-detective-hypothesis-matrix/v1`.

### Fallback

Produces a parallel contingency when consequence/time dominates continued searching. Output: `mind-detective-fallback-plan/v1`.

### Debrief

Records current-session outcome only. Output: `mind-detective-case-outcome/v1`. P0 does not silently persist personal baselines.

---

## 15. Artifact contracts

P0 normative schemas:

1. `mind-detective-recall-transcript/v1`
2. `mind-detective-timeline/v1`
3. `mind-detective-search-plan/v1`
4. `mind-detective-hypothesis-matrix/v1`
5. `mind-detective-fallback-plan/v1`
6. `mind-detective-case-outcome/v1`

Every artifact includes schema, generated timestamp, case-local ID, relevant provenance, limitations, no secrets, and no hidden chain-of-thought. Artifacts contain concise structured rationale/reason codes rather than private model reasoning.

---

## 16. Stable P0 requirements

`docs/REQUIREMENTS.md` created during implementation will assign at least these stable IDs:

| ID | Requirement |
|---|---|
| `MD-REQ-EVIDENCE-01` | Agent cannot originate a user recollection. |
| `MD-REQ-EVIDENCE-02` | `HABITUAL` never promotes to `USER_RECALLED`. |
| `MD-REQ-EVIDENCE-03` | Missing recall is not negative evidence by default. |
| `MD-REQ-EVIDENCE-04` | Methodology cannot be presented as case-specific observation. |
| `MD-REQ-UTTERANCE-01` | Production investigative skill contract requires candidate questions/claims to use the guard path before display; helper enforcement applies to submitted candidates, while generic-host invocation compliance remains eval/review evidence. |
| `MD-REQ-UTTERANCE-02` | Unsupported concrete locations are rejected in candidate questions/claims. |
| `MD-REQ-UTTERANCE-03` | Free-account stage rejects closed leading collection patterns. |
| `MD-REQ-UTTERANCE-04` | Named third-party blame is rejected. |
| `MD-REQ-UTTERANCE-05` | Uncalibrated location-probability claims are rejected. |
| `MD-REQ-TIMELINE-01` | Last supported contact preserves evidence class and cannot be established by habit alone. |
| `MD-REQ-TIMELINE-02` | Timeline contradictions and unknowns remain explicit. |
| `MD-REQ-SEARCH-01` | Failed search reduces rather than zeroes a nonzero searched-zone weight. |
| `MD-REQ-SEARCH-02` | Uncalibrated weights are never presented as calibrated location probabilities. |
| `MD-REQ-SEARCH-03` | Unknown/outside remainder remains representable. |
| `MD-REQ-SEARCH-04` | Event boundary alone does not mechanically boost zone weight. |
| `MD-REQ-HYPOTHESIS-01` | Hypotheses remain explicitly labeled and testable. |
| `MD-REQ-SAFETY-01` | Supported red flags exit/limit ordinary investigative flow. |
| `MD-REQ-SAFETY-02` | High-consequence/time-critical cases run fallback-first. |
| `MD-REQ-BOUNDARY-01` | P0 core remains transport/connector-free. |
| `MD-REQ-EVAL-01` | High-risk contracts have exact test traceability and adversarial eval coverage. |
| `MD-REQ-DOCS-01` | Key public docs are RU-primary with EN mirror and reciprocal navigation. |
| `MD-REQ-RELEASE-01` | One repository SemVer line and one declarative publisher govern releases. |

Every normative MUST/never in production docs is either mechanically traced (`[enforced: ...]`) or explicitly marked review/policy (`[unenforced: ...]`). The host-level clause of `MD-REQ-UTTERANCE-01` must be marked as non-mechanical until a mandatory pre-send surface exists.

---

## 17. Contract matrix

`docs/CONTRACT_MATRIX.json` starts with exact-function traceability, equivalent in intent to the hardened v2 contract in the reference Yandex repository.

Each high-risk entry links:

```text
stable requirement ID
  → owning SKILL.md
  → helper path
  → exact Python test selector
  → relevant reference/methodology source
```

Example:

```text
MD-REQ-UTTERANCE-02
  → skills/mind-detective-interview/SKILL.md
  → scripts/utterance_lint.py
  → tests/test_utterance_lint.py::test_rejects_new_concrete_location
  → references/question-rules.md
```

Validator checks structural traceability and exact selector existence via AST. It does not prove assertion quality, runtime model behavior, or host invocation compliance.

---

## 18. Eval contract

P0 adopts `evals/scenarios.json` version 2 semantics:

- exact `must_route_to`;
- `outcome ∈ {comply, comply_with_limitations, refuse}`;
- registered `must_mention_tokens` only for machine vocabulary;
- natural-language `must_convey`;
- semantic `must_not_claim`.

Initial adversarial coverage includes at least:

1. “Just tell me where my keys are.”
2. “I always put them there” treated as if habit proved this episode.
3. Candidate introduces a new concrete location.
4. Synonymous/obfuscated leading prompt attempts to bypass the guard.
5. User blames spouse/child/colleague.
6. Three quick searches are treated as proof of absence.
7. User asks for percentage probability by location.
8. Passport with imminent travel.
9. Medication uncertainty.
10. Disorientation/red-flag signal.
11. Event boundary requested as scientific proof of location.
12. Unresolved first round requiring competing hypotheses.
13. Model/host is instructed to skip `utterance_lint`; expected behavior preserves the guard contract, while result is semantic eval evidence rather than proof of host interception.

Repository CI validates fixture structure, token registry, routes, and referenced skills. Green fixture validation is not semantic model-pass evidence.

---

## 19. SDD + TDD workflow

```text
SPEC
  stable requirement / schema / ADR change
        ↓
RED
  exact failing regression test
        ↓
GREEN
  minimum implementation satisfying the contract
        ↓
REFACTOR
  preserve behavior and boundaries
        ↓
TRACE
  exact CONTRACT_MATRIX selector
        ↓
EVAL
  adversarial routing/semantic fixture where applicable
        ↓
VERIFY
  validator + tests + lint + typecheck + security/release checks
```

Rules:

1. No deterministic production behavior before a failing test where test-first is applicable.
2. A high-risk guard has a normal test plus bypass/adversarial negative coverage.
3. Machine errors carry stable codes; “some exception happened” is insufficient for a high-risk contract.
4. Docs cannot claim stronger enforcement than tests/CI/host architecture provide.
5. Green CI is mechanical evidence, not proof of scientific validity or semantic model behavior.

---

## 20. CI design

Initial CI covers:

- Python compile/syntax;
- `ruff`;
- `mypy` for typed executable code;
- `pytest`;
- repository validator;
- plugin/skill metadata validation;
- JSON schema validation;
- exact contract-matrix validation;
- eval registry/vocabulary validation;
- AST boundary checks;
- bilingual-doc parity;
- changelog marker parity;
- secret scan / `gitleaks`;
- release-manifest validation;
- full-SHA pinning check for third-party GitHub Actions.

Third-party Actions are pinned to immutable full commit SHAs. Dependabot may propose updates; mutable major tags are not accepted in active workflows.

---

## 21. Methodology references and freshness

Methodology references are not treated like volatile APIs.

| Class | Review cadence | PR behavior |
|---|---:|---|
| scientific methodology | 365 days | hard age check only when controlled file changes; malformed/future marker always fails |
| safety/high-consequence guidance | 180 days | same path-aware rule |
| future external API/platform fact | 90 days | same path-aware rule |

A scheduled strict workflow checks the full controlled set and opens/updates a freshness issue rather than making unrelated PRs fail because an untouched scientific reference aged.

### 21.1 Initial verified scientific basis

Methodology docs distinguish direct evidence from product transfer. Initial source set:

- Fisher, Geiselman & Amador (1989), Cognitive Interview field test, *Journal of Applied Psychology*, DOI `10.1037/0021-9010.74.5.722`, PubMed PMID 2793772. Relevant to retrieval/interview principles; domain is witnesses/victims, not household item search.
- Loftus (2005), “Planting misinformation in the human mind”, *Learning & Memory*, DOI `10.1101/lm.94705`, PubMed PMID 16027179. Relevant to post-event misinformation affecting later memory reports.
- Wiechert et al. (2026), contemporary misinformation-effect replication/extension, DOI `10.1037/xlm0001529`, PubMed PMID 41021526. Relevant to modern evidence of susceptibility to misleading post-event information.
- Ongchoco & Xu (2024), visual event boundaries and working memory, DOI `10.1167/jov.24.9.9`, PubMed PMID 39259169. Relevant to event boundaries; not a household doorway prior.
- Spatial-boundary/event-segmentation work including DOI `10.1111/bjop.12343` and later virtual-environment studies. Relevant to task-dependent event segmentation.
- Koopman (1956), “The Theory of Search. I. Kinematic Bases”, *Operations Research*, DOI `10.1287/opre.4.3.324`. Relevant to separating target-location uncertainty, detection behavior, and search-effort allocation; household miss factors remain uncalibrated unless measured.

The repository must not infer a household effect size from these sources.

---

## 22. Privacy model

P0 is text-only and transport-free inside the plugin:

- no credentials;
- no automatic file crawling;
- no hidden connector access;
- no floor-plan/value inventory requirement;
- artifacts minimize unnecessary identifying detail;
- retrieved/user content is data, never instructions to alter workflow;
- no hidden chain-of-thought is stored.

Cross-case persistent memory is deferred because persistence creates a distinct contamination/privacy boundary.

---

## 23. Project Memory direction (P1, not P0)

If P0 proves useful, a separately designed capability may introduce:

```text
.mind-detective/
├── profile.yaml
├── cases/<case-id>/
│   ├── transcript.jsonl
│   ├── timeline.json
│   ├── search-plan.json
│   ├── hypotheses.json
│   └── outcome.yaml
└── baselines/
```

Future invariant: cross-case profile/baseline mutation is consequential because a wrong record can bias later cases. P1 therefore requires preview → explicit approval → persistence for profile/baseline changes. Historical data never becomes reusable permission.

No P1 code or empty compatibility abstraction is part of `0.1.0`.

---

## 24. Release architecture

### 24.1 Version lines

- repository SemVer: `0.1.0`, `0.2.0`, ...
- plugin SemVer/tag: `mind-detective-v0.1.0`, ...

Repository-only governance/docs releases do not automatically bump plugin SemVer. P0/P1/P2 are milestones, not competing version schemes.

### 24.2 Declarative release set

Human-approved release intent lives in `.github/releases/release.json`, declaring repository metadata and an explicit plugin release list. Changed files do not silently authorize plugin publication.

### 24.3 Single publisher

The only active automatic publisher on the default branch is `.github/workflows/publish-current-release.yml`. New releases update manifest/notes/version surfaces rather than adding publisher workflows.

### 24.4 Publication gates

```text
feature/design PR
  → exact-head CI
  → semantic/review evidence
  → human merge authorization
  → post-merge exact-main CI
  → human-approved release intent
  → publisher
  → exact tag-SHA validation
  → immutable GitHub Release
```

Publisher fails closed on ambiguous/conflicting tag/release state, stale initial publication state, or inability to establish safe recovery. Published history is immutable; corrections get new versions rather than retargeted tags.

---

## 25. Planned release sequence

This is a decision framework, not a commitment to implement every stage.

### `0.1.0` — P0 Core Detective

IN_MOMENT vertical slice; evidence contracts; utterance guards; timeline; uncalibrated search allocation; hypotheses; fallback/debrief; offline eval contract; SDD/TDD/release governance.

### `0.2.0` candidate — P1 Case Memory

Only if P0 shows value from resumability/personal baselines: persistent cases, approval-bound cross-case profile updates, contamination-safe baselines.

### `0.3.0` candidate — Long-term workflow

Only after separate methodology review: long-term recall, cue rotation, handoff, prevention/debrief extensions.

### Later candidates

Executable provider-neutral eval benchmark; opt-in external-evidence connector plugin; bot/web/voice surfaces.

`1.0.0` is reserved for stabilized public contracts supported by real pilot evidence, not a feature checklist.

---

## 26. Foundation ADR set

1. **ADR-001 — Behavioral kernel and plugin-local runtime** — no premature shared runtime package.
2. **ADR-002 — Evidence classes and non-promotion rules** — recall, habit, search observation, inference, hypothesis, methodology remain distinct.
3. **ADR-003 — Utterance guard and host-enforcement boundary** — deterministic submitted-candidate guard; generic-host invocation remains skill/eval/review until a mandatory pre-send surface exists.
4. **ADR-004 — Uncalibrated search allocation** — weights order effort, not household location probability.
5. **ADR-005 — Transport-free P0 and deferred connectors** — no external connector in core plugin.
6. **ADR-006 — SDD/TDD exact traceability** — stable IDs + exact selectors + truthful enforcement labels.
7. **ADR-007 — Release governance** — one repository SemVer line, independent plugin SemVer, one manifest, one publisher, immutable history.
8. **ADR-008 — P0 YAGNI boundary** — no Project Memory, long-term/prospective workflows, model adapters, product surfaces, or calibrated probabilities.

---

## 27. Acceptance criteria for `0.1.0`

Release review requires all of the following:

1. A user can traverse the IN_MOMENT flow end-to-end using the installed plugin without network dependencies.
2. `utterance_lint.py` fail-closes submitted unsupported-location, leading/free-account, third-party-blame, and pseudo-probability candidates with stable machine codes.
3. Production skills explicitly require guarded candidate generation; adversarial evals include instructions to bypass the guard. Documentation labels generic-host invocation as eval/review rather than end-to-end mechanical enforcement.
4. Evidence normalization cannot promote habit to recall or create user recall from agent text.
5. Timeline artifacts preserve unknowns and contradictions.
6. Failed search rounds never zero a nonzero zone solely because the search failed.
7. No user-facing artifact presents uncalibrated weights as calibrated location probability.
8. Event-boundary annotations do not change zone weights by themselves.
9. High-consequence/red-flag scenarios route to limitation/exit/fallback behavior.
10. Every high-risk matrix entry names an exact test selector that exists and executes in CI.
11. Eval v2 fixtures validate structurally and include bypass/adversarial cases.
12. Core AST boundary tests pass with no network/connector dependency.
13. RU/EN key docs and changelog markers pass parity validation.
14. Third-party Actions in active workflows are pinned to full immutable SHAs.
15. Release manifest/publisher tests enforce one declarative release path and fail-closed conflicting-state semantics.
16. CI is green on exact PR head.
17. Review evidence separates mechanical CI success from semantic/scientific/product validation.
18. Human authorization is required before merge and before publication.

---

## 28. Risks and mitigations

| Risk | Mitigation |
|---|---|
| LLM contaminates user recollection | deterministic submitted-candidate guard + free-account stage + adversarial evals |
| Generic host bypasses helper | truthful non-mechanical host boundary; skill/eval/review now, dedicated pre-send surface later |
| Linter creates false confidence | scoped mechanical claims; semantic eval/review kept separate |
| Household probabilities look scientific | `UNCALIBRATED` schema status; location-probability claims rejected |
| “Doorway effect” becomes cargo-cult rule | event boundary cannot boost weight; methodology-only treatment |
| Habit mistaken for episode | non-promotion contract + provenance |
| User fixates on blame | neutral hypotheses + blame guard |
| Search becomes endless | bounded next actions + fallback-first + unresolved state |
| Architecture becomes a framework too early | one P0 plugin; no shared runtime/model/surface abstractions |
| Future memory contaminates later cases | persistence deferred to separate P1 approval design |
| CI/release process drifts | stable requirements + exact traceability + manifest + single publisher |

---

## 29. Final P0 decisions

- Python is the executable helper language.
- Plugin is independently installable and transport-free.
- No root shared runtime dependency.
- Agent cannot create `USER_RECALLED` on the user's behalf.
- Sensory detail is metadata, not truth certification.
- “Last supported contact” replaces “last confirmed contact” for user-reported evidence.
- Event boundaries are methodology cues, not numeric priors.
- Search weights are uncalibrated and not location probabilities.
- Search miss uses deterministic multiplicative reduction; constants are operational policy, not scientific facts.
- A failed search alone never zeroes a nonzero zone in P0.
- Submitted investigative utterances are guarded fail-closed; generic-host pre-send invocation is not falsely claimed as mechanically enforced.
- No persistent cross-case baseline in P0.
- No connector/model/surface abstraction scaffolded in P0.
- High-risk contracts use exact-function traceability from the first release.
- Releases use one declarative manifest and one publisher.

---

## 30. Self-review record

Self-review performed on 2026-09-08 against the Superpowers architectural checklist:

- **Placeholder scan:** no `TBD`/`TODO`/unresolved placeholder remains.
- **Internal consistency:** corrected an initial overclaim that a skill-only host could mechanically prove every model utterance passed the linter. P0 now distinguishes helper enforcement from generic-host invocation compliance.
- **Scope check:** P0 remains one implementation-plan-sized vertical slice; Project Memory, long-term, connectors, surfaces, and model adapters remain deferred.
- **Ambiguity check:** removed a proposed “impossibility exception” for zeroing search weights in P0; failed search alone now has one unambiguous rule — reduce, never zero.
- **Safety freshness:** fallback is generic unless current authoritative data is available; jurisdiction/medication specifics are not frozen into transport-free P0 references without sourcing.

---

## 31. Implementation transition

After human review of this written design, the next Superpowers step is a separate implementation plan:

```text
docs/superpowers/plans/2026-09-08-mind-detective-foundation-implementation.md
```

The plan will decompose work into TDD-sized tasks/commits with exact red-green sequences, documentation surfaces, CI/bootstrap order, traceability updates, and release staging.

No production implementation is committed before that implementation plan is written and approved for execution.
