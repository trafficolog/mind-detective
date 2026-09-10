from __future__ import annotations

from .contracts import ProposalModel
from .core_bridge import validate_or_migrate_case_payload

from scripts.planner import select_next_action
from scripts.search_log import SearchResult
from scripts.store import case_from_dict


def build_checklist_proposal(
    case_payload: dict[str, object],
    mode: str,
) -> ProposalModel:
    case = case_from_dict(validate_or_migrate_case_payload(case_payload))

    if mode == "reconstruction":
        related = [statement.id for statement in case.statements[-3:]]
        return ProposalModel(
            kind="clarification",
            copy_key="reconstruction.clarify_supported_sequence",
            related_statement_ids=related,
        )

    rejected = {feedback.candidate_id for feedback in case.action_feedback}
    candidates = [candidate for candidate in case.candidates if candidate.id not in rejected]
    action = select_next_action(candidates)
    if action is not None:
        return ProposalModel(
            kind="next_action",
            candidate_id=action.candidate_id,
            target=action.target,
            copy_key="next_action.check_target",
            rationale_codes=list(action.rationale_codes),
        )

    for check in reversed(case.search_checks):
        if check.result in {SearchResult.PARTIAL, SearchResult.INACCESSIBLE} or check.inaccessible_parts:
            return ProposalModel(
                kind="clarification",
                target=check.target,
                copy_key="empty.resolve_partial_check",
            )

    return ProposalModel(
        kind="need_more_information",
        copy_key="empty.add_supported_place_or_reconstruct",
    )
