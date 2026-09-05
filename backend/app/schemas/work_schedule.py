from datetime import time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.work_schedule_day import DayOfWeek


class WorkScheduleDayCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day_of_week: DayOfWeek
    start_time: time | None = None
    end_time: time | None = None
    break_minutes: int = Field(default=0, ge=0, le=1440)

    @model_validator(mode="after")
    def validate_day(self):
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError("start_time and end_time must be provided together")
        if self.start_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.start_time is not None:
            minutes = (self.end_time.hour * 60 + self.end_time.minute) - (
                self.start_time.hour * 60 + self.start_time.minute
            )
            if self.break_minutes >= minutes:
                raise ValueError(
                    "break_minutes must be less than scheduled working minutes"
                )
        return self


class WorkScheduleDayResponse(WorkScheduleDayCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class WorkScheduleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    days: list[WorkScheduleDayCreate] = Field(default_factory=list)
    # Legacy fields accepted for existing clients/data.
    monday_hours: Decimal = Field(default=0, ge=0, le=24)
    tuesday_hours: Decimal = Field(default=0, ge=0, le=24)
    wednesday_hours: Decimal = Field(default=0, ge=0, le=24)
    thursday_hours: Decimal = Field(default=0, ge=0, le=24)
    friday_hours: Decimal = Field(default=0, ge=0, le=24)
    saturday_hours: Decimal = Field(default=0, ge=0, le=24)
    sunday_hours: Decimal = Field(default=0, ge=0, le=24)
    expected_daily_hours: Decimal = Field(default=8, ge=0, le=24)
    is_active: bool = True

    @model_validator(mode="after")
    def unique_days(self):
        days = [day.day_of_week for day in self.days]
        if len(days) != len(set(days)):
            raise ValueError("A schedule cannot contain the same day more than once")
        return self


class WorkScheduleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    days: list[WorkScheduleDayCreate] | None = None
    monday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    tuesday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    wednesday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    thursday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    friday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    saturday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    sunday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    expected_daily_hours: Decimal | None = Field(default=None, ge=0, le=24)
    is_active: bool | None = None

    @model_validator(mode="after")
    def unique_days(self):
        if self.days is not None:
            days = [day.day_of_week for day in self.days]
            if len(days) != len(set(days)):
                raise ValueError(
                    "A schedule cannot contain the same day more than once"
                )
        return self


class WorkScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str | None
    days: list[WorkScheduleDayResponse] = Field(default_factory=list)
    monday_hours: Decimal
    tuesday_hours: Decimal
    wednesday_hours: Decimal
    thursday_hours: Decimal
    friday_hours: Decimal
    saturday_hours: Decimal
    sunday_hours: Decimal
    expected_daily_hours: Decimal
    is_active: bool
    total_weekly_hours: Decimal
