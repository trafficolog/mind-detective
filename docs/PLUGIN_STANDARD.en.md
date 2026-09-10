# Plugin Standard

[Русский](PLUGIN_STANDARD.md)

Required metadata paths are root `.agents/plugins/marketplace.json`, root `.claude-plugin/marketplace.json`, plugin-local `.codex-plugin/plugin.json`, and plugin-local `.claude-plugin/plugin.json`. `.agents-plugin/plugin.json` is forbidden. The Codex descriptor is the plugin-version SSOT.

0.1.0 exposes exactly five production skills. Each skill states inputs, deterministic calls, outputs, limitations, and a mode/lifecycle transition. Plugin runtime remains locally installable and does not depend on a root runtime package.

High-risk active `MD-REQ-*` entries link an owning skill, helper, exact unittest selector, and reference in `CONTRACT_MATRIX.json`. Host-semantic behavior that cannot be mechanically proven must be labelled skill-contract + eval + review, not end-to-end machine enforcement.
