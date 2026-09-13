# Claude development context

Use the same repository contracts as `AGENTS.md`.

The current released Web implementation contract is `0.4.0` Web Reconstruction:

- design: `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md`;
- implementation plan: `docs/superpowers/plans/2026-09-12-mind-detective-web-reconstruction-0.4.0.md`.

The approved next-cycle research/design gate is `0.4.1` Reconstruction Assistant:

- research spec: `docs/superpowers/specs/2026-09-13-mind-detective-0.4.1-reconstruction-assistant-research.md`;
- research/design execution plan: `docs/superpowers/plans/2026-09-13-mind-detective-0.4.1-reconstruction-assistant-design.md`.

The older v2 design/implementation artifacts dated 2026-09-09 remain historical architecture evidence; do not treat them as the current Web boundary.

For investigative wording, distinguish reconstruction from search planning. Reconstruction must not seed unsupported concrete locations. The released deterministic Reconstruction path remains canonical and must work without a live model. Any `0.4.1` assistant path is research-only unless a later explicit GO and production implementation authorization are recorded: model output may be only a candidate clarification question, and canonical evidence appears only after an explicit user answer passes the existing deterministic Case mutation path.

Search planning may propose concrete locations only as explicit proposals. Generic hosts do not provide a mandatory repository-controlled pre-send interception hook, so never overclaim guard coverage.
