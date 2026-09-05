from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def list_departments(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:read")

    return list(db.scalars(select(Department).order_by(Department.name)).all())


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=201,
)
def create_department(
    data: DepartmentCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:write")

    existing = db.scalar(select(Department).where(Department.code == data.code))

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Department code already exists",
        )

    department = Department(**data.model_dump())

    db.add(department)

    try:
        db.commit()
        db.refresh(department)
        return department

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Department conflicts with existing data",
        ) from exc


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:read")

    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    return department


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: str,
    data: DepartmentUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:write")

    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(department, field, value)

    try:
        db.commit()
        db.refresh(department)
        return department

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Department update conflicts with existing data",
        ) from exc


@router.post(
    "/{department_id}/activate",
    response_model=DepartmentResponse,
)
def activate_department(
    department_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:write")

    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    department.is_active = True

    db.commit()
    db.refresh(department)

    return department


@router.post(
    "/{department_id}/deactivate",
    response_model=DepartmentResponse,
)
def deactivate_department(
    department_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "departments:write")

    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    department.is_active = False

    db.commit()
    db.refresh(department)

    return department
