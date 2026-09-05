from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.department import Department

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


class DepartmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        max_length=150,
    )
    code: str = Field(
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    is_active: bool | None = None


@router.get("")
def list_departments(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "departments:read",
    )

    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post(
    "",
    status_code=201,
)
def create_department(
    data: DepartmentCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "departments:write",
    )

    existing = db.scalar(select(Department).where(Department.code == data.code))

    if existing:
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
            detail="Department conflicts with an existing department",
        ) from exc


@router.get("/{department_id}")
def get_department(
    department_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "departments:read",
    )

    department = db.get(
        Department,
        department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    return department


@router.patch("/{department_id}")
def update_department(
    department_id: str,
    data: DepartmentUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "departments:write",
    )

    department = db.get(
        Department,
        department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(department, key, value)

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
