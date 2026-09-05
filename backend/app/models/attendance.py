import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LATE = "LATE"
    ON_LEAVE = "ON_LEAVE"
    HOLIDAY = "HOLIDAY"


class AttendanceRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "attendance_records"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_attendance_employee_date",
        ),
    )

    employee_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    work_schedule_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "work_schedules.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    check_in: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    check_out: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    expected_hours: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        default=0,
        nullable=False,
    )

    worked_hours: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        default=0,
        nullable=False,
    )

    overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        default=0,
        nullable=False,
    )

    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus),
        default=AttendanceStatus.PRESENT,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="attendance_records",
    )

    work_schedule: Mapped["WorkSchedule | None"] = relationship(
        back_populates="attendance_records",
    )