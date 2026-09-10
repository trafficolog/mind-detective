# MIND Detective 0.2.0 LiteLLM Provider Override

**Status:** Approved canonical override  
**Applies to:** `0.2.0` Web/PWA design and implementation plan  
**Approved:** 2026-09-10

## Decision

For the `0.2.0` assistant arm, **LiteLLM Proxy is the single live model gateway**.

This document supersedes the earlier implementation-plan statements that named direct OpenAI credentials/model configuration as the live provider boundary. The product still uses the pinned OpenAI Python SDK as an OpenAI-compatible transport client to LiteLLM Proxy; that does **not** make OpenAI the configured live gateway.

## Server-side configuration

Assistant proposal execution reads only server-side configuration:

- `LITELLM_API_KEY` — LiteLLM proxy virtual/master key; required when the assistant arm invokes the gateway.
- `MIND_DETECTIVE_LITELLM_BASE_URL` — LiteLLM proxy endpoint; defaults to `http://127.0.0.1:4000` for local development.
- `MIND_DETECTIVE_LITELLM_MODEL` — model alias/name exposed by the configured LiteLLM proxy; required when assistant proposals are invoked.

No provider key, proxy endpoint, or model credential enters the Nuxt bundle or canonical Case payload.

## LiteLLM-specific semantics

- Model identifiers are treated as LiteLLM proxy aliases/deployments, so the application does not encode an upstream vendor-specific model taxonomy.
- The application calls the LiteLLM OpenAI-compatible Responses API through `AsyncOpenAI(base_url=..., api_key=...)`.
- Structured proposals remain `ProposalModel` objects and still pass the same MIND Detective guard/controller path before rendering.
- `store=False` remains set on proposal calls.
- Provider routing, fallback, upstream credentials, budgets, and deployment selection belong to LiteLLM configuration, not MIND Detective Case/domain state.
- Application logs continue to exclude full Case payloads, user text, target text, raw model output, and provider secrets by default.

## Unchanged architectural constraints

- Python `CaseController` remains the only domain reducer.
- Browser persistence remains IndexedDB-local; the FastAPI adapter remains stateless with respect to stored cases.
- Checklist and assistant arms use the same product shell.
- No Bayesian/POD or calibrated location probabilities are introduced.
- Multi-provider routing inside MIND Detective remains out of scope because LiteLLM is the gateway abstraction for `0.2.0`.

## Implementation mapping

The implementation-plan references should be interpreted as follows:

- `openai_provider.py` → `litellm_provider.py`
- `OpenAIProposalClient` → `LiteLLMProposalClient`
- `OPENAI_API_KEY` → `LITELLM_API_KEY`
- `MIND_DETECTIVE_OPENAI_MODEL` → `MIND_DETECTIVE_LITELLM_MODEL`
- direct provider endpoint → `MIND_DETECTIVE_LITELLM_BASE_URL`

The pinned `openai==3.8.0` dependency remains an adapter dependency solely for LiteLLM's OpenAI-compatible Responses API surface.
