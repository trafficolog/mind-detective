from __future__ import annotations

LOCAL_EXECUTION_CONTRACT = "mind-detective-local-execution/v1"
GENERATOR_VERSION = "local-execution-generator/v1"

SUPPORTED_CASE_SCHEMAS: tuple[str, ...] = ("mind-detective-case/v2",)
SUPPORTED_COMMAND_TYPES: tuple[str, ...] = (
    "set_mode",
    "record_free_account",
    "add_statement",
    "record_search_check",
    "refine_search_check",
    "reject_next_action",
    "pause",
    "resume",
    "close_found",
    "close_unresolved",
)

STABLE_LOCAL_ERRORS: frozenset[str] = frozenset(
    {
        "MD_WEB_STALE_COMMAND",
        "MD_WEB_FORBIDDEN_FIELD",
        "MD_WEB_COMMAND_PAYLOAD",
        "MD_WEB_COMMAND_ID_CONFLICT",
        "MD_WEB_CASE_ID_CONFLICT",
        "MD_WEB_EXECUTION_CONTRACT_MISMATCH",
        "MD_RECON_MODE_REQUIRED",
        "MD_RECON_FREE_ACCOUNT_REQUIRED",
        "MD_RECON_FREE_ACCOUNT_EXISTS",
    }
)
