from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.employee import EmployeeStatus
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services import employee_service

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    department_id: str | None = None,
    status: EmployeeStatus | None = None,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "employees:read")

    return employee_service.list_employees(
        db=db,
        department_id=department_id,
        status=status,
    )


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=201,
)
def create_employee(
    data: EmployeeCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "employees:write")

    try:
        return employee_service.create_employee(
            db=db,
            data=data.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "employees:read")

    try:
        return employee_service.get_employee(
            db=db,
            employee_id=employee_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "employees:write")

    try:
        return employee_service.update_employee(
            db=db,
            employee_id=employee_id,
            data=data.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        if str(exc) == "Employee not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def terminate_employee(
    employee_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "employees:write")

    try:
        return employee_service.terminate_employee(
            db=db,
            employee_id=employee_id,
        )
    except ValueError as exc:
        if str(exc) == "Employee not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )
