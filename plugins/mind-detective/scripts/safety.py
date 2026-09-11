from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class SafetyRoute(str, Enum):
    ORDINARY_SEARCH = "ordinary_search"
    LIMIT_AND_ESCALATE = "limit_and_escalate"


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    route: SafetyRoute
    codes: tuple[str, ...]
    message_key: str


_MEDICATION_ACTION_PATTERNS = (
    r"\b(?:я\s+)?уже\s+(?:принял|приняла|выпил|выпила)\w*\s+(?:таблет|лекарств|доз)\w*",
    r"\bпринимал[аи]?\s+ли\s+(?:я\s+)?(?:таблет|лекарств|доз)\w*",
    r"\bdid\s+i\s+(?:already\s+)?take\s+(?:the\s+)?(?:pill|medicine|dose)\b",
    r"\bhave\s+i\s+(?:already\s+)?taken\s+(?:the\s+)?(?:pill|medicine|dose)\b",
)
_HAZARDOUS_ACTION_PATTERNS = (
    r"\b(?:я\s+)?выключил[аи]?\s+(?:плит|утюг|обогревател|газ)\w*",
    r"\b(?:я\s+)?перекрыл[аи]?\s+газ\b",
    r"\bdid\s+i\s+(?:turn\s+off|shut\s+off)\s+(?:the\s+)?(?:stove|iron|heater|gas)\b",
)
_SECURITY_ACTION_PATTERNS = (
    r"\b(?:я\s+)?(?:запер|заперла|закрыл|закрыла)\w*\s+(?:входн\w*\s+)?двер\w*",
    r"\b(?:я\s+)?поставил[аи]?\s+(?:дом|квартир\w*)\s+на\s+сигнализац\w*",
    r"\bdid\s+i\s+(?:lock|arm)\s+(?:the\s+)?(?:door|alarm)\b",
)


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def classify_request(text: str) -> SafetyDecision:
    normalized = text.casefold().replace("ё", "е")
    codes: list[str] = []

    if _matches(normalized, _MEDICATION_ACTION_PATTERNS):
        codes.append("MD_SAFE_MEDICATION_ACTION")
    if _matches(normalized, _HAZARDOUS_ACTION_PATTERNS):
        codes.append("MD_SAFE_HAZARDOUS_ACTION")
    if _matches(normalized, _SECURITY_ACTION_PATTERNS):
        codes.append("MD_SAFE_SECURITY_ACTION")

    if codes:
        return SafetyDecision(
            route=SafetyRoute.LIMIT_AND_ESCALATE,
            codes=tuple(dict.fromkeys(codes)),
            message_key="high_risk_forgotten_action",
        )
    return SafetyDecision(
        route=SafetyRoute.ORDINARY_SEARCH,
        codes=(),
        message_key="ordinary_lost_item_search",
    )
