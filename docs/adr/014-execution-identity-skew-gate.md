# ADR 014 — Execution identity and skew gate

Status: Accepted for `0.3.0`.

## Context

After deterministic mutation moved into the browser, an assistant proposal can cross a server running a different portable-kernel/generated-executor build. Silent version skew could make a model proposal reason over semantics different from those that produced the local Case.

## Decision

The generated local-execution build exposes an identity containing contract `version`, `kernel_sha256`, `generated_sha256`, and `generator_version`. The API exposes its expected identity and every assistant proposal request carries the client identity.

The server validates all identity fields before creating/calling the model provider. Missing or mismatched identity fails closed with `MD_WEB_EXECUTION_CONTRACT_MISMATCH`. The local deterministic mutation remains committed; skew is a proposal-boundary failure, not a reason to roll back valid local state.

Network transport failure is distinct from version skew: transport failure may use a local deterministic checklist fallback, while a confirmed skew is surfaced explicitly. Old assistant requests are not replayed automatically after reconnect.

## Consequences

- model calls cannot silently cross known local/server execution skew;
- identity is content/build metadata, not a probability or user profile;
- deployment must keep client and API generated contracts aligned;
- deterministic offline search remains available independently of live-model availability.
