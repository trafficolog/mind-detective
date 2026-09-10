# MIND Detective 0.2.0 Requirements

Это нормативный реестр стабильных контрактов MIND Detective. Статус `active` означает, что требование имеет конкретный control path и exact test selector в `docs/CONTRACT_MATRIX.json`. Green fixture/contract validation подтверждает реализованный контроль, но не является доказательством научной валидности продукта или semantic compliance произвольной live-model генерации.

## Базовые контракты 0.1.0, сохраняемые в 0.2.0

- `MD-REQ-CASE-01` — один канонический Case Controller владеет детерминированным состоянием кейса. **Status: active.**
- `MD-REQ-STATEMENT-01` — `source` и `statement_type` являются независимыми полями. **Status: active.**
- `MD-REQ-STATEMENT-02` — assistant не может быть источником `recollection`, `habit` или `observation`. **Status: active.**
- `MD-REQ-STATEMENT-03` — vividness/confidence/sensory detail не повышают truth status механически. **Status: active.**
- `MD-REQ-RECONSTRUCT-01` — free account предшествует детальным уточнениям. **Status: active.**
- `MD-REQ-RECONSTRUCT-02` — reconstruction questions не вводят неподдержанные конкретные локации. **Status: active.**
- `MD-REQ-RECONSTRUCT-03` — «не помню» остаётся явной неопределённостью. **Status: active.**
- `MD-REQ-TIMELINE-01` — timeline сохраняет unknown intervals и contradictions. **Status: active.**
- `MD-REQ-SEARCH-01` — каждая физическая проверка хранит target, method, result и accessibility state. **Status: active.**
- `MD-REQ-SEARCH-02` — повторные проверки не трактуются как независимое probability evidence. **Status: active.**
- `MD-REQ-SEARCH-03` — конкретные локации допустимы как search suggestions, но не как memories/facts. **Status: active.**
- `MD-REQ-SEARCH-04` — выбирается одно next action без numerical location probability и hidden belief weight. **Status: active.**
- `MD-REQ-SEARCH-05` — superficial и thorough checks различимы в истории. **Status: active.**
- `MD-REQ-RESUME-01` — сохранённый кейс возобновляется без evidence strengthening и потери истории. **Status: active.**
- `MD-REQ-STORE-01` — persistence case-local, explicit и deletable. **Status: active.**
- `MD-REQ-STORE-02` — продукт не делает cross-case learning или hidden aggregation. **Status: active.**
- `MD-REQ-SAFETY-01` — high-risk forgotten actions не входят в ordinary physical-search reasoning. **Status: active.**
- `MD-REQ-CLOSE-01` — outcome фиксирует результат без диагностики forgetting mechanism. **Status: active.**
- `MD-REQ-EVAL-01` — high-risk contracts имеют deterministic tests и adversarial eval scenarios. **Status: active.**
- `MD-REQ-DOCS-01` — ключевые публичные docs RU-primary с EN mirrors. **Status: active.**
- `MD-REQ-RELEASE-01` — один repository SemVer, independent plugin SemVer, один manifest и один publisher. **Status: active.**

## Web/PWA 0.2.0

- `MD-WEB-REQ-SHELL-01` — checklist и AI используют один shell/navigation/action-card/input structure; arm identity не раскрывается как отдельный UX. **Status: active.**
- `MD-WEB-REQ-MODE-01` — каждая journal entry сохраняет immutable provenance `reconstruction` / `search` / `system`. **Status: active.**
- `MD-WEB-REQ-MODE-02` — mode представлен label + icon + typography/treatment, а не одним цветом. **Status: active.**
- `MD-WEB-REQ-STATE-01` — Nuxt-клиент не содержит параллельного Case reducer; canonical mutation приходит только полным Case от Python API. **Status: active.**
- `MD-WEB-REQ-QUEUE-01` — mutations проходят через sequential retryable pending-command queue; retry сохраняет command/entity/time identity. **Status: active.**
- `MD-WEB-REQ-CHECK-01` — one-tap `Проверил` записывает нейтральный `reported_check` и не повышает качество проверки автоматически. **Status: active.**
- `MD-WEB-REQ-CHECK-02` — `inaccessible_parts` ортогонален method quality и не кодируется как новый Web check method. **Status: active.**
- `MD-WEB-REQ-SUMMARY-01` — checked/remaining/inaccessible summary постоянно видим и вычисляется из canonical Case. **Status: active.**
- `MD-WEB-REQ-CREATE-01` — production first-case flow — одно поле + одна primary action, без engine/arm selector. **Status: active.**
- `MD-WEB-REQ-RESUME-01` — active/paused browser-local cases listable/resumable без усиления evidence. **Status: active.**
- `MD-WEB-REQ-EMPTY-01` — empty planner показывает deterministic need-more-information state без выдуманной локации. **Status: active.**
- `MD-WEB-REQ-GUARD-01` — blocked AI proposal даёт visible reviewed system event + deterministic fallback; rejected raw text не сохраняется для последующего reveal. **Status: active.**
- `MD-WEB-REQ-ACTION-01` — next action можно отклонить с canonical categorical feedback, после чего он не повторяется немедленно без нового основания. **Status: active.**
- `MD-WEB-REQ-CLOSE-01` — found context различает current suggested action, elsewhere/unplanned, after previous check и unknown; unresolved остаётся отдельным outcome. **Status: active.**
- `MD-WEB-REQ-STORE-01` — IndexedDB является canonical Web persistence; приложение не вводит server-side case database. **Status: active.**
- `MD-WEB-REQ-STORE-02` — persistence capability проверяется/запрашивается после meaningful engagement и описывается без гарантии backup. **Status: active.**
- `MD-WEB-REQ-EXPORT-01` — local JSON export/import versioned, validated и поддерживает deterministic v1→v2 migration. **Status: active.**
- `MD-WEB-REQ-PWA-01` — service worker кэширует shell/static assets, но не API/Case/user/model/evaluation data и не регистрирует background sync. **Status: active.**
- `MD-WEB-REQ-I18N-01` — RU/EN copy maps имеют exact key parity и одинаковые safety/privacy semantics. **Status: active.**
- `MD-WEB-REQ-EVAL-01` — local evaluation events фиксируют взаимодействия/исходы без raw Case/item/location/journal/model text и без background telemetry upload. **Status: active.**
- `MD-WEB-REQ-CORE-01` — Web/API переиспользуют Python CaseController; TypeScript port/domain reducer отсутствует. **Status: active.**
- `MD-WEB-REQ-PRIVACY-01` — browser-local persistence отдельно раскрывается от transient minimum-context processing через configured LiteLLM/model provider; server-side secrets не попадают в client bundle. **Status: active.**
- `MD-WEB-REQ-RELEASE-01` — `0.2.0` публикуется только через существующий hardened publisher после exact-main CI и отдельного human-approved full 40-hex SHA gate. **Status: active.**

`docs/CONTRACT_MATRIX.json` является machine-readable trace map для всех перечисленных требований.
