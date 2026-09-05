from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.time_off import TimeOffStatus


class TimeOffTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    default_allocation: Decimal = Field(
        default=0,
        ge=0,
    )
    is_paid: bool = True
    is_active: bool = True


class TimeOffTypeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None
    default_allocation: Decimal | None = Field(
        default=None,
        ge=0,
    )
    is_paid: bool | None = None
    is_active: bool | None = None


class TimeOffTypeResponse(TimeOffTypeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str


class AllocationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: str
    time_off_type_id: str
    year: int = Field(
        ge=2000,
        le=2100,
    )
    allocated_days: Decimal = Field(
        ge=0,
    )


class AllocationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allocated_days: Decimal = Field(ge=0)


class AllocationResponse(AllocationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    used_days: Decimal


class TimeOffRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: str
    time_off_type_id: str
    start_date: date
    end_date: date
    requested_days: Decimal | None = Field(
        default=None,
        gt=0,
    )
    reason: str | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")

        return self


class TimeOffRequestResponse(TimeOffRequestCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requested_days: Decimal
    status: TimeOffStatus
    reviewed_by: str | None
    reviewed_at: datetime | None
