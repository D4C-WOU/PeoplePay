from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.work_schedule import WorkSchedule
from app.schemas.work_schedule import (
    WorkScheduleCreate,
    WorkScheduleResponse,
    WorkScheduleUpdate,
)

router = APIRouter(
    prefix="/schedules",
    tags=["Working Schedules"],
)


@router.get(
    "",
    response_model=list[WorkScheduleResponse],
)
def list_schedules(
    active_only: bool = False,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "schedules:read")

    stmt = select(WorkSchedule).order_by(WorkSchedule.created_at.desc())

    if active_only:
        stmt = stmt.where(WorkSchedule.is_active.is_(True))

    return list(db.scalars(stmt).all())


@router.post(
    "",
    response_model=WorkScheduleResponse,
    status_code=201,
)
def create_schedule(
    data: WorkScheduleCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "schedules:write")

    schedule = WorkSchedule(**data.model_dump())

    db.add(schedule)

    try:
        db.commit()
        db.refresh(schedule)
        return schedule

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Unable to create work schedule",
        )


@router.get(
    "/{schedule_id}",
    response_model=WorkScheduleResponse,
)
def get_schedule(
    schedule_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "schedules:read")

    schedule = db.get(
        WorkSchedule,
        schedule_id,
    )

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Work schedule not found",
        )

    return schedule


@router.patch(
    "/{schedule_id}",
    response_model=WorkScheduleResponse,
)
def update_schedule(
    schedule_id: str,
    data: WorkScheduleUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "schedules:write")

    schedule = db.get(
        WorkSchedule,
        schedule_id,
    )

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Work schedule not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(schedule, field, value)

    try:
        db.commit()
        db.refresh(schedule)
        return schedule

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Unable to update work schedule",
        )
