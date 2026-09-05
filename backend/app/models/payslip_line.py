from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import UUIDMixin


class PayslipLine(UUIDMixin, Base):
    __tablename__ = "payslip_lines"

    payslip_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "payslips.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    salary_rule_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "salary_rules.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    rule_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    rule_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=1,
        nullable=False,
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        default=0,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    payslip: Mapped["Payslip"] = relationship(
        back_populates="lines",
    )

    salary_rule: Mapped["SalaryRule | None"] = relationship(
        back_populates="payslip_lines",
    )