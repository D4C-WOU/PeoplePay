import enum
from datetime import time

from sqlalchemy import Enum, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import UUIDMixin


class DayOfWeek(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class WorkScheduleDay(UUIDMixin, Base):
    __tablename__ = "work_schedule_days"

    __table_args__ = (
        UniqueConstraint(
            "work_schedule_id", "day_of_week", name="uq_work_schedule_day"
        ),
    )

    work_schedule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_schedules.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek), nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    work_schedule: Mapped["WorkSchedule"] = relationship(back_populates="days")
