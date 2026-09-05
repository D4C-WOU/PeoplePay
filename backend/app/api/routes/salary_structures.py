from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.salary_structure import SalaryStructure
from app.schemas.salary_structure import (
    SalaryStructureCreate,
    SalaryStructureResponse,
    SalaryStructureUpdate,
)

router = APIRouter(
    prefix="/salary/structures",
    tags=["Salary Structures"],
)


@router.get(
    "",
    response_model=list[SalaryStructureResponse],
)
def list_salary_structures(
    active_only: bool = False,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "salary:read")

    stmt = select(SalaryStructure).order_by(SalaryStructure.name)

    if active_only:
        stmt = stmt.where(SalaryStructure.is_active.is_(True))

    return db.scalars(stmt).all()


@router.post(
    "",
    response_model=SalaryStructureResponse,
    status_code=201,
)
def create_salary_structure(
    data: SalaryStructureCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "salary:write")

    existing = db.scalar(
        select(SalaryStructure).where(SalaryStructure.code == data.code)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Salary structure code already exists",
        )

    structure = SalaryStructure(**data.model_dump())

    db.add(structure)

    try:
        db.commit()
        db.refresh(structure)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Salary structure code already exists",
        )

    return structure


@router.get(
    "/{structure_id}",
    response_model=SalaryStructureResponse,
)
def get_salary_structure(
    structure_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "salary:read")

    structure = db.get(
        SalaryStructure,
        structure_id,
    )

    if structure is None:
        raise HTTPException(
            status_code=404,
            detail="Salary structure not found",
        )

    return structure


@router.patch(
    "/{structure_id}",
    response_model=SalaryStructureResponse,
)
def update_salary_structure(
    structure_id: str,
    data: SalaryStructureUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "salary:write")

    structure = db.get(
        SalaryStructure,
        structure_id,
    )

    if structure is None:
        raise HTTPException(
            status_code=404,
            detail="Salary structure not found",
        )

    updates = data.model_dump(exclude_unset=True)

    if "code" in updates and updates["code"] != structure.code:
        existing = db.scalar(
            select(SalaryStructure).where(
                SalaryStructure.code == updates["code"],
                SalaryStructure.id != structure_id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Salary structure code already exists",
            )

    for field, value in updates.items():
        setattr(structure, field, value)

    try:
        db.commit()
        db.refresh(structure)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Salary structure update violates a database constraint",
        )

    return structure
