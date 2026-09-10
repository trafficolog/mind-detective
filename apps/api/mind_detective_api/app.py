from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .commands import execute_command
from .contracts import (
    CaseCommandRequest,
    CaseCreateRequest,
    CaseResponse,
    CaseValidateRequest,
    ExecutionContractResponse,
    ProposalRequest,
    ProposalResponse,
)
from .core_bridge import create_case_payload, validate_or_migrate_case_payload
from .execution_contract import ExecutionContractMismatch, execution_contract
from .proposals import build_proposal

_DOMAIN_ERROR = "MD_WEB_DOMAIN_ERROR"
_DEFAULT_WEB_ORIGIN = "http://127.0.0.1:3000"


def _web_origins() -> list[str]:
    configured = os.environ.get("MIND_DETECTIVE_WEB_ORIGINS", _DEFAULT_WEB_ORIGIN)
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(title="MIND Detective API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_web_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def _error_response(code: str, message: str, status_code: int = 422) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})


def _domain_error(exc: ValueError) -> JSONResponse:
    return _error_response(str(getattr(exc, "code", _DOMAIN_ERROR)), str(exc))


@app.get("/api/v1/execution/contract", response_model=ExecutionContractResponse)
def get_execution_contract() -> ExecutionContractResponse:
    return execution_contract()


@app.post("/api/v1/case/create", response_model=CaseResponse)
def create_case(request: CaseCreateRequest) -> CaseResponse:
    return CaseResponse(
        case=create_case_payload(request.case_id, request.item_label, request.now),
    )


@app.post("/api/v1/case/validate", response_model=CaseResponse)
def validate_case(request: CaseValidateRequest) -> CaseResponse | JSONResponse:
    try:
        payload = validate_or_migrate_case_payload(request.case)
    except ValueError as exc:
        return _domain_error(exc)
    return CaseResponse(case=payload)


@app.post("/api/v1/case/command", response_model=CaseResponse)
def command_case(request: CaseCommandRequest) -> CaseResponse | JSONResponse:
    try:
        payload = execute_command(request.case, request.command)
    except ValueError as exc:
        return _domain_error(exc)
    return CaseResponse(case=payload)


@app.post("/api/v1/proposal/next", response_model=ProposalResponse)
async def next_proposal(request: ProposalRequest) -> ProposalResponse | JSONResponse:
    try:
        return await build_proposal(request)
    except ExecutionContractMismatch as exc:
        return _error_response(exc.code, str(exc), status_code=409)
    except ValueError as exc:
        return _domain_error(exc)
