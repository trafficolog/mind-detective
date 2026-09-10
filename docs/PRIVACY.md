# Privacy / Конфиденциальность

## Два разных контура хранения

Plugin surface сохраняет прежний 0.1.0 contract: Case создаётся в памяти процесса, а запись на диск выполняется только по явному действию пользователя (`save`/`pause`/`retain`) в `.mind-detective/cases/<case-id>/case.json`. Плагин не создаёт cross-case index, общий пользовательский профиль, hidden priors или автоматическое обучение на предыдущих кейсах.

В Web/PWA 0.2.0 каноническая browser copy хранится локально в IndexedDB. Service worker кэширует только application shell/static assets. Case payload, пользовательский текст, model output и evaluation records не должны попадать в Cache Storage или background sync. Persistent-storage permission повышает устойчивость browser-local storage, но **не является резервной копией**; для переноса предусмотрен явный JSON export/import.

## Local persistence не означает «данные никогда не покидают устройство»

В checklist arm доменные изменения идут через stateless FastAPI adapter и Python `CaseController`. В AI arm минимальный контекст, необходимый для конкретного proposal request, дополнительно transiently обрабатывается настроенным **LiteLLM Proxy** и выбранным model provider. Это transport/model-processing boundary, а не server-side Case storage.

Provider credentials и LiteLLM secrets остаются только на сервере и не должны попадать в browser bundle. Raw model output не является каноническим Case state: предложение проходит server-side proposal/guard boundary, а заблокированный raw proposal не сохраняется клиентом для последующего reveal.

## Минимизация данных

Web surface также не создаёт cross-case index или общий пользовательский профиль. Evaluation log хранит только allowlisted interaction/outcome metadata и отвергает raw `item_label`, location target, journal/user text и raw model output.

Не следует вводить в Case данные, не необходимые для поиска: credentials, access tokens, платёжные данные, подробные медицинские сведения, полный домашний адрес или другую идентифицирующую информацию без необходимости.

Case artifacts не содержат hidden chain-of-thought, `belief_weight`, POD или numerical location probability. Любое будущее cloud sync, account system, connector storage или расширение telemetry требует отдельной privacy/threat-model review.
