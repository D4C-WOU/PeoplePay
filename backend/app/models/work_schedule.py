from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class WorkSchedule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "work_schedules"

    name: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True,
    )

    monday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    tuesday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    wednesday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    thursday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    friday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    saturday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    sunday_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=0,
    nullable=False,
    )

    expected_daily_hours: Mapped[Decimal] = mapped_column(
    Numeric(5, 2),
    default=8,
    nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    nullable=False,
    )

    contracts: Mapped[list["Contract"]] = relationship(
    back_populates="work_schedule",
    )

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
    back_populates="work_schedule",
    )


    @property
    def total_weekly_hours(self) -> Decimal:
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
