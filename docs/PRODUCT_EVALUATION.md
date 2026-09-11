# Product Evaluation

Цель — проверить, даёт ли диалоговый AI практическую добавочную ценность поверх deterministic search controller, а не доказать заранее выбранную гипотезу.

## Arms

- **A — обычный поиск:** внешний contextual baseline без MIND Detective UI/скрытой structured assistance.
- **B — checklist/controller:** Web/PWA, canonical Case и deterministic local executor без conversational AI.
- **C — B + conversational AI:** тот же product shell и execution semantics; отличие ограничено live assistant proposal generation. Transport fallback не меняет assignment: session остаётся C.

Обычное использование продукта не рандомизируется. B/C assignment существует только в explicit evaluation mode и хранится отдельно от `Case v2`.

## Canonical protocol documents

- [Approved design](superpowers/specs/2026-09-11-mind-detective-product-evaluation-design.md)
- [Staged protocol](evaluation/STAGED_PROTOCOL.md)
- [Real-pilot protocol](evaluation/REAL_PILOT_PROTOCOL.md)
- [External arm A protocol](evaluation/EXTERNAL_A_PROTOCOL.md)
- [Analysis runbook](evaluation/ANALYSIS.md)

Analysis CLI:

```bash
python -m scripts.analyze_evaluation export.json --seed 1729 --bootstrap 2000 --json-out summary.json
```

## Primary decision

Staged B↔C is primary. `time_to_next_useful_action` is reconstructed retrospectively from `case_started` → first shown proposal that later reaches matching `check_finished` without prior rejection. Sessions without an observed useful action are right-censored at terminal time or 10 minutes. Primary summary is 10-minute RMTUA with participant-clustered uncertainty.

Secondary evidence includes duplicate checks, fixed 1–5 task-load/convenience ratings, found/unresolved/abandoned distribution, proposal safety, handoff continuity, fallback, and technical failures. All assigned/started sessions remain visible in ITT; abandonment, fallback, incomplete participation, and missing ratings are not silently removed.

A product-direction claim requires at least 32 protocol-complete staged participants and at least 8 per counterbalance cell. Arm A remains contextual and does not alter the C-vs-B product decision.

## Privacy

Evaluation storage/export is local-only by default, explicit-export only, and allowlist-based. It rejects Case payload/content, item/location text, journal/statement/user text, evaluator free text, and raw model output. Normal Case export and evaluation export remain separate.

## Falsifiable rule

Если C не даёт practically meaningful lift относительно B при сопоставимом safety/readiness profile, default core следует упростить до deterministic checklist/controller. Если результат inconclusive, следующий номер версии сам по себе не является основанием объявлять победителя.

Green deterministic/browser/analysis fixtures подтверждают machinery, conformance и reproducibility, но не являются доказательством causal product lift или научной валидности исследования.
