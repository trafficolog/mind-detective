from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InteractionMode(str, Enum):
    UNSELECTED = "unselected"
    RECONSTRUCTION = "reconstruction"
    SEARCH = "search"


class JournalMode(str, Enum):
    RECONSTRUCTION = "reconstruction"
    SEARCH = "search"
    SYSTEM = "system"


class JournalAuthor(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class JournalEntry:
    id: str
    author: JournalAuthor
    mode: JournalMode
    entry_type: str
    text: str
    created_at: str
    statement_ids: tuple[str, ...] = ()
    search_check_ids: tuple[str, ...] = ()
