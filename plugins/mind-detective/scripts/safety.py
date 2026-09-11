from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .portable_kernel import classify_safety_text_json


class SafetyRoute(str, Enum):
    ORDINARY_SEARCH = "ordinary_search"
    LIMIT_AND_ESCALATE = "limit_and_escalate"


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    route: SafetyRoute
    codes: tuple[str, ...]
    message_key: str


def classify_request(text: str) -> SafetyDecision:
    payload = classify_safety_text_json(text)
    route = payload["route"]
    codes = payload["codes"]
    message_key = payload["message_key"]
    if not isinstance(route, str) or not isinstance(codes, list) or not isinstance(message_key, str):
        raise RuntimeError("MD_SAFE_PORTABLE_CONTRACT")
    if not all(isinstance(code, str) for code in codes):
        raise RuntimeError("MD_SAFE_PORTABLE_CONTRACT")
    return SafetyDecision(
        route=SafetyRoute(route),
        codes=tuple(codes),
        message_key=message_key,
    )
