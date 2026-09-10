from __future__ import annotations

from typing import Protocol

from .checklist import build_checklist_proposal
from .contracts import ProposalModel, ProposalRequest, ProposalResponse
from .core_bridge import validate_or_migrate_case_payload

from scripts.controller import CaseController
from scripts.guard import InteractionMode as GuardMode
from scripts.guard import lint_candidate
from scripts.journal import JournalAuthor, JournalEntry, JournalMode
from scripts.statements import StatementSource
from scripts.store import case_from_dict, case_to_dict


class ProposalClient(Protocol):
    async def propose(self, case: dict[str, object], mode: str) -> ProposalModel: ...


def _guard_text(proposal: ProposalModel) -> str:
    parts = [proposal.target or "", proposal.copy_key]
    parts.extend(proposal.rationale_codes)
    return " ".join(part for part in parts if part)


def _known_reconstruction_locations(case_payload: dict[str, object]) -> set[str]:
    case = case_from_dict(case_payload)
    return {
        statement.original_text
        for statement in case.statements
        if statement.source is StatementSource.USER
    }


def _append_guard_event(
    case_payload: dict[str, object],
    request: ProposalRequest,
) -> dict[str, object]:
    case = case_from_dict(case_payload)
    entry_id = f"guard-{request.request_id}"
    if any(entry.id == entry_id for entry in case.interaction_journal):
        return case_to_dict(case)
    event = JournalEntry(
        id=entry_id,
        author=JournalAuthor.SYSTEM,
        mode=JournalMode.SYSTEM,
        entry_type="ai_guard_blocked",
        text="guard.ai_proposal_blocked",
        created_at=request.now,
    )
    updated = CaseController().append_journal_entry(case, event, request.now)
    return case_to_dict(updated)


async def build_assistant_proposal(
    request: ProposalRequest,
    client: ProposalClient,
) -> ProposalResponse:
    canonical = validate_or_migrate_case_payload(request.case)
    proposed = await client.propose(canonical, request.mode)
    guard_mode = (
        GuardMode.RECONSTRUCTION
        if request.mode == "reconstruction"
        else GuardMode.SEARCH_PLANNING
    )
    guard = lint_candidate(
        _guard_text(proposed),
        mode=guard_mode,
        known_locations=_known_reconstruction_locations(canonical),
    )
    if guard.allowed:
        return ProposalResponse(case=canonical, proposal=proposed)

    fallback = build_checklist_proposal(canonical, request.mode)
    updated = _append_guard_event(canonical, request)
    return ProposalResponse(
        case=updated,
        proposal=fallback,
        guard_code=guard.codes[0],
    )


async def build_proposal(
    request: ProposalRequest,
    client: ProposalClient | None = None,
) -> ProposalResponse:
    canonical = validate_or_migrate_case_payload(request.case)
    if request.experimental_arm == "checklist":
        return ProposalResponse(
            case=canonical,
            proposal=build_checklist_proposal(canonical, request.mode),
        )
    if client is None:
        from .litellm_provider import LiteLLMProposalClient

        client = LiteLLMProposalClient.from_env()
    return await build_assistant_proposal(request, client)
