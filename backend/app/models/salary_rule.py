import enum
from decimal import Decimal

from sqlalchemy import (
    Boolean,
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


class SalaryRuleCategory(str, enum.Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    TAX = "TAX"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"


class CalculationType(str, enum.Enum):
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"
    FORMULA = "FORMULA"


class SalaryRule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "salary_rules"

    __table_args__ = (
        UniqueConstraint(
            "salary_structure_id",
            "code",
            name="uq_salary_rules_structure_code",
        ),
    )

    salary_structure_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "salary_structures.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[SalaryRuleCategory] = mapped_column(
        Enum(SalaryRuleCategory),
        nullable=False,
    )

    calculation_type: Mapped[CalculationType] = mapped_column(
        Enum(CalculationType),
        default=CalculationType.FIXED,
        nullable=False,
    )

    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )

    formula: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    salary_structure: Mapped["SalaryStructure"] = relationship(
        back_populates="rules",
    )

    payslip_lines: Mapped[list["PayslipLine"]] = relationship(
        back_populates="salary_rule",
    )