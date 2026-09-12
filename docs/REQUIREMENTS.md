# MIND Detective 0.3.0 Requirements

Это нормативный реестр стабильных контрактов MIND Detective. `active` означает наличие конкретного control path и exact test selector в `docs/CONTRACT_MATRIX.json`. Green contract test подтверждает реализацию контроля, но не доказывает научную валидность продукта или semantic compliance произвольной live-model генерации.

## Базовые контракты

- `MD-REQ-CASE-01` — один канонический Case Controller владеет детерминированной семантикой кейса. **Status: active.**
- `MD-REQ-STATEMENT-01` — `source` и `statement_type` независимы. **Status: active.**
- `MD-REQ-STATEMENT-02` — assistant не может быть источником recollection/habit/observation. **Status: active.**
- `MD-REQ-STATEMENT-03` — vividness/confidence/sensory detail не повышают truth status механически. **Status: active.**
- `MD-REQ-RECONSTRUCT-01` — free account предшествует детальным уточнениям. **Status: active.**
- `MD-REQ-RECONSTRUCT-02` — reconstruction questions не вводят неподдержанные конкретные локации. **Status: active.**
- `MD-REQ-RECONSTRUCT-03` — «не помню» остаётся явной неопределённостью. **Status: active.**
- `MD-REQ-TIMELINE-01` — timeline сохраняет unknown intervals и contradictions. **Status: active.**
- `MD-REQ-SEARCH-01` — физическая проверка хранит target, method, result и accessibility state. **Status: active.**
- `MD-REQ-SEARCH-02` — повторные проверки не являются независимым probability evidence. **Status: active.**
- `MD-REQ-SEARCH-03` — конкретные локации допустимы как search suggestions, но не как memories/facts. **Status: active.**
- `MD-REQ-SEARCH-04` — выбирается одно next action без numerical location probability/hidden belief weight. **Status: active.**
- `MD-REQ-SEARCH-05` — superficial и thorough checks различимы. **Status: active.**
- `MD-REQ-RESUME-01` — resume не усиливает evidence и не теряет историю. **Status: active.**
- `MD-REQ-STORE-01` — persistence case-local, explicit и deletable. **Status: active.**
- `MD-REQ-STORE-02` — нет cross-case learning/hidden aggregation. **Status: active.**
- `MD-REQ-SAFETY-01` — high-risk forgotten actions не входят в ordinary physical-search reasoning. **Status: active.**
- `MD-REQ-CLOSE-01` — outcome фиксируется без диагностики forgetting mechanism. **Status: active.**
- `MD-REQ-EVAL-01` — high-risk contracts имеют deterministic tests и adversarial eval scenarios. **Status: active.**
- `MD-REQ-DOCS-01` — ключевые публичные docs RU-primary с EN mirrors. **Status: active.**
- `MD-REQ-RELEASE-01` — один repository SemVer, independent plugin SemVer, один manifest и один publisher. **Status: active.**

## Web/PWA contracts, сохранённые и уточнённые в 0.3.0

Web/PWA реализует физический Search/checklist surface. Полная reconstruction остаётся plugin/agent capability: Web может безопасно читать сохранённые reconstruction evidence/journal entries и переводить такое дело в Search, но не собирает новый reconstruction account, не добавляет recollection через placeholder composer и не запрашивает assistant proposal в reconstruction mode.

- `MD-WEB-REQ-SHELL-01` — checklist и AI используют один shell/navigation/action-card/input structure. **Status: active.**
- `MD-WEB-REQ-MODE-01` — journal entry сохраняет immutable provenance reconstruction/search/system. **Status: active.**
- `MD-WEB-REQ-MODE-02` — mode представлен label + icon + typography/treatment, не одним цветом. **Status: active.**
- `MD-WEB-REQ-STATE-01` — Web не содержит hand-maintained Case reducer; canonical deterministic state изменяется только certified generated executor или server compatibility path, возвращающим полный Case. **Status: active.**
- `MD-WEB-REQ-QUEUE-01` — retry после local persistence failure повторяет byte-equivalent Case snapshot и тот же command envelope; network command queue не является primary deterministic path. **Status: active.**
- `MD-WEB-REQ-CHECK-01` — one-tap check записывает нейтральный reported_check без автоматического повышения качества. **Status: active.**
- `MD-WEB-REQ-CHECK-02` — inaccessible parts ортогональны method quality. **Status: active.**
- `MD-WEB-REQ-SUMMARY-01` — checked/remaining/inaccessible summary постоянно вычисляется из canonical Case. **Status: active.**
- `MD-WEB-REQ-CREATE-01` — first-case flow остаётся одним полем + одной primary action. **Status: active.**
- `MD-WEB-REQ-RESUME-01` — active/paused local cases listable/resumable без усиления evidence. **Status: active.**
- `MD-WEB-REQ-EMPTY-01` — empty planner показывает need-more-information без выдуманной локации. **Status: active.**
- `MD-WEB-REQ-GUARD-01` — blocked assistant proposal даёт reviewed system event + deterministic fallback; rejected raw text не раскрывается позже. **Status: active.**
- `MD-WEB-REQ-ACTION-01` — next action можно отклонить с categorical feedback без немедленного повторения без нового основания. **Status: active.**
- `MD-WEB-REQ-CLOSE-01` — found context и unresolved outcome остаются явными. **Status: active.**
- `MD-WEB-REQ-STORE-01` — IndexedDB является canonical Web persistence; server-side Case database не вводится. **Status: active.**
- `MD-WEB-REQ-STORE-02` — persistence capability описывается без гарантии backup. **Status: active.**
- `MD-WEB-REQ-EXPORT-01` — JSON export/import versioned, validated и поддерживает deterministic v1→v2 migration. **Status: active.**
- `MD-WEB-REQ-PWA-01` — service worker кэширует только shell/static assets, без API/Case/user/model/evaluation data и Background Sync. **Status: active.**
- `MD-WEB-REQ-I18N-01` — RU/EN copy maps имеют exact key parity и одинаковые safety/privacy semantics. **Status: active.**
- `MD-WEB-REQ-EVAL-01` — local evaluation events не содержат raw Case/item/location/journal/model text и не загружаются background telemetry. **Status: active.**
- `MD-WEB-REQ-CORE-01` — Python portable kernel является source semantics; Web выполняет только generated certified artifact, а не hand-maintained port. **Status: active.**
- `MD-WEB-REQ-PRIVACY-01` — local persistence отделена от transient minimum-context processing через LiteLLM/provider; server secrets отсутствуют в client bundle. **Status: active.**
- `MD-WEB-REQ-RELEASE-01` — publication идёт только через hardened publisher после exact-main CI и human-approved full 40-hex SHA. **Status: active.**

