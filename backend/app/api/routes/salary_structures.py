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
    tags=["Salary"],
)


@router.get(
    "",
    response_model=list[SalaryStructureResponse],
)
def list_structures(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "salary:read")

    return db.scalars(select(SalaryStructure).order_by(SalaryStructure.name)).all()


@router.post(
    "",
    response_model=SalaryStructureResponse,
    status_code=201,
)
def create_structure(
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
        return structure

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Salary structure conflicts with an existing structure",
        ) from exc


@router.get(
    "/{structure_id}",
    response_model=SalaryStructureResponse,
)
def get_structure(
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
def update_structure(
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

    for key, value in updates.items():
        setattr(structure, key, value)

    if "code" in updates:
        duplicate = db.scalar(
            select(SalaryStructure).where(
                SalaryStructure.id != structure.id,
                SalaryStructure.code == structure.code,
            )
        )

        if duplicate:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Salary structure code already exists",
            )

    try:
        db.commit()
        db.refresh(structure)
        return structure

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Salary structure conflicts with an existing structure",
        ) from exc
