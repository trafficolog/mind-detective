from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class SearchMethod(str, Enum):
    GLANCE = "glance"
    VISUAL_SYSTEMATIC = "visual_systematic"
    EMPTY_AND_CHECK = "empty_and_check"
    TACTILE = "tactile"
    INACCESSIBLE = "inaccessible"


class SearchResult(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    PARTIAL = "partial"
    INACCESSIBLE = "inaccessible"


@dataclass(frozen=True, slots=True)
class SearchCheck:
    id: str
    target: str
    method: SearchMethod
    started_at: str
    completed_at: str | None
    result: SearchResult
    inaccessible_parts: tuple[str, ...]
    based_on: tuple[str, ...]
    notes: tuple[str, ...]


_STOP_WORDS = frozenset({"в", "на", "из", "the", "in", "on"})


def normalize_target(text: str) -> tuple[str, ...]:
    normalized = text.casefold().replace("ё", "е")
    tokens = re.findall(r"[\w-]+", normalized, flags=re.UNICODE)
    return tuple(token for token in tokens if token not in _STOP_WORDS)


def is_duplicate_target(a: str, b: str) -> bool:
    a_tokens = set(normalize_target(a))
    b_tokens = set(normalize_target(b))
    if not a_tokens or not b_tokens:
        return False
    if a_tokens == b_tokens:
        return True
    smaller, larger = (a_tokens, b_tokens) if len(a_tokens) <= len(b_tokens) else (b_tokens, a_tokens)
    return len(smaller) >= 2 and smaller.issubset(larger)


@dataclass(slots=True)
class SearchLog:
    _checks: list[SearchCheck] = field(default_factory=list)

    @property
    def checks(self) -> tuple[SearchCheck, ...]:
        return tuple(self._checks)

    def add(self, check: SearchCheck) -> tuple[SearchCheck, ...]:
        self._checks.append(check)
        return self.checks
