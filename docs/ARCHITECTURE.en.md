# Architecture

[Русский](ARCHITECTURE.md)

The canonical `Case` plus `CaseController` is the single deterministic state center. Skills orchestrate dialogue and call helper modules but do not create parallel sources of truth.

The plugin-local runtime separates provenance (`statements.py`), uncertainty-preserving sequence (`timeline.py`), durable physical checks (`search_log.py`), categorical one-next-action selection (`planner.py`), mode-aware utterance checks (`guard.py`), explicit case-local persistence (`store.py`), and derived handoff/outcome artifacts (`artifacts.py`). Safety routing precedes ordinary search reasoning.

P0 is Python-standard-library-only and transport-free. It contains no connector runtime, ModelAdapter, Web/PWA, voice/messenger surface, cloud storage, cross-case learning, Bayesian/POD/numerical location model, or hidden belief weight.

Normative requirements live in `REQUIREMENTS.md`; exact traceability lives in `CONTRACT_MATRIX.json`. Eval fixtures are machine-checkable expectations, not proof of live-model semantic compliance. See ADRs under `docs/adr/`.
