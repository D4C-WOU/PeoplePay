from decimal import Decimal
from datetime import datetime

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class WorkSchedule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "work_schedules"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Legacy hour fields remain so existing records continue to work. New schedules
    # should use work_schedule_days (day/start/end/break).
    monday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    tuesday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    wednesday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    thursday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    friday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    saturday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    sunday_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    expected_daily_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=8, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    contracts: Mapped[list["Contract"]] = relationship(back_populates="work_schedule")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="work_schedule"
    )
    days: Mapped[list["WorkScheduleDay"]] = relationship(
        back_populates="work_schedule",
        cascade="all, delete-orphan",
        order_by="WorkScheduleDay.day_of_week",
    )

    @property
    def total_weekly_hours(self) -> Decimal:
        if self.days:
            total = Decimal("0")
            for day in self.days:
                if day.start_time is None or day.end_time is None:
                    continue
                start = datetime.combine(datetime.today().date(), day.start_time)
                end = datetime.combine(datetime.today().date(), day.end_time)
                if end < start:
                    end = end.replace(day=end.day + 1)
                minutes = Decimal(str((end - start).total_seconds() / 60)) - Decimal(
                    day.break_minutes
                )
                total += max(Decimal("0"), minutes) / Decimal("60")
            return total.quantize(Decimal("0.01"))

        hours = (
            self.monday_hours
            + self.tuesday_hours
            + self.wednesday_hours
            + self.thursday_hours
            + self.friday_hours
            + self.saturday_hours
            + self.sunday_hours
        )
        return Decimal(str(hours)).quantize(Decimal("0.01"))
