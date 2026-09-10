from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence


_ERROR = "MD_LOCAL_CANONICAL_JSON"


def _validate_json_value(value: object, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise ValueError(f"{_ERROR}: floating value at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{_ERROR}: non-string object key at {path}")
            _validate_json_value(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not isinstance(value, list):
            raise ValueError(f"{_ERROR}: only JSON arrays are accepted at {path}")
        for index, child in enumerate(value):
            _validate_json_value(child, f"{path}[{index}]")
        return
    raise ValueError(f"{_ERROR}: unsupported value at {path}: {type(value).__name__}")


def canonical_json(value: object) -> str:
    _validate_json_value(value)
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{_ERROR}: serialization failed") from exc


def canonical_sha256(value: object) -> str:
    encoded = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
