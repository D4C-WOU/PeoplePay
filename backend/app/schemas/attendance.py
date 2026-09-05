from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    employee_id: str
    work_schedule_id: str | None = None
    attendance_date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    expected_hours: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: str | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if (
            self.check_in is not None
            and self.check_out is not None
            and self.check_out < self.check_in
        ):
            raise ValueError("check_out cannot be before check_in")

        return self


class AttendanceUpdate(BaseModel):
    check_in: datetime | None = None
    check_out: datetime | None = None
    expected_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )
    status: AttendanceStatus | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if (
            self.check_in is not None
            and self.check_out is not None
            and self.check_out < self.check_in
        ):
            raise ValueError("check_out cannot be before check_in")

        return self


class AttendanceResponse(AttendanceCreate):
    id: str
    worked_hours: Decimal
    overtime_hours: Decimal
