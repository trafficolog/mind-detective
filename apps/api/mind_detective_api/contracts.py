from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ProposalCopyKey = Literal[
    "reconstruction.clarify_supported_sequence",
    "next_action.check_target",
    "empty.resolve_partial_check",
    "empty.add_supported_place_or_reconstruct",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CaseCreateRequest(StrictModel):
    case_id: str = Field(min_length=1)
    item_label: str = Field(min_length=1)
    now: str = Field(min_length=1)


class CaseValidateRequest(StrictModel):
    case: dict[str, object]


class CaseResponse(StrictModel):
    case: dict[str, object]


class CommandEnvelope(StrictModel):
    command_id: str = Field(min_length=1)
    expected_updated_at: str = Field(min_length=1)
    command_type: Literal[
        "set_mode",
        "add_statement",
        "record_search_check",
        "refine_search_check",
        "reject_next_action",
        "pause",
        "resume",
        "close_found",
        "close_unresolved",
    ]
    now: str = Field(min_length=1)
    payload: dict[str, object]


class CaseCommandRequest(StrictModel):
    case: dict[str, object]
    command: CommandEnvelope


class ProposalModel(StrictModel):
    kind: Literal["next_action", "clarification", "need_more_information", "fallback"]
    candidate_id: str | None = None
    target: str | None = None
    copy_key: ProposalCopyKey
    rationale_codes: list[str] = Field(default_factory=list)
    related_statement_ids: list[str] = Field(default_factory=list)


class ExecutionIdentity(StrictModel):
    version: str = Field(min_length=1)
    kernel_sha256: str = Field(min_length=1)
    generated_sha256: str = Field(min_length=1)
    generator_version: str = Field(min_length=1)


class ExecutionContractResponse(ExecutionIdentity):
    case_schemas: list[str]


class ProposalRequest(StrictModel):
    request_id: str = Field(min_length=1)
    now: str = Field(min_length=1)
    case: dict[str, object]
    mode: Literal["reconstruction", "search"]
    locale: Literal["ru", "en"]
    experimental_arm: Literal["checklist", "assistant"]
    execution_identity: ExecutionIdentity | None = None


class ProposalResponse(StrictModel):
    case: dict[str, object]
    proposal: ProposalModel
    guard_code: str | None = None


class ApiError(StrictModel):
    code: str
    message: str
