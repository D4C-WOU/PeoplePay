import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.routes import attendance, auth, contracts, dashboard, departments, employees, payruns, payslips, salary_rules, salary_structures, schedules, time_off, users
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": settings.APP_NAME}


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"success": False, "message": str(exc), "data": None})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(part) for part in first_error.get("loc", []) if part != "body")
    message = first_error.get("msg", "Invalid request data")
    if field:
        message = f"{field}: {message}"
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": message, "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Something went wrong. Please try again.",
            "data": None,
        },
    )


for router in (
    auth.router, users.router, departments.router, employees.router, contracts.router,
    schedules.router, attendance.router, time_off.router, salary_structures.router,
    salary_rules.router, payruns.router, payslips.router, dashboard.router,
):
    app.include_router(router, prefix="/api/v1")
