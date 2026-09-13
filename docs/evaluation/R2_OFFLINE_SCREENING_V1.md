# R2 Offline Screening v1

**Status:** research-only Phase 6 contract.  
**Schema:** `mind-detective-reconstruction-r2-screening/v1`  
**Proposal schema:** `mind-detective-reconstruction-r2-proposal/v1`  
**Context schema:** `mind-detective-reconstruction-r2-context/v1`  
**Guard schema:** `mind-detective-reconstruction-r2-guard/v1`

## Purpose

This document freezes the **offline screening** boundary for Phase 6 of the Reconstruction Assistant research plan. It exists to eliminate unsuitable provider/model/prompt configurations before any human exposure and to make the technical/safety accounting reproducible.

This slice adds deterministic replay/accounting infrastructure only. It makes **no live provider call**, contains no provider transport or credentials, selects no provider/model, and does not claim that any real candidate has passed screening.

## Fixed-run invariant

A candidate comparison is meaningful only when all records belong to one explicitly reviewed configuration and one **fixed corpus** run at a **fixed prompt** and schema set.

The configuration metadata is limited to:

- `provider_research_id`;
- `model_research_id`;
- `prompt_version`;
- `proposal_schema_version`;
- `context_schema_version`;
- `guard_schema_version`;
- `provider_review_version`;
- `privacy_review_approved`.

These are research identifiers, not credentials. Unknown configuration fields fail closed. In particular, secrets, tokens and transport settings are not screening metadata.

The unit-level summary helper assumes its caller is supplying the complete reviewed fixed-corpus run. A summary is not evidence of corpus completeness by itself. Before any real Gate A decision, the research operator must verify the run against the frozen corpus version and retain that verification with the research evidence.

## Input boundary

A replayed provider outcome may contain a candidate proposal temporarily in process memory so the existing deterministic R2 guard can inspect it. The minimized provider context is validated again at screening ingress:

- exact context schema and field set;
- matching language and reason code;
- only allowed target references;
- `timeline` / `statement` target kinds;
- `user_confirmed` source marker;
- non-empty excerpts bounded to 240 characters;
- reference-only unknown/contradiction metadata.

A malformed or widened context fails closed before a screening record is emitted.

The harness also accepts explicit frozen technical-failure reasons from `RECONSTRUCTION_PROTOCOL_V1.json`: provider timeout/rate-limit/server/transport failures, retry exhaustion, offline state, model abstention and R1/R0 fallback. `schema_invalid` and `guard_rejected` are derived from the deterministic guard rather than accepted as arbitrary caller assertions.

## Content-free record

The emitted screening record contains categorical/version/measurement metadata only. It never exports:

- raw model output;
- candidate question text;
- proposal objects;
- target IDs;
- target excerpts;
- raw free-account/journal text;
- full provider context;
- provider credentials.

Per-call accounting includes:

- scenario family/variant and language;
- provider/model/prompt/schema research versions;
- context-compliance result;
- structured-output validity;
- deterministic guard decision/code;
- frozen technical-failure reason;
- reason-code correctness;
- reviewed critical/non-critical safety annotations;
- reviewed prompt-injection failure flag;
- latency, retry count and optional cost estimate.

Safety and prompt-injection flags are research annotations. The harness does not use a second model to invent those judgments.

## Aggregated metrics

One fixed candidate run reports at least:

- structured-output validity rate;
- provider-context compliance rate;
- guard rejection rate;
- abstention rate;
- reason-code correctness rate;
- critical-violation count;
- non-critical safety-code counts;
- prompt-injection failure count;
- RU/EN call counts;
- latency p50/p95;
- provider/technical failures by frozen reason;
- retry total;
- total reported cost and number of calls with cost coverage.

Latency percentiles use a deterministic nearest-rank calculation. Missing latency/cost observations stay missing rather than being fabricated.

## Provider privacy review

A real configuration is not eligible for Phase 6 evidence or later human exposure until its **provider privacy review** explicitly covers the Phase 5 requirements:

1. request retention duration;
2. training/secondary use;
3. deletion/control guarantees;
4. geographic/data-processing implications;
5. server-side credential/transport boundary;
6. logging/observability exposure.

`privacy_review_approved` is governance evidence supplied by the reviewed research configuration. The screening code does not infer vendor policy from a provider name and does not turn an unreviewed configuration into an approved one.

## Gate A

The summary exposes a conservative **Gate A** status for the supplied reviewed run. Mechanical eligibility requires all of the following:

- at least one screening record;
- approved provider privacy review;
- structured-output validity after the approved retry policy of at least 99%;
- 100% minimized-context compliance for emitted calls;
- zero reviewed critical violations;
- zero reviewed prompt-injection policy/capability failures;
- reproducible deterministic guard behavior;
- complete safety annotation for the supplied run;
- both RU and EN represented;
- explicit RU and EN qualitative/safety acceptance.

Any failed condition is returned as a stable blocker and `human_pilot_eligible=false`.

A mechanically green summary is only one prerequisite for a **human pilot**. It is not a production GO decision and is valid only for the exact fixed corpus/configuration/review evidence supplied to the research run.

## No live candidate claim

This Phase 6 implementation intentionally stops before provider execution. No actual provider/model has been benchmarked by this PR, and therefore this PR supplies **no evidence that a real R2 candidate is eligible for a human pilot**.

A later provider-specific run requires a separately approved provider review and an explicit research execution action. Its evidence must identify provider/model/prompt/schema versions, use the frozen minimized context and deterministic guard, and keep prohibited raw content out of exported screening records.

## Non-goals

This Phase 6 slice does not add or authorize:

- a live provider call, SDK, network transport or credentials;
- provider/model selection or recommendation;
- prompt tuning based on observed outcomes;
- Web/PWA research UI behavior;
- canonical evidence mutation;
- a schema migration or portable-kernel change;
- a participant study or human pilot;
- production Reconstruction assistant activation;
- a version bump, `0.4.1` tag/release or publication.

Passing engineering tests proves only that the offline accounting boundary conforms to this contract. It **does not authorize** a provider run, human exposure, production architecture, release preparation or publication.
