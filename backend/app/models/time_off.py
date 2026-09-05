import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class TimeOffStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class TimeOffType(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "time_off_types"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    default_allocation: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
    )

    is_paid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    allocations: Mapped[list["TimeOffAllocation"]] = relationship(
        back_populates="time_off_type",
    )

    requests: Mapped[list["TimeOffRequest"]] = relationship(
        back_populates="time_off_type",
    )


class TimeOffAllocation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "time_off_allocations"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "time_off_type_id",
            "year",
            name="uq_time_off_allocation",
        ),
    )

    employee_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    time_off_type_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "time_off_types.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    allocated_days: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
    )

    used_days: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="time_off_allocations",
    )

    time_off_type: Mapped["TimeOffType"] = relationship(
        back_populates="allocations",
    )


class TimeOffRequest(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "time_off_requests"

    employee_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    time_off_type_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "time_off_types.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    requested_days: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[TimeOffStatus] = mapped_column(
        Enum(TimeOffStatus),
        default=TimeOffStatus.PENDING,
        nullable=False,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="time_off_requests",
    )

    time_off_type: Mapped["TimeOffType"] = relationship(
        back_populates="requests",
    )