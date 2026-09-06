from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.attendance import (
    AttendanceRecord,
    AttendanceStatus,
)
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.schemas.pagination import Page
from app.services import attendance_service

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
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
    response_model=list[AttendanceResponse] | Page[AttendanceResponse],
)
def list_records(
    employee_id: str | None = None,
    attendance_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status: AttendanceStatus | None = None,
    page: int | None = Query(default=None, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None:
            if page is not None:
                return Page(items=[], total=0, page=page, page_size=page_size, pages=0)
            return []

        employee_id = user.employee.id

    else:
        require_permission(
            user,
            "attendance:read",
        )

    try:
        return attendance_service.list_attendance(
            db=db,
            employee_id=employee_id,
            attendance_date=attendance_date,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            page_size=page_size,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=201,
)
def create(
    data: AttendanceCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )
        data.employee_id = user.employee.id
    else:
        require_permission(
            user,
            "attendance:write",
        )

    try:
        return attendance_service.create_attendance(
            db=db,
            data=data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get(
    "/{record_id}",
    response_model=AttendanceResponse,
)
def get(
    record_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    record = db.get(
        AttendanceRecord,
        record_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found",
        )

    if _is_employee(user):
        _verify_employee_access(
            user,
            record.employee_id,
        )
    else:
        require_permission(
            user,
            "attendance:read",
        )

    return record


@router.patch(
    "/{record_id}",
    response_model=AttendanceResponse,
)
def update(
    record_id: str,
    data: AttendanceUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    record = db.get(
        AttendanceRecord,
        record_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found",
        )

    if _is_employee(user):
        _verify_employee_access(
            user,
            record.employee_id,
        )
    else:
        require_permission(
            user,
            "attendance:write",
        )

    try:
        return attendance_service.update_attendance(
            db=db,
            record=record,
            data=data.model_dump(exclude_unset=True),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )
