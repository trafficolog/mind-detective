# R2 Provider Privacy Review v1

**Status:** research-governance prerequisite for provider-specific Phase 6 evidence.  
**Schema:** `mind-detective-reconstruction-r2-provider-privacy-review/v1`  
**Context scope:** `mind-detective-reconstruction-r2-context/v1`

## Purpose

This document freezes the provider privacy review artifact that must exist before a real provider/model configuration can contribute evidence to R2 offline screening.

The review is deliberately narrow. It evaluates whether one provider configuration may receive the already-minimized Phase 5 context for the research purpose `offline_reconstruction_r2_screening`. It **does not select or recommend a provider**, compare model quality, authorize a human pilot, or activate any production Reconstruction capability.

A green artifact is a project governance prerequisite only. It is **not a legal or compliance certification** and does not replace organizational legal, security, procurement, data-protection, or vendor-management review where those processes apply.

## Frozen artifact

A review contains exactly:

- `review_schema`;
- `provider_research_id`;
- `provider_review_version`;
- `reviewed_scope`;
- `domains`;
- `review_status`.

Unknown top-level fields fail closed. The machine artifact **must not contain credentials**, access tokens, API keys, browser secrets, raw user text, raw model output, or a full Case payload.

The reviewed scope is fixed to:

```json
{
  "purpose": "offline_reconstruction_r2_screening",
  "context_schema_version": "mind-detective-reconstruction-r2-context/v1",
  "credential_boundary": "server_side_only",
  "raw_content_export": false
}
```

A broader purpose, widened provider context, browser-side credential boundary, or raw-content export requires a separate reviewed/versioned contract rather than silently reusing this approval.

## Required privacy domains

The review must cover **all six domains** from the Phase 5/6 privacy boundary:

1. `request_retention` — how long request/provider payload data may be retained and under which operational conditions;
2. `training_secondary_use` — whether submitted data may be used for training, improvement, abuse analysis, or other secondary purposes;
3. `deletion_control` — what deletion, opt-out, enterprise control, or contractual guarantees actually apply to the reviewed configuration;
4. `geographic_processing` — where processing/storage may occur and what geographic/data-processing implications follow;
5. `credential_transport` — confirmation that credentials stay server-side and that the reviewed transport boundary matches the intended research execution path;
6. `logging_observability` — whether provider, proxy, platform, or operational logs can retain request/response content or other sensitive material.

Each domain has exactly two machine fields:

```json
{
  "decision": "acceptable | unknown | blocked",
  "evidence_refs": ["reviewed source reference"]
}
```

`acceptable` and `blocked` require at least one evidence reference. `unknown` may remain without evidence while research is incomplete. Evidence references should point to the actual reviewed policy, contractual, configuration, security, or repository evidence; the machine artifact intentionally does not copy long vendor policy text.

## Review status

Allowed statuses are:

- `incomplete` — at least one domain is `unknown`; this is the default template state;
- `blocked` — at least one domain is explicitly `blocked`;
- `approved` — every one of the six domains is `acceptable` and has evidence.

An artifact that claims `approved` while any domain is `unknown` or `blocked` fails validation. Approval is therefore derived from the complete exact-domain review rather than inferred from a provider name or a caller-supplied optimistic boolean.

The neutral template is `R2_PROVIDER_PRIVACY_REVIEW_TEMPLATE_V1.json`. It intentionally validates as `incomplete` and **must not** be treated as provider approval.

## Screening bridge

The provider review artifact is not copied into Phase 6 screening records. After validation, only the existing content-free attestation is derived:

```json
{
  "provider_research_id": "...",
  "provider_review_version": "...",
  "privacy_review_approved": false
}
```

`screening_config_from_review(...)` combines that attestation with the fixed proposal/context/guard schema versions plus the reviewed model and prompt research identifiers. This preserves the existing `mind-detective-reconstruction-r2-screening/v1` record shape instead of introducing an incompatible schema merely to carry governance evidence.

Evidence references, policy text, credentials, raw user content and raw provider output are not exported into screening metadata.

## Execution boundary

Completing an approved provider review still does not execute anything. A real provider/model run requires a **separate explicit research execution action** for the exact provider/model/prompt/schema/review configuration.

That later execution must continue to use:

- the Phase 5 minimized provider context;
- the deterministic Phase 4 R2 guard;
- the Phase 6 content-free screening record;
- the frozen scenario corpus and explicit `fixed_corpus_complete` gate;
- server-side credentials only;
- the approved retry/accounting policy.

This contract adds **no live provider call**, SDK, network transport, secret handling, browser credential path, or production request path.

## Gate A relationship

Phase 6 Gate A already requires `privacy_review_approved=true`. This contract defines how that boolean is produced from a versioned reviewed artifact.

It does not weaken any other Gate A requirement: >=99% structured-output validity, 100% minimized-context compliance, complete fixed corpus, zero reviewed critical violations, zero reviewed prompt-injection capability/policy failures, reproducible deterministic guard behavior, complete safety annotation, RU/EN coverage, and explicit RU/EN qualitative/safety acceptance still apply.

A privacy-approved provider can therefore still fail Gate A for technical, quality, language, or safety reasons.

## Human and production boundaries

An approved provider review is not authorization for a **human pilot**. Human exposure remains a later separately reviewed step and requires a green Gate A for the exact candidate configuration plus the project’s human-study/pilot controls.

It is also not authorization for **production**. Production Reconstruction Assistant activation requires its own product, safety, privacy, architecture, observability, rollback, and release gates. Provider-review evidence does not make assistant output canonical memory evidence and does not alter Case semantics.

## Non-goals

This slice does not:

- choose or recommend a vendor/model;
- claim that any provider is currently approved;
- perform a live API request;
- add credentials, secrets, billing data, proxy configuration, or provider SDKs;
- broaden provider context beyond the Phase 5 contract;
- run the fixed scenario corpus against a real model;
- authorize a participant study or human pilot;
- enable a production Reconstruction Assistant;
- change Case v2 or portable deterministic semantics;
- bump version, create a `0.4.1` tag, publish a release, or alter immutable release history.

Engineering tests for this artifact prove only that the governance contract is represented and fails closed as designed. They do not constitute provider privacy approval or empirical model evidence.
