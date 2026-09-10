from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionFeedbackReason(str, Enum):
    ALREADY_CHECKED = "already_checked"
    IMPOSSIBLE_NOW = "impossible_now"
    IRRELEVANT = "irrelevant"
    UNSAFE_OR_UNCOMFORTABLE = "unsafe_or_uncomfortable"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class ActionFeedback:
    id: str
    candidate_id: str
    reason: ActionFeedbackReason
    recorded_at: str
