from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.payslip import PayslipStatus
from app.schemas.payslip import PayslipResponse
from app.services import payslip_service
from app.services.pdf_service import generate_payslip_pdf

router = APIRouter(
    prefix="/payslips",
    tags=["Payslips"],
)


def _is_employee(user) -> bool:
    return user.role.value == "EMPLOYEE"


def _verify_employee_access(
    user,
    employee_id: str,
) -> None:
    if _is_employee(user):
        if user.employee is None or user.employee.id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )


@router.get(
    "",
    response_model=list[PayslipResponse],
)
def list_payslips(
    employee_id: str | None = None,
    payrun_id: str | None = None,
    status: PayslipStatus | None = None,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None:
            return []

        employee_id = user.employee.id

    else:
        require_permission(
            user,
            "payslips:read",
        )

    return payslip_service.list_payslips(
        db=db,
        employee_id=employee_id,
        payrun_id=payrun_id,
        status=status,
    )


@router.get(
    "/{payslip_id}",
    response_model=PayslipResponse,
)
def get_payslip(
    payslip_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        payslip = payslip_service.get_payslip(
            db=db,
            payslip_id=payslip_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if _is_employee(user):
        _verify_employee_access(
            user,
            payslip.employee_id,
        )
    else:
        require_permission(
            user,
            "payslips:read",
        )

    return payslip


@router.get(
    "/{payslip_id}/pdf",
)
def get_payslip_pdf(
    payslip_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        payslip = payslip_service.get_payslip(
            db=db,
            payslip_id=payslip_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if _is_employee(user):
        _verify_employee_access(
            user,
            payslip.employee_id,
        )
    else:
        require_permission(
            user,
            "payslips:read",
        )

    try:
        pdf_bytes = generate_payslip_pdf(payslip)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    filename = f"payslip-{payslip.employee_number}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
