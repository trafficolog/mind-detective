from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .contracts import CaseCreateRequest, CaseResponse, CaseValidateRequest
from .core_bridge import create_case_payload, validate_or_migrate_case_payload

_REPO_ROOT_IMPORT_ERROR = "MD_WEB_DOMAIN_ERROR"

app = FastAPI(title="MIND Detective API", version="0.2.0")


def _error_response(code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=422, content={"code": code, "message": message})


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
        code = getattr(exc, "code", _REPO_ROOT_IMPORT_ERROR)
        return _error_response(str(code), str(exc))
    return CaseResponse(case=payload)
