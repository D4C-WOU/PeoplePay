from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator

from app.models.time_off import TimeOffStatus


class TimeOffTypeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    default_allocation: Decimal = Field(default=0, ge=0)
    is_paid: bool = True
    is_active: bool = True


class TimeOffTypeResponse(TimeOffTypeCreate):
    model_config = {"from_attributes": True}
    id: str


class AllocationCreate(BaseModel):
    employee_id: str
    time_off_type_id: str
    year: int = Field(ge=2000, le=2100)
    allocated_days: Decimal = Field(ge=0)


class AllocationResponse(AllocationCreate):
    model_config = {"from_attributes": True}
    id: str
    used_days: Decimal


class TimeOffRequestCreate(BaseModel):
    employee_id: str
    time_off_type_id: str
    start_date: date
    end_date: date
    requested_days: Decimal = Field(gt=0)
    reason: str | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class TimeOffRequestResponse(TimeOffRequestCreate):
    model_config = {"from_attributes": True}
    id: str
    status: TimeOffStatus
    reviewed_by: str | None
    reviewed_at: datetime | None
