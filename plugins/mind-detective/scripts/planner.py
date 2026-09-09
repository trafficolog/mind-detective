from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeVar


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


_T = TypeVar("_T")


def _keep_best(
    items: list[_T],
    getter: Callable[[_T], object],
    order: tuple[object, ...],
) -> list[_T]:
    for preferred in order:
        matched = [item for item in items if getter(item) == preferred]
        if matched:
            return matched
    return items


def select_next_action(candidates: list[CandidateCheck]) -> NextAction | None:
    pool = [candidate for candidate in candidates if candidate.safety is not Safety.UNSAFE]
    if not pool:
        return None

    pool = _keep_best(
        pool,
        lambda item: item.urgency_relevance,
        (UrgencyRelevance.HIGH, UrgencyRelevance.NORMAL),
    )
    pool = _keep_best(
        pool,
        lambda item: item.basis,
        (CandidateBasis.EPISODE, CandidateBasis.HABIT, CandidateBasis.GENERIC),
    )
    pool = _keep_best(
        pool,
        lambda item: item.route_relation,
        (RouteRelation.DIRECT, RouteRelation.INDIRECT, RouteRelation.NONE),
    )
    pool = _keep_best(
        pool,
        lambda item: item.check_state,
        (CheckState.UNCHECKED, CheckState.PARTIAL, CheckState.CHECKED),
    )
    pool = _keep_best(pool, lambda item: item.effort, (Effort.LOW, Effort.MEDIUM, Effort.HIGH))
    chosen = min(pool, key=lambda item: item.id)

    codes: list[str] = []
    if chosen.urgency_relevance is UrgencyRelevance.HIGH:
        codes.append("MD_PLAN_URGENT")
    codes.append(f"MD_PLAN_BASIS_{chosen.basis.value.upper()}")
    codes.append(f"MD_PLAN_{chosen.route_relation.value.upper()}_ROUTE")
    codes.append(f"MD_PLAN_{chosen.check_state.value.upper()}")
    codes.append(f"MD_PLAN_{chosen.effort.value.upper()}_EFFORT")
    if chosen.safety is Safety.CAUTION:
        codes.append("MD_PLAN_CAUTION")

    return NextAction(
        candidate_id=chosen.id,
        target=chosen.target,
        rationale_codes=tuple(codes),
    )
