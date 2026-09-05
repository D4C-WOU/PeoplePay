import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class PayslipStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Payslip(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payslips"

    payrun_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("payruns.id", ondelete="RESTRICT"),
        nullable=False,
    )

    employee_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    contract_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True,
    )

    employee_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    employee_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    deductions_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    status: Mapped[PayslipStatus] = mapped_column(
        Enum(PayslipStatus),
        default=PayslipStatus.DRAFT,
        nullable=False,
    )

    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    payrun: Mapped["Payrun"] = relationship(
        back_populates="payslips",
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="payslips",
    )

    contract: Mapped["Contract | None"] = relationship(
        back_populates="payslips",
    )

    lines: Mapped[list["PayslipLine"]] = relationship(
        back_populates="payslip",
    )