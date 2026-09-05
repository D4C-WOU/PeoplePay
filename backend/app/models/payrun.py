import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    Enum,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class PayrunStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Payrun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payruns"

    __table_args__ = (
        UniqueConstraint(
            "period_start",
            "period_end",
            name="uq_payruns_period",
        ),
    )

    period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    payment_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[PayrunStatus] = mapped_column(
        Enum(PayrunStatus),
        default=PayrunStatus.DRAFT,
        nullable=False,
    )

    employee_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_gross: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    total_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    total_net: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    payslips: Mapped[list["Payslip"]] = relationship(
        back_populates="payrun",
    )