# MIND Detective / Детектив памяти

<!-- release-0.1.0 -->

[English](README.en.md)

**MIND Detective — помощник систематического поиска потерянных вещей.** Он помогает разгрузить рабочую память во время поиска: зафиксировать собственные воспоминания пользователя без превращения их в «факты», вести журнал уже выполненных физических проверок, выбрать одно полезное следующее действие и продолжить сохранённый кейс после паузы.

## Что делает 0.1.0

- нейтрально структурирует рассказ пользователя и сохраняет неопределённость;
- различает `recollection`, `habit`, `observation`, `hypothesis` и `search_suggestion` по происхождению;
- записывает физические `SearchCheck`: место, метод, результат и недоступные части;
- выбирает одно следующее действие по прозрачным категориальным правилам;
- сохраняет только явно выбранный кейс в `.mind-detective/cases/<case-id>/case.json`;
- возобновляет и передаёт кейс без потери уже выполненных проверок;
- отделяет поиск физического предмета от опасной неопределённости о том, было ли выполнено действие.

## Чего продукт не заявляет

MVP не является медицинским инструментом, не сообщает «истинную» причину забывания, не присваивает локациям калиброванные проценты, не использует Bayesian/POD/hidden belief weight и не считает повторные быстрые проверки независимыми доказательствами отсутствия. Generic Claude Code/Codex host также не даёт репозиторию обязательного pre-send interceptor: guard механически контролирует только переданные ему candidate utterances.

## Архитектура

```text
Skill host / future UI
          │
          ▼
     Case Controller
   ┌──────┼────────┐
   ▼      ▼        ▼
statements timeline SearchCheck log
   │               │
   └───────┬───────┘
           ▼
 categorical planner
           │
           ▼
 one next action
           │
           ▼
 explicit case-local save/resume/delete
```

Плагин содержит ровно пять production skills: `mind-detective`, `mind-detective-reconstruct`, `mind-detective-plan`, `mind-detective-resume`, `mind-detective-close`. Runtime — Python standard library first, без transport/provider SDK.

## Разработка и проверка

Проект использует SDD + TDD: `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`. Высокорисковые требования имеют стабильные `MD-REQ-*`, exact unittest selectors в `docs/CONTRACT_MATRIX.json` и adversarial scenarios в `plugins/mind-detective/evals/scenarios.json`.

Начните с [Getting Started](docs/GETTING_STARTED.md), затем см. [Architecture](docs/ARCHITECTURE.md), [Methodology](docs/METHODOLOGY.md), [Privacy](docs/PRIVACY.md) и [Product Evaluation](docs/PRODUCT_EVALUATION.md).
