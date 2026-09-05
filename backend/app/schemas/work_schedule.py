from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WorkScheduleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    monday_hours: Decimal = Field(default=0, ge=0, le=24)
    tuesday_hours: Decimal = Field(default=0, ge=0, le=24)
    wednesday_hours: Decimal = Field(default=0, ge=0, le=24)
    thursday_hours: Decimal = Field(default=0, ge=0, le=24)
    friday_hours: Decimal = Field(default=0, ge=0, le=24)
    saturday_hours: Decimal = Field(default=0, ge=0, le=24)
    sunday_hours: Decimal = Field(default=0, ge=0, le=24)

    expected_daily_hours: Decimal = Field(
        default=8,
        ge=0,
        le=24,
    )

    is_active: bool = True


class WorkScheduleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    monday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    tuesday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    wednesday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    thursday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    friday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    saturday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    sunday_hours: Decimal | None = Field(default=None, ge=0, le=24)

    expected_daily_hours: Decimal | None = Field(
        default=None,
        ge=0,
        le=24,
    )

    is_active: bool | None = None


class WorkScheduleResponse(WorkScheduleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    total_weekly_hours: Decimal
