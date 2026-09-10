from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class InteractionMode(str, Enum):
    RECONSTRUCTION = "reconstruction"
    SEARCH_PLANNING = "search_planning"


@dataclass(frozen=True, slots=True)
class GuardResult:
    allowed: bool
    codes: tuple[str, ...]
    details: tuple[str, ...]


_LOCATION_PATTERNS: dict[str, tuple[str, ...]] = {
    "car": (r"\bмашин\w*\b", r"\bавтомобил\w*\b", r"\bcar\b"),
    "kitchen": (r"\bкухн\w*\b", r"\bkitchen\b"),
    "pocket": (r"\bкарман\w*\b", r"\bpocket\w*\b"),
    "bag": (r"\bсумк\w*\b", r"\bbag\b"),
    "table": (r"\bстол\w*\b", r"\btable\b"),
    "sofa": (r"\bдиван\w*\b", r"\bsofa\b", r"\bcouch\b"),
    "closet": (r"\bшкаф\w*\b", r"\bcloset\b", r"\bcabinet\b"),
    "bathroom": (r"\bванн\w*\b", r"\bbathroom\b"),
    "bedroom": (r"\bспальн\w*\b", r"\bbedroom\b"),
    "hallway": (r"\bкоридор\w*\b", r"\bhallway\b"),
    "entryway": (r"\bприхож\w*\b", r"\bentryway\b"),
    "fridge": (r"\bхолодильник\w*\b", r"\bfridge\b", r"\brefrigerator\b"),
}

_PROBABILITY_PATTERNS = (
    r"\bвероятност\w*\b",
    r"\bшанс\w*\b",
    r"\bprobabilit\w*\b",
    r"\bchance\b",
    r"\b\d{1,3}\s*%",
)
_FALSE_MEMORY_PATTERNS = (
    r"\bвы\s+точно\s+(?:положили|оставили|видели|брали)\b",
    r"\bты\s+точно\s+(?:положил|оставил|видел|брал)\b",
    r"\byou\s+definitely\s+(?:put|left|saw|took)\b",
    r"\bremember\s+that\s+you\b",
)
_MECHANISM_PATTERNS = (
    r"\bзабыл\w*\b.*\bиз[- ]?за\b",
    r"\bэто\s+(?:из[- ]?за|потому\s+что)\b.*\b(?:стресс|двер|отвлеч)\w*\b",
    r"\bforgot\w*\b.*\bbecause\b",
    r"\bdoorway\b.*\bmade\s+you\s+forget\b",
)
_SEARCH_AS_MEMORY_PATTERNS = (
    r"\bне\s+нашл\w*\b.*\bзначит\b.*\bне\s+(?:клал|клали|оставлял|оставляли)\b",
    r"\bdidn['’]?t\s+find\b.*\bmeans\b.*\bnever\s+(?:put|left)\b",
)
_SUPERFICIAL_ABSENCE_PATTERNS = (
    r"\bбыстро\s+(?:посмотрел\w*|проверил\w*)\b.*\bзначит\b.*\b(?:точно\s+)?нет\b",
    r"\bглянул\w*\b.*\bзначит\b.*\b(?:точно\s+)?нет\b",
    r"\bquick\s+(?:look|glance)\b.*\b(?:proves|means)\b.*\bnot\s+there\b",
)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _find_location_keys(text: str) -> set[str]:
    lowered = text.casefold().replace("ё", "е")
    return {
        key
        for key, patterns in _LOCATION_PATTERNS.items()
        if any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in patterns)
    }


def lint_candidate(
    text: str,
    *,
    mode: InteractionMode,
    known_locations: set[str],
) -> GuardResult:
    codes: list[str] = []
    details: list[str] = []
    normalized = text.casefold().replace("ё", "е")

    if mode is InteractionMode.RECONSTRUCTION:
        candidate_locations = _find_location_keys(normalized)
        known_keys: set[str] = set()
        for location in known_locations:
            known_keys.update(_find_location_keys(location))
        unknown = sorted(candidate_locations - known_keys)
        if unknown:
            codes.append("MD_G_RECON_NEW_LOCATION")
            details.append("unsupported reconstruction location:" + ",".join(unknown))

    if _matches_any(normalized, _FALSE_MEMORY_PATTERNS):
        codes.append("MD_G_FALSE_MEMORY")
    if _matches_any(normalized, _MECHANISM_PATTERNS):
        codes.append("MD_G_MECHANISM_DIAGNOSIS")
    if _matches_any(normalized, _PROBABILITY_PATTERNS):
        codes.append("MD_G_LOCATION_PROBABILITY")
    if _matches_any(normalized, _SEARCH_AS_MEMORY_PATTERNS):
        codes.append("MD_G_SEARCH_AS_MEMORY")
    if _matches_any(normalized, _SUPERFICIAL_ABSENCE_PATTERNS):
        codes.append("MD_G_SUPERFICIAL_PROVES_ABSENCE")

    unique_codes = tuple(dict.fromkeys(codes))
    return GuardResult(allowed=not unique_codes, codes=unique_codes, details=tuple(details))
