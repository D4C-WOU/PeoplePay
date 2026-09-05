from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.work_schedule import WorkSchedule

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


class ScheduleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        max_length=100,
    )
    description: str | None = None

    monday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    tuesday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    wednesday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    thursday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    friday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    saturday_hours: Decimal = Field(
        default=0,
        ge=0,
    )
    sunday_hours: Decimal = Field(
        default=0,
        ge=0,
    )

    expected_daily_hours: Decimal = Field(
        default=8,
        ge=0,
    )
    is_active: bool = True


class ScheduleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None

    monday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    tuesday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    wednesday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    thursday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    friday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    saturday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    sunday_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    expected_daily_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    is_active: bool | None = None


@router.get("")
def list_schedules(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "schedules:read",
    )

    return db.scalars(select(WorkSchedule).order_by(WorkSchedule.name)).all()


@router.post(
    "",
    status_code=201,
)
def create_schedule(
    data: ScheduleCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "schedules:write",
    )

    schedule = WorkSchedule(**data.model_dump())

    db.add(schedule)

    try:
        db.commit()
        db.refresh(schedule)
        return schedule

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Work schedule conflicts with existing data",
        ) from exc


@router.get("/{schedule_id}")
def get_schedule(
    schedule_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "schedules:read",
    )

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


@router.patch("/{schedule_id}")
def update_schedule(
    schedule_id: str,
    data: ScheduleUpdate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "schedules:write",
    )

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

    for key, value in updates.items():
        setattr(schedule, key, value)

    try:
        db.commit()
        db.refresh(schedule)
        return schedule

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Work schedule update conflicts with existing data",
        ) from exc
