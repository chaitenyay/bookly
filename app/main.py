import uuid
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.books.routes import book_router
from app.auth.routes import auth_router
from app.author.routes import author_router
from app.members.routes import member_router
from app.publisher.routes import publisher_router
from app.loans.routes import loan_router
from contextlib import asynccontextmanager
from app.common.error_repsonses import _error_response
from app.common.logging import clear_request_id, set_request_id, setup_logging
from app.db.main import init_db
from app.config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here (e.g., connect to the database)
    print("Starting up...")
    await init_db()  # Initialize the database (create tables, etc.)    
    yield
    # Perform any shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")

version = "v1"  # Define API version

app = FastAPI(
    title="Bookly API",
    description="A simple API for managing books.",
    version=version,
    lifespan=lifespan
) 
logger = setup_logging()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


crud_prefixes = (
    f"/api/{version}/auth",
    f"/api/{version}/books",
    f"/api/{version}/authors",
    f"/api/{version}/members",
    f"/api/{version}/publishers",
    f"/api/{version}/loans",
)


def _is_crud_request(request: Request) -> bool:
    return request.url.path.startswith(crud_prefixes)


@app.middleware("http")
async def request_context_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    set_request_id(request_id)

    start_time = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        logger.exception(
            "Request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
            },
        )
        clear_request_id()
        raise

    response.headers["X-Request-ID"] = request_id
    duration_ms = round((perf_counter() - start_time) * 1000, 2)
    log_payload = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    if response.status_code >= 400:
        log_payload["error_code"] = getattr(request.state, "error_code", None)
        log_payload["error_message"] = getattr(request.state, "error_message", None)
        log_payload["error_details"] = getattr(request.state, "error_details", None)
        logger.error("Request failed", extra=log_payload)
    else:
        logger.info("Request completed", extra=log_payload)
    clear_request_id()
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if not _is_crud_request(request):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    validation_errors = exc.errors()
    first_error = validation_errors[0] if validation_errors else {}
    raw_error_code = str(first_error.get("type", "validation_error")).upper().replace(".", "_")
    error_code = "MISSING_DATA" if raw_error_code == "MISSING" else raw_error_code
    details = "; ".join(
        f"{'.'.join(map(str, err.get('loc', [])))}: {err.get('msg', 'Invalid value')}"
        for err in validation_errors
    )
    return _error_response(
        request=request,
        status_code=422,
        error_code=error_code,
        message="Request validation failed",
        details=details or "Invalid request input",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if not _is_crud_request(request):
        detail = exc.detail if exc.detail else "HTTP error"
        return JSONResponse(status_code=exc.status_code, content={"detail": detail}, headers=exc.headers)

    detail_text = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return _error_response(
        request=request,
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message="Request failed",
        details=detail_text,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if not _is_crud_request(request):
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    return _error_response(
        request=request,
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="Unexpected server error",
        details="An internal server error occurred.",
    )


# @app.get("/")
# def home():
#     d = Config.DATABASE_URL
#     return f"Bookly - A Book Library Service. Database URL: {d}"

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])  # Include the book router to handle book-related endpoints
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])  # Include the auth router to handle authentication-related endpoints
app.include_router(author_router, prefix=f"/api/{version}/authors", tags=["Authors"])  # Include the author router to handle author-related endpoints
app.include_router(member_router, prefix=f"/api/{version}/members", tags=["Members"])  # Include the member router to handle member-related endpoints
app.include_router(publisher_router, prefix=f"/api/{version}/publishers", tags=["Publishers"])  # Include the publisher router to handle publisher-related endpoints
app.include_router(loan_router, prefix=f"/api/{version}/loans", tags=["Loans"])  # Include the loan router to handle loan-related endpoints
