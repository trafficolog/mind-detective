# ADR 012: LiteLLM — единственный live-model gateway Web 0.2.0

Status: Accepted for 0.2.0

## Context

AI proposal generation требует внешней model processing, но provider-specific clients в Web/API размыли бы privacy, credentials и guard boundary.

## Decision

FastAPI обращается только к настроенному LiteLLM Proxy. Provider credentials и LiteLLM secrets остаются server-side. В AI request передаётся только минимальный контекст, необходимый для текущего proposal. Raw model output не становится canonical Case state: он проходит proposal validation/guard, после чего Web получает reviewed structured proposal/fallback.

Blocked raw proposal не сохраняется для последующего reveal. Application/evaluation logs по умолчанию не содержат raw Case, user text или model output.

## Consequences

- client bundle не знает provider credentials;
- смена model provider происходит за LiteLLM boundary, а не через новый client/API adapter;
- browser-local storage нельзя описывать как «данные никогда не покидают устройство»;
- расширение отправляемого контекста или telemetry требует privacy review.
