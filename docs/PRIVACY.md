# Privacy / Конфиденциальность

## Case-local persistence

Plugin surface сохраняет Case на диск только по **явному действию пользователя** (`save`/`pause`/`retain`) в `.mind-detective/cases/<case-id>/case.json`. Плагин не создаёт cross-case index, общий профиль пользователя, hidden priors или автоматическое обучение на предыдущих кейсах.

В Web/PWA canonical Case хранится локально в IndexedDB. Deterministic create, Reconstruction и Search mutations выполняются generated local executor и атомарно записывают Case вместе с execution receipt. Они не требуют отправки Case mutation в `/api/v1/case/*`.

Reconstruction сохраняет свободный рассказ **дословно** как `entry_type=free_account`, `author=user`, `mode=reconstruction`. `free_account` не классифицируется автоматически как recollection/habit/observation. Structured reconstruction evidence появляется только после явного подтверждения пользователя; unknowns/contradictions остаются частью canonical Case, а не скрываются или заменяются догадками.

Service worker кэширует только application shell/static assets. Case payload, user text, model output и evaluation records не попадают в precache/background sync. Persistent Storage API не является гарантией backup; переносимость обеспечивается explicit JSON export/import того же `mind-detective-case/v2`.

## Reconstruction не требует передачи рассказа модели

Local deterministic Reconstruction (`record_free_account`, `rebuild_timeline`) работает без model provider и после PWA preload может выполняться офлайн. Vue UI передаёт пользовательские payloads в generated local execution boundary и не отправляет raw free account в модель как обязательную часть reconstruction flow.

Live-model clarification не является зависимостью Reconstruction core. Если пользователь позднее явно переходит в Search и включён assistant arm, минимально необходимый transient context текущего Search proposal может пересечь server boundary по правилам ниже; это отдельная операция и не превращает model output в canonical user memory evidence.

## Local-first не означает «никаких внешних данных» для Search AI

Checklist/local deterministic path не требует model provider. Search assistant proposal — отдельная transient processing boundary: минимально необходимый контекст текущего proposal может пройти через stateless FastAPI, LiteLLM Proxy и настроенного model provider. Provider credentials и LiteLLM secrets остаются server-side.

Assistant request несёт execution identity; mismatch блокируется до provider creation. При transport failure используется local deterministic fallback, и прежний model request не ставится в reconnect replay queue.

Raw model output не становится canonical Case автоматически: server-side proposal/guard boundary возвращает reviewed structured proposal или deterministic fallback. Заблокированный raw proposal не сохраняется для последующего reveal. Assistant-authored recollection/habit/observation не допускаются.

## Evaluation и минимизация данных

Browser evaluation log остаётся локальным и allowlisted. Он хранит interaction/outcome metadata, но отвергает raw `item_label`, location target, journal/user text и raw model output; background telemetry upload отсутствует.

Текущий B↔C evaluation измеряет Search assistant proposal arm и не требует отправки Reconstruction free account/evidence в evaluation log. Normal Case export и evaluation export остаются раздельными.

Не следует помещать в Case credentials, access tokens, платёжные данные, подробные медицинские сведения, полный домашний адрес или другую идентифицирующую информацию без необходимости.

Case artifacts не содержат hidden chain-of-thought, `belief_weight`, POD или numerical location probability. Будущие cloud sync, account system, connector storage или расширение telemetry требуют отдельной privacy/threat-model review.