## Web Reconstruction Foundation 0.4.0

Следующие контракты реализованы Tasks 2–7 и активированы только после появления production path, exact test selector и проверки production reachability.

- `MD-WEB-REQ-RECONSTRUCT-01` — raw free account предшествует detailed reconstruction statements. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-02` — recollection/habit/observation в Web имеют user provenance и остаются user-originated/user-confirmed. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-03` — reconstruction не вводит неподдержанные concrete locations как cues. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-04` — unknown intervals и contradictions сохраняются и отображаются канонически. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-05` — timeline mutation выполняется через portable authoritative semantics и generated Web execution. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-06` — raw account, structured evidence, derived uncertainty, proposals и Search семантически и визуально различимы. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-07` — переход reconstruction → Search явный и не повышает evidence status. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-08` — deterministic reconstruction работает offline после PWA preload. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-09` — RU/EN reconstruction copy имеет exact key parity и эквивалентную safety/privacy semantics. **Status: active.**
- `MD-WEB-REQ-RECONSTRUCT-10` — Case v2 export/import сохраняет reconstruction state без server validation dependency. **Status: active.**

## Offline deterministic execution 0.3.0

- `MD-OFFLINE-REQ-KERNEL-01` — portable kernel имеет exact versioned contract и JSON-compatible observable surface. **Status: active.**
- `MD-OFFLINE-REQ-GENERATOR-01` — generator принимает только restricted certified Python AST/intrinsics и детерминированно создаёт TypeScript artifact. **Status: active.**
- `MD-OFFLINE-REQ-CONFORMANCE-01` — committed corpus проверяет observable parity Python и generated TypeScript. **Status: active.**
- `MD-OFFLINE-REQ-API-01` — API compatibility adapters делегируют portable kernel, не реконструируя отдельную domain semantics. **Status: active.**
- `MD-OFFLINE-REQ-INTRINSIC-01` — casefold, whitespace split, string ordering, clone/error semantics сертифицированы явно. **Status: active.**
- `MD-OFFLINE-REQ-LOCAL-01` — deterministic create/mutations работают без Case API network calls. **Status: active.**
- `MD-OFFLINE-REQ-ATOMIC-01` — Case и execution receipt фиксируются одной IndexedDB transaction; failed commit не меняет canonical persisted Case. **Status: active.**
- `MD-OFFLINE-REQ-IDEMPOTENCE-01` — повтор того же command id/input возвращает сохранённый canonical result, конфликтующий reuse fail-closed. **Status: active.**
- `MD-OFFLINE-REQ-CREATE-01` — local create является create-only и защищает case-id conflict. **Status: active.**
- `MD-OFFLINE-REQ-PROPOSAL-01` — deterministic checklist proposal доступен локально из той же portable semantics. **Status: active.**
- `MD-OFFLINE-REQ-ASSISTANT-01` — assistant transport failure использует local fallback без reconnect replay. **Status: active.**
- `MD-OFFLINE-REQ-IDENTITY-01` — server публикует execution identity version/kernel/generated/generator hashes. **Status: active.**
- `MD-OFFLINE-REQ-SKEW-01` — mismatch execution identity блокирует assistant provider call, но не откатывает уже committed local deterministic mutation. **Status: active.**
- `MD-OFFLINE-REQ-PRIVACY-01` — local deterministic Case path не отправляет Case mutations в API; model boundary остаётся отдельным transient assistant path. **Status: active.**
- `MD-OFFLINE-REQ-PWA-01` — после preload PWA выполняет canonical search workflow offline и восстанавливает persisted Case. **Status: active.**
- `MD-OFFLINE-REQ-RELEASE-01` — repository/plugin release 0.3.0 публикуются из exact verified main SHA через единственный hardened publisher. **Status: active.**

`docs/CONTRACT_MATRIX.json` является machine-readable trace map всех требований выше.
