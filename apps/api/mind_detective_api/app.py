from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .commands import execute_command
from .contracts import (
    CaseCommandRequest,
    CaseCreateRequest,
    CaseResponse,
    CaseValidateRequest,
    ProposalRequest,
    ProposalResponse,
)
from .core_bridge import create_case_payload, validate_or_migrate_case_payload
from .proposals import build_proposal

_DOMAIN_ERROR = "MD_WEB_DOMAIN_ERROR"

app = FastAPI(title="MIND Detective API", version="0.2.0")


def _error_response(code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=422, content={"code": code, "message": message})


def _domain_error(exc: ValueError) -> JSONResponse:
    return _error_response(str(getattr(exc, "code", _DOMAIN_ERROR)), str(exc))


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
    except ValueError as exc:
        return _domain_error(exc)
