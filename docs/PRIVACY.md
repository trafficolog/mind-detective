# Privacy / Конфиденциальность

## Case-local persistence

Plugin surface сохраняет Case на диск только по **явному действию пользователя** (`save`/`pause`/`retain`) в `.mind-detective/cases/<case-id>/case.json`. Плагин не создаёт cross-case index, общий профиль пользователя, hidden priors или автоматическое обучение на предыдущих кейсах.

В Web/PWA canonical Case хранится локально в IndexedDB. Deterministic create и mutations выполняются generated local executor и атомарно записывают Case вместе с execution receipt. Они не требуют отправки Case mutation в `/api/v1/case/*`.

Service worker кэширует только application shell/static assets. Case payload, user text, model output и evaluation records не попадают в precache/background sync. Persistent Storage API не является гарантией backup; переносимость обеспечивается explicit JSON export/import.

## Local-first не означает «никаких внешних данных» для AI

Checklist/local deterministic path не требует model provider. Assistant proposal — отдельная transient processing boundary: минимально необходимый контекст текущего proposal может пройти через stateless FastAPI, LiteLLM Proxy и настроенного model provider. Provider credentials и LiteLLM secrets остаются server-side.

Assistant request несёт execution identity; mismatch блокируется до provider creation. При transport failure используется local deterministic fallback, и прежний model request не ставится в reconnect replay queue.

Raw model output не становится canonical Case автоматически: server-side proposal/guard boundary возвращает reviewed structured proposal или deterministic fallback. Заблокированный raw proposal не сохраняется для последующего reveal.

## Evaluation и минимизация данных

Browser evaluation log остаётся локальным и allowlisted. Он хранит interaction/outcome metadata, но отвергает raw `item_label`, location target, journal/user text и raw model output; background telemetry upload отсутствует.

Не следует помещать в Case credentials, access tokens, платёжные данные, подробные медицинские сведения, полный домашний адрес или другую идентифицирующую информацию без необходимости.

Case artifacts не содержат hidden chain-of-thought, `belief_weight`, POD или numerical location probability. Будущие cloud sync, account system, connector storage или расширение telemetry требуют отдельной privacy/threat-model review.
