from datetime import datetime, timezone
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.logging import get_request_id
from app.common.schemas import APIErrorDetail, APIErrorResponse


def _error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: str,
) -> JSONResponse:
    request_id = (
        getattr(request.state, "request_id", None)
        or get_request_id()
        or request.headers.get("X-Request-ID")
        or str(uuid.uuid4())
    )
    error_payload = APIErrorResponse(
        status="error",
        statusCode=status_code,
        error=APIErrorDetail(
            code=error_code,
            message=message,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        ),
        requestId=request_id,
    )
    request.state.error_code = error_code
    request.state.error_message = message
    request.state.error_details = details
    return JSONResponse(status_code=status_code, content=error_payload.model_dump())
