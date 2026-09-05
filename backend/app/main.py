import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import attendance, auth, contracts, dashboard, departments, employees, payruns, payslips, salary_rules, salary_structures, schedules, time_off, users
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

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


for router in (
    auth.router, users.router, departments.router, employees.router, contracts.router,
    schedules.router, attendance.router, time_off.router, salary_structures.router,
    salary_rules.router, payruns.router, payslips.router, dashboard.router,
):
    app.include_router(router, prefix="/api/v1")
