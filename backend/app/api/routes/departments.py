from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.department import Department

router = APIRouter(prefix="/departments", tags=["Departments"])


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


@router.get("")
def list_departments(user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    require_permission(user, "departments:read")
    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post("", status_code=201)
def create(data: DepartmentCreate, user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    require_permission(user, "departments:write")
    if db.scalar(select(Department).where(Department.code == data.code)): raise HTTPException(409, "Department code already exists")
    obj=Department(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/{department_id}")
def get(department_id: str, user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    require_permission(user, "departments:read")
    obj=db.get(Department, department_id)
    if not obj: raise HTTPException(404, "Department not found")
    return obj


@router.patch("/{department_id}")
def update(department_id: str, data: DepartmentUpdate, user=Depends(get_current_active_user), db: Session=Depends(get_db)):
    require_permission(user, "departments:write")
    obj=db.get(Department, department_id)
    if not obj: raise HTTPException(404, "Department not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj
