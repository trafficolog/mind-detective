from __future__ import annotations

from .contracts import ProposalModel
from .core_bridge import validate_or_migrate_case_payload

from scripts.portable_kernel import build_checklist_proposal_json


def build_checklist_proposal(
    case_payload: dict[str, object],
    mode: str,
) -> ProposalModel:
    canonical = validate_or_migrate_case_payload(case_payload)
    return ProposalModel.model_validate(build_checklist_proposal_json(canonical, mode))
