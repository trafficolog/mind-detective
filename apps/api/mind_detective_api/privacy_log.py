from __future__ import annotations

from collections.abc import Mapping


class PrivacyLogError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


_ALLOWED_FIELDS = frozenset(
    {
        "request_id",
        "arm",
        "outcome_code",
        "latency_bucket",
        "model_id",
    }
)
_SENSITIVE_FIELDS = frozenset(
    {
        "case",
        "item_label",
        "user_text",
        "target",
        "journal_text",
        "statement_text",
        "raw_model_output",
    }
)


def build_privacy_log(event_name: str, metadata: Mapping[str, object]) -> dict[str, object]:
    keys = set(metadata)
    sensitive = sorted(keys & _SENSITIVE_FIELDS)
    if sensitive:
        raise PrivacyLogError(
            "MD_WEB_LOG_SENSITIVE_FIELD",
            "sensitive log fields are forbidden: " + ",".join(sensitive),
        )
    unexpected = sorted(keys - _ALLOWED_FIELDS)
    if unexpected:
        raise PrivacyLogError(
            "MD_WEB_LOG_FIELD",
            "unexpected log fields: " + ",".join(unexpected),
        )
    return {"event": event_name, **dict(metadata)}
