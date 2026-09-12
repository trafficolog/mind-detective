# Стандарт плагина

[English](PLUGIN_STANDARD.en.md)

## Metadata

Обязательные пути: root `.agents/plugins/marketplace.json`, root `.claude-plugin/marketplace.json`, plugin-local `.codex-plugin/plugin.json` и `.claude-plugin/plugin.json`. `.agents-plugin/plugin.json` запрещён. Version SSOT — `.codex-plugin/plugin.json`.

## Skills

Текущий production contract содержит ровно пять skills: router, reconstruct, plan, resume и close. Каждый skill фиксирует inputs, deterministic calls, outputs, limitations и mode/lifecycle transition. Runtime helpers находятся внутри plugin и не зависят от root-package installation.

## Contracts

Поведенческие инварианты получают `MD-REQ-*`. Active high-risk requirement обязан иметь owning skill, helper, exact unittest selector и reference в `CONTRACT_MATRIX.json`. Active helper должен быть достижим от production surface; одного существования файла недостаточно. Host-semantic enforcement, который нельзя доказать механически, должен быть назван `skill_contract+eval+review`, а не «machine enforced end-to-end».

## Distribution boundary

Не выносить plugin runtime в shared library только ради DRY. Общий код появляется лишь когда distribution/installability contract действительно это требует.
