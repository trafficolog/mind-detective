# R2 minimized provider context v1

**Status:** research-only Phase 5 boundary for the approved Reconstruction Assistant study.  
**Schema:** `mind-detective-reconstruction-r2-context/v1`  
**Base product truth:** released deterministic `0.4.0` Reconstruction; `Case v2` remains unchanged.  
**Provider stance:** provider-agnostic; this phase makes no external model/provider call.

## Purpose

Phase 5 defines the smallest provider-visible payload that may be considered by the later offline R2 model/provider screening phase. It does not select a provider and does not authorize a live-model pilot.

The builder receives the already bounded synthetic research context used by the staged corpus, validates it fail-closed, and serializes only the target-specific information required to formulate one clarification question. There is **no Case mutation** and no new portable command.

## Exact provider payload

The future research transport may receive only the output of the minimized builder:

```json
{
  "context_schema": "mind-detective-reconstruction-r2-context/v1",
  "language_code": "en",
  "reason_code": "timeline_gap",
  "targets": [
    {
      "ref_id": "evt_1",
      "ref_kind": "timeline",
      "excerpt": "I left the office.",
      "source": "user_confirmed"
    }
  ],
  "unknown_refs": ["u1"],
  "contradiction_refs": ["c1"]
}
```

Target excerpts are explicit user-confirmed text and are bounded to **240 characters per target**. Oversize, empty, missing, extra, duplicate, out-of-scope, or unknown source fields fail closed rather than broadening the payload.

Unknown and contradiction metadata is reference-only. Hidden unknown text, contradiction explanations, participant latent facts, inferred answers, confidence, probability, diagnoses, or suggested resolutions are not provider fields.

## Default exclusions

The minimized provider payload excludes by contract:

- raw free account / full verbatim account;
- full Case payload;
- full interaction journal;
- unrelated statements, events, locations, actions, and entities;
- evaluation history and arm history;
- provider secrets or credentials in browser-visible data;
- cross-case or profile context;
- participant latent facts from staged fixtures;
- raw evaluation telemetry;
- Search state or Search recommendations not required by the clarification target.

The corpus-level `supported_entities`, `supported_locations`, and `supported_actions` remain deterministic source/guard inputs where already defined, but the Phase 5 builder does not serialize those collections into the provider payload.

## Context matrix

| Provider field | Why needed | User content? | Retention implication | Local/export telemetry |
| --- | --- | --- | --- | --- |
| `context_schema` | Version the minimized contract | No | Contract metadata only | May be recorded as version metadata |
| `language_code` | Produce RU/EN question in the active language | No | Locale metadata | May be recorded |
| `reason_code` | Constrain the model to the deterministic clarification category | No | Research protocol metadata | May be recorded |
| `targets[].ref_id` | Bind the question to an approved deterministic target | Indirect identifier only | Provider sees opaque local reference id | Raw ref ids are not required in evaluation export |
| `targets[].ref_kind` | Distinguish timeline vs user statement target | No | Structural metadata | May be aggregated |
| `targets[].excerpt` | Supply only the bounded user-confirmed evidence necessary to ask the question | **Yes** | Provider receives user content; provider retention/training/deletion terms must be reviewed before use | Raw excerpt must not appear in privacy-safe research export |
| `targets[].source` | Preserve provenance as explicitly user-confirmed | No | Structural metadata | May be aggregated |
| `unknown_refs[]` | Tell the generator that an approved target includes an explicit unknown without revealing hidden text | Indirect identifier only | Opaque metadata | Count may be audited; raw ids need not be exported |
| `contradiction_refs[]` | Signal a scoped contradiction without supplying a forced resolution | Indirect identifier only | Opaque metadata | Count may be audited; raw ids need not be exported |

## Retention and provider review boundary

Phase 5 deliberately does not encode vendor-specific retention assumptions. Before any configuration can enter **Phase 6** offline model/provider screening, the selected provider/model configuration must have an explicit review of:

- request retention duration;
- training or secondary-use policy;
- deletion/control guarantees;
- geographic/data-processing implications where applicable;
- credentials and server-side transport boundary;
- logging and observability exposure.

If those terms are not acceptable for the bounded user content above, the configuration is not eligible for Phase 6.

## Input boundary and fail-closed behavior

For corpus compatibility, the builder accepts exactly the currently frozen staged `model_visible_context` field set:

- `language_code`;
- `supported_entities`;
- `supported_locations`;
- `supported_actions`;
- `timeline_refs`;
- `statement_refs`;
- `unknown_markers`;
- `contradiction_refs`.

An unexpected source field fails closed. This prevents later callers from silently adding a raw free account, full Case, full interaction journal, evaluation history, provider secrets, cross-case profile, or another convenience field without a reviewed contract change.

Only approved timeline/statement target ids are serialized as textual targets. Their excerpt mapping must match the target ids exactly. Related unknown/contradiction ids must already exist in the staged visible scope and are serialized as ids only.

## Privacy-safe context audit

`context_audit()` emits only content-free aggregate metadata:

- context schema;
- target count;
- unknown-reference count;
- contradiction-reference count;
- total bounded excerpt character count.

It does not emit user excerpts or local target/reference ids. This is compatible with the frozen research rule that raw user/model content is not exported as evaluation telemetry.

## Broader-context variants

A minimized-context candidate that cannot ask useful questions does **not** automatically gain broader access. Any broader-context research variant requires a separate reviewed/versioned contract that:

1. states exactly which missing field is necessary and why;
2. adds an explicit privacy/retention review;
3. remains analytically distinct from the minimized variant;
4. preserves the same R2 proposal schema and deterministic guard boundary;
5. does not mutate Case or convert assistant output into canonical evidence.

## Phase boundary

Phase 5 adds no transport/client and stores no provider credentials. A later Phase 6 implementation may bind an approved server-side research adapter to this payload for offline screening, but it must preserve the exact output/guard contract and the protocol's provider failure telemetry.

This phase does not add:

- a live model/provider call or provider selection;
- prompt tuning or model benchmarking;
- a human pilot or production assistant;
- Web research UI wiring;
- browser provider secrets;
- Case schema or portable-kernel changes;
- assistant-authored recollection, habit, observation, or canonical evidence;
- raw provider/user content in evaluation export;
- active production `MD-WEB-REQ-RECON-ASSIST-*` requirements;
- a `0.4.1` version bump, release, tag, or publication action.
