# R2 provider-specific privacy reviews — 2026-09-13

**Status:** research-governance evidence only.  
**Parent contract:** `mind-detective-reconstruction-r2-provider-privacy-review/v1`.  
**Scope:** synthetic fixed-corpus Phase 6 offline screening with the Phase 5 minimized context only.  
**Execution authorization:** none.

## What `approved` means here

The three machine artifacts in `docs/evaluation/provider-reviews/` review narrowly named provider configurations against the six-domain privacy contract merged in PR #45.

`approved` means only that the documented configuration is privacy-eligible for the already-frozen **synthetic** offline screening scope when every constraint below is actually satisfied at execution time. It does **not** mean:

- that the repository owner currently has the required vendor entitlement, contract, project setting or regional feature enabled;
- that a provider or model has been selected or recommended;
- that a model has been called or benchmarked;
- that Gate A has passed;
- that participant data may be sent to the provider;
- that a human pilot or production path is authorized.

Account/project configuration is intentionally not encoded as a secret-bearing repository artifact. A later execution preflight must confirm the effective vendor controls without committing credentials or raw provider/user content.

## Common boundary

All three approved profiles inherit the same project constraints:

- purpose is exactly `offline_reconstruction_r2_screening`;
- context schema is exactly `mind-detective-reconstruction-r2-context/v1`;
- only the Phase 5 minimized provider context may be sent;
- corpus content is synthetic/staged research material, not participant or production Case content;
- credentials remain server-side only;
- raw provider input/output is not exported into screening telemetry;
- proposal schema and deterministic guard remain frozen;
- external tools, browsing, MCP, file upload or other context-expanding provider features are out of scope unless a later review explicitly adds them;
- provider policy/configuration drift invalidates reuse of the review until re-reviewed and versioned.

## OpenAI API — `openai-api-eu-zdr`

Machine artifact: `provider-reviews/OPENAI_API_EU_ZDR_V1.json`.

The approved profile requires all of the following:

1. an API project configured for **Europe (EEA + Switzerland)** data residency/regional processing;
2. approved **Zero Data Retention** controls for that project/organization;
3. a ZDR-compatible text request path only;
4. no stateful Conversations/Assistants/Threads/Vector Store path;
5. no background mode, extended prompt caching, Code Interpreter, file persistence, remote MCP, web search or other unnecessary tool path for this screening run;
6. no API data-sharing/training opt-in;
7. `store=false` semantics and server-side credentials;
8. no raw request/response content in project telemetry.

OpenAI documents that API inputs/outputs are not used for training by default; ZDR excludes customer content from abuse-monitoring logs for eligible customers; and the Europe API region supports regional storage and processing for supported services. API audit logs are administrative/configuration metadata and are outside ZDR, but OpenAI documents them separately from request/response customer content.

Evidence:

- https://platform.openai.com/docs/models/default-usage-policies-by-endpoint
- https://openai.com/business-data/
- https://openai.com/index/offering-zero-data-retention-for-frontier-models/
- https://help.openai.com/en/articles/9687866-admin-and-audit-logs-api-for-the-api-platform

### Execution preflight blockers

Do not run this profile until the actual API project is confirmed to have Europe residency and ZDR enabled and the chosen model/endpoint is supported in that region. Public documentation proves capability, not entitlement/configuration of a specific account.

## Anthropic API — `anthropic-api-zdr`

Machine artifact: `provider-reviews/ANTHROPIC_API_ZDR_V1.json`.

The approved profile is **not** the default Anthropic API retention path. It requires an Anthropic-approved **Zero Data Retention agreement** for the commercial API and all of the following:

1. direct Anthropic API use under the commercial organization covered by that ZDR agreement;
2. normal message-generation requests only;
3. no Files API, Workbench, beta product, explicit prompt caching, batch mode or third-party web-search path that changes/overrides ZDR handling;
4. no feedback/development-partner or other explicit training opt-in;
5. server-side credentials only;
6. no raw request/response export into project telemetry.

Anthropic documents 30-day backend retention for standard API inputs/outputs, but states that approved enterprise API customers may have ZDR arrangements under which raw inputs/outputs are not stored except as required by law or to combat misuse. Anthropic also states that UserSafety classifier results may still be retained under ZDR. The project accepts that metadata only for this synthetic fixed-corpus research scope.

Anthropic also documents that commercial data processing may occur across the US, Europe, Asia and Australia and that data storage is US-only by default unless otherwise agreed. Because this review covers synthetic Phase 6 fixtures rather than participant/production content, that geography is acceptable for this narrow research profile; this finding must **not** be reused for a human pilot or production privacy decision.

