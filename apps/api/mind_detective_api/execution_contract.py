from __future__ import annotations

import json
from functools import lru_cache

from .contracts import ExecutionContractResponse, ExecutionIdentity
from .runtime_paths import resolve_execution_metadata_path

_MISMATCH_CODE = "MD_WEB_EXECUTION_CONTRACT_MISMATCH"


class ExecutionContractMismatch(ValueError):
    code = _MISMATCH_CODE


@lru_cache(maxsize=1)
def execution_contract() -> ExecutionContractResponse:
    try:
        metadata_path = resolve_execution_metadata_path()
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("MD_WEB_EXECUTION_CONTRACT_METADATA_UNAVAILABLE") from exc
    if not isinstance(raw, dict):
        raise RuntimeError("MD_WEB_EXECUTION_CONTRACT_METADATA_INVALID")
    try:
        return ExecutionContractResponse.model_validate(raw)
    except ValueError as exc:
        raise RuntimeError("MD_WEB_EXECUTION_CONTRACT_METADATA_INVALID") from exc


def require_matching_execution_identity(identity: ExecutionIdentity | None) -> None:
    if identity is None:
        raise ExecutionContractMismatch("execution identity is required for assistant proposals")
    expected = execution_contract()
    fields = ("version", "kernel_sha256", "generated_sha256", "generator_version")
    if any(getattr(identity, field) != getattr(expected, field) for field in fields):
        raise ExecutionContractMismatch("client execution contract does not match server execution contract")
