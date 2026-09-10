from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .portable_kernel import select_next_action_json


class RouteRelation(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    NONE = "none"


class CheckState(str, Enum):
    UNCHECKED = "unchecked"
    PARTIAL = "partial"
    CHECKED = "checked"


class Effort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Safety(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"


class UrgencyRelevance(str, Enum):
    HIGH = "high"
    NORMAL = "normal"


class CandidateBasis(str, Enum):
    EPISODE = "episode"
    HABIT = "habit"
    GENERIC = "generic"


@dataclass(frozen=True, slots=True)
class CandidateCheck:
    id: str
    target: str
    route_relation: RouteRelation
    check_state: CheckState
    effort: Effort
    safety: Safety
    urgency_relevance: UrgencyRelevance
    basis: CandidateBasis
    based_on: tuple[str, ...]
    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NextAction:
    candidate_id: str
    target: str
    rationale_codes: tuple[str, ...]


def _candidate_to_json(candidate: CandidateCheck) -> dict[str, object]:
    return {
        "id": candidate.id,
        "target": candidate.target,
        "route_relation": candidate.route_relation.value,
        "check_state": candidate.check_state.value,
        "effort": candidate.effort.value,
        "safety": candidate.safety.value,
        "urgency_relevance": candidate.urgency_relevance.value,
        "basis": candidate.basis.value,
        "based_on": list(candidate.based_on),
        "rationale": list(candidate.rationale),
    }


def _required_str(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"portable planner returned invalid {key}")
    return value


def select_next_action(candidates: list[CandidateCheck]) -> NextAction | None:
    raw = select_next_action_json([_candidate_to_json(candidate) for candidate in candidates])
    if raw is None:
        return None
    codes_raw = raw.get("rationale_codes")
    if not isinstance(codes_raw, list) or not all(isinstance(code, str) for code in codes_raw):
        raise ValueError("portable planner returned invalid rationale_codes")
    return NextAction(
        candidate_id=_required_str(raw, "candidate_id"),
        target=_required_str(raw, "target"),
        rationale_codes=tuple(codes_raw),
    )