Paid API customers do not have ad-hoc deletion for standard retained requests. The deletion-control decision is therefore acceptable here only because the reviewed profile requires ZDR for raw inputs/outputs; standard-retention API use is outside the approved profile.

Evidence:

- https://privacy.anthropic.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to
- https://privacy.anthropic.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data
- https://privacy.anthropic.com/en/articles/7996885-how-do-you-use-personal-data-in-model-training
- https://privacy.claude.com/en/articles/7996875-can-you-delete-data-that-i-sent-via-api
- https://privacy.anthropic.com/en/articles/7996890-where-are-your-servers-located-do-you-host-your-models-on-eu-servers

### Execution preflight blockers

Do not run this profile until an actual Anthropic API ZDR agreement/entitlement is confirmed for the organization used by the run. A normal paid API key with default 30-day retention does not satisfy this profile.

## Google Vertex AI — `google-vertex-ai-eu-zdr`

Machine artifact: `provider-reviews/GOOGLE_VERTEX_AI_EU_ZDR_V1.json`.

The approved profile requires all of the following:

1. Generative AI on Vertex AI in an EU data-location/regional processing configuration supported by the selected model;
2. no Grounding with Google Search, Grounding with Google Maps, RAG Engine or other persistence-expanding feature;
3. no Gemini Live session resumption;
4. if the project is subject to prompt logging for abuse monitoring, the documented abuse-monitoring exception required for zero data retention must be approved before the run;
5. no persistent prompt resource, batch workflow or other application-state feature for the screening path;
6. project-level in-memory caching disabled for the research run as an additional minimization control, even though Google documents its default 24-hour in-memory cache as non-at-rest and compatible with data-residency/ZDR requirements;
7. server-side Google Cloud credentials only;
8. no raw request/response content in project telemetry.

Google documents a training restriction for managed Vertex AI models: customer data is not used to train/fine-tune models without prior permission or instruction. Google also documents the controls required to reach zero data retention, including abuse-monitoring exceptions where applicable, and lists Generative AI on Vertex AI among services that can be configured for data location, with documented exclusions for grounding/RAG features.

Evidence:

- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/security-controls
- https://cloud.google.com/terms/data-residency

### Execution preflight blockers

Do not run this profile until the exact Google Cloud project, region, chosen model availability, abuse-monitoring status/exception where applicable, and cache setting have been verified. Generic Gemini API or consumer Gemini use does not satisfy this profile.

## Comparison at the privacy gate

| Profile | Review status | Required non-default control | Geography for this review | Raw I/O retention target | Training use |
|---|---|---|---|---|---|
| `openai-api-eu-zdr` | approved for synthetic Phase 6 scope | EU project + ZDR | EU regional processing | ZDR-compatible request path | no training by default / no opt-in |
| `anthropic-api-zdr` | approved for synthetic Phase 6 scope | Anthropic API ZDR agreement | multi-region processing; raw I/O not stored under reviewed ZDR profile | ZDR raw inputs/outputs; safety classifier metadata may remain | no commercial API training unless opted in/agreed |
| `google-vertex-ai-eu-zdr` | approved for synthetic Phase 6 scope | EU regional project + zero-retention controls / abuse exception if applicable | configured EU data location | zero-retention profile; no persistence-expanding features | no training/fine-tuning without permission/instruction |

This table is not a ranking. Privacy approval is a prerequisite, not model-quality evidence.

## Mandatory preflight before any real provider call

A later, separately authorized execution must record content-free evidence that:

1. the exact `provider_research_id` matches one of these reviewed profiles;
2. the vendor account/project really has the required ZDR/residency/retention controls active;
3. the chosen model and endpoint are supported under that exact configuration;
4. prohibited provider features are disabled/not invoked;
5. credentials exist only in a server-side secret boundary and are never committed or returned to the browser;
6. only the frozen synthetic corpus and Phase 5 minimized context are used;
7. prompt/schema/guard versions match the screening configuration;
8. no raw request/response content is exported to screening telemetry;
9. provider-policy evidence has not materially changed since this review version;
10. a separate explicit human authorization has been given for the actual provider/model execution.

If any item is not established, the run remains unauthorized even though the machine provider review says `approved`.

## Staleness and re-review

These reviews are dated evidence. A provider policy, product, regional capability, retention feature, endpoint behavior or project control may change. Material changes require a new `provider_review_version` and a fresh review artifact. Existing artifacts must not be silently edited to preserve a historical approval claim.

No provider/model screening, Gate A claim, human pilot, production activation, `0.4.1` version bump, tag or release is performed by this documentation slice.
