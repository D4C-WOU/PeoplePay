import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class ContractType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"


class ContractStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    CANCELLED = "CANCELLED"


class Contract(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "contracts"

    employee_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    salary_structure_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "salary_structures.id",
            ondelete="RESTRICT",
        ),
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

    contract_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    contract_type: Mapped[ContractType] = mapped_column(
        Enum(ContractType),
        default=ContractType.FULL_TIME,
        nullable=False,
    )

    base_salary: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=0,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus),
        default=ContractStatus.ACTIVE,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="contracts",
    )

    salary_structure: Mapped["SalaryStructure"] = relationship(
        back_populates="contracts",
    )

    work_schedule: Mapped["WorkSchedule | None"] = relationship(
        back_populates="contracts",
    )

    payslips: Mapped[list["Payslip"]] = relationship(
        back_populates="contract",
    )