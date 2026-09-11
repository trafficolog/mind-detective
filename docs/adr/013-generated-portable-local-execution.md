# ADR 013 — Generated portable local execution

Status: Accepted for `0.3.0`.

## Context

The Web/PWA needs deterministic Case operations while offline. Maintaining a separate handwritten TypeScript reducer would create semantic drift from the Python domain source; keeping every mutation behind FastAPI would make offline operation impossible.

## Decision

Python remains the authoritative executable semantics. A deliberately restricted portable kernel and certified intrinsics define the local-execution contract. A repository generator validates that source against an allowlisted AST/call surface and emits a committed TypeScript artifact plus source-identity metadata.

The generated artifact is never hand-maintained. CI regenerates it and requires no diff. A deterministic committed corpus executes against Python during corpus generation and against TypeScript in Vitest to verify observable parity over the supported surface.

The Web local executor adds only persistence/idempotence orchestration. Canonical Case plus execution receipt are committed atomically in IndexedDB. `command_id` reuse with inconsistent input fails closed.

## Consequences

- deterministic Case creation/mutations/checklist proposals work offline after the app is loaded;
- there is still one authored semantic source, not two reducers;
- expanding the portable Python subset requires generator/certification/conformance changes first;
- this does not claim arbitrary Python↔TypeScript equivalence;
- Case schema remains `mind-detective-case/v2`.
