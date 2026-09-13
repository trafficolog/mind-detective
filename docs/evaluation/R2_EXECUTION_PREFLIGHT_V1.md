# R2 Execution Preflight v1

**Status:** research-governance prerequisite for any separately authorized real provider/model screening run.  
**Schema:** `mind-detective-reconstruction-r2-execution-preflight/v1`  
**Parent privacy gate:** `mind-detective-reconstruction-r2-provider-privacy-review/v1`  
**Frozen corpus id:** `mind-detective-reconstruction-r2-fixed-corpus/v1`

## Purpose

This contract sits after an approved provider-specific privacy review and before any real provider/model request.

A `ready` preflight means only that the documented technical/privacy preconditions have evidence for the exact provider/model/prompt/corpus configuration. It **does not authorize execution**. A real provider/model call still requires **separate explicit human authorization** for that exact configuration.

The preflight performs no provider call, does not read credentials, does not inspect secret values, and does not add an SDK, transport, proxy, browser credential path or network executor.

## Frozen artifact

The preflight contains exactly:

- `preflight_schema`;
- `provider_research_id`;
- `provider_review_version`;
- `model_research_id`;
- `prompt_version`;
- `proposal_schema_version`;
- `context_schema_version`;
- `guard_schema_version`;
- `corpus_id`;
- `checks`;
- `preflight_status`.

Unknown top-level fields fail closed. The artifact must not contain API keys, tokens, account identifiers, credential material, raw provider payloads, free-account text, Case payloads, prompts, model response text, or other user content.

The provider identity and review version must exactly match one already-approved provider privacy review. The proposal/context/guard versions must exactly match the frozen Phase 4/5/6 contracts. `corpus_id` is also frozen and must equal `mind-detective-reconstruction-r2-fixed-corpus/v1`; exploratory subsets, alternate corpus versions or caller-defined identifiers cannot be relabeled as this preflight.

## Required checks

The check set is exact and frozen:

1. `profile_entitlement_verified` — the actual vendor account/project is verified to have the controls required by the reviewed provider profile, such as ZDR, regional processing or equivalent account-level entitlement;
2. `model_endpoint_supported` — the chosen model/endpoint is supported under that exact reviewed profile and region/retention configuration;
3. `prohibited_features_disabled` — tools or features that expand context, persistence or retention beyond the reviewed profile are disabled or not invoked;
4. `server_side_credentials_verified` — the execution path uses server-side credentials only; evidence refers to the credential boundary/configuration, never to the credential value itself;
5. `synthetic_corpus_only` — the run is bound to the frozen synthetic research corpus, not participant or production content;
6. `minimized_context_only` — only the Phase 5 minimized context contract may be sent;
7. `frozen_versions_match` — prompt/proposal/context/guard/runtime configuration matches the reviewed research configuration;
8. `raw_telemetry_disabled` — no raw request/response content is exported into research telemetry or ordinary application observability;
9. `policy_evidence_current` — provider policy/configuration evidence has been checked for material drift since the provider-specific privacy review.

Each check contains exactly:

```json
{
  "status": "pass | fail | unknown",
  "evidence_refs": ["content-free evidence reference"]
}
```

`pass` and `fail` require at least one evidence reference. Evidence references may point to reviewed provider policy, internal configuration records, a synthetic corpus manifest, an immutable repository artifact, or other content-free verification evidence. They must not contain secret values or raw user/provider content.

## Deterministic status

`preflight_status` is not trusted as an optimistic caller assertion. It must agree with the deterministic check outcomes:

- `ready` — every required check is `pass`;
- `blocked` — at least one required check is `fail`;
- `incomplete` — no check failed, but at least one check is `unknown`.

A caller cannot relabel an incomplete or blocked preflight as ready.

A non-approved provider privacy review cannot enter this preflight stage at all.

## Content-free attestation

After validation, the allowed attestation is limited to:

```json
{
  "provider_research_id": "...",
  "provider_review_version": "...",
  "model_research_id": "...",
  "prompt_version": "...",
  "corpus_id": "mind-detective-reconstruction-r2-fixed-corpus/v1",
  "preflight_status": "ready | blocked | incomplete",
  "preflight_ready": true
}
```

The attestation excludes evidence references, credentials, account identifiers, policy text, request/response content, Case content and user text.

`preflight_ready=true` is a technical/privacy readiness statement only. It is deliberately **not** an `execution_authorized` flag and must not be treated as one.

## Screening bridge

`screening_config_from_preflight(...)` may re-derive the existing Phase 6 `ScreeningConfig` only when the validated preflight is `ready`.

This function performs no I/O. It does not contact a provider, retrieve a model, verify a secret, run a prompt or execute the fixed corpus. It only re-derives the already-frozen content-free screening metadata from the approved provider review plus the ready preflight identity/version binding.

Actual execution remains a separate action and requires separate explicit human authorization.

## Provider-specific application

For the provider profiles introduced by the preceding provider-specific privacy review slice, the preflight must verify the real effective account/project settings rather than assuming entitlement from public provider documentation.

Examples include:

- OpenAI API profile: confirm the actual project has the reviewed EU residency and ZDR controls active and that the chosen text endpoint/model is supported under that configuration;
- Anthropic API profile: confirm the actual organization is covered by the reviewed API ZDR agreement and that no excluded retention-expanding feature is used;
- Google Vertex AI profile: confirm the actual project/region/model/retention controls and any required abuse-monitoring exception are effective.

Failure to establish any required profile control makes the preflight blocked or incomplete even if the provider-specific machine review itself is `approved`.

## Corpus and context boundary

This phase is limited to the synthetic fixed-corpus Phase 6 screening path identified exactly by `mind-detective-reconstruction-r2-fixed-corpus/v1`.

It does not authorize participant data. It does not authorize production Case content. It does not widen the provider-visible payload beyond the **Phase 5 minimized context**. The raw free account, full Case, unrelated statements/events, Search state and any other excluded context remain out of scope.

## Telemetry boundary

Execution preflight evidence and the later Phase 6 screening export must remain content-free. There must be **no raw request/response** content in the research record or ordinary observability path used for this study.

Provider-side operational metadata that is unavoidable under an approved provider profile must already be covered by that provider-specific privacy review and confirmed by `policy_evidence_current` / `profile_entitlement_verified` before a run can become ready.

## Explicit execution gate

Even with:

- an approved provider privacy review;
- a provider-specific reviewed profile;
- all nine preflight checks passing;
- `preflight_status=ready`;

the system still **does not authorize execution**.

A later action must receive separate explicit human authorization for the exact provider/model/prompt/corpus/review/preflight configuration before any network request is made.

That later execution action must fail closed if the authorization scope does not exactly match the ready preflight identity/version binding.

## Non-goals

This contract does not:

- make a provider call;
- add a provider SDK, HTTP client, proxy or live transport;
- read, create or store API keys or other credentials;
- prove that any real vendor account currently has the required controls active;
- choose or rank providers/models;
- run the fixed corpus;
- claim Gate A;
- authorize participant data or a human pilot;
- enable production Reconstruction;
- change Case v2 or portable deterministic semantics;
- bump `0.4.1`, create a tag, publish a release or alter immutable release history.

Engineering tests for this slice prove only that the preflight contract is represented, version-bound and fail-closed. They are not empirical provider/model evidence and are not execution authorization.
