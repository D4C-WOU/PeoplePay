from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.payrun import PayrunStatus
from app.schemas.payrun import (
    PayrunCreate,
    PayrunResponse,
)
from app.schemas.pagination import Page
from app.services import payroll_service
from app.services.email_service import send_payrun_payslips
from app.services.validation_service import validate_payrun

router = APIRouter(
    prefix="/payruns",
    tags=["Payroll"],
)


@router.get(
    "",
    response_model=list[PayrunResponse] | Page[PayrunResponse],
)
def list_payruns(
    status: PayrunStatus | None = None,
    page: int | None = Query(default=None, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:read",
    )

    return payroll_service.list_payruns(
        db,
        status,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=PayrunResponse,
    status_code=201,
)
def create_payrun(
    data: PayrunCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:write",
    )

    try:
        return payroll_service.create_payrun(
            db,
            **data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.get(
    "/{payrun_id}",
    response_model=PayrunResponse,
)
def get_payrun(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:read",
    )

    try:
        return payroll_service.get_payrun(
            db,
            payrun_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{payrun_id}/validation",
)
def validate(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "payroll:read")
    try:
        payrun = payroll_service.get_payrun(db, payrun_id)
        return validate_payrun(db, payrun)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{payrun_id}/process",
    response_model=PayrunResponse,
)
def process_payrun(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:write",
    )

    try:
        payrun = payroll_service.get_payrun(
            db,
            payrun_id,
        )

        return payroll_service.process_payrun(
            db,
            payrun,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Payrun not found":
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=409,
            detail=message,
        ) from exc


@router.post(
    "/{payrun_id}/finalize",
    response_model=PayrunResponse,
)
def finalize_payrun(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:write",
    )

    try:
        payrun = payroll_service.get_payrun(
            db,
            payrun_id,
        )

        return payroll_service.finalize_payrun(
            db,
            payrun,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Payrun not found":
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=409,
            detail=message,
        ) from exc


@router.post(
    "/{payrun_id}/cancel",
    response_model=PayrunResponse,
)
def cancel_payrun(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "payroll:write",
    )

    try:
        payrun = payroll_service.get_payrun(
            db,
            payrun_id,
        )

        return payroll_service.cancel_payrun(
            db,
            payrun,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Payrun not found":
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=409,
            detail=message,
        ) from exc


@router.post(
    "/{payrun_id}/send-payslips",
)
def send_payslips(
    payrun_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "payroll:write")

    try:
        payrun = payroll_service.get_payrun(db, payrun_id)
        result = send_payrun_payslips(db, payrun)
        return result
    except ValueError as exc:
        message = str(exc)
        status = 404 if message == "Payrun not found" else 409
        raise HTTPException(status_code=status, detail=message) from exc
