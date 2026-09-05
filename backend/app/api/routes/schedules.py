from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.work_schedule import WorkSchedule

router=APIRouter(prefix="/schedules", tags=["Schedules"])

class ScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    monday_hours: Decimal = Field(default=0, ge=0)
    tuesday_hours: Decimal = Field(default=0, ge=0)
    wednesday_hours: Decimal = Field(default=0, ge=0)
    thursday_hours: Decimal = Field(default=0, ge=0)
    friday_hours: Decimal = Field(default=0, ge=0)
    saturday_hours: Decimal = Field(default=0, ge=0)
    sunday_hours: Decimal = Field(default=0, ge=0)
    expected_daily_hours: Decimal = Field(default=8, ge=0)
    is_active: bool = True

class ScheduleUpdate(BaseModel):
    name: str | None=None
    description: str | None=None
    expected_daily_hours: Decimal | None=Field(default=None, ge=0)
    is_active: bool | None=None

@router.get("")
def list_schedules(user=Depends(get_current_active_user), db:Session=Depends(get_db)):
    require_permission(user,"schedules:read"); return db.scalars(select(WorkSchedule).order_by(WorkSchedule.name)).all()

@router.post("",status_code=201)
def create(data:ScheduleCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"schedules:write"); obj=WorkSchedule(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/{schedule_id}")
def get(schedule_id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"schedules:read"); obj=db.get(WorkSchedule,schedule_id)
    if not obj: raise HTTPException(404,"Work schedule not found")
    return obj

@router.patch("/{schedule_id}")
def update(schedule_id:str,data:ScheduleUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"schedules:write"); obj=db.get(WorkSchedule,schedule_id)
    if not obj: raise HTTPException(404,"Work schedule not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj
